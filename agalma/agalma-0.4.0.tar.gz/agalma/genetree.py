# Agalma - an automated phylogenomics workflow
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
Builds gene trees for each alignment of homologous sequences, it builds a
phylogenetic tree using the maximum likelihood optimality criterion as
implemented in RAxML (see http://www.exelixis-lab.org/ and
doi:10.1093/bioinformatics/btl446).

Builds a species tree when the input is a single supermatrix alignment.

Use either ALIGN_DIR or --previous for a specific set of alignments, otherwise
this pipeline will search for the output from the most recent run of multalign,
multalignx, or supermatrix for the given catalog ID.
"""

import os
import random
import sys
from Bio import AlignIO
from dendropy import Tree
from glob import glob
from agalma import config
from biolite import diagnostics
from biolite import report
from biolite import utils
from biolite import wrappers

from biolite.pipeline import Pipeline

pipe = Pipeline('genetree', __doc__)

### ARGUMENTS ###

pipe.add_path_arg('align_dir', nargs='?', metavar='DIR', default=None, help="""
	An explicit path to a directory containing a FASTA (.fa) file for
	each alignment.""")

pipe.add_arg('--previous', '-p', metavar='RUN_ID', default=None, help="""
	Use the alignments from a previous run of multalign of multalignx.""")

pipe.add_arg('--seq_type', '-t', default='protein', help="""
	Type of alignments: either protein or nucleotide sequences.""")

pipe.add_arg('--model', '-m', default='PROTGAMMAWAG', help="""
	The substitution model of evolution for RAxML.""")

pipe.add_arg('--bootstrap', '-b', type=int, default=0, help="""
	Number of bootstrap replicates to run for RAxML.""")

pipe.add_arg('--raxml_flags', '-f', default='', help="""
	Extra parameters to pass to RAxML. Make sure the flags make sense: refer to
	the RAxML Manual for help.""")

### STAGES ###

@pipe.stage
def init(id, seq_type, previous, align_dir):
	"""Determine path to input alignments"""

	if seq_type == 'protein': key = 'protdir'
	elif seq_type == 'nucleotide': key = 'nucdir'
	else: utils.die("unknown sequence type", seq_type)

	align_dir = diagnostics.lookup_prev_val(
					id, previous, align_dir, key, 'multalign', 'multalignx')

	if not align_dir:
		utils.die("could not determine alignment directory")

	ingest('align_dir')


@pipe.stage
def convert_format(align_dir, outdir):
	"""Convert alignments from fasta to phylip format"""

	phylip_dir = "phylip-alignments"
	utils.safe_mkdir(phylip_dir)

	for fasta in glob(os.path.join(align_dir, '*.fa')):
		basename = os.path.splitext(os.path.basename(fasta))[0]
		phylip = os.path.join(phylip_dir, basename + '.phy')
		# Convert to phylip-relaxed to allow taxon names longer than 10
		try:
			AlignIO.convert(fasta, 'fasta', phylip, 'phylip-relaxed')
		except ValueError:
			utils.info("warning: skipping empty cluster '%s'" % basename)

	ingest('phylip_dir')


@pipe.stage
def genetrees(phylip_dir, seq_type, model, bootstrap, raxml_flags, outdir):
	"""Build gene trees"""

	prot_models = ('PROTCATWAG', 'PROTCATLG',
	               'PROTGAMMAWAG', 'PROTGAMMALG')
	nuc_models = ('GTRMIX', 'GTRCAT', 'GTRGAMMA')

	if seq_type == 'protein' and model not in prot_models:
		utils.die(
			"%s is not a valid model for %s sequences" % (model, seq_type))
	elif seq_type == 'nucleotide' and model not in nuc_models:
		utils.die(
			"%s is not a valid model for %s sequences" % (model, seq_type))

	raxml_dir = os.path.join(outdir, 'raxml-trees')
	utils.safe_mkdir(raxml_dir)

	if bootstrap > 0:
		# Configure raxml to run both bootstraps and ml
		seed = 12345
		raxml_flags = '-f a -N {0} -x {1} '.format(bootstrap, seed) + raxml_flags

	commands = "genetree.sh"
	with open(commands, 'w') as f:
		for phylip in glob(os.path.join(phylip_dir, '*.phy')):
			basename = os.path.splitext(os.path.basename(phylip))[0]
			pars_rseed = random.randint(0,sys.maxint)
			print >>f, '{0} -s {1} -n {2} -m {3} -w {4} {5} -T {6} -p {7}'.format(
				config.get_command('raxml')[0], phylip, basename, model,
				raxml_dir, raxml_flags, config.get_resource('threads'),
				pars_rseed)
	# Run RAxML
	wrappers.Parallel(
		commands, "--joblog genetree.log --resume-failed --halt 1",
		threads=1)

	finish('raxml_dir')


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

# vim: noexpandtab ts=4 sw=4
