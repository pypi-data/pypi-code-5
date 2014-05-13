#!/usr/bin/env python

"""Manage IPython.parallel clusters in the notebook.

Authors:

* Brian Granger
"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2008-2011  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import os

from zmq.eventloop import ioloop

from IPython.config.configurable import LoggingConfigurable
from IPython.utils.traitlets import Dict, Instance, CFloat
from IPython.parallel.apps.ipclusterapp import IPClusterStart
from IPython.core.profileapp import list_profiles_in
from IPython.core.profiledir import ProfileDir
from IPython.utils.path import get_ipython_dir


class DummyIPClusterStart(IPClusterStart):

    """Dummy subclass to skip init steps that conflict with global app.

    Instantiating and initializing this class should result in fully configured
    launchers, but no other side effects or state.
    """

    def init_signal(self):
        pass

    def reinit_logging(self):
        pass


class ClusterManager(LoggingConfigurable):

    profiles = Dict()

    delay = CFloat(1., config=True,
                   help="delay (in s) between starting the controller and the engines")

    loop = Instance('zmq.eventloop.ioloop.IOLoop')

    def _loop_default(self):
        from zmq.eventloop.ioloop import IOLoop
        return IOLoop.instance()

    def build_launchers(self, profile_dir):
        starter = DummyIPClusterStart(log=self.log)
        starter.initialize(['--profile-dir', profile_dir])
        cl = starter.controller_launcher
        esl = starter.engine_launcher
        n = starter.n
        return cl, esl, n

    def get_profile_dir(self, name, path):
        p = ProfileDir.find_profile_dir_by_name(path, name=name)
        return p.location

    def update_profiles(self):
        """List all profiles in the ipython_dir and cwd.
        """
        for path in [get_ipython_dir(), os.getcwdu()]:
            for profile in list_profiles_in(path):
                pd = self.get_profile_dir(profile, path)
                if profile not in self.profiles:
                    self.log.debug("Adding cluster profile '%s'" % profile)
                    self.profiles[profile] = {
                        'profile': profile,
                        'profile_dir': pd,
                        'status': 'stopped'
                    }

    def list_profiles(self):
        self.update_profiles()
        # sorted list, but ensure that 'default' always comes first
        default_first = lambda name: name if name != 'default' else ''
        result = [self.profile_info(p)
                  for p in sorted(self.profiles, key=default_first)]
        return result

    def check_profile(self, profile):
        if profile not in self.profiles:
            raise IOError(u'profile not found')

    def profile_info(self, profile):
        self.check_profile(profile)
        result = {}
        data = self.profiles.get(profile)
        result['profile'] = profile
        result['profile_dir'] = data['profile_dir']
        result['status'] = data['status']
        if 'n' in data:
            result['n'] = data['n']
        return result

    def start_cluster(self, profile, n=None):
        """Start a cluster for a given profile."""
        self.check_profile(profile)
        data = self.profiles[profile]
        if data['status'] == 'running':
            raise ValueError(u'cluster already running')
        cl, esl, default_n = self.build_launchers(data['profile_dir'])
        n = n if n is not None else default_n

        def clean_data():
            data.pop('controller_launcher', None)
            data.pop('engine_set_launcher', None)
            data.pop('n', None)
            data['status'] = 'stopped'

        def engines_stopped(r):
            self.log.debug('Engines stopped')
            if cl.running:
                cl.stop()
            clean_data()
        esl.on_stop(engines_stopped)

        def controller_stopped(r):
            self.log.debug('Controller stopped')
            if esl.running:
                esl.stop()
            clean_data()
        cl.on_stop(controller_stopped)

        dc = ioloop.DelayedCallback(lambda: cl.start(), 0, self.loop)
        dc.start()
        dc = ioloop.DelayedCallback(
            lambda: esl.start(n), 1000 * self.delay, self.loop)
        dc.start()

        self.log.debug('Cluster started')
        data['controller_launcher'] = cl
        data['engine_set_launcher'] = esl
        data['n'] = n
        data['status'] = 'running'
        return self.profile_info(profile)

    def stop_cluster(self, profile):
        """Stop a cluster for a given profile."""
        self.check_profile(profile)
        data = self.profiles[profile]
        if data['status'] == 'stopped':
            raise ValueError(u'cluster not running')
        data = self.profiles[profile]
        cl = data['controller_launcher']
        esl = data['engine_set_launcher']
        if cl.running:
            cl.stop()
        if esl.running:
            esl.stop()
        # Return a temp info dict, the real one is updated in the on_stop
        # logic above.
        result = {
            'profile': data['profile'],
            'profile_dir': data['profile_dir'],
            'status': 'stopped'
        }
        return result

    def stop_all_clusters(self):
        for p in self.profiles.keys():
            self.stop_cluster(p)


# rom subprocess import Popen, PIPE
# rom time import sleep
# rom uuid import uuid1
#
# rom IPython.parallel import Client
#
# rom pyqi.util import pyqi_system_call
#
# lass Computable(object):
#   def __init__(self, item, *args):
#       self.is_system_call = isinstance(item, str)
#       self.is_function_call = not self.is_system_call
#       self.item = item
#       self.args = args
#       self.result = None
#
# lass Manager(object):
#   def __init__(self, n_engines, worker_exec='', **stage):
#       if n_engines < 0:
#           raise ValueError("Need a positive number of engines")
#
# this should work fine for a local distribution, but possibly
#       self.cluster_id = uuid1()
#       ipcont_cmd = ['ipcontroller',
#                     '--cluster-id=%s' % self.cluster_id]
#       ipeng_cmd = ['ipengine',
#                    '--cluster-id=%s' % self.cluster_id]
#
#       self._ipcont_proc = Popen(ipcont_cmd, stdout=PIPE, stderr=PIPE)
#       sleep(1)
#       self._ipeng_procs = [Popen(ipeng_cmd, stdout=PIPE, stderr=PIPE)
#                            for i in range(n_engines)]
#
#       self.client = Client(cluster_id=self.cluster_id)
#       connect_attempts = 0
#       while len(self.client) < n_engines and connect_attempts < 30:
#           sleep(1)
#           connect_attempts += 1
#
#       if len(self.client) == 0:
#           raise ValueError("Timeout attempting to connect to engines!")
#
#       self.dview = self.client.direct_view()
#       self.lview = self.client.load_balanced_view()
#
#       self.dview.push(stage)
#       self.dview.execute(worker_exec, block=True)
#
#   def __del__(self):
#       self.client.shutdown(targets='all', hub=True)
#
#   def submit(self, computables):
#       for c in computables:
#           if c.is_system_call:
#               c.result = self.lview.apply(pyqi_system_call, c.item)
#           else:
#               c.result = self.lview.apply(c.item, *c.args)
#
#   def wait(self, computables=None):
#       if computables is None:
#           self.lview.wait(computables)
#       else:
#           self.lview.wait([c.result for c in computables])
#
