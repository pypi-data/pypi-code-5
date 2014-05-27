'''
Copyright (c) 2014, Emmanuel Levijarvi
All rights reserved.
License BSD
'''
from __future__ import print_function
import argparse
import datetime
import sqlite3
import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
from tempodb import Client

__version__ = "1.0.0"

DEFAULT_CONFIG = os.path.join(os.path.expanduser("~"), '.tempodb-archive.cfg')
CONFIG_SECTION = 'tempodb'
KEEP_DAYS = 30
INTERVAL = 24
DEFAULT_DATABASE_NAME = 'tempodb-archive.sqlite3'


class TempoDBArchive(object):
    def __init__(self, api_key, api_secret, interval=INTERVAL,
                 keep_days=KEEP_DAYS):
        self.keep_days = datetime.timedelta(days=keep_days)
        self.interval = datetime.timedelta(hours=interval)
        self.client = Client(api_key, api_secret)

    def get_series_keys(self):
        try:
            return self._series_keys
        except AttributeError:
            self._series_keys = [p.key for p in self.client.get_series()]
        return self._series_keys

    def get_datapoints(self, series_key, delete=False):
        ts = datetime.datetime.utcnow()
        end = datetime.datetime(ts.year, ts.month, ts.day) - self.keep_days
        while True:
            start = end - self.interval
            data = self.client.read_key(series_key, start, end, tz='UTC')
            yield data.data
            if not data.data:
                break
            if delete:
                self.client.delete_key(series_key, start, end)
            end = start

    def write_sqlite(self, series_key, data, filename=DEFAULT_DATABASE_NAME):
        conn = sqlite3.connect(filename)
        cur = conn.cursor()
        # I know this might possibly run untrusted code but I'm not aware of
        # a built-in method for escaping identifiers and this is just an
        # archive tool.
        query = '''CREATE TABLE IF NOT EXISTS "{0}" (
                   timestamp text UNIQUE NOT NULL,
                   value real NOT NULL)'''.format(series_key)
        cur.execute(query)
        query = 'INSERT INTO "{0}" values (?, ?)'.format(series_key)
        with conn:
            [cur.execute(query, (str(reading.ts), reading.value))
             for reading in data]
        conn.close()

    def archive(self, series=None, delete=False):
        if series in (None, []):
            series_keys = self.get_series_keys()
        elif isinstance(series, str):
            series_keys = (series,)
        else:
            series_keys = series
        for key in series_keys:
            if key not in self.get_series_keys():
                print('Series {0} does not exist'.format(key))
                continue
            self.archive_series(key, delete)

    def archive_series(self, series_key, delete=False):
        start = datetime.datetime.utcnow() - self.keep_days
        start_date = datetime.datetime(start.year, start.month, start.day)
        for day, data in enumerate(self.get_datapoints(series_key, delete), 1):
            delta = self.interval * day
            archive_date = (start_date - delta).strftime("%Y-%m-%d")
            print('Archiving {0} for day {1}'.format(series_key, archive_date))
            try:
                self.write_sqlite(series_key, data)
            except sqlite3.IntegrityError:
                print('Skipping', archive_date)


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="TempoDB Archive Tool",
                                     prog='tempodb-archive')
    parser.add_argument('--version', help='Display Version',
                        action='version',
                        version='%(prog)s {0}'.format(__version__))
    parser.add_argument('-c', '--config-file', default=argparse.SUPPRESS,
                        help="Configuration Filename")
    parser.add_argument('--api-key', default=argparse.SUPPRESS,
                        help="TempoDB API Key")
    parser.add_argument('--api-secret', default=argparse.SUPPRESS,
                        help="TempoDB API Secret")
    subparsers = parser.add_subparsers(help='commands')
    parser_list = subparsers.add_parser('list', help='list available series')
    parser_list.set_defaults(cmd='list')
    parser_archive = subparsers.add_parser('archive',
                                           help='archive datapoints')
    parser_archive.add_argument('series_keys', nargs='*',
                                default=argparse.SUPPRESS)
    parser_archive.add_argument('-d', '--delete', action='store_true',
                                default=argparse.SUPPRESS,
                                help='Delete archived datapoints from TempoDB')
    parser_archive.add_argument('--keep-days', default=argparse.SUPPRESS,
        help='Number of days worth of datapoints to keep on TempoDB.')
    parser_archive.add_argument('--interval', default=argparse.SUPPRESS,
        help='Number of hours worth of datapoints to fetch per TempoDB call.')
    parser_archive.set_defaults(cmd='archive')
    return vars(parser.parse_args(args))


def parse_config(config_filename=None):
    defaults = {'keep_days': str(KEEP_DAYS), 'interval': str(INTERVAL)}
    config = configparser.SafeConfigParser(defaults, dict)
    config_files = [f for f in (config_filename, DEFAULT_CONFIG)
                    if f is not None]
    config.read(config_files)
    config_dict = config.items(CONFIG_SECTION)
    if 'series names' in config_dict:
        series_names = config_dict['series names'].split(',')
        config_dict['series names'] = [sn.strip() for sn in series_names]
    if 'delete' in config_dict:
        config_dict['delete'] = config.getboolean(CONFIG_SECTION, 'delete')
    return {k.replace(' ', '_'): v for k, v in config_dict}


def main():
    args = parse_args()
    config = parse_config(args.get('config_file', None))
    config.update(args)
    tdb = TempoDBArchive(config['api_key'], config['api_secret'])
    if config['cmd'] == 'list':
        print('Series Keys')
        print('-' * 20)
        for key in tdb.get_series_keys():
            print(key)
    elif config['cmd'] == 'archive':
        tdb.archive(config.get('series_keys', None),
                    config.get('delete', False))


if __name__ == '__main__':
    main()
