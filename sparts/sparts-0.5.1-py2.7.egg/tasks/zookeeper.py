# Copyright (c) 2014, Facebook, Inc.  All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#

from sparts.fileutils import NamedTemporaryDirectory
from sparts.tasks.twisted_command import CommandTask
from sparts.vtask import VTask

from functools import partial


class ZookeeperServerTask(VTask):
    DEPS = [CommandTask]
    LOOPLESS = True

    @property
    def cmd(self):
        return self.service.requireTask(CommandTask)

    def _event(self, *args, **kwargs):
        print "_event", args, kwargs

    def initTask(self):
        self.tempdir = NamedTemporaryDirectory()
        self.tempdir.makedirs('data')
        self.tempdir.makedirs('log')
        self.tempdir.makedirs('bin')
        self.tempdir.symlink('/usr/share/zookeeper/bin/zkServer.sh',
                             'bin/zkServer.sh')
        self.tempdir.writefile('zoo.cfg', self.getZkConfig())

    def start(self):
        binpath = self.tempdir.join('bin/zkServer.sh')
        self.cmd.run('%s start-foreground %s' %
                     (binpath, self.tempdir.join('zoo.cfg')),
                     on_stdout=partial(self._event, 'stdout'),
                     on_stderr=partial(self._event, 'stderr'),
                     on_exit=partial(self._event, 'exit'),
                     env={
                        'ZOOCFG': self.tempdir.join('zoo.cfg'),
                        'ZOOCFGDIR': self.tempdir.name,
                        'ZOO_DATADIR': self.tempdir.join('data'),
                        'ZOO_LOG_DIR': self.tempdir.join('log'),
                     }
                    )

    def getZkConfig(self, port=2181):
        return """
tickTime=2000
initLimit=10
syncLimit=5
dataDir={datadir}
port={port}
        """.format(datadir=self.tempdir.join('data'),
                   port=port)
