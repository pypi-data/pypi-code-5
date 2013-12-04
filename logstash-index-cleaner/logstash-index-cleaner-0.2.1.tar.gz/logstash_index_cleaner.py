#!/usr/bin/env python
"""
Deletes all indices with a datestamp older than "days-to-keep" for daily
if you have hourly indices, it will delete all of those older than "hours-to-keep"

This script presumes an index is named typically, e.g. logstash-YYYY.MM.DD
It will work with any name-YYYY.MM.DD or name-YYYY.MM.DD.HH type sequence
"""

# TODO: Unit tests. The code is somewhat broken up into logical parts that may be tested separately.
#       Better error reporting?
#       Improve the get_index_epoch method to parse more date formats. Consider renaming (to "parse_date_to_timestamp"?)

import logging
import sys
import time
import argparse
from datetime import timedelta

import pyes


__version__ = '0.2.1'


def make_parser():
    """ Creates an ArgumentParser to parse the command line options. """
    parser = argparse.ArgumentParser(description='Delete old logstash indices from Elasticsearch.')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s '+__version__)

    parser.add_argument('--host', help='Elasticsearch host.', default='localhost')
    parser.add_argument('--port', help='Elasticsearch port', default=9200, type=int)
    parser.add_argument('-t', '--timeout', help='Elasticsearch timeout', default=30, type=int)

    parser.add_argument('-p', '--prefix', help='Prefix for the indices. Indices that do not have this prefix are skipped.', default='logstash-')
    parser.add_argument('-s', '--separator', help='Time unit separator', default='.')

    parser.add_argument('-H', '--hours-to-keep', action='store', help='Number of hours to keep.', type=int)
    parser.add_argument('-d', '--days-to-keep', action='store', help='Number of days to keep.', type=int)

    parser.add_argument('-n', '--dry-run', action='store_true', help='If true, does not perform any changes to the Elasticsearch indices.', default=False)
    parser.add_argument('--log-level', action='store', help="Log level to be used", default='INFO', choices='DEBUG INFO WARN ERROR CRITICAL FATAL'.split())
    parser.add_argument('--log-verbose', action='store_true', help="Show more verbose log message, including timestamp and log level", default=False)

    return parser


def get_index_epoch(index_timestamp, separator='.'):
    """ Gets the epoch of the index.

    :param index_timestamp: A string on the format YYYY.MM.DD[.HH]
    :return The creation time (epoch) of the index.
    """
    year_month_day_optionalhour = index_timestamp.split(separator)
    if len(year_month_day_optionalhour) == 3:
        year_month_day_optionalhour.append('3')

    return time.mktime([int(part) for part in year_month_day_optionalhour] + [0,0,0,0,0])


def find_expired_indices(connection, days_to_keep, hours_to_keep, separator, prefix, logger):
    """ Generator that yields expired indices.

    :return: Yields tuples on the format ``(index_name, expired_by)`` where index_name
        is the name of the expired index and expired_by is the number of seconds (a float value) that the
        index was expired by.
    """
    utc_now_time = time.time() + time.altzone
    days_cutoff = utc_now_time - days_to_keep * 24 * 60 * 60 if days_to_keep is not None else None
    hours_cutoff = utc_now_time - hours_to_keep * 60 * 60 if hours_to_keep is not None else None

    for index_name in sorted(set(connection.get_indices().keys())):
        if not index_name.startswith(prefix):
            logger.info('Skipping index due to missing prefix {0}: {1}'.format(prefix, index_name))
            continue

        unprefixed_index_name = index_name[len(prefix):]

        # find the timestamp parts (i.e ['2011', '01', '05'] from '2011.01.05') using the configured separator
        parts = unprefixed_index_name.split(separator)

        # perform some basic validation
        if len(parts) < 3 or len(parts) > 4 or not all([item.isdigit() for item in parts]):
            logger.warning('Could not find a valid timestamp from the index: {0}'.format(index_name))
            continue

        # find the cutoff. if we have more than 3 parts in the timestamp, the timestamp includes the hours and we
        # should compare it to the hours_cutoff, otherwise, we should use the days_cutoff
        cutoff = hours_cutoff
        if len(parts) == 3:
            cutoff = days_cutoff

        # but the cutoff might be none, if the current index only has three parts (year.month.day) and we're only
        # removing hourly indices:
        if cutoff is None:
            logger.info('Skipping {0} because it is of a type (hourly or daily) that I\'m not asked to delete.'.format(index_name))
            continue

        index_epoch = get_index_epoch(unprefixed_index_name)

        # if the index is older than the cutoff
        if index_epoch < cutoff:
            yield index_name, cutoff-index_epoch

        else:
            logger.info('{0} is {1} above the cutoff.'.format(index_name, timedelta(seconds=index_epoch-cutoff)))


def get_logger(log_level, verbose):
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    if verbose:
        formatter = logging.Formatter('[%(name)s:%(levelname)s] %(asctime)s: %(message)s')
        handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def main():
    start = time.time()

    parser = make_parser()
    arguments = parser.parse_args()
    logger = get_logger(arguments.log_level, arguments.log_verbose)

    if not arguments.hours_to_keep and not arguments.days_to_keep:
        logger.error('Invalid arguments: You must specify either the number of hours or the number of days to keep.')
        parser.print_help()
        return

    connection = pyes.ES('{0}:{1}'.format(arguments.host, arguments.port), timeout=arguments.timeout)

    if arguments.days_to_keep:
        logger.info('Deleting daily indices older than {0} days.'.format(arguments.days_to_keep))
    if arguments.hours_to_keep:
        logger.info('Deleting hourly indices older than {0} hours.'.format(arguments.hours_to_keep))

    logger.info('')

    for index_name, expired_by in find_expired_indices(connection, arguments.days_to_keep, arguments.hours_to_keep, arguments.separator, arguments.prefix, logger):
        expiration = timedelta(seconds=expired_by)

        if arguments.dry_run:
            logger.info('Would have attempted deleting index {0} because it is {1} older than the calculated cutoff.'.format(index_name, expiration))
            continue

        logger.info('Deleting index {0} because it was {1} older than cutoff.'.format(index_name, expiration))

        deletion = connection.delete_index_if_exists(index_name)
        # ES returns a dict on the format {u'acknowledged': True, u'ok': True} on success.
        if deletion.get('ok'):
            logger.info('Successfully deleted index: {0}'.format(index_name))
        else:
            logger.error('Error deleting index: {0}. ({1})'.format(index_name, deletion))

    logger.info('')
    logger.info('Done in {0}.'.format(timedelta(seconds=time.time()-start)))


if __name__ == '__main__':
    main()
