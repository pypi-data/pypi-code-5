#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging

from supervisor import childutils


class SVDog(object):
    def __init__(self, logger_name=None, processes=None, excludes=None):
        self.processes = processes
        self.excludes = excludes
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.logger = logging.getLogger(logger_name or __name__)
 
    def run(self):
        while True:
            headers, payload = childutils.listener.wait(self.stdin, self.stdout)

            if not payload.endswith('\n'):
                payload = payload + '\n'

            pheaders, pdata = childutils.eventdata(payload)

            if self.excludes and pheaders.get('pheaders') in self.excludes:
                childutils.listener.ok(self.stdout)
                continue

            if self.processes and pheaders.get('pheaders') not in self.processes:
                childutils.listener.ok(self.stdout)
                continue
 
            self.logger.fatal('%s\n%s', headers, payload)
            childutils.listener.ok(self.stdout)
