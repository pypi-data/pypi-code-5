# core Python packages
import datetime
import itertools
import logging
import os
import sys
from copy import deepcopy


# third party packages
import pyhcup
from pyhcup.parser import df_wtl
from pyhcup.parser import replace_sentinels
from pyhcup.db import insert_sql as gen_insert_sql
from pyhcup.meta import is_long as meta_is_long


# django packages
from django.utils.timezone import utc
from django.conf import settings
#import shortcuts to use with raw sql (!) later
from django.db import connections as cnxns
from django.db import transaction as tx
from django import db as djangodb


# local project and app packages
from djhcup_staging.models import State, DataSource, FileType, File, Column, ImportQueue, ImportBatch, StagingTable
from djhcup_staging.utils.misc import dead_batches


# start a logger
logger = logging.getLogger('default')


# make these tasks app-agnostic with @celery.shared_task
import celery
from celery.result import AsyncResult


HACHOIR_DB_ENTRY = 'djhcup'

# check to see if psycopg2 is how we're going
DB_DEF = settings.DATABASES[HACHOIR_DB_ENTRY]
DB_BACKEND = DB_DEF['ENGINE'].split('.')[-1]

@celery.shared_task
@tx.atomic # turn off autocommit
def reset_dead():
    """Resets dead (interrupted) ImportBatch and ImportQueue objects intelligently.
    
    Types of failure:
    
    1. batch is started but not complete and celery task is no longer held in queue or being processed
        --> ignore any related ImportQueue objects where completed is not null and status is SUCCESS
        --> delete db records in related StagingTable for state-year combinations on incomplete ImportQueue objects
        Code is written in for this below
    """
    
    b_reset = 0
    iq_reset = 0
    
    # grab a database cursor for use downstream
    cursor = cnxns[HACHOIR_DB_ENTRY].cursor()

    # get the dead batches
    dead_batch_qs = dead_batches()
    
    # loop through dead batches cleaning up individual ImportQueue entries
    for b in dead_batch_qs:
        # get related ImportQueue objects
        inc_iq_qs = ImportQueue.objects.filter(batch__pk=b.pk)
        
        # but leave any successful imports alone
        dead_iq_qs = inc_iq_qs.exclude(status='SUCCESS')
        
        # make a list of tuples representing the state-years to roll back
        rollback_lst = [(iq.file.state.abbreviation, iq.file.year) for iq in dead_iq_qs]
        
        # build a SQL delete statement and list of parameters to delete records for these dead imports
        sql = "DELETE FROM "
        
        # tack on table identity (w/optional schema)
        table = b.destination.name
        if b.destination.schema is not None:
            table = b.destination.schema + "." + table
        sql += table
        
        # form WHERE clause with placeholders
        sql += " WHERE " + " OR ".join("(STATE=%s AND YEAR=%s)" for rb in rollback_lst)
        
        # cap it off
        sql += ";"
        
        params = [val for y in rollback_lst for val in y]
        
        # execute the deletes
        cursor.execute(sql, params)
        
        # the staging db has auto-commit turned off by default
        tx.commit(using=HACHOIR_DB_ENTRY)
        
        [logger.info("Deleted records in %s for %s %s" % (table, v[0], v[1])) for v in rollback_lst]
        logger.info("Total records deleted: %s" % cursor.rowcount)
        
        # move on to resetting the ImportQueue objects themselves
        dead_iq_qs.update(start=None, complete=None, status='NEW')
        iq_reset += dead_iq_qs.count()
        
        # and, finally, the batch, too
        b.start=None
        b.complete=None
        b.status='NEW'
        b.save()
        
        b_reset += 1
    
    logger.info("Reset %s dead ImportBatch objects and %s ImportQueue objects" % (b_reset, iq_reset))
    return b_reset, iq_reset


@celery.shared_task(bind=True, ignore_result=True)
def batch_import(self, batch_id):
    """Attempts to import the indicated batch"""
    
    batch = ImportBatch.objects.get(pk=batch_id)
    batch.status = 'RECEIVED'
    batch.celery_task_id = self.request.id
    batch.save()
    
    enqueued = ImportQueue.objects.filter(batch=batch)
    #destination = batch.destination
    logger.info('Found %s' % (batch))
    
    if batch.complete:
        response = 'Batch %i was previously completed at %s, and therefore will not be run' % (batch.pk, batch.complete)
        logger.error(response)
        batch.fail()
        return False
    
    elif enqueued.count() < 1:
        response = 'Batch %i has no items enqueued, and therefore will not be run' % batch.pk
        logger.warning(response)
        batch.fail()
        return True

    else:
        batch_begin = datetime.datetime.utcnow().replace(tzinfo=utc)
        batch.start = batch_begin
        batch.status = 'IN PROCESS'
        batch.save()
        logger.info('Begin batch %s' % (batch))
        
        job = celery.group(
            import_dispatch.si(load.pk) for load in enqueued
            )
        job()
        
        # put a task into background for periodic check that the batch has completed
        batch_complete.apply_async((batch.pk,), countdown=600)
        
        return True


@celery.shared_task(bind=True, ignore_result=True)
def import_dispatch(self, importqueue_pk, insert_size=5, slice_size=1000):
    load = ImportQueue.objects.get(pk=importqueue_pk)
    
    """
    # TODO: Sim. to the batch_import blocks that are commented out above, these bits are more important for an integration step. They exist to prevent double-loading into a common table, but I don't necessarily want to prevent making duplicate staging tables for a given File object.
    
    destination = load.batch.destination
    similar_load_qs = ImportQueue.objects.filter(
        batch__destination=destination,
        file__state=load.file.state,
        file__year=load.file.year,
        file__file_type__source=load.file.file_type.source
        )
    similar_completed = similar_load_qs.filter(complete__isnull=False, status='SUCCESS')
    similar_started = similar_load_qs.filter(start__isnull=False)
    

    if similar_completed.count() > 0:
        #appears to already have been imported. skip this one
        logger.warning('It looks like <%s> was already imported successfully to <%s> at %s; skipping for now' % (load, destination, similar_completed[0].complete))
        load.fail()
        return False
    
    elif similar_started.count() > 0:
        #appears to already have been imported. skip this one
        logger.warning('It looks like an import was already started for importing <%s> to <%s> at %s; skipping for now' % (load, destination, similar_started[0].start))
        load.fail()
        return False

    else:
    """
    # proceed with making the file happen
    load.status = 'QUEUED'
    load.save()
    
    logger.info('Queued for dispatch: %s' % (load))
    
    dsabbr = load.file.file_type.source.abbreviation
    
    # FROM HERE BELOW, SPLIT OFF PSYCOPG2 VS NOT
    if ('psycopg2' in DB_BACKEND and (
            ((dsabbr.upper() in ['CORE', 'BASE', 'CHGS']) or
                (dsabbr.upper() in ['CHGS'] and meta_is_long(load.get_meta()))
                )
            )
        ):
        # do it Rockapella
        logger.info('Sending to pg_import_file: %s' % (load))
        pg_import_file.delay(load.pk)
        return True
    
    else:
        logger.info('Sending to chunk_import_file: %s' % (load))
        chunk_import_file.delay(load.pk)
        return True


@celery.shared_task(bind=True, ignore_result=True)
def pg_import_file(self, importqueue_pk, drop_rawload=True):
    """Assumes psycopg2 availability.
    """
    
    load = ImportQueue.objects.get(pk=importqueue_pk)
    load.status = 'RECEIVED'
    load.celery_task_id = self.request.id
    load.start = datetime.datetime.utcnow().replace(tzinfo=utc)
    load.save()
    load.log('Beginning import with psycopg2',
             level='INFO', logger=logger, status='IN PROCESS')
    
    # TODO: move to integration
    #destination = load.batch.destination
    
    load.log('Begin import',
             level='INFO', logger=logger)
    
    """
    TODO: Re-enable if appropriate; omitted for convenience atm
    cols_saved = load.record_columns()
    if cols_saved > 0:
        load.log('Columns saved: %s' % (load),
                level='INFO', logger=logger)
    else:
        load.log('No columns saved',
                level='WARNING', logger=logger)
    """
    
    #schema = destination.schema
    state = load.file.state.abbreviation
    year = load.file.year
    dsabbr = load.file.file_type.source.abbreviation
    
    if dsabbr == 'CORE':
        # this is a first-pass CORE import
        stcat = 'SID_CORE_SOURCE'
        # TODO: Expand for non-SID nomenclature
    elif dsabbr == 'CHGS':
        stcat = 'SID_CHARGES_SOURCE'
    else:
        raise Exception("wtf are you doing? you know this code is all borked right now.")
    
    stg_table_name = '_'.join(str(x) for x in [state, year, 'stg', stcat])
    handle = load.file.open()

    # establish connection directly with psycopg2
    import psycopg2
    cnxn = psycopg2.connect(
        host=DB_DEF['HOST'],
        port=DB_DEF['PORT'],
        user=DB_DEF['USER'],
        password=DB_DEF['PASSWORD'],
        database=DB_DEF['NAME'],
        )
    
    # get helper functions
    from pyhcup.db import pg_rawload, pg_staging, pg_shovel, pg_wtl_shovel, pg_drop
    
    
    # segregate the csv loads from the non-csv loads
    if str(load.file.filename).split('.')[-1] == 'csv':
        # just do a csv load, and assume a header is present
        
        affected_rows = 0
        
    else:
        # use the old style code
        # let 'er rip
        meta = load.get_meta()
        
        load.log('Creating raw import table via pg_rawload()',
                level='INFO', logger=logger)
        rawload = pg_rawload(cnxn, handle, meta)
        load.log('Raw import table %s populated' % (rawload),
                level='INFO', logger=logger)
        
        if load.file.file_type.source.abbreviation in pyhcup.parser.LONG_MAPS.keys():
            pk_fields = None
            load.log('Staging will be done with no primary key',
                    level='INFO', logger=logger)
        else:
            pk_fields = ['key', 'state', 'year']
            load.log('Staging will be done with primary key %s' % (pk_fields),
                    level='INFO', logger=logger)
        
        load.log('Creating staging table via pg_staging()',
                level='INFO', logger=logger)
        staging = pg_staging(cnxn, rawload, meta, state, year, pk_fields=pk_fields,
                             table_name=stg_table_name)
        load.log('Staging table populated: %s' % (stg_table_name),
                level='INFO', logger=logger)
        
        affected_rows = staging[1]
        
        # save info about this import in a StagingTable object
        imported = StagingTable(
            imported_via = load,
            name = stg_table_name,
            category = stcat,
            records = affected_rows
        )
        
        imported.save()
        
        load.log('StagingTable %s recorded for %s' % (stg_table_name, imported.pk))
        
        
        if dsabbr in ['CHGS'] and not meta_is_long(meta):
            # wide charges should get wide-to-long shoveled
            # TODO: adjust this using StagingTable records
            category = dsabbr
            load.log('This is a wide-to-long pg load',
                    level='INFO', logger=logger)
            #logger.info()
            load.log('Inserting contents of staging table %s to master table %s' % (staging[0], table),
                    level='INFO', logger=logger)
            affected_rows = pg_wtl_shovel(cnxn, meta, category, staging[0], stg_table_name)
            #logger.info('Inserted contents of staging table %s to master table %s (%s rows): %s' % (staging[0], table, affected_rows, load))
            load.log('Inserted contents of staging table %s to master table %s (%s rows)' % (staging[0], raw_table_name, affected_rows),
                    level='INFO', logger=logger)
        """
        else:
            fields = [x for x in meta.field if x.lower() not in ['state', 'year']]
            fields += ['state', 'year']
            
            #logger.info('Inserting contents of staging table %s to master table %s: %s' % (staging[0], table, load))
            load.log('Inserting contents of staging table %s to master table %s' % (staging[0], table),
                    level='INFO', logger=logger)
            affected_rows = pg_shovel(cnxn, staging[0], table, fields)
            logger.info('Inserted contents of staging table %s to master table %s (%s rows): %s' % (staging[0], raw_table_name, affected_rows, load))
            load.log('Inserted contents of staging table %s to master table %s (%s rows)' % (staging[0], raw_table_name, affected_rows),
                    level='INFO', logger=logger)
        """
        
        if drop_rawload:
            # TODO: Rework this section a little more elegantly
            drop_targets = [rawload]#, staging[0]]
            #logger.info('Dropping intermediate tables %s: %s' % (drop_targets, load))
            load.log('Dropping intermediate tables: %s' % (drop_targets),
                    level='INFO', logger=logger)
            for dtbl in drop_targets:
                #logger.info('Dropping intermediate table %s: %s' % (dtbl, load))
                load.log('Dropping intermediate table: %s' % (dtbl),
                        level='INFO', logger=logger)
                drop_result = pg_drop(cnxn, dtbl)
                if drop_result == True:
                    logger.info('Successfully dropped intermediate table %s: %s' % (dtbl, load))
                    load.log('Successfully dropped intermediate table: %s' % (dtbl),
                            level='INFO', logger=logger)
                else:
                    logger.error('Failed to drop %s: %s' % (dtbl, load))
                    load.log('Failed to drop: %s' % (dtbl),
                            level='ERROR', logger=logger)
    
    # affected_rows will evaluate un-True in the case of any troubles
    if affected_rows:
        load.success('Import complete (%s rows)' % (affected_rows))
        #logger.info('Import complete: %s (%s rows)' % (load, affected_rows))
        return True
    else:
        load.fail('Import failed')
        #logger.error('Import failed: %s' % load)
        return False


@celery.shared_task(bind=True, ignore_result=True)
def chunk_import_file(self, importqueue_pk, insert_size=5, slice_size=1000):
    """Imports a file with a tangled web of task distribution in order to effect parallelization.
    """
    
    load = ImportQueue.objects.get(pk=importqueue_pk)
    load.status = 'RECEIVED'
    load.celery_task_id = self.request.id
    load.save()
    
    logger.info('Received for import with celery task chunking: %s' % (load))
    
    destination = load.batch.destination
    
    # proceed with making the file happen
    load.status = 'IN PROCESS'
    load.start = datetime.datetime.utcnow().replace(tzinfo=utc)
    load.save()
    
    logger.info('Begin import: %s' % (load))
    
    cols_saved = load.record_columns()
    if cols_saved > 0:
        logger.info('Columns saved: %s for %s' % (cols_saved, load))
    else:
        logger.info('No columns saved for %s' % (load))
    
    table = destination.name
    schema = destination.schema
    state = load.file.state.abbreviation
    year = load.file.year
    dsabbr = destination.source.abbreviation
    
    handle = load.file.open()
    meta = load.get_meta()
    
    # make a generator to yield one slice_size slice of the file in question at a time
    reader = pyhcup.parser.read(handle, meta, chunksize=slice_size)

    # take 5
    # loop through slices and dispatch chunker.chunks() for each
    # this is preferred to a chain so that it doesn't wait to start until after all the signatures are generated
    result_lst = []
    for df in reader:
        # everything we insert will always have a state and year associated with it
        # if they aren't already in the frame, add them from the passed values
        # (which should in turn be from the loadfile object)
        if 'state' not in df.columns.map(lambda x: str(x).lower()):
            df['state'] = state
        
        if 'year' not in df.columns.map(lambda x: str(x).lower()):
            df['year'] = year
        
        cleaned_df = replace_sentinels(df)
        
        if dsabbr == 'CHGS' and not meta_is_long(meta):
            # this is a wide charges file
            # convert before chunking it out
            cleaned_df = df_wtl(cleaned_df, category='CHGS')
        
        result_lst.append(chunker(
                cleaned_df,
                table,
                schema,
                insert_size
                )
            )
    
    # take 6
    # slices chained, chunker.chunks() for each
    # this is preferred to another chunker here as all files chunking simultaneously
    # tends to hang for a while
    """
    result_lst = [
        # ...
        for df in reader
    ]
    for df in reader:
        # everything we insert will always have a state and year associated with it
        # if they aren't already in the frame, add them from the passed values
        # (which should in turn be from the loadfile object)
        if 'state' not in df.columns.map(lambda x: str(x).lower()):
            df['state'] = state
        
        if 'year' not in df.columns.map(lambda x: str(x).lower()):
            df['year'] = year
        
        cleaned_df = replace_sentinels(df)
        
        if dsabbr == 'CHGS' and not meta_is_long(meta):
            # this is a wide charges file
            # convert before chunking it out
            cleaned_df = df_wtl(cleaned_df, category='CHGS')
        
        result_lst.append(chunker(
                cleaned_df,
                table,
                schema,
                insert_size
                )
            )
    """
    
    import_complete.apply_async((result_lst, load.pk), countdown=10)
    return True


@celery.shared_task
def chunker(df_slice, table, schema, insert_size=5):
    """These should be slices far too large to build a SQL string on; e.g. >100"""
    
    r = xrange(0, len(df_slice), insert_size)
    
    # build chunks of insert jobs and turn it into a group
    job = chunk_insert.chunks(
        zip(
            (df_slice[x:x+insert_size] for x in r),
            (table for x in r),
            (schema for x in r)
            ),
        10
        ).group()
    
    return job.delay() # gives back an async resultgroup object
    # for which .ready() will be True if all tasks have completed
    # and for which .successful() will be True if all tasks were successfully completed


@celery.shared_task
@tx.atomic # turn off autocommit
def chunk_insert(df_chunk, table, schema, placeholder_representation="%s"):    
    cursor = cnxns[HACHOIR_DB_ENTRY].cursor()
    
    #df_chunk = replace_sentinels(df_chunk)
    
    try:
        #print "df_chunk is %s" % df_chunk
        #print "table is %s" % table
        #print "schema is %s" % schema
        #print "placeholder is %s" % placeholder_representation
        insert_sql, values = gen_insert_sql(df_chunk, table, schema=schema, placeholder=placeholder_representation)    
        logger.debug('Generated sql and values lists (params)')
    except:
        e = sys.exc_info()[0]
        logger.warning('Failed to generate SQL insert statement and parameters list using pyhcup.db.insert_sql(). Raised %s.' % e)
        #logger.warning('df_chunk is %s' % df_chunk)
        #logger.warning('table is %s' % table)
        #logger.warning('schema is %s' % schema)
        #logger.warning('placeholder is %s' % placeholder_representation)
        return False
    
    
    try:
        cursor.execute(insert_sql, values)
        logger.debug('Executed sql using params')
    except:
        e = sys.exc_info()[0]
        logger.warning('Failed to execute SQL insert statement and parameters list using cursor.execute(). Raised %s.' % e)
        #logger.warning('insert_sql is %s' % insert_sql)
        #logger.warning('values is %s' % values)
        
    
    tx.commit(using=HACHOIR_DB_ENTRY)
    #logger.debug('Committed transaction')
    
    # Do not hold a copy of the query.
    djangodb.reset_queries()
    #logger.debug('Inserted chunk successfully from state-year %s-%s to table %s' % (state, year, table))
    return cursor.rowcount


@celery.shared_task(bind=True, max_retries=None, default_retry_delay=10)
def import_complete(self, result_lst, importqueue_pk):
    """Checks periodically to see if these have completed and updates associated ImportQueue obj with outcome
    """
    
    iq = ImportQueue.objects.get(pk=importqueue_pk)
    des = iq.batch.destination
    
    
    if all(r.ready() for r in itertools.chain(*result_lst)):
        if all(r.successful() for r in itertools.chain(*result_lst)):
            iq.success()
            logger.info('Import complete: %s' % iq)
            return True
        else:
            iq.fail()
            logger.error('Import failed: %s' % iq)
            raise Exception('Import failed: %s' % iq)
    else:
        raise self.retry(exc=Exception('Import not yet complete: %s' % iq))


@celery.shared_task(bind=True, max_retries=None, default_retry_delay=900)# default_retry_delay=60)
def batch_complete(self, batch_pk):
    """Checks to see if each item in the batch has a completion timestamp in db, and updates batch db entry to reflect success/failure of overall batch.
    """
    
    # grab the django representation of this ImportBatch
    b = ImportBatch.objects.get(pk=batch_pk)
    
    # and, while we're at it, the associated ImportQueue objects
    enqueued = ImportQueue.objects.filter(batch=b)
    
    try:
        # test if all completed, one way or another
        if all(q.complete is not None for q in enqueued):
            
            # test if the outcomes were all SUCCESS
            if all(q.successful() for q in enqueued):
                b.success()
                logger.info('Batch completed successfully: %s' % b)
                return True
            else:
                b.fail()
                logger.error('One or more imports failed: %s' % b)
                return False
        else:
            # since some haven't completed yet, raise IncompleteStream and retry
            raise celery.exceptions.IncompleteStream
    
    except celery.exceptions.IncompleteStream as exc:
        # try again a little later, when the streams are more complete
        raise self.retry(exc=Exception('Batch not yet complete: %s' % b))
