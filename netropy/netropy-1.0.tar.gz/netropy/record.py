"""record

The record data structure and helper functions.
"""


import collections
import hashlib


# -----------------------------------------------------------------------------
# The main data structure
# -----------------------------------------------------------------------------


record_fields = ['version', 'frequency', 'timeStamp',
                 'seedValue', 'previousOutputValue',
                 'signatureValue', 'outputValue', 'statusCode']

record_field_ints = ('frequency', 'timeStamp')

Record = collections.namedtuple('Record', record_fields)


# -----------------------------------------------------------------------------
# Parsing helpers
# -----------------------------------------------------------------------------


def _extract_value(field_name, raw_xml):
    """Extract a value from raw xml

    Simplistic string parsing version...
    """
    val = raw_xml.split("%s>" % field_name)[1].rstrip('</')
    return val


def parse_record_xml(record_xml):
    """Parse record xml and return a dictionary

    Simplistic string parsing version...
    """
    rec = {}
    for field_name in record_fields:
        val = _extract_value(field_name, record_xml)
        if field_name in record_field_ints:
            val = int(val)
        rec[field_name] = val
    return rec


# -----------------------------------------------------------------------------
# Record validation
# -----------------------------------------------------------------------------

def verify_record(record):
    """Verify a record is internally consistent

    signatureValue - This can't be verified as there is no public key
    outputValue - This should be a hash of the signatureValue

    From the schema file info for outputValue:
    The SHA-512 hash of the signatureValue as a 64 byte hex string

    reminder:
    The outputValue hash is a hash of the signatureValue byte string, not
    the signatureValue hex string.  See decode('hex').

    """
    signature_value = record['signatureValue']
    output_value = record['outputValue']
    sv_hash = hashlib.sha512(signature_value.decode('hex')).hexdigest().upper()
    return sv_hash == output_value


def verify_pair(record1, record2):
    """Verify two records which are chained together

    Any given record (except the first) should be chained to the previous
    by a matching hash in previousOutputValue.

    From the schema file info for outputValue:
    The SHA-512 hash value for the previous record - 64 byte hex string
    
    """
    rec1_output_value = record1['outputValue']
    rec2_previous_output_value = record2['previousOutputValue']
    return rec1_output_value == rec2_previous_output_value


