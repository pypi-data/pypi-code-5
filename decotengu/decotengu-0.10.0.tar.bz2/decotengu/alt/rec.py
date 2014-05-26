#
# DecoTengu - dive decompression library.
#
# Copyright (C) 2013-2014 by Artur Wroblewski <wrobell@pld-linux.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import math
import logging

from ..engine import Step, Phase
from ..ft import recurse_while

logger = logging.getLogger(__name__)


class RecFistStopFinder(object):
    def __init__(self, engine):
        self.engine = engine

    def cc(self, v):
        engine = self.engine
        p3m = engine._p3m
        surface_pressure = engine.surface_pressure
        return math.ceil((v - surface_pressure) / p3m) * p3m + surface_pressure

    def ff(self, abs_p, limit, gas, data):
        engine = self.engine

        t = engine._pressure_to_time(abs_p - limit, engine.ascent_rate)

        if __debug__:
            logger.debug('{} -> {} for {}'.format(abs_p, limit, t))
        data = engine._tissue_pressure_ascent(abs_p, t, gas, data)
        abs_p = limit
        limit = self.cc(engine.model.ceiling_limit(data, data.gf))
        return abs_p, limit, gas, data

    def __call__(self, start, abs_p, gas):
        """
        Find first first decompression stop using Schreiner equation and
        bisect algorithm.

        Method returns dive step - start of first decompression stop.

        Below, by depth we mean absolute pressure of depth expressed in
        bars.

        The first decompression stop depth is searched between depth of
        starting dive step and target depth parameter. The latter can be
        surface or any other depth divisible by 3.

        The depth of first decompression stop is the shallowest depth,
        which does not breach the ascent limit imposed by ascent ceiling.
        The depth is divisble by 3.

        The implementation of the algorithm does not use
        :func:`decotengu.DecoTengu._step_next_ascent` method, so it can be
        safely overriden, i.e. by code using tabular based tissue
        calculations.

        :param start: Starting dive step indicating current depth.
        :param abs_p: Absolute pressure of target depth - surface or gas
            switch depth.
        :param gas: Gas mix configuration.
        """
        assert start.abs_p > abs_p, '{} vs. {}'.format(start.abs_p, abs_p)
        assert self._to_depth(abs_p) % 3 == 0, self._to_depth(abs_p)
        engine = self.engine


        end_abs_p = abs_p
        f_check = lambda abs_p, limit, gas, data: abs_p - limit >= engine._p3m and limit >= end_abs_p
            
        limit = self.cc(engine.model.ceiling_limit(start.data, start.data.gf))
        if start.abs_p - limit < engine._p3m:
            #logger.debug('xxx {} {} {}'.format(start, limit))
            return start

        abs_p, limit, _, data = recurse_while(f_check, self.ff, start.abs_p, limit, gas, start.data)
        time = engine._pressure_to_time(abs_p - limit, engine.ascent_rate)
        data = engine._tissue_pressure_ascent(abs_p, time, gas, data)
        stop = Step(Phase.ASCENT, limit, start.time + time, gas, data)

        if __debug__:
            p = start.abs_p - engine._time_to_pressure(time, engine.ascent_rate)
            depth = engine._to_depth(p)

            assert depth % 3 == 0, \
                'Invalid first stop depth pressure {}bar ({}m)' \
                .format(p, depth)

            if abs(p - abs_p) < const.EPSILON:
                logger.debug(
                    'find first stop: free from {} to {}, ascent time={}' \
                    .format(start.abs_p, abs_p, time)
                )
            else:
                logger.debug(
                    'find first stop: found at {}, ascent time={}' \
                    .format(p, time)
                )

        return stop


# vim: sw=4:et:ai
