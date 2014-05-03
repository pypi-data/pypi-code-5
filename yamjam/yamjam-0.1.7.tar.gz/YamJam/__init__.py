#!/usr/bin/env python
''' yamjam is a unified generic config method.  It allows multiple internal
projects to share common configuration settings, keeping the information stored
in a more secure area readable only by the user.
'''
import yaml
from yaml import YAMLError
import os
import warnings


def mergeDicts(s, t):
    '''being deprecated use merge_dicts'''
    wmsg = "mergeDicts will be deprecated in 0.1.8. Use merge_dicts."
    warnings.warn(wmsg, PendingDeprecationWarning)
    return merge_dicts(s, t)


def merge_dicts(bcfg, ocfg):
    '''smartly merge dictionaries bcfg and ocfg, unlike dict.update()'''
    for k in ocfg:
        if type(ocfg[k]) is type({}):
            if k in bcfg:  # if there is a similar element in bcfg
                merge_dicts(bcfg[k], ocfg[k]) # merge them

            else:
                bcfg[k] = ocfg[k] # else no merge required, just add it in

        else: # not a dict, so just replace
            bcfg[k] = ocfg[k]

    return bcfg


def yamjam(yjFnames='~/.yamjam/config.yaml;config.yaml', merge=True, safe=True):
    '''The main yamjam config file is located ~/.yamjam/config.yaml
        on windows:  c:\documents and settings\[username]\.yamjam\config.yaml
        on unix:     ~\.yamjam\config.yam;
       Then yamjam looks for possible overrides/additions in the local
       config.yaml(if it exists)

    You can override the config file(s) when you call the function by specifying
    a different one explicitly. i.e.
        myConfig = yamjam('file/path/filename')

    By default YamJam looks for 2 config.yaml files, the main and then a project
    specific one.  You may specify one or more files. Each file path listed
    should be separated by semi-colons(;)

    merge=True - Use smart merge as compared to the dict.update() method

    The file is yaml formatted which is a superset of json.
    http://www.yaml.org/

    Every call to yamjam() re-reads the config file.  If you wish to cache the
    info then do it in the calling code. i.e.
        myConfig = yamjam()

    If you only want to cache part of the configuration
        myCfg = yamjam()['mykey']
    '''
    if safe:
        yaml_loader = yaml.safe_load
    else:
        yaml_loader = yaml.load

    config = {}
    for _yjFname in [f.strip() for f in yjFnames.split(';')]:
        if os.path.exists(os.path.expanduser(_yjFname)):
            ycfg = yaml_loader(open(os.path.expanduser(_yjFname), "rb").read())
            if ycfg:
                if merge:
                    config = merge_dicts(config, ycfg)
                else:
                    config.update(ycfg)
    return config
