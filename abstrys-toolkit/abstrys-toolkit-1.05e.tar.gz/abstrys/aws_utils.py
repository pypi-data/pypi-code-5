# Abstrys Amazon Web Services (AWS) Utility Library
#
# Provides classes and functions useful for working with AWS

import sys
import os
import hashlib
from cmd_utils import *

try:
    import boto
except ImportError, e:
    print "boto is not installed. Run 'pip install boto' on the command-line"
    print "to install it first."
    sys.exit(1)

try:
    import yaml
except ImportError, e:
    print "pyyaml is not installed. Run 'pip install pyyaml' on the command-line"
    print "to install it first."
    sys.exit(1)


def split_s3_path(s3_path):
    """Get a bucket name and object path from an 's3 path'.
    An S3 path is one in which the object path is appended to the bucket name.
    For example: my-music-bucket/path/to/file.mp3

    S3 paths may also begin with the character sequence "S3://" to disambiguate
    it from a local path in arguments that might accept both.

    Returns a tuple containing the bucket name and object path.
    """
    # If the s3_path begins with an "S3://" or "s3://", strip it off.
    if s3_path.startswith('S3://') or s3_path.startswith('s3://'):
        s3_path = s3_path[5:]

    # Split the s3 path after the *first* slash character. The bucket name
    # can't have a slash in it; anything after the first slash is considered
    # the S3 object name.
    if '/' in s3_path:
        return s3_path.split('/', 1)
    else:
        return (s3_path, None)


def get_s3_key(s3_path):
    """Get an S3 key from an S3 path."""
    # first, get the bucket and object.
    (s3_bucket_name, s3_object_name) = split_s3_path(s3_path)

    try:
        # create (or get) the s3 bucket.
        s3_bucket = s3.get_bucket(s3_bucket_name)
    except:
        print_error("Eeek! something happened!")
        sys.exit(1)

    # does the s3 object exist?
    if s3_object_name in s3_bucket:
        return s3_bucket.get_key(s3_object_name)

    return None


def load_aws_authentication(
        access_key_id = None, secret_access_key = None, config_file_path = None):
    """Load AWS authentication strings from a config file or from environment
    variables. Return a tuple containing the access key ID and secret access
    key."""

    if secret_access_key and access_key_id:
        return (access_key_id, secret_access_key)

    # first, look for a YAML config file.
    if config_file_path and os.path.exists(config_file_path):
        # We're expecting a YAML-formatted file like this:
        #
        #     ---
        #     access_key_id:     ACCESSKEYID
        #     secret_access_key: SECRETACCESKEY
        #
        f = open(config_file_path, 'r')
        config = yaml.safe_load(f)
        f.close()
        # Whatever command-line args *weren't* specified, fill them in with
        # details from the file.
        if not access_key_id:
            access_key_id = config['access_key_id']
        if not secret_access_key:
            secret_access_key = config['secret_access_key']

    # if the config file didn't work out, look for creds in the environment.
    if not (access_key_id and secret_access_key):
        # There are still some credentials missing. Look in the environment.
        if not access_key_id:
            access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        if not secret_access_key:
            secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

    return (access_key_id, secret_access_key)


def get_s3(access_key_id = None, secret_access_key = None, config_file = None):
    """Authenticate with AWS and return an S3 object. Returns None if it failed
    to get the S3 object."""
    # Rules:
    #
    # 1. If the access_key_id and/or secret access key is specified, then use
    #    its values in preference to all others.
    #
    # 2. If a file exists, use its values in preference to environment
    #    variables.
    #
    # 3. If any credentials are still missing, look in the environment.

    (access_key_id, secret_access_key) = load_aws_authentication(access_key_id,
            secret_access_key, config_file)

    if access_key_id and secret_access_key:
        return boto.connect_s3(access_key_id, secret_access_key)
    else:
        print_error("Could not find AWS Access keys... No connection possible.")
        return None

#
# Functions to work with MD5 hashes in the context of AWS S3
#

def get_s3_md5_hex_digest(s3_path=None, s3_object=None):
    if not s3_object:
        s3_object = get_s3_key(s3_path)
    if s3_object == None:
        return None
    return s3_object.get_metadata('md5-hexdigest')

def set_s3_md5_hex_digest(md5_hex_string, s3_object=None, s3_path=None):
    if not s3_object and not s3_path:
        print_error("Must set either object or s3 path for set_s3_md5_hex_digest!")
        sys.exit(1)

    s3_bucket = None
    s3_object_name = None

    if s3_object:
        # get the info from the S3 object (key)
        s3_bucket = s3_object.bucket
        s3_bucket_name = s3_bucket.name
        s3_object_name = s3_object.name
    else:
        # first, get the bucket and object.
        (s3_bucket_name, s3_object_name) = get_bucket_and_object_from_s3_path(s3_path)
        try:
            # create (or get) the s3 bucket.
            s3_bucket = s3.get_bucket(s3_bucket_name)
        except:
            print_error("Eeek! something happened!")
            sys.exit(1)

    # copy the key (this is currently the only way to update an object's
    # metadata...
    s3_bucket.copy_key(
            s3_object_name, s3_bucket_name, s3_object_name,
            metadata={'md5-hexdigest': md5_hex_string}, preserve_acl=True)


def get_local_md5_hex_digest(local_path):
    if not os.path.isfile(local_path):
        print_error("Error -- path is not a file: %s" % local_path)
        return None
    file_to_calc = open(local_path, 'rb')
    md5 = hashlib.md5()
    for bit_o_file in file_to_calc:
        md5.update(bit_o_file)
    file_to_calc.close()
    return md5.hexdigest()



