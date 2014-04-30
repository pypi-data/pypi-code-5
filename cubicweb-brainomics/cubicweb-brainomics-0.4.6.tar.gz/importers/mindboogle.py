# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import os.path as osp
import glob

import nibabel as nb

from cubicweb.dataimport import SQLGenObjectStore as Store

from cubes.brainomics.importers.helpers import get_image_info


if __name__ == '__main__':
    base_path = osp.abspath(sys.argv[4])
    store = Store(session)
    global_study = store.create_entity('Study', data_filepath=unicode(base_path), name = u'mindboggle',
                                       description=u'''The Mindboggle-101 dataset includes manually labeled anatomical regions for 101 healthy subjects. The manually edited cortical labels follow sulcus landmarks according to the Desikan-Killiany-Tourville (DKT) protocol. See http://www.frontiersin.org/Brain_Imaging_Methods/10.3389/fnins.2012.00171/full “101 labeled brain images and a consistent human cortical labeling protocol”
Arno Klein, Jason Tourville. Frontiers in Brain Imaging Methods. 6:171. DOI: 10.3389/fnins.2012.00171
    and http://mindboggle.info/data.html''')
    for study_path in ('Extra-18_volumes', 'MMRR-21_volumes', 'NKI-RS-22_volume',
                       'NKI-TRT-20_volumes', 'OASIS-TRT-20_volumes'):
        full_study_path = osp.join(base_path, study_path)
        if not osp.exists(full_study_path):
            print '%s does not exist, skip it' % full_study_path
            continue
        # Create study
        count_subject = 0
        study = store.create_entity('Study', data_filepath=unicode(full_study_path),
                                    name = unicode(study_path))
        for subject_path in glob.iglob(osp.join(full_study_path,'*')):
            subject_id = subject_path.split('/')[-1]
            print '--->', subject_id
            subject = store.create_entity('Subject', identifier=unicode(subject_id),
                                          gender=u'unknown', handedness=u'unknown')
            store.relate(subject.eid, 'related_studies', study.eid)
            store.relate(subject.eid, 'related_studies', global_study.eid)
            assessment = store.create_entity('Assessment',identifier=u'label',
                                             related_study=study.eid,
                                             protocol=u'mindboggle-label')
            store.relate(subject.eid, 'concerned_by', assessment.eid)
            for image in glob.iglob(osp.join(full_study_path, subject_path, '*.nii.gz')):
                image_id = image.split('/')[-1].split('.')[0]
                anat = {'identifier': u'%s_%s' % (subject_id, image_id),
                        'label': u'labels' if 'labels' in image_id else u'anatomy',
                        'format': u'nii.gz',
                        'type': u'normalized T1',
                        'related_study': study.eid,
                        'filepath': unicode(osp.relpath(image, start=full_study_path)),
                        'valid': True, 'completed': True, 'description': 'Image from Mindboggle'}
                mri_data = store.create_entity('MRIData', sequence=u'T1')
                # MRI data
                mri_data = {'sequence': u'T1'}
                mri_data.update(get_image_info(image))
                mri_data = store.create_entity('MRIData', **mri_data)
                anat['has_data'] = mri_data.eid
                anat['related_study'] = study.eid
                anat = store.create_entity('Scan', **anat)
                store.relate(anat.eid, 'concerns', subject.eid, subjtype='Scan')
                store.relate(assessment.eid, 'generates', anat.eid, subjtype='Assessment')
            count_subject += 1
        # Flush
        store.flush()
        store.commit()
        print '-------> %s subjects imported for %s' % (count_subject, study_path)
