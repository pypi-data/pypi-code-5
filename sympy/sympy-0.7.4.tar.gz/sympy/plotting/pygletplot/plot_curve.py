from __future__ import print_function, division

from pyglet.gl import *
from plot_mode_base import PlotModeBase
from sympy.core import S
from sympy.core.compatibility import xrange


class PlotCurve(PlotModeBase):

    style_override = 'wireframe'

    def _on_calculate_verts(self):
        self.t_interval = self.intervals[0]
        self.t_set = list(self.t_interval.frange())
        self.bounds = [[S.Infinity, -S.Infinity, 0],
                       [S.Infinity, -S.Infinity, 0],
                       [S.Infinity, -S.Infinity, 0]]
        evaluate = self._get_evaluator()

        self._calculating_verts_pos = 0.0
        self._calculating_verts_len = float(self.t_interval.v_len)

        self.verts = list()
        b = self.bounds
        for t in self.t_set:
            try:
                _e = evaluate(t)    # calculate vertex
            except (NameError, ZeroDivisionError):
                _e = None
            if _e is not None:      # update bounding box
                for axis in range(3):
                    b[axis][0] = min([b[axis][0], _e[axis]])
                    b[axis][1] = max([b[axis][1], _e[axis]])
            self.verts.append(_e)
            self._calculating_verts_pos += 1.0

        for axis in range(3):
            b[axis][2] = b[axis][1] - b[axis][0]
            if b[axis][2] == 0.0:
                b[axis][2] = 1.0

        self.push_wireframe(self.draw_verts(False))

    def _on_calculate_cverts(self):
        if not self.verts or not self.color:
            return

        def set_work_len(n):
            self._calculating_cverts_len = float(n)

        def inc_work_pos():
            self._calculating_cverts_pos += 1.0
        set_work_len(1)
        self._calculating_cverts_pos = 0
        self.cverts = self.color.apply_to_curve(self.verts,
                                                self.t_set,
                                                set_len=set_work_len,
                                                inc_pos=inc_work_pos)
        self.push_wireframe(self.draw_verts(True))

    def calculate_one_cvert(self, t):
        vert = self.verts[t]
        return self.color(vert[0], vert[1], vert[2],
                          self.t_set[t], None)

    def draw_verts(self, use_cverts):
        def f():
            glBegin(GL_LINE_STRIP)
            for t in xrange(len(self.t_set)):
                p = self.verts[t]
                if p is None:
                    glEnd()
                    glBegin(GL_LINE_STRIP)
                    continue
                if use_cverts:
                    c = self.cverts[t]
                    if c is None:
                        c = (0, 0, 0)
                    glColor3f(*c)
                else:
                    glColor3f(*self.default_wireframe_color)
                glVertex3f(*p)
            glEnd()
        return f
