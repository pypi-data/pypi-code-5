#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os, time
import time
import json
try:
    import regex as re
except ImportError:
    import re
import baker

def ignore_sigpipe(f):
    """decorator to supress sigpipe error"""
    def wrap(*args, **kw):
        try:
            return f(*args, **kw)
        except IOError, e:
            if e.errno!=32:
                raise
    wrap.func_name=f.func_name
    wrap.__name__=f.__name__
    return wrap

def read_lines(fh=sys.stdin, strip=True):
    """unbuffered readlines"""

    if strip:
        proc=lambda l: l.strip('\n')
    else:
        proc=lambda l: l

    while True:
        line=fh.readline()
        if not line:
            break
        yield proc(line)

### duration syntax
def _dclasses():
    s=1
    m=60
    h=60*m
    d=h*24
    w=d*7
    n=d*30
    y=d*365
    return locals()
dclasses=_dclasses()

def duration_notation_to_sec(dn):
    if not isinstance(dn, basestring):
        return dn
    m=re.match('^(\d+)(\p{Alphabetic=Yes})$', dn)
    dnum,dclass=m.groups()
    duration_s=int(dnum)*dclasses[dclass]
    return duration_s
###

@baker.command
def times(duration="24h", step=60*60, direction=-1, start=None):
    """sequence of time in unix epoch"""
    duration_s=duration_notation_to_sec(duration)
    step_s=duration_notation_to_sec(step)
    if not start:
        start=int(time.time())

    for t in range(start, start+direction*duration_s, direction*step_s):
        print t

@baker.command
def slowly(dwell=1):
    """slow down the stream"""

    dwell=float(dwell)

    while True:
        line=sys.stdin.readline()
        if not line:
            break
        sys.stdout.write(line)
        sys.stdout.flush()
        time.sleep(dwell)

@baker.command
def db_zip_rows():
    """heading+rows to json dict stream"""

    val_filter=lambda v: None if v=="NULL" else v

    line=sys.stdin.readline()
    heading=line.strip('\n').split('\t')
    for line in sys.stdin.readlines():
        cols=[ val_filter(c) for c in line.strip('\n').split('\t') ]
        print json.dumps(dict(zip(heading,cols)))

def vals_from_json():
    while True:
        line=sys.stdin.readline()
        if not line:
            break
        yield json.loads(line)

@baker.command
def dict_trans_key(key_mapping):
    """translate keys in dict stream"""

    key_mapping=json.loads(key_mapping)
    
    for d in vals_from_json():
        print json.dumps(dict([ (key_mapping.get(k,k),v) for k,v in d.items() ]))

@baker.command
def dict_trans_val(val_mapping):
    """translate values in dict stream.

    ### examples
    * normalize datetime
      echo '{"timestamp":"Sun May 11 09:32:33 PDT 2014"}' | dict_trans_val '{"timestamp":"iso8061z"}' 
      {"timestamp": "2014-05-11T09:32:33-07:00Z"}
    """
    # todo: generalize this to arbitrary path and operator
    # A lot of massaging can be done with built-in python expressions.
    # For anything else, functions have to be defined here.
    import dateutil.parser
    ops=dict(
        iso8061=lambda dt: dateutil.parser.parse(dt).isoformat(),
        iso8061z=lambda dt: dateutil.parser.parse(dt).isoformat()+'Z',
             )

    val_mapping=json.loads(val_mapping)
    mapper=dict( [ (k,ops[transformer_name]) for k,transformer_name in val_mapping.items() ])

    d2={}
    for d in vals_from_json():
        for k,v in d.items():
            transformer=mapper.get(k)
            v2=transformer(v) if transformer else v
            d2[k]=v2
        print json.dumps(d2)

@baker.command
def dict_update(update):
    """apply delta to dict streams
    """

    updated=json.loads(update)
    for d in vals_from_json():
        d.update(updated)
        print json.dumps(d)

@baker.command
def x_jsonpath(selector):
    """select elements with jsonpath in dict stream.
    """

    from jsonpath import jsonpath
    for val in vals_from_json():
        print jsonpath(val, selector)

def regex_parse(rx):
    """apply regex to text stream and yield match dicts
    """

    rxo=re.compile(rx)
    
    for line in read_lines():
        m=rxo.search(line)
        if m:
            yield m.groupdict()

@baker.command
def text_parse(rx):
    """regex-based text parsing"""
    for match_dict in parse(rx):
        print json.dumps(match_dict)

if __name__=='__main__':

    try:
        baker.run()
    except IOError, e:
        if e.errno!=32:
            raise
