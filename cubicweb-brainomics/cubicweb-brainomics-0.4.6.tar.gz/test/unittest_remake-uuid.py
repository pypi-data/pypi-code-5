import os
import os.path as osp
import tempfile
import logging
import csv
from cubicweb.utils import make_uid
from cubicweb.devtools.testlib import CubicWebTC
from cubes.brainomics.ccplugin import copy_file, update_ident_fpath, get_ids_uids_from_csv



class TestBrainomicsRemakeUid(CubicWebTC):

    def setup_database(self):
        super(TestBrainomicsRemakeUid, self).setup_database()
        ce = self.request().create_entity
        self.rql = self.session.execute
        _study = ce('Study', name=u'Test study', data_filepath=u'/tmp',
                    description=u'Test study with dummy data', keywords=u'test;dummy')
        self.subject_1 = ce('Subject', identifier=u'demo_subject_1', gender=u'female',
                            handedness=u'right')
        self.subject_2 = ce('Subject', identifier=u'demo_subject_2', gender=u'male',
                            handedness=u'ambidextrous')
        self.scan_11 = ce('Scan', identifier=u'anat_1709',
                          label=u'anatomy', type=u'normalized T1', format=u'nii.hz',
                          completed=True, valid=True, filepath=u'1709/anat.nii.gz',
                          concerns=self.subject_1, related_study=_study)
        self.scan_12 = ce('Scan', identifier=u'anat_1899',
                          label=u'anatomy', type=u'normalized T1', format=u'nii.hz',
                          completed=True, valid=True, filepath=u'1899/anat.nii.gz',
                          concerns=self.subject_1, related_study=_study)
        self.scan_21 = ce('Scan', identifier=u'anat_2325',
                          label=u'anatomy', type=u'normalized T1', format=u'nii.hz',
                          completed=True, valid=True, filepath=u'2325/anat.nii.gz',
                          concerns=self.subject_2, related_study=_study)
        self.scan_22 = ce('Scan', identifier=u'anat_3785',
                          label=u'anatomy', type=u'normalized T1', format=u'nii.hz',
                          completed=True, valid=True, filepath=u'3785/anat.nii.gz',
                          concerns=self.subject_2, related_study=_study)
        _center = ce('Center', identifier=u'testing_center', name=u'Testing Center')
        self.assessment = ce('Assessment', identifier=u'assessment_3125',
                             related_study=_study, reverse_holds=_center,
                             reverse_concerned_by=self.subject_1)
        self.log = logging.getLogger('brainomics test: remake-uuid')
        fh = logging.FileHandler('brainomics_test.log')
        self.log.addHandler(fh)

    def test_copy_file(self):
        for fpath, full_fpath in ((scan.filepath, scan.full_filepath)
                                  for scan in (self.scan_11, self.scan_12, self.scan_21, self.scan_22)):
            dest_path = osp.join(full_fpath.split(fpath)[0], 
                                 unicode(make_uid()) + '_' + osp.basename(fpath))
            with tempfile.NamedTemporaryFile(suffix=osp.basename(fpath)) as f:
                copy_file(f.name, dest_path, logger=self.log)
            if osp.isfile(dest_path):
                os.remove(dest_path)

    def test_update_fpath_nodelete(self):
        fpath_query = 'Any F WHERE X is IN (Scan, GenomicMeasure), X filepath F'
        old_fpaths = self.rql(fpath_query, build_descr=False)
        for s in self.rql('Any X WHERE X is Subject'):
            update_ident_fpath(self.session, s[0], unicode(make_uid()), logger=self.log)
        new_fpaths = self.rql(fpath_query, build_descr=False)
        self.assertNotEqual(old_fpaths, new_fpaths)

    def test_update_fpath_delete(self):
        fpath_query = 'Any F WHERE X is IN (Scan, GenomicMeasure), X filepath F'
        old_fpaths = self.rql(fpath_query, build_descr=False)
        for s in self.rql('Any X WHERE X is Subject'):
            update_ident_fpath(self.session, s[0], unicode(make_uid()), delete=True, logger=self.log)
        new_fpaths = self.rql(fpath_query, build_descr=False)
        self.assertNotEqual(old_fpaths, new_fpaths)

    def test_update_ident(self):
        ident_query = 'Any I WHERE X is IN (Scan, GenomicMeasure, QuestionnaireRun), X identifier I'
        old_idents = self.rql(ident_query, build_descr=False)
        for s in self.rql('Any X WHERE X is Subject'):
            update_ident_fpath(self.session, s[0], unicode(make_uid()), logger=self.log)
        new_idents = self.rql(ident_query)
        self.assertNotEqual(old_idents, new_idents)

    def test_update_ident_assessment(self):
        assess_ident_query = 'Any I WHERE X is Assessment, X identifier I'
        old_idents = self.rql(assess_ident_query, build_descr=False)
        for s in self.rql('Any X WHERE X is Subject'):
            update_ident_fpath(self.session, s[0], unicode(make_uid()), logger=self.log)
        new_idents = self.rql(assess_ident_query, build_descr=False)
        self.assertNotEqual(old_idents, new_idents)

    def test_get_uid_from_csv(self):
        old_new_uuids = {}
        identifiers_rset = self.rql('Any I WHERE X is Subject, X identifier I', 
                                    build_descr=False)
        # Generate test CSV
        test_csv_fname = 'external_uuids.csv'
        with open(test_csv_fname, 'wb') as csvf:
            csvw = csv.writer(csvf, delimiter='\t')
            for old_identifier in identifiers_rset: 
                old_new_uuids[old_identifier[0]] = u'test_' + unicode(make_uid())
                csvw.writerow([old_identifier[0], old_new_uuids[old_identifier[0]]])
        # Verify that the new UUIDs are correctly retrieved from the CSV
        ids_uids = get_ids_uids_from_csv(test_csv_fname, logger=self.log)
        for old_identifier in identifiers_rset:
            self.assertEqual(old_new_uuids[old_identifier[0]], 
                             ids_uids[old_identifier[0]])




if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
