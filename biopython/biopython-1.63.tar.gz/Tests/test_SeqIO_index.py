# Copyright 2009-2012 by Peter Cock.  All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

"""Unit tests for Bio.SeqIO.index(...) and index_db() functions."""

try:
    import sqlite3
except ImportError:
    #Try and run what tests we can on Python 2.4 or Jython
    #where we don't expect this to be installed.
    sqlite3 = None

import sys
import os
import unittest
import tempfile
import gzip
import warnings
from io import BytesIO

from Bio._py3k import _as_bytes, _bytes_to_string, StringIO

from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
from Bio.SeqIO._index import _FormatToRandomAccess
from Bio.Alphabet import generic_protein, generic_nucleotide, generic_dna

from seq_tests_common import compare_record

from Bio import BiopythonParserWarning
from Bio import MissingPythonDependencyError
try:
    from test_bgzf import _have_bug17666
    do_bgzf = _have_bug17666()
except MissingPythonDependencyError:
    do_bgzf = False

def add_prefix(key):
    """Dummy key_function for testing index code."""
    return "id_" + key


def gzip_open(filename, format):
    #At time of writing, under Python 3.2.2 seems gzip.open(filename, mode)
    #insists on giving byte strings (i.e. binary mode)
    #See http://bugs.python.org/issue13989
    if sys.version_info[0] < 3 or format in SeqIO._BinaryFormats:
        return gzip.open(filename)
    handle = gzip.open(filename)
    data = handle.read()  # bytes!
    handle.close()
    return StringIO(_bytes_to_string(data))


if sqlite3:
    class OldIndexTest(unittest.TestCase):
        """Testing a pre-built index (make sure cross platform etc).

        >>> from Bio import SeqIO
        >>> d = SeqIO.index_db("triple_sff.idx", ["E3MFGYR02_no_manifest.sff", "greek.sff", "paired.sff"], "sff")
        >>> len(d)
        54
        """
        def test_old(self):
            """Load existing index with no options."""
            d = SeqIO.index_db("Roche/triple_sff.idx")
            self.assertEqual(54, len(d))

        def test_old_format(self):
            """Load existing index with correct format."""
            d = SeqIO.index_db("Roche/triple_sff.idx", format="sff")
            self.assertEqual(54, len(d))

        def test_old_format_wrong(self):
            """Load existing index with wrong format."""
            self.assertRaises(ValueError, SeqIO.index_db,
                              "Roche/triple_sff.idx", format="fasta")

        def test_old_files(self):
            """Load existing index with correct files."""
            d = SeqIO.index_db("Roche/triple_sff.idx",
                               ["E3MFGYR02_no_manifest.sff", "greek.sff", "paired.sff"])
            self.assertEqual(54, len(d))

        def test_old_files_wrong(self):
            """Load existing index with wrong files."""
            self.assertRaises(ValueError, SeqIO.index_db,
                              "Roche/triple_sff.idx", ["a.sff", "b.sff", "c.sff"])

        def test_old_files_wrong2(self):
            """Load existing index with wrong number of files."""
            self.assertRaises(ValueError, SeqIO.index_db,
                              "Roche/triple_sff.idx",
                              ["E3MFGYR02_no_manifest.sff", "greek.sff"])


class IndexDictTests(unittest.TestCase):
    """Cunning unit test where methods are added at run time."""
    def setUp(self):
        h, self.index_tmp = tempfile.mkstemp("_idx.tmp")
        os.close(h)

    def tearDown(self):
        if os.path.isfile(self.index_tmp):
            os.remove(self.index_tmp)

    def simple_check(self, filename, format, alphabet, comp):
        """Check indexing (without a key function)."""
        if comp:
            h = gzip_open(filename, format)
            id_list = [rec.id for rec in SeqIO.parse(h, format, alphabet)]
            h.close()
        else:
            id_list = [rec.id for rec in SeqIO.parse(filename, format, alphabet)]

        rec_dict = SeqIO.index(filename, format, alphabet)
        self.check_dict_methods(rec_dict, id_list, id_list)
        rec_dict.close()
        del rec_dict

        if not sqlite3:
            return

        #In memory,
        #note here give filenames as list of strings
        rec_dict = SeqIO.index_db(":memory:", [filename], format,
                                  alphabet)
        self.check_dict_methods(rec_dict, id_list, id_list)
        rec_dict.close()
        del rec_dict

        #check error conditions
        self.assertRaises(ValueError, SeqIO.index_db,
                          ":memory:", format="dummy")
        self.assertRaises(ValueError, SeqIO.index_db,
                          ":memory:", filenames=["dummy"])

        #Saving to file...
        index_tmp = self.index_tmp
        if os.path.isfile(index_tmp):
            os.remove(index_tmp)

        #To disk,
        #note here we give the filename as a single string
        #to confirm that works too (convience feature).
        rec_dict = SeqIO.index_db(index_tmp, filename, format,
                                  alphabet)
        self.check_dict_methods(rec_dict, id_list, id_list)
        rec_dict.close()
        rec_dict._con.close()  # hack for PyPy
        del rec_dict

        #Now reload it...
        rec_dict = SeqIO.index_db(index_tmp, [filename], format,
                                  alphabet)
        self.check_dict_methods(rec_dict, id_list, id_list)
        rec_dict.close()
        rec_dict._con.close()  # hack for PyPy
        del rec_dict

        #Now reload without passing filenames and format
        rec_dict = SeqIO.index_db(index_tmp, alphabet=alphabet)
        self.check_dict_methods(rec_dict, id_list, id_list)
        rec_dict.close()
        rec_dict._con.close()  # hack for PyPy
        del rec_dict
        os.remove(index_tmp)

    def key_check(self, filename, format, alphabet, comp):
        """Check indexing with a key function."""
        if comp:
            h = gzip_open(filename, format)
            id_list = [rec.id for rec in SeqIO.parse(h, format, alphabet)]
            h.close()
        else:
            id_list = [rec.id for rec in SeqIO.parse(filename, format, alphabet)]

        key_list = [add_prefix(id) for id in id_list]
        rec_dict = SeqIO.index(filename, format, alphabet, add_prefix)
        self.check_dict_methods(rec_dict, key_list, id_list)
        rec_dict.close()
        del rec_dict

        if not sqlite3:
            return

        #In memory,
        rec_dict = SeqIO.index_db(":memory:", [filename], format, alphabet,
                                  add_prefix)
        self.check_dict_methods(rec_dict, key_list, id_list)
        #check error conditions
        self.assertRaises(ValueError, SeqIO.index_db,
                          ":memory:", format="dummy",
                          key_function=add_prefix)
        self.assertRaises(ValueError, SeqIO.index_db,
                          ":memory:", filenames=["dummy"],
                          key_function=add_prefix)
        rec_dict.close()
        del rec_dict

        #Saving to file...
        index_tmp = filename + ".key.idx"
        if os.path.isfile(index_tmp):
            os.remove(index_tmp)
        rec_dict = SeqIO.index_db(index_tmp, [filename], format, alphabet,
                                  add_prefix)
        self.check_dict_methods(rec_dict, key_list, id_list)
        rec_dict.close()
        rec_dict._con.close()  # hack for PyPy
        del rec_dict

        #Now reload it...
        rec_dict = SeqIO.index_db(index_tmp, [filename], format, alphabet,
                                  add_prefix)
        self.check_dict_methods(rec_dict, key_list, id_list)
        rec_dict.close()
        rec_dict._con.close()  # hack for PyPy
        del rec_dict

        #Now reload without passing filenames and format
        rec_dict = SeqIO.index_db(index_tmp, alphabet=alphabet,
                                  key_function=add_prefix)
        self.check_dict_methods(rec_dict, key_list, id_list)
        rec_dict.close()
        rec_dict._con.close()  # hack for PyPy
        del rec_dict
        os.remove(index_tmp)
        #Done

    def check_dict_methods(self, rec_dict, keys, ids):
        self.assertEqual(set(keys), set(rec_dict.keys()))
        #This is redundant, I just want to make sure len works:
        self.assertEqual(len(keys), len(rec_dict))
        #Make sure boolean evaluation works
        self.assertEqual(bool(keys), bool(rec_dict))
        for key, id in zip(keys, ids):
            self.assertTrue(key in rec_dict)
            self.assertEqual(id, rec_dict[key].id)
            self.assertEqual(id, rec_dict.get(key).id)
        #Check non-existant keys,
        assert chr(0) not in keys, "Bad example in test"
        try:
            rec = rec_dict[chr(0)]
            raise ValueError("Accessing a non-existent key should fail")
        except KeyError:
            pass
        self.assertEqual(rec_dict.get(chr(0)), None)
        self.assertEqual(rec_dict.get(chr(0), chr(1)), chr(1))
        if hasattr(dict, "iteritems"):
            #Python 2.x
            for key, rec in rec_dict.items():
                self.assertTrue(key in keys)
                self.assertTrue(isinstance(rec, SeqRecord))
                self.assertTrue(rec.id in ids)
        else:
            #Python 3
            assert not hasattr(rec_dict, "iteritems")
            for key, rec in rec_dict.items():
                self.assertTrue(key in keys)
                self.assertTrue(isinstance(rec, SeqRecord))
                self.assertTrue(rec.id in ids)
            for rec in rec_dict.values():
                self.assertTrue(key in keys)
                self.assertTrue(isinstance(rec, SeqRecord))
                self.assertTrue(rec.id in ids)
        #Check the following fail
        self.assertRaises(NotImplementedError, rec_dict.popitem)
        self.assertRaises(NotImplementedError, rec_dict.pop, chr(0))
        self.assertRaises(NotImplementedError, rec_dict.pop, chr(0), chr(1))
        self.assertRaises(NotImplementedError, rec_dict.clear)
        self.assertRaises(NotImplementedError, rec_dict.__setitem__, "X", None)
        self.assertRaises(NotImplementedError, rec_dict.copy)
        self.assertRaises(NotImplementedError, rec_dict.fromkeys, [])

    def get_raw_check(self, filename, format, alphabet, comp):
        #Also checking the key_function here
        if comp:
            h = gzip.open(filename, "rb")
            raw_file = h.read()
            h.close()
            h = gzip_open(filename, format)
            id_list = [rec.id.lower() for rec in
                       SeqIO.parse(h, format, alphabet)]
            h.close()
        else:
            h = open(filename, "rb")
            raw_file = h.read()
            h.close()
            id_list = [rec.id.lower() for rec in
                       SeqIO.parse(filename, format, alphabet)]

        if format in ["sff"]:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', BiopythonParserWarning)
                rec_dict = SeqIO.index(filename, format, alphabet,
                                       key_function = lambda x : x.lower())
        else:
            rec_dict = SeqIO.index(filename, format, alphabet,
                                   key_function = lambda x : x.lower())

        self.assertEqual(set(id_list), set(rec_dict.keys()))
        self.assertEqual(len(id_list), len(rec_dict))
        for key in id_list:
            self.assertTrue(key in rec_dict)
            self.assertEqual(key, rec_dict[key].id.lower())
            self.assertEqual(key, rec_dict.get(key).id.lower())
            raw = rec_dict.get_raw(key)
            self.assertTrue(raw.strip())
            self.assertTrue(raw in raw_file)
            rec1 = rec_dict[key]
            #Following isn't very elegant, but it lets me test the
            #__getitem__ SFF code is working.
            if format in SeqIO._BinaryFormats:
                handle = BytesIO(raw)
            else:
                handle = StringIO(_bytes_to_string(raw))
            if format == "sff":
                rec2 = SeqIO.SffIO._sff_read_seq_record(handle,
                            rec_dict._proxy._flows_per_read,
                            rec_dict._proxy._flow_chars,
                            rec_dict._proxy._key_sequence,
                            rec_dict._proxy._alphabet,
                            trim=False)
            elif format == "sff-trim":
                rec2 = SeqIO.SffIO._sff_read_seq_record(handle,
                            rec_dict._proxy._flows_per_read,
                            rec_dict._proxy._flow_chars,
                            rec_dict._proxy._key_sequence,
                            rec_dict._proxy._alphabet,
                            trim=True)
            elif format == "uniprot-xml":
                self.assertTrue(raw.startswith(_as_bytes("<entry ")))
                self.assertTrue(raw.endswith(_as_bytes("</entry>")))
                #Currently the __getitem__ method uses this
                #trick too, but we hope to fix that later
                raw = """<?xml version='1.0' encoding='UTF-8'?>
                <uniprot xmlns="http://uniprot.org/uniprot"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="http://uniprot.org/uniprot
                http://www.uniprot.org/support/docs/uniprot.xsd">
                %s
                </uniprot>
                """ % _bytes_to_string(raw)
                handle = StringIO(raw)
                rec2 = SeqIO.read(handle, format, alphabet)
            else:
                rec2 = SeqIO.read(handle, format, alphabet)
            self.assertEqual(True, compare_record(rec1, rec2))
        rec_dict.close()
        del rec_dict

    if sqlite3:
        def test_duplicates_index_db(self):
            """Index file with duplicate identifers with Bio.SeqIO.index_db()"""
            self.assertRaises(ValueError, SeqIO.index_db, ":memory:",
                              ["Fasta/dups.fasta"], "fasta")

    def test_duplicates_index(self):
        """Index file with duplicate identifers with Bio.SeqIO.index()"""
        self.assertRaises(ValueError, SeqIO.index, "Fasta/dups.fasta", "fasta")

    def test_duplicates_to_dict(self):
        """Index file with duplicate identifers with Bio.SeqIO.to_dict()"""
        handle = open("Fasta/dups.fasta", "rU")
        iterator = SeqIO.parse(handle, "fasta")
        self.assertRaises(ValueError, SeqIO.to_dict, iterator)
        handle.close()

tests = [
    ("Ace/contig1.ace", "ace", generic_dna),
    ("Ace/consed_sample.ace", "ace", None),
    ("Ace/seq.cap.ace", "ace", generic_dna),
    ("Quality/wrapping_original_sanger.fastq", "fastq", None),
    ("Quality/example.fastq", "fastq", None), #Unix newlines
    ("Quality/example.fastq", "fastq-sanger", generic_dna),
    ("Quality/example_dos.fastq", "fastq", None), #DOS/Windows newlines
    ("Quality/tricky.fastq", "fastq", generic_nucleotide),
    ("Quality/sanger_faked.fastq", "fastq-sanger", generic_dna),
    ("Quality/solexa_faked.fastq", "fastq-solexa", generic_dna),
    ("Quality/illumina_faked.fastq", "fastq-illumina", generic_dna),
    ("EMBL/epo_prt_selection.embl", "embl", None),
    ("EMBL/U87107.embl", "embl", None),
    ("EMBL/TRBG361.embl", "embl", None),
    ("EMBL/A04195.imgt", "embl", None),  # Not a proper EMBL file, an IMGT file
    ("EMBL/A04195.imgt", "imgt", None),
    ("GenBank/NC_000932.faa", "fasta", generic_protein),
    ("GenBank/NC_005816.faa", "fasta", generic_protein),
    ("GenBank/NC_005816.tsv", "tab", generic_protein),
    ("GenBank/NC_005816.ffn", "fasta", generic_dna),
    ("GenBank/NC_005816.fna", "fasta", generic_dna),
    ("GenBank/NC_005816.gb", "gb", None),
    ("GenBank/cor6_6.gb", "genbank", None),
    ("IntelliGenetics/vpu_nucaligned.txt", "ig", generic_nucleotide),
    ("IntelliGenetics/TAT_mase_nuc.txt", "ig", None),
    ("IntelliGenetics/VIF_mase-pro.txt", "ig", generic_protein),
    ("Phd/phd1", "phd", generic_dna),
    ("Phd/phd2", "phd", None),
    ("Phd/phd_solexa", "phd", generic_dna),
    ("Phd/phd_454", "phd", generic_dna),
    ("NBRF/B_nuc.pir", "pir", generic_nucleotide),
    ("NBRF/Cw_prot.pir", "pir", generic_protein),
    ("NBRF/clustalw.pir", "pir", None),
    ("SwissProt/sp001", "swiss", None),
    ("SwissProt/sp010", "swiss", None),
    ("SwissProt/sp016", "swiss", None),
    ("SwissProt/multi_ex.txt", "swiss", None),
    ("SwissProt/multi_ex.xml", "uniprot-xml", None),
    ("SwissProt/multi_ex.fasta", "fasta", None),
    ("Roche/E3MFGYR02_random_10_reads.sff", "sff", generic_dna),
    ("Roche/E3MFGYR02_random_10_reads.sff", "sff-trim", generic_dna),
    ("Roche/E3MFGYR02_index_at_start.sff", "sff", generic_dna),
    ("Roche/E3MFGYR02_index_in_middle.sff", "sff", generic_dna),
    ("Roche/E3MFGYR02_alt_index_at_start.sff", "sff", generic_dna),
    ("Roche/E3MFGYR02_alt_index_in_middle.sff", "sff", generic_dna),
    ("Roche/E3MFGYR02_alt_index_at_end.sff", "sff", generic_dna),
    ("Roche/E3MFGYR02_no_manifest.sff", "sff", generic_dna),
    ("Roche/greek.sff", "sff", generic_nucleotide),
    ("Roche/greek.sff", "sff-trim", generic_nucleotide),
    ("Roche/paired.sff", "sff", None),
    ("Roche/paired.sff", "sff-trim", None),
    ]
for filename, format, alphabet in tests:
    assert format in _FormatToRandomAccess
    tasks = [(filename, None)]
    if do_bgzf and os.path.isfile(filename + ".bgz"):
        tasks.append((filename + ".bgz", "bgzf"))
    for filename, comp in tasks:

        def funct(fn, fmt, alpha, c):
            f = lambda x : x.simple_check(fn, fmt, alpha, c)
            f.__doc__ = "Index %s file %s defaults" % (fmt, fn)
            return f
        setattr(IndexDictTests, "test_%s_%s_simple"
                    % (format, filename.replace("/", "_").replace(".", "_")),
                funct(filename, format, alphabet, comp))
        del funct

        def funct(fn, fmt, alpha, c):
            f = lambda x : x.key_check(fn, fmt, alpha, c)
            f.__doc__ = "Index %s file %s with key function" % (fmt, fn)
            return f
        setattr(IndexDictTests, "test_%s_%s_keyf"
                    % (format, filename.replace("/", "_").replace(".", "_")),
                funct(filename, format, alphabet, comp))
        del funct

        def funct(fn, fmt, alpha, c):
            f = lambda x : x.get_raw_check(fn, fmt, alpha, c)
            f.__doc__ = "Index %s file %s get_raw" % (fmt, fn)
            return f
        setattr(IndexDictTests, "test_%s_%s_get_raw"
                    % (format, filename.replace("/", "_").replace(".", "_")),
                funct(filename, format, alphabet, comp))
        del funct

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity = 2)
    unittest.main(testRunner=runner)
