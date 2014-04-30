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
    count_all_subject = 0
    global_study = store.create_entity('Study', data_filepath=unicode(base_path), name = u'openfmri',
                                       description=u'''OpenfMRI.org is a project dedicated to the free and open sharing of functional magnetic resonance imaging (fMRI) datasets, including raw data. See http://openfmri.org/''')
    # All studies
    for study_path in glob.iglob(osp.join(base_path,'*/')):
        study_id = study_path[:-1].split('/')[-1]
        print '--->', study_id
        # XXX use True metadata for studies, P.I. ...
        study = store.create_entity('Study', data_filepath=unicode(osp.abspath(study_path)),
                                    name = u'openfmri-%s' % study_id, keywords='openfmri')
        # Device
        device_path = osp.join(study_path, 'scan_key.txt')
        device_eid = None
        if osp.exists(device_path):
            device = open(device_path).readline()
            if device.strip():
                device = store.create_entity('Device', name=unicode(device.strip()),
                                             model=unicode(device.strip()))
                device_eid = device.eid
        # Tasks definition
        task_path = osp.join(study_path, 'task_key.txt')
        task_eid = None
        if osp.exists(task_path):
            ext_resource = store.create_entity('ExternalResource', name=u'task_key',
                                               related_study=study.eid,
                                               filepath=unicode(osp.relpath(task_path, start=study_path)))
            task_eid = ext_resource.eid
        # Model contrasts and condition_key
        model_path = osp.join(study_path, 'models')
        model_files = {}
        if osp.exists(model_path):
            for model in glob.iglob(osp.join(model_path, 'model*/*.txt')):
                model_id = model.split('/')[-2]
                file_id = model.split('/')[-1]
                ext_resource = store.create_entity('ExternalResource',
                                                   name=unicode(osp.splitext(file_id)[0]),
                                                   related_study=study.eid,
                                                   filepath=unicode(osp.relpath(model, start=study_path)))
                model_files.setdefault(model_id, []).append(ext_resource.eid)
        # Demographics
        demographics_path = osp.join(study_path, 'demographics.txt')
        demographics = {}
        if osp.exists(demographics_path):
            for line in open(demographics_path):
                infos = line.strip().split('\t')
                if len(infos) != 4:
                    print '!!!!', infos
                demographics[infos[1]] = {'gender': infos[2], 'age': int(infos[3])}
        # Subjects
        count_subject = 0
        for subject_path in glob.iglob(osp.join(study_path,'sub*')):
            subject_id = study_id + '_' + subject_path.split('/')[-1]
            print '--->', subject_id
            age, gender = None, None
            if subject_id in demographics:
                age = demographics[subject_id].get('age')
                gender = demographics[subject_id].get('gender')
            subject = store.create_entity('Subject', identifier=unicode(subject_id),
                                          age = age, gender=gender or u'unknown', handedness=u'unknown')
            store.relate(subject.eid, 'related_studies', study.eid)
            store.relate(subject.eid, 'related_studies', global_study.eid)
            # anatomy
            assessment = store.create_entity('Assessment',identifier=u'anat', protocol=u'anat',
                                             related_study=study.eid)
            store.relate(subject.eid, 'concerned_by', assessment.eid)
            for image in glob.iglob(osp.join(study_path, subject_path, 'anatomy/*.nii.gz')):
                image_id = image.split('/')[-1].split('.')[0]
                anat = {'identifier': u'%s_%s' % (subject_id, image_id),
                        'label': u'anatomy',
                        'format': u'nii.gz',
                        'type': u'normalized T1',
                        'related_study': study.eid,
                        'filepath': unicode(osp.relpath(image, start=study_path)),
                        'valid': True, 'completed': True, 'description': 'Image from OpenFmri'}
                mri_data = store.create_entity('MRIData', sequence=u'T1')
                # MRI data
                mri_data = {'sequence': u'T1'}
                mri_data.update(get_image_info(image))
                mri_data = store.create_entity('MRIData', **mri_data)
                anat['has_data'] = mri_data.eid
                anat = store.create_entity('Scan', **anat)
                if device_eid:
                    store.relate(anat.eid, 'uses_device', device_eid)
                store.relate(anat.eid, 'concerns', subject.eid, subjtype='Scan')
                store.relate(assessment.eid, 'generates', anat.eid, subjtype='Assessment')
            # Model
            models = {}
            for model in glob.iglob(osp.join(study_path, subject_path, 'model/*')):
                for model_path in glob.iglob(osp.join(model, '*/*/*.txt')):
                    model_id = unicode(osp.splitext(model_path.split('/')[-1])[0])
                    task_id = unicode(model_path.split('/')[-2])
                    type_id = unicode(model_path.split('/')[-3])
                    name = u'_'.join((subject_id, type_id, task_id))
                    ext_resource = store.create_entity('ExternalResource',
                                                       name=name,
                                                       related_study=study.eid,
                                                       filepath=unicode(osp.relpath(model_path, start=study_path)))
                    models.setdefault(task_id, []).append(ext_resource.eid)
            # Behav
            behavs = {}
            for behav_path in glob.iglob(osp.join(study_path, subject_path, 'behav/*')):
                    behav_id = unicode(osp.splitext(behav_path.split('/')[-1])[0])
                    task_id = unicode(behav_path.split('/')[-2])
                    type_id = unicode(behav_path.split('/')[-3])
                    name = u'_'.join((subject_id, type_id, task_id))
                    ext_resource = store.create_entity('ExternalResource',
                                                       name=name,
                                                       related_study=study.eid,
                                                       filepath=unicode(osp.relpath(behav_path, start=study_path)))
                    behavs.setdefault(task_id, []).append(ext_resource.eid)
            # Bold
            for run in glob.iglob(osp.join(study_path, subject_path, 'BOLD/*')):
                run_id = run.split('/')[-1].split('.')[0]
                assessment = store.create_entity('Assessment',identifier=unicode(run), protocol=u'fmri',
                                             related_study=study.eid)
                store.relate(subject.eid, 'concerned_by', assessment.eid)
                if task_eid:
                    store.relate(assessment.eid, 'external_resources', task_eid)
                image_id = unicode('bold')
                anat = {'identifier': u'%s_%s' % (subject_id, image_id),
                        'label': u'bold',
                        'format': u'nii.gz',
                        'type': u'raw fMRI',
                        'related_study': study.eid,
                        'filepath': unicode(osp.relpath(run+'/bold.nii.gz', start=study_path)),
                        'valid': True, 'completed': True, 'description': 'Image from OpenFmri'}
                mri_data = store.create_entity('MRIData', sequence=u'T1')
                # MRI data
                mri_data = {'sequence': u'EPI'}
                mri_data.update(get_image_info(image))
                mri_data = store.create_entity('MRIData', **mri_data)
                anat['has_data'] = mri_data.eid
                anat = store.create_entity('Scan', **anat)
                store.relate(anat.eid, 'concerns', subject.eid, subjtype='Scan')
                store.relate(assessment.eid, 'generates', anat.eid, subjtype='Assessment')
                if device_eid:
                    store.relate(anat.eid, 'uses_device', device_eid)
                for eid in models.get(run_id, []):
                    store.relate(anat.eid, 'external_resources', eid)
                for eid in behavs.get(run_id, []):
                    store.relate(anat.eid, 'external_resources', eid)
            count_subject += 1
        count_all_subject += count_subject
        print '-------> %s subjects imported for study %s' % (count_subject, study_id)
        # Flush
        store.flush()
    store.commit()
    print '-------> %s subjects imported for all_studies' % count_all_subject
