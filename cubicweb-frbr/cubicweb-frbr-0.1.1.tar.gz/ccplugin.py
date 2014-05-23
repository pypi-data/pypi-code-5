import os
import os.path as osp

from cubicweb.cwctl import CWCTL

from cubes.dataio.xy import XY
from cubes.dataio import interfaces
from cubes.dataio.dataimport import MassiveObjectStore, RDFStore
from cubes.dataio.ccplugin import ImportRDFCommand, _init_cw_connection


class DatabnfImportRDFCommand(ImportRDFCommand):
    """
    Command for importing databnf rdf data
    """
    name = 'import-databnf-rdf'

    def _create_store(self, session, XY):
        external_uris = dict(session.execute('Any U, X WHERE X is ExternalUri, X uri U'))
        internal_store = MassiveObjectStore(session, replace_sep=u' ',
                                            eids_seq_range=10000,
                                            commit_at_flush=False,
                                            autoflush_metadata=False)
        store = RDFStore(session, XY,
                         internal_store=internal_store,
                         external_uris_dict=external_uris)
        self.internal_count = 0
        return store, internal_store

    def _step_flush(self, store, internal_store):
        if self.internal_count and self.internal_count % 10 == 0:
            print 'Flushing', self.internal_count
            internal_store.flush()
        self.internal_count += 1

    def _final_flush(self, store, internal_store):
        internal_store.flush()
        internal_store.flush_meta_data()
        store.convert_all_relations()
        internal_store.cleanup()
        store.commit()
        internal_store.commit()

    def cleanup(self, session):
        # Remove "empty" entity relations
        for subj, obj, new_rtype, etype in (('manifestation', 'work',
                                             'work_manifested', 'WorkManifested'),
                                            ('manifestation', 'contributor',
                                             'contributors', 'Contribution'),
                                            ('manifestation', 'subject',
                                             'subject_manifested', 'SubjectManifested')):
            # Delete entity table
            _sql = ('DELETE FROM cw_%s AS C WHERE NOT EXISTS ('
                    'SELECT * FROM %s_relation AS SU WHERE C.cw_eid=SU.eid_from) '
                    'OR NOT EXISTS (SELECT * FROM %s_relation AS SU WHERE C.cw_eid=SU.eid_from)'
                    % (etype.lower(), subj, obj))
            session.system_sql(_sql)
            # Delete from entities
            _sql = ("DELETE FROM entities AS C WHERE C.type='%s' "
                    "AND NOT EXISTS(SELECT * FROM cw_%s AS T WHERE T.cw_eid=C.eid)"
                    % (etype, etype.lower()))
            session.system_sql(_sql)
            # Cleanup meta tables
            for table in ('is_relation', 'is_instance_of_relation',
                          'cw_source_relation', 'owned_by_relation', 'created_by_relation',
                          '%s_relation' % subj, '%s_relation' % obj):
                _sql = ("DELETE FROM %s AS C WHERE NOT EXISTS ( "
                        "SELECT E.eid FROM entities AS E WHERE C.eid_from=E.eid)" % table)
                session.system_sql(_sql)
            # Inserting shortcuts
            _sql = ('INSERT INTO %(r)s_relation SELECT DISTINCT SU.eid_to, OB.eid_to '
                    'FROM %(s)s_relation AS SU, %(o)s_relation AS OB '
                    'WHERE SU.eid_from=OB.eid_from'
                    % {'r': new_rtype, 's': subj, 'o': obj})
            session.system_sql(_sql)
        session.commit()
        session.set_cnxset()

    def print_stats(self, session):
        # Print some statistics
        etypes = ('Work', 'Expression', 'Manifestation', 'Item',
                  'Contribution', 'WorkManifested', 'SubjectManifested',
                  'Agent', 'Person', 'CorporateBody', 'Family',
                  'Place',' Event', 'Name', 'Subject', 'Concept', 'Object')
        for etype in etypes:
            print etype, '>>>', session.execute('Any COUNT(X) WHERE X is %s' % etype)[0][0]
        rtypes = ('realized_through', 'embodied_in', 'exemplified_by',
                  'main_author', 'close_match', 'exact_match',
                  'same_as', 'see_also', 'depictions',
                  'work_manifested', 'contributors', 'subject_manifested',
                  'related_concept', 'broader_concept', 'aggregated_by')
        for rtype in rtypes:
            print rtype, '>>>', session.execute('Any COUNT(X) WHERE X %s Y' % rtype)[0][0]


    def group_files(self, directory):
        """ Create couples of files that should be imported together
        """
        # We have a list from dataio command
        directory = directory[0]
        seen_files = set()
        for fname in os.listdir(directory):
            fname = osp.join(directory, fname)
            if fname in seen_files:
                continue
            seen_files.add(fname)
            # Compute related file fname
            try:
                num = osp.splitext(fname)[0].rsplit('_', 1)[-1]
                next_num = str('%04i' % (int(num) + 1))
            except:
                continue
            if 'editions' in fname and '__manif_' in fname:
                _new_fname = fname.replace('__manif_%s' % num,
                                           '__expr_%s' % next_num)
                if osp.exists(_new_fname):
                    seen_files.add(_new_fname)
                    yield (fname, _new_fname)
                    continue
            elif 'person_authors__skos_' in fname:
                _new_fname = fname.replace('_person_authors__skos_%s' % num,
                                           '_person_authors__foaf_%s' % next_num)
                if osp.exists(_new_fname):
                    seen_files.add(_new_fname)
                    yield (fname, _new_fname)
                    continue
            elif 'org_authors__skos_' in fname:
                _new_fname = fname.replace('_org_authors__skos_%s' % num,
                                           '_org_authors__foaf_%s' % next_num)
                if osp.exists(_new_fname):
                    seen_files.add(_new_fname)
                    yield (fname, _new_fname)
                    continue
            elif '_works__skos_' in fname:
                _new_fname = fname.replace('_works__skos_%s' % num,
                                           '_works__frbr_%s' % next_num)
                if osp.exists(_new_fname):
                    seen_files.add(_new_fname)
                    yield (fname, _new_fname)
                    continue
            elif '_rameau__skos_' in  fname:
                yield (fname,)
                continue
            elif ('_works__manifestations_' in fname or '_contributions_' in fname
                  or '_docrameau_' in fname or '_study_' in fname):
                yield (fname,)
                continue

    def run(self, args):
        appid = args.pop(0)
        cw_cnx, session = _init_cw_connection(appid)
        session.set_pool()
        # Create the internal store and the RDF store
        store, internal_store = self._create_store(session, XY)
        # Push grouped filenames
        for _filenames in self.group_files(args):
            if len(_filenames) == 1 and 'rameau__skos' in _filenames[0] :
                dicts= interfaces.iterate_build_uri_dict(_filenames, library=self.config.lib,
                                                         rdf_format=self.config.rdf_format,
                                                         max_size=1000)
            else:
                uri_dictionary = interfaces.build_uri_dict(_filenames, library=self.config.lib,
                                                           rdf_format=self.config.rdf_format)
                dicts = (uri_dictionary,)
            for uri_dictionary in dicts:
                uri_dictionary = XY.merge_uri_dictionary(uri_dictionary)
                # Import entities
                self.push_uri_dictionary(store, uri_dictionary)
                # Flush
                self._step_flush(store, internal_store)
        # Final flush
        print 'Final flush'
        self._final_flush(store, internal_store)
        print 'Cleanup'
        self.cleanup(session)
        self.print_stats(session)


CWCTL.register(DatabnfImportRDFCommand)
