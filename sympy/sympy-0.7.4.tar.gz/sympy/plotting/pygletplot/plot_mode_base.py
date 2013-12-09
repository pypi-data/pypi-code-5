from __future__ import print_function, division

from pyglet.gl import *
from plot_mode import PlotMode
from threading import Thread, Event, RLock
from color_scheme import ColorScheme
from sympy.core import S
from sympy.core.compatibility import is_sequence
from time import sleep
import warnings


class PlotModeBase(PlotMode):
    """
    Intended parent class for plotting
    modes. Provides base functionality
    in conjunction with its parent,
    PlotMode.
    """

    ##
    ## Class-Level Attributes
    ##

    """
    The following attributes are meant
    to be set at the class level, and serve
    as parameters to the plot mode registry
    (in PlotMode). See plot_modes.py for
    concrete examples.
    """

    """
    i_vars
        'x' for Cartesian2D
        'xy' for Cartesian3D
        etc.

    d_vars
        'y' for Cartesian2D
        'r' for Polar
        etc.
    """
    i_vars, d_vars = '', ''

    """
    intervals
        Default intervals for each i_var, and in the
        same order. Specified [min, max, steps].
        No variable can be given (it is bound later).
    """
    intervals = []

    """
    aliases
        A list of strings which can be used to
        access this mode.
        'cartesian' for Cartesian2D and Cartesian3D
        'polar' for Polar
        'cylindrical', 'polar' for Cylindrical

        Note that _init_mode chooses the first alias
        in the list as the mode's primary_alias, which
        will be displayed to the end user in certain
        contexts.
    """
    aliases = []

    """
    is_default
        Whether to set this mode as the default
        for arguments passed to PlotMode() containing
        the same number of d_vars as this mode and
        at most the same number of i_vars.
    """
    is_default = False

    """
    All of the above attributes are defined in PlotMode.
    The following ones are specific to PlotModeBase.
    """

    """
    A list of the render styles. Do not modify.
    """
    styles = {'wireframe': 1, 'solid': 2, 'both': 3}

    """
    style_override
        Always use this style if not blank.
    """
    style_override = ''

    """
    default_wireframe_color
    default_solid_color
        Can be used when color is None or being calculated.
        Used by PlotCurve and PlotSurface, but not anywhere
        in PlotModeBase.
    """

    default_wireframe_color = (0.85, 0.85, 0.85)
    default_solid_color = (0.6, 0.6, 0.9)
    default_rot_preset = 'xy'

    ##
    ## Instance-Level Attributes
    ##

    ## 'Abstract' member functions
    def _get_evaluator(self):
        if self.use_lambda_eval:
            try:
                e = self._get_lambda_evaluator()
                return e
            except:
                warnings.warn("\nWarning: creating lambda evaluator failed. "
                       "Falling back on sympy subs evaluator.")
        return self._get_sympy_evaluator()

    def _get_sympy_evaluator(self):
        raise NotImplementedError()

    def _get_lambda_evaluator(self):
        raise NotImplementedError()

    def _on_calculate_verts(self):
        raise NotImplementedError()

    def _on_calculate_cverts(self):
        raise NotImplementedError()

    ## Base member functions
    def __init__(self, *args, **kwargs):
        self.verts = []
        self.cverts = []
        self.bounds = [[S.Infinity, -S.Infinity, 0],
                       [S.Infinity, -S.Infinity, 0],
                       [S.Infinity, -S.Infinity, 0]]
        self.cbounds = [[S.Infinity, -S.Infinity, 0],
                        [S.Infinity, -S.Infinity, 0],
                        [S.Infinity, -S.Infinity, 0]]

        self._draw_lock = RLock()

        self._calculating_verts = Event()
        self._calculating_cverts = Event()
        self._calculating_verts_pos = 0.0
        self._calculating_verts_len = 0.0
        self._calculating_cverts_pos = 0.0
        self._calculating_cverts_len = 0.0

        self._max_render_stack_size = 3
        self._draw_wireframe = [-1]
        self._draw_solid = [-1]

        self._style = None
        self._color = None

        self.predraw = []
        self.postdraw = []

        self.use_lambda_eval = self.options.pop('use_sympy_eval', None) is None
        self.style = self.options.pop('style', '')
        self.color = self.options.pop('color', 'rainbow')
        self.bounds_callback = kwargs.pop('bounds_callback', None)

        self._on_calculate()

    def synchronized(f):
        def w(self, *args, **kwargs):
            self._draw_lock.acquire()
            try:
                r = f(self, *args, **kwargs)
                return r
            finally:
                self._draw_lock.release()
        return w

    @synchronized
    def push_wireframe(self, function):
        """
        Push a function which performs gl commands
        used to build a display list. (The list is
        built outside of the function)
        """
        assert callable(function)
        self._draw_wireframe.append(function)
        if len(self._draw_wireframe) > self._max_render_stack_size:
            del self._draw_wireframe[1]  # leave marker element

    @synchronized
    def push_solid(self, function):
        """
        Push a function which performs gl commands
        used to build a display list. (The list is
        built outside of the function)
        """
        assert callable(function)
        self._draw_solid.append(function)
        if len(self._draw_solid) > self._max_render_stack_size:
            del self._draw_solid[1]  # leave marker element

    def _create_display_list(self, function):
        dl = glGenLists(1)
        glNewList(dl, GL_COMPILE)
        function()
        glEndList()
        return dl

    def _render_stack_top(self, render_stack):
        top = render_stack[-1]
        if top == -1:
            return -1  # nothing to display
        elif callable(top):
            dl = self._create_display_list(top)
            render_stack[-1] = (dl, top)
            return dl  # display newly added list
        elif len(top) == 2:
            if GL_TRUE == glIsList(top[0]):
                return top[0]  # display stored list
            dl = self._create_display_list(top[1])
            render_stack[-1] = (dl, top[1])
            return dl  # display regenerated list

    def _draw_solid_display_list(self, dl):
        glPushAttrib(GL_ENABLE_BIT | GL_POLYGON_BIT)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glCallList(dl)
        glPopAttrib()

    def _draw_wireframe_display_list(self, dl):
        glPushAttrib(GL_ENABLE_BIT | GL_POLYGON_BIT)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glEnable(GL_POLYGON_OFFSET_LINE)
        glPolygonOffset(-0.005, -50.0)
        glCallList(dl)
        glPopAttrib()

    @synchronized
    def draw(self):
        for f in self.predraw:
            if callable(f):
                f()
        if self.style_override:
            style = self.styles[self.style_override]
        else:
            style = self.styles[self._style]
        # Draw solid component if style includes solid
        if style & 2:
            dl = self._render_stack_top(self._draw_solid)
            if dl > 0 and GL_TRUE == glIsList(dl):
                self._draw_solid_display_list(dl)
        # Draw wireframe component if style includes wireframe
        if style & 1:
            dl = self._render_stack_top(self._draw_wireframe)
            if dl > 0 and GL_TRUE == glIsList(dl):
                self._draw_wireframe_display_list(dl)
        for f in self.postdraw:
            if callable(f):
                f()

    def _on_change_color(self, color):
        Thread(target=self._calculate_cverts).start()

    def _on_calculate(self):
        Thread(target=self._calculate_all).start()

    def _calculate_all(self):
        self._calculate_verts()
        self._calculate_cverts()

    def _calculate_verts(self):
        if self._calculating_verts.isSet():
            return
        self._calculating_verts.set()
        try:
            self._on_calculate_verts()
        finally:
            self._calculating_verts.clear()
        if callable(self.bounds_callback):
            self.bounds_callback()

    def _calculate_cverts(self):
        if self._calculating_verts.isSet():
            return
        while self._calculating_cverts.isSet():
            sleep(0)  # wait for previous calculation
        self._calculating_cverts.set()
        try:
            self._on_calculate_cverts()
        finally:
            self._calculating_cverts.clear()

    def _get_calculating_verts(self):
        return self._calculating_verts.isSet()

    def _get_calculating_verts_pos(self):
        return self._calculating_verts_pos

    def _get_calculating_verts_len(self):
        return self._calculating_verts_len

    def _get_calculating_cverts(self):
        return self._calculating_cverts.isSet()

    def _get_calculating_cverts_pos(self):
        return self._calculating_cverts_pos

    def _get_calculating_cverts_len(self):
        return self._calculating_cverts_len

    ## Property handlers
    def _get_style(self):
        return self._style

    @synchronized
    def _set_style(self, v):
        if v is None:
            return
        if v == '':
            step_max = 0
            for i in self.intervals:
                if i.v_steps is None:
                    continue
                step_max = max([step_max, i.v_steps])
            v = ['both', 'solid'][step_max > 40]
        #try:
        assert v in self.styles
        if v == self._style:
            return
        self._style = v
        #except Exception as e:
            #raise RuntimeError(("Style change failed. "
            #                 "Reason: %s is not a valid "
            #                 "style. Use one of %s.") %
            #                 (str(v), ', '.join(self.styles.iterkeys())))

    def _get_color(self):
        return self._color

    @synchronized
    def _set_color(self, v):
        try:
            if v is not None:
                if is_sequence(v):
                    v = ColorScheme(*v)
                else:
                    v = ColorScheme(v)
            if repr(v) == repr(self._color):
                return
            self._on_change_color(v)
            self._color = v
        except Exception as e:
            raise RuntimeError(("Color change failed. "
                                "Reason: %s" % (str(e))))

    style = property(_get_style, _set_style)
    color = property(_get_color, _set_color)

    calculating_verts = property(_get_calculating_verts)
    calculating_verts_pos = property(_get_calculating_verts_pos)
    calculating_verts_len = property(_get_calculating_verts_len)

    calculating_cverts = property(_get_calculating_cverts)
    calculating_cverts_pos = property(_get_calculating_cverts_pos)
    calculating_cverts_len = property(_get_calculating_cverts_len)

    ## String representations

    def __str__(self):
        f = ", ".join(str(d) for d in self.d_vars)
        o = "'mode=%s'" % (self.primary_alias)
        return ", ".join([f, o])

    def __repr__(self):
        f = ", ".join(str(d) for d in self.d_vars)
        i = ", ".join(str(i) for i in self.intervals)
        d = [('mode', self.primary_alias),
             ('color', str(self.color)),
             ('style', str(self.style))]

        o = "'%s'" % (("; ".join("%s=%s" % (k, v)
                                for k, v in d if v != 'None')))
        return ", ".join([f, i, o])
