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
Maps expression-only datasets to an assembly, estimates the read count for each
transcript in the assembly (at the gene and isoform level), and loads these
counts into the Agalma database.
"""

from collections import namedtuple
from agalma import config
from agalma import database
from biolite import diagnostics
from biolite import report
from biolite import utils
from biolite import workflows
from biolite.pipeline import IlluminaPipeline

pipe = IlluminaPipeline('expression', __doc__)

Header = namedtuple(
	'Header',
	"gene isoform confidence genome_type molecule_type")

### ARGUMENTS ###

pipe.add_arg('load_id', metavar='LOAD_ID', help="""
	Load ID for the assembly to use as the reference, or a catalog ID to
	lookup the last load run for that catalog ID.""")

### STAGES ###

@pipe.stage
def find_assembly(id, load_id):
	"""Find assembly in the Agalma database and write to a FASTA file"""

	try:
		load_id = int(load_id)
	except ValueError:
		try:
			load_id = diagnostics.lookup_prev_run(load_id, None, 'load').run_id
		except AttributeError:
			utils.die("no previous loads found for id", load_id)


	assembly = 'assembly.fa'
	headers = {}

	sql = """
		SELECT
			nucleotide_header, nucleotide_seq,
			gene, isoform, confidence, genome_type, molecule_type
		FROM sequences
		WHERE run_id=?;"""

	with open(assembly, 'w') as f:
		for row in database.execute(sql, (load_id,)):
			header = row[0].partition(' ')[0]
			utils.write_fasta(f, row[1], header)
			headers[header] = Header(*row[2:])

	workflows.assembly.stats(assembly)

	ingest('assembly', 'headers')


@pipe.stage
def quantify(data, assembly, outdir):
	"""Build a table of the number of reads covering each transcript"""

	genes, isoforms = workflows.transcriptome.quantify(
									assembly, 'quantify', data[-1], outdir)
	ingest('genes', 'isoforms')


@pipe.stage
def parse_quantify(_run_id, id, headers, genes, isoforms):
	"""Parse the quantified genes to populate the fields of the database"""

	rows = []

	with open(genes) as f:
		next(f) # burn the header line
		for line in f:
			fields = line.rstrip().split()
			expression = float(fields[4])
			rows.append((
				None, _run_id, id,
				fields[0], -1, 0, expression, database.genome_types['unknown'],
				database.molecule_types['unknown'], ''))

	with open(isoforms) as f:
		next(f) # burn the header line
		for line in f:
			fields = line.rstrip().split()
			header = headers[fields[0]]
			expression = float(fields[4])
			rows.append((
				None, _run_id, id,
				header.gene, header.isoform, header.confidence, expression,
				header.genome_type, header.molecule_type, ''))

	ingest('rows')


@pipe.stage
def commit(_run_id, rows):
	"""Commit expression levels to the Agalma database"""

	if not rows:
		utils.info("skipping: no rows were populated")
		return

	database.execute('BEGIN')

	# Clear any previous/failed loads
	database.execute("DELETE FROM expression WHERE run_id=?;", (_run_id,))

	sql = "INSERT INTO expression VALUES (%s);" % (','.join(['?'] * len(rows[0])))
	database.executemany(sql, rows)

	database.execute("COMMIT")


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
		# Generators

# vim: noexpandtab ts=4 sw=4
