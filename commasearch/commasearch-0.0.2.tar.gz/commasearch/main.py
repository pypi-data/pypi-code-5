import os
import csv
import sys
import argparse
from urllib.parse import urlsplit

from commasearch.searcher import search
import commasearch.db as db
import commasearch.indexer.dsv as dsv
import commasearch.indexer.rdbms as rdbms

RBDMS_SCHEMES = {}
DSV_SCHEMES = {'http','https','file'}

def index(url:str):
    scheme = urlsplit(url).scheme
    if scheme in DSV_SCHEMES:
        result = dsv.index(db, url)
    elif scheme in RDBMS_SCHEMES:
        result = rdbms.index(db, url)
    else:
        raise ValueError('The scheme %s:// is not supported.')
    return result

def parser():
    epilog = '''
Data tables are either paths to local files,
links to files on the web, or SQLAlchemy URLs
to database tables. For example,

    , --index ../iris.csv /opt/ChickWeight.tsv \\
        postgres://tlevine:secretpassword@dada.pink/toilets \\
        http://big.dada.pink/scarsdale/assessments.csv

You should index a bunch of files (like with ,open,data)
before you search; otherwise, the search won't be that interesting.
'''
    p = argparse.ArgumentParser(description = 'Search with data tables.',
        epilog = epilog, formatter_class = argparse.RawDescriptionHelpFormatter)
    p.add_argument('-v', '--verbose', action = 'store_true', default = False,
        help = 'print information about how search results were chosen.')
    p.add_argument('-i', '--index', action = 'store_true', default = False,
        help = 'index the files; don\'t search.')
    p.add_argument('-f', '--force', action = 'store_true', default = False,
        help = 'refresh the index of the specified files.')
    p.add_argument('tables', metavar = '[data table]', nargs = '+',
        help = 'tables to search or index, or "-" to read from STDIN')
    return p

def add_file_scheme(maybe_url):
    if urlsplit(maybe_url).scheme == '':
        url = 'file://' + os.path.abspath(maybe_url)
    else:
        url = maybe_url
    return url

def main():
    p = parser().parse_args()
    comma(p)

def comma(p, db = db, stdin = sys.stdin, stdout = sys.stdout, stderr = sys.stderr):
    if p.tables == ['-']:
        tables = stdin
    else:
        tables = p.tables

    urls = map(add_file_scheme, tables)

    if p.index:
        for url in urls:
            if p.force or (url not in db.indices):
                if p.verbose:
                    stdout.write('Indexing %s\n' % url)
                index(url)
    else:
        url = next(urls)
        try:
            next(urls)
        except StopIteration:
            pass
        else:
            stderr.write('Warning: Using only the first file\n')
        if p.verbose:
            writer = csv.writer(stdout)
            writer.writerow(('index', 'result_url', 'overlap_count'))
            writer.writerows(search(db, url))
        else:
            for _, result_url, _ in search(db, url):
                stdout.write('/%s\n' % result_url)
