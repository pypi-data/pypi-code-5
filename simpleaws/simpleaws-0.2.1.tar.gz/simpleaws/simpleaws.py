"""
Simple AWS

An idiot-proof way to make a public S3 based-service.

Supports S3, Cloudfront and STS.

"""
import boto
from boto.s3.connection import Location
from boto.s3.lifecycle import Lifecycle, Transition, Rule

import string
import uuid
import json

global iam
global s3
global cloudfront
global connected

###
##  This template method is being deprecated,
##  in favor of building actual dict/JSON objects,
##  I'm just keeping it here for reference.
###

S3_USER_POLICY_TEMPLATE = """{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Effect":"Allow",
         "Action":[
            "s3:PutObject",
            "s3:PutObjectAcl",
            "s3:PutObjectAclVersion",
            "s3:GetObject",
            "s3:GetObjectVersion",
            "s3:DeleteObject",
            "s3:DeleteObjectVersion"
         ],
         "Resource":"arn:aws:s3:::BUCKET_NAME/DIRECTORY_NAME/USER_NAME/*"
      },
      {
         "Effect":"Allow",
         "Action":[
            "s3:ListBucket",
            "s3:GetBucketLocation",
            "s3:ListAllMyBuckets"
         ],
         "Resource":"arn:aws:s3:::BUCKET_NAME/DIRECTORY_NAME"
      }
   ]
}
"""

connected = False
AWS_ACCESS_KEY = ''
AWS_SECRET_ACCESS_KEY = ''

iam = None
s3 = None
cloudfront = None

def set_keys(AWS_ACCESS_KEY_VAR, AWS_SECRET_ACCESS_KEY_VAR):
    global AWS_ACCESS_KEY
    global AWS_SECRET_ACCESS_KEY

    AWS_ACCESS_KEY = AWS_ACCESS_KEY_VAR
    AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY_VAR

    return True

def connect():

    global connected
    global AWS_ACCESS_KEY
    global AWS_SECRET_ACCESS_KEY

    global iam
    global s3
    global cloudfront

    if not connected:
        iam = boto.connect_iam(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY)
        s3 = boto.connect_s3(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY)
        cloudfront = boto.connect_cloudfront(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY)
        connected = True

    return connected

def generate_user_policy(username, buckets, directoryname):
    S3_USER_POLICY_DICT = {}
    S3_USER_POLICY_DICT['Version'] = "2012-10-17"
    S3_USER_POLICY_DICT['Statement'] = []

    # This gives the user the ability to upload
    object_statement = {}
    object_statement['Effect'] = 'Allow'
    object_statement['Action'] = []
    object_statement['Action'].append('s3:PutObject')
    object_statement['Action'].append('s3:PutObjectAcl')
    object_statement['Action'].append('s3:PutObjectAclVersion')
    object_statement['Action'].append('s3:GetObject')
    object_statement['Action'].append('s3:GetObjectVersion')
    object_statement['Action'].append('s3:DeleteObject')
    object_statement['Action'].append('s3:DeleteObjectVersion')
    object_statement['Resource'] = []

    # They also need to be able to able to see other stuff about their bucket structure.
    access_statement = {}
    access_statement['Effect'] = 'Allow'
    access_statement['Action'] = []
    access_statement['Action'].append("s3:ListBucket")
    access_statement['Action'].append("s3:GetBucketLocation")
    access_statement['Action'].append("s3:ListAllMyBuckets")
    access_statement['Resource'] = []

    for bucket in buckets:

        object_resource_string = "arn:aws:s3:::BUCKET_NAME/DIRECTORY_NAME/USER_NAME/*".replace('BUCKET_NAME', bucket).replace('DIRECTORY_NAME', directoryname).replace('USER_NAME', username)
        object_statement['Resource'].append(object_resource_string)

        access_resource_string = "arn:aws:s3:::BUCKET_NAME/DIRECTORY_NAME".replace('BUCKET_NAME', bucket).replace('DIRECTORY_NAME', directoryname)
        access_statement['Resource'].append(access_resource_string)

    # Add these statements to the policy
    S3_USER_POLICY_DICT['Statement'].append(object_statement)
    S3_USER_POLICY_DICT['Statement'].append(access_statement)

    policy = json.dumps(S3_USER_POLICY_DICT, indent=2)

    return policy

###
##
## Create a new IAM user, and give them read/write access
## to a defined subdirectory in a list of buckets.
##
###

def create_user(username, bucketnames, directoryname):
    connect()

    def create_retry(username, bucketnames, directoryname, tries):

        if tries is 0:
            print "Something went wrong. Not sure what happened. Sorry."
            return None

        try:
            response = iam.create_user(username)
            user = response.user

            # Old way of doing it..
            # policy_json = S3_USER_POLICY_TEMPLATE.replace('BUCKET_NAME', bucketname).replace('DIRECTORY_NAME', directoryname).replace('USER_NAME', username)

            # New way of doing it: generate that shit!
            policy_json = generate_user_policy(username, bucketnames, directoryname)
            print policy_json

            response = iam.put_user_policy(user_name=username, policy_name=directoryname + "_" + username, policy_json=policy_json)
            return user

        except Exception, e:
            print e
            return create_retry(username + '-' + str(uuid.uuid4())[0:8], bucketnames, directoryname, tries-1)

    return create_retry(username, bucketnames, directoryname, 5)

###
##
## Get a user's AWS access keys.
##
###

def get_user_keys(username):
    connect()

    response = iam.create_access_key(username)
    access_key = response.access_key_id
    secret_key = response.secret_access_key

    return {
            'AWS_ACCESS_KEY': access_key,
            'AWS_SECRET_ACCESS_KEY': secret_key
            }

###
##
## Create a new bucket. Defaults to US east, but other locations can be supplied.
## Also set ACL policy so that other buckets can read from it.
##
###

def create_bucket(bucketname, location=None):
    connect()

    def create_retry(bucketname, location, tries):

        if tries is 0:
            return None

        try:
            if location:
                bucket = s3.create_bucket(bucketname, location=location)
            else:
                bucket = s3.create_bucket(bucketname)

            # Allow anybody to read this bucket,
            # and also set the principal so our other AWS services
            # can read it as well.
            bucket.set_acl('public-read')

            return bucket

        except Exception, e:
            print e
            return create_retry(bucketname + '-' + str(uuid.uuid4()), location, tries-1)

    return create_retry(bucketname, location, 5)

###
##
## Sets a glacier backup bucket for a defined bucket.
##
###

def backup_bucket(bucketname):
    connect()

    bucket = s3.get_bucket(bucketname)
    to_glacier = Transition(days=1, storage_class='GLACIER')
    rule = Rule('ruleid', '/', 'Enabled', transition=to_glacier)
    lifecycle = Lifecycle()
    lifecycle.append(rule)
    bucket.configure_lifecycle(lifecycle)

    return True

###
##
## Sets a Cloudfront policy for a defined bucket.
##
###

def move_bucket_to_cloudfront(bucketname):
    connect()

    origin = boto.cloudfront.origin.S3Origin(bucketname + '.s3.amazonaws.com')

    distro = cloudfront.create_distribution(origin=origin, enabled=True, comment=bucketname + " Distribution")
    return distro.domain_name
