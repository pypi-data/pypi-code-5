#!/usr/bin/env python
#
# Agalma - Tools for processing gene sequence data and automating workflows
# Copyright (c) 2012-2014 Brown University. All rights reserved.
#
# This file is part of Agalma.
#
# Agalma is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Agalma is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Agalma.  If not, see <http://www.gnu.org/licenses/>.

"""
Assembles reads into transcripts, processes the assembly, and generates
assembly diagnostics. Read pairs are first filtered at a more stringent
mean quality threshold. Transcriptome assembly is generated with Trinity
assembler.
"""

import os
from glob import glob
from agalma import config
from biolite import diagnostics
from biolite import report
from biolite import utils
from biolite import workflows
from biolite import wrappers
from biolite.pipeline import IlluminaPipeline

pipe = IlluminaPipeline('assemble', __doc__)

### ARGUMENTS ###

pipe.add_arg('--quality', '-q', type=int, metavar='MIN', default=33, help="""
	Filter out reads that have a mean quality < MIN.""")

pipe.add_arg('--nreads', '-n', type=int, metavar='N', default=0, help="""
	Number of high quality reads to assemble (0 means all).""")

pipe.add_arg('--min_length', '-l', type=int, metavar='L', default=300, help="""
	Only keep transcripts longer than L nucleotides.""")

pipe.add_arg('--iworm_kmer_size', type=int, metavar='K', default=25, help="""
	k-mer size for inchworm.""")

pipe.add_arg('--chrysalis_dir', metavar='DIR', default='chrysalis', help="""
	Name of directory for chrysalis output.""")

pipe.add_arg('--max_reads_per_graph', type=int, default=200000, help="""
	Maximum number of reads to anchor within a single graph.""")

pipe.add_path_arg('--components_dir', metavar='DIR', default='components', help="""
	Name of directory for chrysalis component bins (many small files).""")

### STAGES ###

pipe.add_data_sources("sanitize", "remove_rrna")

@pipe.stage
def prep_data(id, data, quality, nreads):
	"""Filter out low-quality reads and interleave into a single FASTA file"""

	if len(data[-1]) == 1:
		fasta = ['single.fa']
		paired = False
	elif len(data[-1]) == 2:
		fasta = ['both.fa']
		paired = True
	else:
		utils.die("expected either 1 (SE) or 2 (PE) input FASTQ files")

	# Filter reads and interleave them into a single FASTA file.
	wrappers.FilterIllumina(
			data[-1], [], "-f -s / -a -b -q", quality, "-n", nreads,
			stdout=fasta[-1])
	diagnostics.log_path(fasta[-1])

	# Parse the number of reads from the diagnostics.
	entity = "%s.filter_illumina" % diagnostics.get_entity()
	nreads = int(diagnostics.local_lookup(entity)['pairs_kept'])
	diagnostics.log('nreads', nreads)

	log_state('data')
	ingest('fasta', 'paired', 'nreads')


@pipe.stage
def jellyfish(fasta, iworm_kmer_size):
	"""Count kmers with jellyfish and dump to FASTA file"""
	wrappers.JellyfishCount(fasta[-1], iworm_kmer_size, '--both-strands')
	fasta.append('jellyfish.K%d.fa' % iworm_kmer_size)
	utils.truncate_file(fasta[-1])
	for f in glob('mer_counts_*'):
		wrappers.JellyfishDump(f, stdout_append=fasta[-1])


@pipe.stage
def inchworm(fasta, iworm_kmer_size):
	"""Assemble the data into unique sequences of transcripts"""
	fasta.append('inchworm.K%d.fa' % iworm_kmer_size)
	wrappers.Inchworm(
		'--kmers', fasta[-2], '-K', iworm_kmer_size, '--DS', stdout=fasta[-1])


@pipe.stage
def chrysalis(fasta, paired, min_length, max_reads_per_graph, chrysalis_dir):
	"""Cluster the Inchworm contigs and construct de Bruijn graphs"""
	chrysalis_dir = utils.safe_mkdir(chrysalis_dir)
	args = [
		'-min', min_length,
		'-max_reads', max_reads_per_graph,
		'-o', chrysalis_dir]
	if paired:
		args += ('-paired', '-reads_for_pairs', fasta[0])
	wrappers.Chrysalis(fasta[0], fasta[-1], *args)
	wrappers.PartitionChrysalis(
		os.path.join(chrysalis_dir, 'bundled_iworm_contigs.fasta.deBruijn'),
		os.path.join(chrysalis_dir, 'readsToComponents.out.sort'),
		'-N', 1000, '-L', min_length)
	components = [
		x.rstrip().partition('\t')[2] for x in
		open(os.path.join(chrysalis_dir, 'component_base_listing.txt'))]
	ingest('components')


@pipe.stage
def quantify_graphs(components, max_reads_per_graph):
	"""Partition the full read set among the Chrysalis graphs"""
	commands = "quantify_graph.sh"
	with open(commands, 'w') as f:
		for component in components:
			print >>f, "{2} -g {0}.graph.tmp -i {0}.reads.tmp -o {0}.graph.out -max_reads {1}".format(component, max_reads_per_graph, config.get_command('QuantifyGraph')[0])
	wrappers.Parallel(
		commands, "--joblog quantify_graph.log --resume-failed --halt 1")


@pipe.stage
def butterfly(components, paired, min_length):
	"""Trace the read paths and construct alternatively spliced isoforms"""
	if paired: reinforcement = 75
	else: reinforcement = 25

	threads = int(config.get_resource('threads'))
	max_mem = utils.mem_to_mb(config.get_resource('memory')) / threads
	min_mem = min(256, max_mem)

	# Java uses roughly 2 CPUs per Butterfly call with GC etc. so reduce
	# the number of threads by half.
	threads = max(1, threads/2)

	commands = "butterfly.sh"
	with open(commands, 'w') as f:
		for component in components:
			print >>f, "{} -Xms{}M -Xmx{}M -jar {} -N 100000 -L {} -F {} -C {}.graph --max_number_of_paths_per_node=10 --path_reinforcement_distance={} --triplet-lock".format(
				config.get_command('java')[0], min_mem, max_mem,
				config.get_command('butterfly')[0],
				min_length, int(diagnostics.lookup_insert_size().max),
				component, reinforcement)

	wrappers.Parallel(
		commands, "--joblog butterfly.log --resume-failed --halt 1",
		max_concurrency=threads)


@pipe.stage
def write_assembly(nreads, components, min_length, outdir):
	"""Write out contigs with Oases-style headers"""
	assembly = os.path.join(outdir, 'assembly_trinity_%d.fa' % nreads)
	workflows.transcriptome.write_trinity(components, assembly)
	diagnostics.log_path(assembly)
	finish('assembly')


### RUN ###

if __name__ == "__main__":
	# Run the pipeline.
	pipe.run()
	# Push the local diagnostics to the global database.
	diagnostics.merge()

### REPORT ###

class Report(report.BaseReport):
	def init(self):
		self.name = pipe.name
		# Lookups
		self.lookup('filter', 'assemble.prep_data.filter_illumina')
		self.percent('filter', 'percent_kept', 'pairs_kept', 'pairs')
		if 'filter' in self.data:
			# Pull the quality treshold out of the command arguments.
			self.data.filter['quality'] = self.extract_arg(
								'assemble.prep_data.filter_illumina', '-q')
		# Generators
		self.generator(self.filter_table)

	def filter_table(self):
		if 'filter' in self.data:
			html = [self.header("Illumina Filtering")]
			html += self.summarize(report.filter_schema, 'filter')
			return html

# vim: noexpandtab ts=4 sw=4
