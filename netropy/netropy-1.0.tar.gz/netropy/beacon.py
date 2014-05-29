"""beacon

Functions for interacting with the remote beacon to retrieve records.


rest api root:
    https://beacon.nist.gov/rest/

rest api example endpoints:
    https://beacon.nist.gov/rest/record/1395971640
    https://beacon.nist.gov/rest/record/previous/1395971640
    https://beacon.nist.gov/rest/record/next/1395971640
    https://beacon.nist.gov/rest/record/last/
    https://beacon.nist.gov/rest/record/start-chain/1395971640

"""

import datetime

import requests

import record


_nist = "https://beacon.nist.gov/rest"


def _retrieve_record(record_url):
    """Perform the http request against the beacon rest api"""
    response = requests.get(record_url)
    if response.status_code is not 200:
        raise Exception("Error retrieving record (%s)" % (record_url, ))
    rec = record.parse_record_xml(response.text)
    return rec


def latest_timestamp(frequency=60):
    """Generate the expected most recent timestamp
    
    Warning: If your local clock is off, this may not return an invalid time

    """
    now = int(datetime.datetime.now().strftime('%s'))
    now -= now % frequency
    return now


def get_record(timestamp, apiroot=_nist):
    """Retrieve a record given a specific timestamp"""
    record_url = "%s/record/%s" % (apiroot, timestamp)
    return _retrieve_record(record_url)


def current(apiroot=_nist):
    """Retrieve the current record from the beacon"""
    timestamp = latest_timestamp()
    record_url = "%s/record/%s" % (apiroot, timestamp)
    return _retrieve_record(record_url)


def previous(record, apiroot=_nist):
    """Given a timestamp, return the previous record"""
    timestamp = record['timeStamp']
    record_url = "%s/record/previous/%s" % (apiroot, timestamp)
    return _retrieve_record(record_url)


def next(record, apiroot=_nist):
    """Given a timestamp, return the next record"""
    timestamp = record['timeStamp']
    record_url = "%s/record/next/%s" % (apiroot, timestamp)
    return _retrieve_record(record_url)


def last(apiroot=_nist):
    """Retrieve the last record in the chain"""
    record_url = "%s/record/last/" % (apiroot, )
    return _retrieve_record(record_url)


def start_chain(record, apiroot=_nist):
    """Given a timestamp, return the initial record in the chain"""
    timestamp = record['timeStamp']
    record_url = "%s/record/start-chain/%s" % (apiroot, timestamp)
    return _retrieve_record(record_url)


