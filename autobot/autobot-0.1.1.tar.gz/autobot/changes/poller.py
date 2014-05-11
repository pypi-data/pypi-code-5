# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

import os
import time
import tempfile
from datetime import datetime
from twisted.python import log
from twisted.internet import defer, utils

from buildbot.changes import base, changes

class Poller(base.PollingChangeSource):
    """
    This will poll a remote resource for changes and submit
    them to the change master.
    """

    src = '' # repository type

    compare_attrs = ["repourl", "branch", "workdir",
                     "pollInterval", "binary", "usetimestamps",
                     "category", "project"]

    def __init__(self, repourl, binary=None, branch=None,
                 workdir=None, pollInterval=10*60,
                 usetimestamps=True,
                 category=None, project=None,
                 pollinterval=-2):

        # for backward compatibility; the parameter used to be spelled with 'i'
        if pollinterval != -2:
            pollInterval = pollinterval

        if project is None: project = ''
        self.repourl = repourl
        self.branch = branch
        self.pollInterval = pollInterval
        self.lastChange = time.time()
        self.lastPoll = time.time()
        self.binary = binary
        self.workdir = workdir
        self.usetimestamps = usetimestamps
        self.category = category
        self.project = project
        self.changeCount = 0
        self.commitInfo  = {}
        self.initLock = defer.DeferredLock()

        if not self.workdir:
            self.workdir = tempfile.mkdtemp()

        self.name = '%s: %s#%s' % (self.__class__.__name__, repourl, branch)

    def initRepository(self, _):
        """initialize a repository or whatever"""

        # make the directory, if necessary
        d = defer.succeed(None)
        def make_dir(_):
            dirpath = os.path.dirname(self.workdir.rstrip(os.sep))
            if not os.path.exists(dirpath):
                log.msg('%s: creating parent directories for workdir' % self.name)
                os.makedirs(dirpath)
        d.addCallback(make_dir)

        # perform the initialization
        def processCommand(command):
            d = utils.getProcessOutputAndValue(self.binary,
                                               command,
                                               env=dict(PATH=os.environ['PATH']))
            return d
        for command in self.initializationCommands():
            self.log('%s %s' % (self.binary, ' '.join(command)))
            d.addCallback(lambda _: processCommand(command[:]))
            # XXX for some retarded reason, only the first one of these
            # seems actually to get called
            # i don't know....all i do know is that i'm tired of writing
            # twisted code

        # finish up
        def log_finished(_):
            log.msg("%s: finished initializing working dir %s from %s" % (self.name, self.workdir, self.repourl))
        d.addCallback(log_finished)
        return d

    def log(self, msg):
        log.msg('%s: %s' % (self.name, msg))

    def describe(self):
        status = ""
        if not self.parent:
            status = "[STOPPED - check log]"
        str = '%s watching the remote repository %s, branch: %s %s' \
                % (self.name, self.repourl, self.branch, status)
        return str

    def poll(self):
        """poll for new changes"""

        d = self._get_changes()
        d.addCallback(self._process_changes)
        d.addErrback(self._process_changes_failure)
        d.addCallback(self._catch_up)
        d.addErrback(self._catch_up_failure)
        return d

    ### functions relating to hashing

    def _setPreHash(self, _hash):
        self.preHash = _hash.strip()
        self.log("preHash is %s" % self.preHash)

    def _setPostHash(self, _hash):
        self.postHash = _hash.strip()
        self.log("postHash is %s" % self.postHash)

    def _get_changes(self):
        """update the changes if the hash doesnt match"""

        self.lastPoll = time.time()
        self.log('polling repo at %s : %s' % (self.repourl, self.lastPoll))

        d = defer.succeed(None)
        # ensure the repository is initialized
        if not self.isInitialized():
            self.log('Initializing new repository at %s' % self.workdir)
            d.addCallback(self.initRepository)

        # get the hash before updating
        d.addCallback(self._hash)
        d.addCallback(self._setPreHash)

        # update
        d.addCallback(self._fetch)

        # set the post hash
        d.addCallback(self._hash)
        d.addCallback(self._setPostHash)

        return d

    ### functions related to processing changes

    def _process_changes(self, _):
        """processes the changes between the preHash and the postHash"""

        d = defer.succeed(None)

        # get the change list
        self.changeCount = 0
        if self.preHash == self.postHash:
            return d

        d.addCallback(self._change_list)
        d.addCallback(self._process_change_list)
        return d

    def _process_change_list(self, revList):

        self.changeCount = len(revList)
        self.log('processing %d changes: %s in "%s"'
                 % (self.changeCount, revList, self.workdir) )

        # get metadata for changes and send them to master
        d = defer.succeed(None)
        for rev in revList:
            d.addCallback(self._process_change, rev)
        return d

    def _process_change(self, something, rev):
        self.commitInfo = {}
        self.log('processing change %s (something=%s)' % (rev, something))
        d = defer.succeed(None)
        d.addCallback(self._get_commit_timestamp, rev)
        d.addCallback(self._get_commit_name, rev)
        d.addCallback(self._get_commit_files, rev)
        d.addCallback(self._get_commit_comments, rev)
        d.addCallback(self._add_change, rev)
        return d

    def _add_change(self, _, rev):
        log.msg("_add_change results: %s" % self.commitInfo)

        # convert the timestamp into a datetime object
        # (required in buildbot 0.8.5)
        timestamp = self.commitInfo['timestamp']
        if isinstance(timestamp, int) or isinstance(timestamp, float):
            timestamp = datetime.utcfromtimestamp(timestamp)

        self.log('timestamp: %s' % timestamp)

        # send the change to the master
        c = changes.Change(who=self.commitInfo['name'],
                           revision=rev,
                           files=self.commitInfo['files'],
                           comments=self.commitInfo['comments'],
                           when=self.commitInfo['timestamp'],
                           branch=self.branch,
                           category=self.category,
                           project=self.project,
                           repository=self.repourl)
        log.msg("parent: %s, %s" % (self.parent, getattr(self.parent, 'module', None)))
        self.master.addChange(author=self.commitInfo['name'],
                              revision=rev,
                              files=self.commitInfo['files'],
                              comments=self.commitInfo['comments'],
                              when_timestamp=timestamp,
                              branch=self.branch,
                              category=self.category,
                              project=self.project,
                              repository=self.repourl,
                              src=self.src)
        self.lastChange = self.lastPoll


    def _process_changes_failure(self, f):
        log.msg('%s: repo poll failed' % self.name)
        log.err(f)
        # eat the failure to continue along the defered chain - we still want to catch up
        return None

    def _catch_up_failure(self, f):
        log.err(f)
        log.msg('%s: please resolve issues in local repo: %s' % (self.name, self.workdir))
        # this used to stop the service, but this is (a) unfriendly to tests and (b)
        # likely to leave the error message lost in a sea of other log messages

    def _convert_nonzero_to_failure(self, res):
        "utility method to handle the result of getProcessOutputAndValue"
        (stdout, stderr, code) = res
        if code != 0:
            raise EnvironmentError('command failed with exit code %d: %s' % (code, stderr))

    def _stop_on_failure(self, f):
        "utility method to stop the service when a failure occurs"
        if self.running:
            d = defer.maybeDeferred(lambda : self.stopService())
            d.addErrback(log.err, 'while stopping broken %s service' % self.name)
        return f


###

class HgPoller(Poller):
    """poller for a mercurial source"""

    src = 'hg' # type

    def __init__(self, repourl, binary='hg', branch='default', **kwargs):
        Poller.__init__(self, repourl, binary=binary, branch=branch, **kwargs)

    def isInitialized(self):
        """is the repository initialized?"""
        return os.path.exists(os.path.join(self.workdir, '.hg'))

    def checkoutBranch(self, _):
        """checkout the branch"""
        d = utils.getProcessOutput(self.binary, ['checkout', self.branch],
                                   path=self.workdir,
                                   env=dict(PATH=os.environ['PATH']),
                                   errortoo=True)
        return d

    def initializationCommands(self):
        """commands to initialize a mercurial repository"""
        commands = [ [ 'clone', self.repourl, self.workdir ] ]
        if self.branch != 'default':
            commands.append(['-r', self.workdir, 'checkout', self.branch])
        return commands

    def update(self, _):
        args = ['pull', self.repourl]
        d = utils.getProcessOutput(self.binary, args, path=self.workdir,
                                   env=dict(PATH=os.environ['PATH']),
                                   errortoo=True )
        return d


    def _fetch(self, _):
        d = self.checkoutBranch(None)
        d.addCallback(self.update)
        return d

    def _hash(self, _):
        """commit hash"""
        d = utils.getProcessOutput(self.binary, ['tip', '--template', '{node}\\n'],
                                   path=self.workdir,
                                   env=dict(PATH=os.environ['PATH']), errortoo=False )
        return d


    def _change_list(self, _):
        """
        return a deferred something-or-other that has the changes to be
        processed.  XXX the format is pretty particular
        """
        range = '%s:%s' % (self.preHash, self.postHash)
        d = utils.getProcessOutput(self.binary, ['log', '-r', range, '--template', '{node}\\n'],
                                   path=self.workdir,
                                   env=dict(PATH=os.environ['PATH']), errortoo=False )
        def split_changes(raw_changes):
            changes = raw_changes.strip()
            if not changes:
                return []
            return changes.split()[1:]
        d.addCallback(split_changes)

        return d

    def _catch_up(self, rev):
        if self.changeCount == 0:
            self.log('%s: no changes, no catch_up' % self.postHash)
            return
        self.log('catching up to %s' % self.postHash)
        args = ['update']
        d = utils.getProcessOutputAndValue(self.binary, args, path=self.workdir, env=dict(PATH=os.environ['PATH']))
        d.addCallback(self._convert_nonzero_to_failure)
        return d

    ### functions for retrieving various metadatas

    ### timestamp

    def _get_commit_timestamp(self, _, rev):
        # unix timestamp
        args = ['log', '-r', rev, '--template', '{date|hgdate}']
        d = utils.getProcessOutput(self.binary, args, path=self.workdir, env=dict(PATH=os.environ['PATH']), errortoo=False )
        d.addCallback(self._get_commit_timestamp_from_output)
        return d

    def _get_commit_timestamp_from_output(self, output):
        stripped_output = output.strip()
        if self.usetimestamps:
            try:
                _stamp, offset = output.split()
                stamp = float(_stamp)
            except Exception, e:
                log.msg('%s: caught exception converting output "%s" to timestamp' % (self.name, stripped_output))
                raise e
            self.commitInfo['timestamp'] = stamp
        else:
            self.commitInfo['timestamp'] = None

    ### commit author ('name')

    def _get_commit_name(self, _, rev):
        """get the author of a commit"""
        args = ['log', '-r', rev, '--template', '{author}']
        d = utils.getProcessOutput(self.binary, args, path=self.workdir, env=dict(PATH=os.environ['PATH']), errortoo=False )
        d.addCallback(self._get_commit_name_from_output)
        return d

    def _get_commit_name_from_output(self, output):
        stripped_output = output.strip()
        if len(stripped_output) == 0:
            raise EnvironmentError('could not get commit name for rev')
        self.commitInfo['name'] = stripped_output
        return self.commitInfo['name'] # for tests, or so gitpoller says

    ### files

    def _get_commit_files(self, _, rev):
        """get the files associated with a commit"""
        args = ['log', '-r', rev, '--template', '{files}']
        d = utils.getProcessOutput(self.binary, args, path=self.workdir, env=dict(PATH=os.environ['PATH']), errortoo=False )
        d.addCallback(self._get_commit_files_from_output)
        return d

    def _get_commit_files_from_output(self, output):
        fileList = output.strip().split()
        self.commitInfo['files'] = fileList
        return self.commitInfo['files']

    ### commit comments

    def _get_commit_comments(self, _, rev):
        """get the commit message"""
        args = ['log', '-r', rev, '--template', '{desc}']
        d = utils.getProcessOutput(self.binary, args, path=self.workdir, env=dict(PATH=os.environ['PATH']), errortoo=False )
        d.addCallback(self._get_commit_comments_from_output)
        return d

    def _get_commit_comments_from_output(self, output):
        stripped_output = output.strip()
        self.commitInfo['comments'] = stripped_output
        return self.commitInfo['comments']


###

class GitPoller(Poller):

    src = 'git'

    def __init__(self, repourl, binary='git', branch='master', **kwargs):
        Poller.__init__(self, repourl, binary=binary, branch=branch, **kwargs)

    def isInitialized(self):
        """is the repository initialized?"""
        return os.path.exists(os.path.join(self.workdir, '.git'))

    def checkoutBranch(self, _):
        """checkout the branch"""
        # XXX I have no clue why I am doing this except that I'm working
        # around twisted evidently not doing what I think its doing
        # so in the face of a clearly superior architecture I will
        # randomly stab around and hope to god that eventually,
        # through sheer dumb luck, I can get on the proper branch
        d = utils.getProcessOutput(self.binary, ['checkout', self.branch],
                                   path=self.workdir,
                                   env=dict(PATH=os.environ['PATH']),
                                   errortoo=True)
        return d


    def initializationCommands(self):
        """commands needed to initialize the repository"""
        commands = [ [ 'clone', self.repourl, self.workdir ] ]
        if self.branch != 'master':
            git_dir = self.workdir.rstrip('/')
            commands.append(['--git-dir', git_dir + '/.git',
                             '--work-tree', git_dir,
                             'checkout', self.branch])
        log.msg('GitPoller: initializationCommands: %s' % commands)
        return commands

    def update(self, _):
        args = ['pull', 'origin', self.branch]
        d = utils.getProcessOutput(self.binary, args, path=self.workdir,
                                   env=dict(PATH=os.environ['PATH']),
                                   errortoo=True)
        return d

    def _fetch(self, _):
        d = self.checkoutBranch(None)
        d.addCallback(self.update)
        return d

    def _hash(self, _):
        """
        get hash of where you are now:
        git rev-parse HEAD
        """
        d = utils.getProcessOutput(self.binary, ['rev-parse', 'HEAD'],
                                   path=self.workdir,
                                   env=dict(PATH=os.environ['PATH']), errortoo=False)
        return d


    def _change_list(self, _):
        range = '%s..%s' % (self.preHash, self.postHash)
        d = utils.getProcessOutput(self.binary,
                                   ['log', range, r'--format=%H'],
                                   path=self.workdir,
                                   env=dict(PATH=os.environ['PATH']),
                                   errortoo=False)
        def split_changes(raw_changes):
            changes = raw_changes.strip()
            if not changes:
                return []
            return changes.split()
        d.addCallback(split_changes)
        return d

    def _catch_up(self, rev):
        if self.changeCount == 0:
            self.log('%s: no changes, no catch_up' % self.postHash)
            return
        self.log('catching up to %s' % self.postHash)

        # XXX keeping this in as a dummy for now
        # should *really* do fetch earlier and *now* do pull
        # (or whatever)
        args = ['status']
        d = utils.getProcessOutputAndValue(self.binary, args, path=self.workdir, env=dict(PATH=os.environ['PATH']))
        d.addCallback(self._convert_nonzero_to_failure)
        return d

    ### metadata for commits

    ### timestamp

    def _get_commit_timestamp(self, _, rev):
        # unix timestamp
        args = ['log', rev, '--no-walk', r'--format=%ct']
        d = utils.getProcessOutput(self.binary, args, path=self.workdir,
                                   env=dict(PATH=os.environ['PATH']),
                                   errortoo=False )
        d.addCallback(self._get_commit_timestamp_from_output)
        return d

    def _get_commit_timestamp_from_output(self, output):
        stripped_output = output.strip()
        if self.usetimestamps:
            try:
                stamp = float(stripped_output)
            except Exception, e:
                    self.log('caught exception converting output \'%s\' to timestamp' % stripped_output)
                    raise e
            self.commitInfo['timestamp'] = stamp
        else:
            self.commitInfo['timestamp'] = None
        return self.commitInfo['timestamp'] # for tests

    ### commit author ('name')

    def _get_commit_name(self, _, rev):
        args = ['log', rev, '--no-walk', r'--format=%aE']
        d = utils.getProcessOutput(self.binary, args, path=self.workdir,
                                   env=dict(PATH=os.environ['PATH']),
                                   errortoo=False )
        d.addCallback(self._get_commit_name_from_output)
        return d

    def _get_commit_name_from_output(self, output):
        stripped_output = output.strip()
        if len(stripped_output) == 0:
            raise EnvironmentError('could not get commit name for rev')
        self.commitInfo['name'] = stripped_output
        return self.commitInfo['name'] # for tests

    ### files

    def _get_commit_files(self, _, rev):
        args = ['log', rev, '--name-only', '--no-walk', r'--format=%n']
        d = utils.getProcessOutput(self.binary, args, path=self.workdir,
                                   env=dict(PATH=os.environ['PATH']),
                                   errortoo=False )
        d.addCallback(self._get_commit_files_from_output)
        return d

    def _get_commit_files_from_output(self, output):
        fileList = output.split()
        self.commitInfo['files'] = fileList
        return self.commitInfo['files'] # for tests


    ### comments

    def _get_commit_comments(self, _, rev):
        args = ['log', rev, '--no-walk', r'--format=%s%n%b']
        d = utils.getProcessOutput(self.binary, args, path=self.workdir,
                                   env=dict(PATH=os.environ['PATH']),
                                   errortoo=False )
        d.addCallback(self._get_commit_comments_from_output)
        return d

    def _get_commit_comments_from_output(self, output):
        stripped_output = output.strip()
        if len(stripped_output) == 0:
            raise EnvironmentError('could not get commit comment for rev')
        self.commitInfo['comments'] = stripped_output
        return self.commitInfo['comments'] # for tests
