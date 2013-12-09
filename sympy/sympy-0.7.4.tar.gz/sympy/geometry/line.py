"""Line-like geometrical entities.

Contains
========
LinearEntity
Line
Ray
Segment

"""
from __future__ import print_function, division

from sympy.core import S, C, sympify, Dummy
from sympy.functions.elementary.trigonometric import _pi_coeff as pi_coeff
from sympy.core.logic import fuzzy_and
from sympy.simplify.simplify import simplify
from sympy.solvers import solve
from sympy.geometry.exceptions import GeometryError
from .entity import GeometryEntity
from .point import Point
from .util import _symbol

# TODO: this should be placed elsewhere and reused in other modules


class Undecidable(ValueError):
    pass


class LinearEntity(GeometryEntity):
    """An abstract base class for all linear entities (line, ray and segment)
    in a 2-dimensional Euclidean space.

    Attributes
    ==========

    p1
    p2
    coefficients
    slope
    points

    Notes
    =====

    This is an abstract class and is not meant to be instantiated.
    Subclasses should implement the following methods:

        * __eq__
        * contains

    See Also
    ========

    sympy.geometry.entity.GeometryEntity

    """

    def __new__(cls, p1, p2, **kwargs):
        p1 = Point(p1)
        p2 = Point(p2)
        if p1 == p2:
            # Rolygon returns lower priority classes...should LinearEntity, too?
            return p1  # raise ValueError("%s.__new__ requires two unique Points." % cls.__name__)

        return GeometryEntity.__new__(cls, p1, p2, **kwargs)

    @property
    def p1(self):
        """The first defining point of a linear entity.

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(5, 3)
        >>> l = Line(p1, p2)
        >>> l.p1
        Point(0, 0)

        """
        return self.args[0]

    @property
    def p2(self):
        """The second defining point of a linear entity.

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(5, 3)
        >>> l = Line(p1, p2)
        >>> l.p2
        Point(5, 3)

        """
        return self.args[1]

    @property
    def coefficients(self):
        """The coefficients (`a`, `b`, `c`) for the linear equation `ax + by + c = 0`.

        See Also
        ========

        sympy.geometry.line.Line.equation

        Examples
        ========

        >>> from sympy import Point, Line
        >>> from sympy.abc import x, y
        >>> p1, p2 = Point(0, 0), Point(5, 3)
        >>> l = Line(p1, p2)
        >>> l.coefficients
        (-3, 5, 0)

        >>> p3 = Point(x, y)
        >>> l2 = Line(p1, p3)
        >>> l2.coefficients
        (-y, x, 0)

        """
        p1, p2 = self.points
        if p1.x == p2.x:
            return (S.One, S.Zero, -p1.x)
        elif p1.y == p2.y:
            return (S.Zero, S.One, -p1.y)
        return tuple([simplify(i) for i in
               (self.p1.y - self.p2.y,
                self.p2.x - self.p1.x,
                self.p1.x*self.p2.y - self.p1.y*self.p2.x)])

    def is_concurrent(*lines):
        """Is a sequence of linear entities concurrent?

        Two or more linear entities are concurrent if they all
        intersect at a single point.

        Parameters
        ==========

        lines : a sequence of linear entities.

        Returns
        =======

        True : if the set of linear entities are concurrent,
        False : otherwise.

        Notes
        =====

        Simply take the first two lines and find their intersection.
        If there is no intersection, then the first two lines were
        parallel and had no intersection so concurrency is impossible
        amongst the whole set. Otherwise, check to see if the
        intersection point of the first two lines is a member on
        the rest of the lines. If so, the lines are concurrent.

        See Also
        ========

        sympy.geometry.util.intersection

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(3, 5)
        >>> p3, p4 = Point(-2, -2), Point(0, 2)
        >>> l1, l2, l3 = Line(p1, p2), Line(p1, p3), Line(p1, p4)
        >>> l1.is_concurrent(l2, l3)
        True

        >>> l4 = Line(p2, p3)
        >>> l4.is_concurrent(l2, l3)
        False

        """

        # Concurrency requires intersection at a single point; One linear
        # entity cannot be concurrent.
        if len(lines) <= 1:
            return False

        try:
            # Get the intersection (if parallel)
            p = lines[0].intersection(lines[1])
            if len(p) == 0:
                return False

            # Make sure the intersection is on every linear entity
            for line in lines[2:]:
                if p[0] not in line:
                    return False
            return True
        except AttributeError:
            return False

    def is_parallel(l1, l2):
        """Are two linear entities parallel?

        Parameters
        ==========

        l1 : LinearEntity
        l2 : LinearEntity

        Returns
        =======

        True : if l1 and l2 are parallel,
        False : otherwise.

        See Also
        ========

        coefficients

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(1, 1)
        >>> p3, p4 = Point(3, 4), Point(6, 7)
        >>> l1, l2 = Line(p1, p2), Line(p3, p4)
        >>> Line.is_parallel(l1, l2)
        True

        >>> p5 = Point(6, 6)
        >>> l3 = Line(p3, p5)
        >>> Line.is_parallel(l1, l3)
        False

        """
        try:
            a1, b1, c1 = l1.coefficients
            a2, b2, c2 = l2.coefficients
            return bool(simplify(a1*b2 - b1*a2) == 0)
        except AttributeError:
            return False

    def is_perpendicular(l1, l2):
        """Are two linear entities perpendicular?

        Parameters
        ==========

        l1 : LinearEntity
        l2 : LinearEntity

        Returns
        =======

        True : if l1 and l2 are perpendicular,
        False : otherwise.

        See Also
        ========

        coefficients

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2, p3 = Point(0, 0), Point(1, 1), Point(-1, 1)
        >>> l1, l2 = Line(p1, p2), Line(p1, p3)
        >>> l1.is_perpendicular(l2)
        True

        >>> p4 = Point(5, 3)
        >>> l3 = Line(p1, p4)
        >>> l1.is_perpendicular(l3)
        False

        """
        try:
            a1, b1, c1 = l1.coefficients
            a2, b2, c2 = l2.coefficients
            return bool(simplify(a1*a2 + b1*b2) == 0)
        except AttributeError:
            return False

    def angle_between(l1, l2):
        """The angle formed between the two linear entities.

        Parameters
        ==========

        l1 : LinearEntity
        l2 : LinearEntity

        Returns
        =======

        angle : angle in radians

        Notes
        =====

        From the dot product of vectors v1 and v2 it is known that:

            ``dot(v1, v2) = |v1|*|v2|*cos(A)``

        where A is the angle formed between the two vectors. We can
        get the directional vectors of the two lines and readily
        find the angle between the two using the above formula.

        See Also
        ========

        is_perpendicular

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2, p3 = Point(0, 0), Point(0, 4), Point(2, 0)
        >>> l1, l2 = Line(p1, p2), Line(p1, p3)
        >>> l1.angle_between(l2)
        pi/2

        """
        v1 = l1.p2 - l1.p1
        v2 = l2.p2 - l2.p1
        return C.acos(v1.dot(v2)/(abs(v1)*abs(v2)))

    def parallel_line(self, p):
        """Create a new Line parallel to this linear entity which passes
        through the point `p`.

        Parameters
        ==========

        p : Point

        Returns
        =======

        line : Line

        See Also
        ========

        is_parallel

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2, p3 = Point(0, 0), Point(2, 3), Point(-2, 2)
        >>> l1 = Line(p1, p2)
        >>> l2 = l1.parallel_line(p3)
        >>> p3 in l2
        True
        >>> l1.is_parallel(l2)
        True

        """
        d = self.p1 - self.p2
        return Line(p, p + d)

    def perpendicular_line(self, p):
        """Create a new Line perpendicular to this linear entity which passes
        through the point `p`.

        Parameters
        ==========

        p : Point

        Returns
        =======

        line : Line

        See Also
        ========

        is_perpendicular, perpendicular_segment

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2, p3 = Point(0, 0), Point(2, 3), Point(-2, 2)
        >>> l1 = Line(p1, p2)
        >>> l2 = l1.perpendicular_line(p3)
        >>> p3 in l2
        True
        >>> l1.is_perpendicular(l2)
        True

        """
        d1, d2 = (self.p1 - self.p2).args
        if d2 == 0:  # If a horizontal line
            if p.y == self.p1.y:  # if p is on this linear entity
                return Line(p, p + Point(0, 1))
            else:
                p2 = Point(p.x, self.p1.y)
                return Line(p, p2)
        else:
            p2 = Point(p.x - d2, p.y + d1)
            return Line(p, p2)

    def perpendicular_segment(self, p):
        """Create a perpendicular line segment from `p` to this line.

        The enpoints of the segment are ``p`` and the closest point in
        the line containing self. (If self is not a line, the point might
        not be in self.)

        Parameters
        ==========

        p : Point

        Returns
        =======

        segment : Segment

        Notes
        =====

        Returns `p` itself if `p` is on this linear entity.

        See Also
        ========

        perpendicular_line

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2, p3 = Point(0, 0), Point(1, 1), Point(0, 2)
        >>> l1 = Line(p1, p2)
        >>> s1 = l1.perpendicular_segment(p3)
        >>> l1.is_perpendicular(s1)
        True
        >>> p3 in s1
        True
        >>> l1.perpendicular_segment(Point(4, 0))
        Segment(Point(2, 2), Point(4, 0))

        """
        if p in self:
            return p
        pl = self.perpendicular_line(p)
        p2 = Line(self).intersection(pl)[0]
        return Segment(p, p2)

    @property
    def length(self):
        """
        The length of the line.

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(3, 5)
        >>> l1 = Line(p1, p2)
        >>> l1.length
        oo
        """
        return S.Infinity

    @property
    def slope(self):
        """The slope of this linear entity, or infinity if vertical.

        Returns
        =======

        slope : number or sympy expression

        See Also
        ========

        coefficients

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(3, 5)
        >>> l1 = Line(p1, p2)
        >>> l1.slope
        5/3

        >>> p3 = Point(0, 4)
        >>> l2 = Line(p1, p3)
        >>> l2.slope
        oo

        """
        d1, d2 = (self.p1 - self.p2).args
        if d1 == 0:
            return S.Infinity
        return simplify(d2/d1)

    @property
    def points(self):
        """The two points used to define this linear entity.

        Returns
        =======

        points : tuple of Points

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(5, 11)
        >>> l1 = Line(p1, p2)
        >>> l1.points
        (Point(0, 0), Point(5, 11))

        """
        return (self.p1, self.p2)

    def projection(self, o):
        """Project a point, line, ray, or segment onto this linear entity.

        Parameters
        ==========

        other : Point or LinearEntity (Line, Ray, Segment)

        Returns
        =======

        projection : Point or LinearEntity (Line, Ray, Segment)
            The return type matches the type of the parameter ``other``.

        Raises
        ======

        GeometryError
            When method is unable to perform projection.

        Notes
        =====

        A projection involves taking the two points that define
        the linear entity and projecting those points onto a
        Line and then reforming the linear entity using these
        projections.
        A point P is projected onto a line L by finding the point
        on L that is closest to P. This is done by creating a
        perpendicular line through P and L and finding its
        intersection with L.

        See Also
        ========

        sympy.geometry.point.Point, perpendicular_line

        Examples
        ========

        >>> from sympy import Point, Line, Segment, Rational
        >>> p1, p2, p3 = Point(0, 0), Point(1, 1), Point(Rational(1, 2), 0)
        >>> l1 = Line(p1, p2)
        >>> l1.projection(p3)
        Point(1/4, 1/4)

        >>> p4, p5 = Point(10, 0), Point(12, 1)
        >>> s1 = Segment(p4, p5)
        >>> l1.projection(s1)
        Segment(Point(5, 5), Point(13/2, 13/2))

        """
        tline = Line(self.p1, self.p2)

        def _project(p):
            """Project a point onto the line representing self."""
            if p in tline:
                return p
            l1 = tline.perpendicular_line(p)
            return tline.intersection(l1)[0]

        projected = None
        if isinstance(o, Point):
            return _project(o)
        elif isinstance(o, LinearEntity):
            n_p1 = _project(o.p1)
            n_p2 = _project(o.p2)
            if n_p1 == n_p2:
                projected = n_p1
            else:
                projected = o.__class__(n_p1, n_p2)

        # Didn't know how to project so raise an error
        if projected is None:
            n1 = self.__class__.__name__
            n2 = o.__class__.__name__
            raise GeometryError(
                "Do not know how to project %s onto %s" % (n2, n1))

        return self.intersection(projected)[0]

    def intersection(self, o):
        """The intersection with another geometrical entity.

        Parameters
        ==========

        o : Point or LinearEntity

        Returns
        =======

        intersection : list of geometrical entities

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Line, Segment
        >>> p1, p2, p3 = Point(0, 0), Point(1, 1), Point(7, 7)
        >>> l1 = Line(p1, p2)
        >>> l1.intersection(p3)
        [Point(7, 7)]

        >>> p4, p5 = Point(5, 0), Point(0, 3)
        >>> l2 = Line(p4, p5)
        >>> l1.intersection(l2)
        [Point(15/8, 15/8)]

        >>> p6, p7 = Point(0, 5), Point(2, 6)
        >>> s1 = Segment(p6, p7)
        >>> l1.intersection(s1)
        []

        """
        if isinstance(o, Point):
            if o in self:
                return [o]
            else:
                return []
        elif isinstance(o, LinearEntity):
            a1, b1, c1 = self.coefficients
            a2, b2, c2 = o.coefficients
            t = simplify(a1*b2 - a2*b1)
            if t.equals(0) is not False:  # assume they are parallel
                if isinstance(self, Line):
                    if o.p1 in self:
                        return [o]
                    return []
                elif isinstance(o, Line):
                    if self.p1 in o:
                        return [self]
                    return []
                elif isinstance(self, Ray):
                    if isinstance(o, Ray):
                        # case 1, rays in the same direction
                        if self.xdirection == o.xdirection:
                            if self.source.x < o.source.x:
                                return [o]
                            return [self]
                        # case 2, rays in the opposite directions
                        else:
                            if o.source in self:
                                if self.source == o.source:
                                    return [self.source]
                                return [Segment(o.source, self.source)]
                            return []
                    elif isinstance(o, Segment):
                        if o.p1 in self:
                            if o.p2 in self:
                                return [o]
                            return [Segment(o.p1, self.source)]
                        elif o.p2 in self:
                            return [Segment(o.p2, self.source)]
                        return []
                elif isinstance(self, Segment):
                    if isinstance(o, Ray):
                        return o.intersection(self)
                    elif isinstance(o, Segment):
                        # A reminder that the points of Segments are ordered
                        # in such a way that the following works. See
                        # Segment.__new__ for details on the ordering.
                        if self.p1 not in o:
                            if self.p2 not in o:
                                # Neither of the endpoints are in o so either
                                # o is contained in this segment or it isn't
                                if o in self:
                                    return [self]
                                return []
                            else:
                                # p1 not in o but p2 is. Either there is a
                                # segment as an intersection, or they only
                                # intersect at an endpoint
                                if self.p2 == o.p1:
                                    return [o.p1]
                                return [Segment(o.p1, self.p2)]
                        elif self.p2 not in o:
                            # p2 not in o but p1 is. Either there is a
                            # segment as an intersection, or they only
                            # intersect at an endpoint
                            if self.p1 == o.p2:
                                return [o.p2]
                            return [Segment(o.p2, self.p1)]

                        # Both points of self in o so the whole segment
                        # is in o
                        return [self]

                # Unknown linear entity
                return []

            # Not parallel, so find the point of intersection
            px = simplify((b1*c2 - c1*b2) / t)
            py = simplify((a2*c1 - a1*c2) / t)
            inter = Point(px, py)
            # we do not use a simplistic 'inter in self and inter in o'
            # because that requires an equality test that is fragile;
            # instead we employ some diagnostics to see if the intersection
            # is valid

            def inseg(self):
                def _between(a, b, c):
                    return c >= a and c <= b or c <= a and c >= b
                if _between(self.p1.x, self.p2.x, inter.x) and \
                        _between(self.p1.y, self.p2.y, inter.y):
                    return True

            def inray(self):
                sray = Ray(self.p1, inter)
                if sray.xdirection == self.xdirection and \
                        sray.ydirection == self.ydirection:
                    return True
            for i in range(2):
                if isinstance(self, Line):
                    if isinstance(o, Line):
                        return [inter]
                    elif isinstance(o, Ray) and inray(o):
                        return [inter]
                    elif isinstance(o, Segment) and inseg(o):
                        return [inter]
                elif isinstance(self, Ray) and inray(self):
                    if isinstance(o, Ray) and inray(o):
                        return [inter]
                    elif isinstance(o, Segment) and inseg(o):
                        return [inter]
                elif isinstance(self, Segment) and inseg(self):
                    if isinstance(o, Segment) and inseg(o):
                        return [inter]
                self, o = o, self
            return []

        return o.intersection(self)

    def arbitrary_point(self, parameter='t'):
        """A parameterized point on the Line.

        Parameters
        ==========

        parameter : str, optional
            The name of the parameter which will be used for the parametric
            point. The default value is 't'. When this parameter is 0, the
            first point used to define the line will be returned, and when
            it is 1 the second point will be returned.

        Returns
        =======

        point : Point

        Raises
        ======

        ValueError
            When ``parameter`` already appears in the Line's definition.

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(1, 0), Point(5, 3)
        >>> l1 = Line(p1, p2)
        >>> l1.arbitrary_point()
        Point(4*t + 1, 3*t)

        """
        t = _symbol(parameter)
        if t.name in (f.name for f in self.free_symbols):
            raise ValueError('Symbol %s already appears in object '
            'and cannot be used as a parameter.' % t.name)
        x = simplify(self.p1.x + t*(self.p2.x - self.p1.x))
        y = simplify(self.p1.y + t*(self.p2.y - self.p1.y))
        return Point(x, y)

    def random_point(self):
        """A random point on a LinearEntity.

        Returns
        =======

        point : Point

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(5, 3)
        >>> l1 = Line(p1, p2)
        >>> p3 = l1.random_point()
        >>> # random point - don't know its coords in advance
        >>> p3 # doctest: +ELLIPSIS
        Point(...)
        >>> # point should belong to the line
        >>> p3 in l1
        True

        """
        from random import randint

        # The lower and upper
        lower, upper = -2**32 - 1, 2**32

        if self.slope is S.Infinity:
            if isinstance(self, Ray):
                if self.ydirection is S.Infinity:
                    lower = self.p1.y
                else:
                    upper = self.p1.y
            elif isinstance(self, Segment):
                lower = self.p1.y
                upper = self.p2.y

            x = self.p1.x
            y = randint(lower, upper)
        else:
            if isinstance(self, Ray):
                if self.xdirection is S.Infinity:
                    lower = self.p1.x
                else:
                    upper = self.p1.x
            elif isinstance(self, Segment):
                lower = self.p1.x
                upper = self.p2.x

            a, b, c = self.coefficients
            x = randint(lower, upper)
            y = (-c - a*x) / b
        return Point(x, y)

    def is_similar(self, other):
        """
        Return True if self and other are contained in the same line.

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2, p3 = Point(0, 1), Point(3, 4), Point(2, 3)
        >>> l1 = Line(p1, p2)
        >>> l2 = Line(p1, p3)
        >>> l1.is_similar(l2)
        True
        """
        def _norm(a, b, c):
            if a != 0:
                return 1, b/a, c/a
            elif b != 0:
                return a/b, 1, c/b
            else:
                return c
        return _norm(*self.coefficients) == _norm(*other.coefficients)

    def __contains__(self, other):
        """Return a definitive answer or else raise an error if it cannot
        be determined that other is on the boundaries of self."""
        result = self.contains(other)

        if result is not None:
            return result
        else:
            raise Undecidable(
                "can't decide whether '%s' contains '%s'" % (self, other))

    def contains(self, other):
        """Subclasses should implement this method and should return
            True if other is on the boundaries of self;
            False if not on the boundaries of self;
            None if a determination cannot be made."""
        raise NotImplementedError()

    def __eq__(self, other):
        """Subclasses should implement this method."""
        raise NotImplementedError()

    def __hash__(self):
        return super(LinearEntity, self).__hash__()


class Line(LinearEntity):
    """An infinite line in space.

    A line is declared with two distinct points or a point and slope
    as defined using keyword `slope`.

    Notes
    =====

    At the moment only lines in a 2D space can be declared, because
    Points can be defined only for 2D spaces.

    Parameters
    ==========

    p1 : Point
    pt : Point
    slope : sympy expression

    See Also
    ========

    sympy.geometry.point.Point

    Examples
    ========

    >>> import sympy
    >>> from sympy import Point
    >>> from sympy.abc import L
    >>> from sympy.geometry import Line, Segment
    >>> L = Line(Point(2,3), Point(3,5))
    >>> L
    Line(Point(2, 3), Point(3, 5))
    >>> L.points
    (Point(2, 3), Point(3, 5))
    >>> L.equation()
    -2*x + y + 1
    >>> L.coefficients
    (-2, 1, 1)

    Instantiate with keyword ``slope``:

    >>> Line(Point(0, 0), slope=0)
    Line(Point(0, 0), Point(1, 0))

    Instantiate with another linear object

    >>> s = Segment((0, 0), (0, 1))
    >>> Line(s).equation()
    x
    """

    def __new__(cls, p1, pt=None, slope=None, **kwargs):
        if isinstance(p1, LinearEntity):
            p1, pt = p1.args
        else:
            p1 = Point(p1)
        if pt is not None and slope is None:
            try:
                p2 = Point(pt)
            except NotImplementedError:
                raise ValueError('The 2nd argument was not a valid Point. '
                'If it was a slope, enter it with keyword "slope".')
            if p1 == p2:
                raise ValueError('A line requires two distinct points.')
        elif slope is not None and pt is None:
            slope = sympify(slope)
            if slope.is_bounded is False:
                # when unbounded slope, don't change x
                p2 = p1 + Point(0, 1)
            else:
                # go over 1 up slope
                p2 = p1 + Point(1, slope)
        else:
            raise ValueError('A 2nd Point or keyword "slope" must be used.')

        return LinearEntity.__new__(cls, p1, p2, **kwargs)

    def plot_interval(self, parameter='t'):
        """The plot interval for the default geometric plot of line. Gives
        values that will produce a line that is +/- 5 units long (where a
        unit is the distance between the two points that define the line).

        Parameters
        ==========

        parameter : str, optional
            Default value is 't'.

        Returns
        =======

        plot_interval : list (plot interval)
            [parameter, lower_bound, upper_bound]

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(5, 3)
        >>> l1 = Line(p1, p2)
        >>> l1.plot_interval()
        [t, -5, 5]

        """
        t = _symbol(parameter)
        return [t, -5, 5]

    def equation(self, x='x', y='y'):
        """The equation of the line: ax + by + c.

        Parameters
        ==========

        x : str, optional
            The name to use for the x-axis, default value is 'x'.
        y : str, optional
            The name to use for the y-axis, default value is 'y'.

        Returns
        =======

        equation : sympy expression

        See Also
        ========

        LinearEntity.coefficients

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(1, 0), Point(5, 3)
        >>> l1 = Line(p1, p2)
        >>> l1.equation()
        -3*x + 4*y + 3

        """
        x, y = _symbol(x), _symbol(y)
        p1, p2 = self.points
        if p1.x == p2.x:
            return x - p1.x
        elif p1.y == p2.y:
            return y - p1.y

        a, b, c = self.coefficients
        return simplify(a*x + b*y + c)

    def contains(self, o):
        """Return True if o is on this Line, or False otherwise."""
        if isinstance(o, Point):
            x, y = Dummy(), Dummy()
            eq = self.equation(x, y)
            if not eq.has(y):
                return (solve(eq, x)[0] - o.x).equals(0)
            if not eq.has(x):
                return (solve(eq, y)[0] - o.y).equals(0)
            return (solve(eq.subs(x, o.x), y)[0] - o.y).equals(0)
        elif not isinstance(o, LinearEntity):
            return False
        elif isinstance(o, Line):
            return self.__eq__(o)
        elif not self.is_similar(o):
            return False
        else:
            return o.p1 in self and o.p2 in self

    def __eq__(self, other):
        """Return True if other is equal to this Line, or False otherwise."""
        if not isinstance(other, Line):
            return False
        return Point.is_collinear(self.p1, self.p2, other.p1, other.p2)

    def __hash__(self):
        return super(Line, self).__hash__()


class Ray(LinearEntity):
    """
    A Ray is a semi-line in the space with a source point and a direction.

    Parameters
    ==========

    p1 : Point
        The source of the Ray
    p2 : Point or radian value
        This point determines the direction in which the Ray propagates.
        If given as an angle it is interpreted in radians with the positive
        direction being ccw.

    Attributes
    ==========

    source
    xdirection
    ydirection

    See Also
    ========

    sympy.geometry.point.Point, Line

    Notes
    =====

    At the moment only rays in a 2D space can be declared, because
    Points can be defined only for 2D spaces.

    Examples
    ========

    >>> import sympy
    >>> from sympy import Point, pi
    >>> from sympy.abc import r
    >>> from sympy.geometry import Ray
    >>> r = Ray(Point(2, 3), Point(3, 5))
    >>> r = Ray(Point(2, 3), Point(3, 5))
    >>> r
    Ray(Point(2, 3), Point(3, 5))
    >>> r.points
    (Point(2, 3), Point(3, 5))
    >>> r.source
    Point(2, 3)
    >>> r.xdirection
    oo
    >>> r.ydirection
    oo
    >>> r.slope
    2
    >>> Ray(Point(0, 0), angle=pi/4).slope
    1

    """

    def __new__(cls, p1, pt=None, angle=None, **kwargs):
        p1 = Point(p1)
        if pt is not None and angle is None:
            try:
                p2 = Point(pt)
            except NotImplementedError:
                raise ValueError(
                    'The 2nd argument was not a valid Point;\nif '
                    'it was meant to be an angle it should be '
                    'given with keyword "angle".')
            if p1 == p2:
                raise ValueError('A Ray requires two distinct points.')
        elif angle is not None and pt is None:
            # we need to know if the angle is an odd multiple of pi/2
            c = pi_coeff(sympify(angle))
            p2 = None
            if c is not None:
                if c.is_Rational:
                    if c.q == 2:
                        if c.p == 1:
                            p2 = p1 + Point(0, 1)
                        elif c.p == 3:
                            p2 = p1 + Point(0, -1)
                    elif c.q == 1:
                        if c.p == 0:
                            p2 = p1 + Point(1, 0)
                        elif c.p == 1:
                            p2 = p1 + Point(-1, 0)
                if p2 is None:
                    c *= S.Pi
            else:
                c = angle
            if not p2:
                p2 = p1 + Point(1, C.tan(c))
        else:
            raise ValueError('A 2nd point or keyword "angle" must be used.')

        return LinearEntity.__new__(cls, p1, p2, **kwargs)

    @property
    def source(self):
        """The point from which the ray emanates.

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Ray
        >>> p1, p2 = Point(0, 0), Point(4, 1)
        >>> r1 = Ray(p1, p2)
        >>> r1.source
        Point(0, 0)

        """
        return self.p1

    @property
    def xdirection(self):
        """The x direction of the ray.

        Positive infinity if the ray points in the positive x direction,
        negative infinity if the ray points in the negative x direction,
        or 0 if the ray is vertical.

        See Also
        ========

        ydirection

        Examples
        ========

        >>> from sympy import Point, Ray
        >>> p1, p2, p3 = Point(0, 0), Point(1, 1), Point(0, -1)
        >>> r1, r2 = Ray(p1, p2), Ray(p1, p3)
        >>> r1.xdirection
        oo
        >>> r2.xdirection
        0

        """
        if self.p1.x < self.p2.x:
            return S.Infinity
        elif self.p1.x == self.p2.x:
            return S.Zero
        else:
            return S.NegativeInfinity

    @property
    def ydirection(self):
        """The y direction of the ray.

        Positive infinity if the ray points in the positive y direction,
        negative infinity if the ray points in the negative y direction,
        or 0 if the ray is horizontal.

        See Also
        ========

        xdirection

        Examples
        ========

        >>> from sympy import Point, Ray
        >>> p1, p2, p3 = Point(0, 0), Point(-1, -1), Point(-1, 0)
        >>> r1, r2 = Ray(p1, p2), Ray(p1, p3)
        >>> r1.ydirection
        -oo
        >>> r2.ydirection
        0

        """
        if self.p1.y < self.p2.y:
            return S.Infinity
        elif self.p1.y == self.p2.y:
            return S.Zero
        else:
            return S.NegativeInfinity

    def plot_interval(self, parameter='t'):
        """The plot interval for the default geometric plot of the Ray. Gives
        values that will produce a ray that is 10 units long (where a unit is
        the distance between the two points that define the ray).

        Parameters
        ==========

        parameter : str, optional
            Default value is 't'.

        Returns
        =======

        plot_interval : list
            [parameter, lower_bound, upper_bound]

        Examples
        ========

        >>> from sympy import Point, Ray, pi
        >>> r = Ray((0, 0), angle=pi/4)
        >>> r.plot_interval()
        [t, 0, 10]

        """
        t = _symbol(parameter)
        return [t, 0, 10]

    def __eq__(self, other):
        """Is the other GeometryEntity equal to this Ray?"""
        if not isinstance(other, Ray):
            return False
        return (self.source == other.source) and (other.p2 in self)

    def __hash__(self):
        return super(Ray, self).__hash__()

    def contains(self, o):
        """Is other GeometryEntity contained in this Ray?"""
        if isinstance(o, Ray):
            return (Point.is_collinear(self.p1, self.p2, o.p1, o.p2) and
                    self.xdirection == o.xdirection and
                    self.ydirection == o.ydirection)
        elif isinstance(o, Segment):
            return o.p1 in self and o.p2 in self
        elif isinstance(o, Point):
            if Point.is_collinear(self.p1, self.p2, o):
                if self.xdirection is S.Infinity:
                    rv = o.x >= self.source.x
                elif self.xdirection is S.NegativeInfinity:
                    rv = o.x <= self.source.x
                elif self.ydirection is S.Infinity:
                    rv = o.y >= self.source.y
                else:
                    rv = o.y <= self.source.y
                if isinstance(rv, bool):
                    return rv
                raise Undecidable(
                    'Cannot determine if %s is in %s' % (o, self))
            else:
                # Points are not collinear, so the rays are not parallel
                # and hence it is impossible for self to contain o
                return False

        # No other known entity can be contained in a Ray
        return False


class Segment(LinearEntity):
    """An undirected line segment in space.

    Parameters
    ==========

    p1 : Point
    p2 : Point

    Attributes
    ==========

    length : number or sympy expression
    midpoint : Point

    See Also
    ========

    sympy.geometry.point.Point, Line

    Notes
    =====

    At the moment only segments in a 2D space can be declared, because
    Points can be defined only for 2D spaces.

    Examples
    ========

    >>> import sympy
    >>> from sympy import Point
    >>> from sympy.abc import s
    >>> from sympy.geometry import Segment
    >>> Segment((1, 0), (1, 1)) # tuples are interpreted as pts
    Segment(Point(1, 0), Point(1, 1))
    >>> s = Segment(Point(4, 3), Point(1, 1))
    >>> s
    Segment(Point(1, 1), Point(4, 3))
    >>> s.points
    (Point(1, 1), Point(4, 3))
    >>> s.slope
    2/3
    >>> s.length
    sqrt(13)
    >>> s.midpoint
    Point(5/2, 2)

    """

    def __new__(cls, p1, p2, **kwargs):
        # Reorder the two points under the following ordering:
        #   if p1.x != p2.x then p1.x < p2.x
        #   if p1.x == p2.x then p1.y < p2.y
        p1 = Point(p1)
        p2 = Point(p2)
        if p1 == p2:
            return Point(p1)
        if (p1.x > p2.x) is True:
            p1, p2 = p2, p1
        elif (p1.x == p2.x) is (p1.y > p2.y) is True:
            p1, p2 = p2, p1
        return LinearEntity.__new__(cls, p1, p2, **kwargs)

    def plot_interval(self, parameter='t'):
        """The plot interval for the default geometric plot of the Segment. Gives
        values that will produce the full segment in a plot.

        Parameters
        ==========

        parameter : str, optional
            Default value is 't'.

        Returns
        =======

        plot_interval : list
            [parameter, lower_bound, upper_bound]

        Examples
        ========

        >>> from sympy import Point, Segment
        >>> p1, p2 = Point(0, 0), Point(5, 3)
        >>> s1 = Segment(p1, p2)
        >>> s1.plot_interval()
        [t, 0, 1]

        """
        t = _symbol(parameter)
        return [t, 0, 1]

    def perpendicular_bisector(self, p=None):
        """The perpendicular bisector of this segment.

        If no point is specified or the point specified is not on the
        bisector then the bisector is returned as a Line. Otherwise a
        Segment is returned that joins the point specified and the
        intersection of the bisector and the segment.

        Parameters
        ==========

        p : Point

        Returns
        =======

        bisector : Line or Segment

        See Also
        ========

        LinearEntity.perpendicular_segment

        Examples
        ========

        >>> from sympy import Point, Segment
        >>> p1, p2, p3 = Point(0, 0), Point(6, 6), Point(5, 1)
        >>> s1 = Segment(p1, p2)
        >>> s1.perpendicular_bisector()
        Line(Point(3, 3), Point(9, -3))

        >>> s1.perpendicular_bisector(p3)
        Segment(Point(3, 3), Point(5, 1))

        """
        l = LinearEntity.perpendicular_line(self, self.midpoint)
        if p is None or p not in l:
            return l
        else:
            return Segment(self.midpoint, p)

    @property
    def length(self):
        """The length of the line segment.

        See Also
        ========

        sympy.geometry.point.Point.distance

        Examples
        ========

        >>> from sympy import Point, Segment
        >>> p1, p2 = Point(0, 0), Point(4, 3)
        >>> s1 = Segment(p1, p2)
        >>> s1.length
        5

        """
        return Point.distance(self.p1, self.p2)

    @property
    def midpoint(self):
        """The midpoint of the line segment.

        See Also
        ========

        sympy.geometry.point.Point.midpoint

        Examples
        ========

        >>> from sympy import Point, Segment
        >>> p1, p2 = Point(0, 0), Point(4, 3)
        >>> s1 = Segment(p1, p2)
        >>> s1.midpoint
        Point(2, 3/2)

        """
        return Point.midpoint(self.p1, self.p2)

    def distance(self, o):
        """
        Finds the shortest distance between a line segment and a point.

        Raises
        ======

        NotImplementedError is raised if o is not a Point

        Examples
        ========

        >>> from sympy import Point, Segment
        >>> p1, p2 = Point(0, 1), Point(3, 4)
        >>> s = Segment(p1, p2)
        >>> s.distance(Point(10, 15))
        sqrt(170)
        """
        if isinstance(o, Point):
            return self._do_point_distance(o)
        raise NotImplementedError()

    def _do_point_distance(self, pt):
        """Calculates the distance between a point and a line segment."""

        seg_vector = self.p2 - self.p1
        pt_vector = pt - self.p1
        t = seg_vector.dot(pt_vector)/self.length**2
        if t >= 1:
            distance = Point.distance(self.p2, pt)
        elif t <= 0:
            distance = Point.distance(self.p1, pt)
        else:
            distance = Point.distance(
                self.p1 + Point(t*seg_vector.x, t*seg_vector.y), pt)
        return distance

    def __eq__(self, other):
        """Is the other GeometryEntity equal to this Ray?"""
        if not isinstance(other, Segment):
            return False
        return (self.p1 == other.p1) and (self.p2 == other.p2)

    def __hash__(self):
        return super(Segment, self).__hash__()

    def contains(self, other):
        """
        Is the other GeometryEntity contained within this Segment?

        Examples
        ========

        >>> from sympy import Point, Segment
        >>> p1, p2 = Point(0, 1), Point(3, 4)
        >>> s = Segment(p1, p2)
        >>> s2 = Segment(p2, p1)
        >>> s.contains(s2)
        True
        """
        if isinstance(other, Segment):
            return other.p1 in self and other.p2 in self
        elif isinstance(other, Point):
            if Point.is_collinear(self.p1, self.p2, other):
                t = Dummy('t')
                x, y = self.arbitrary_point(t).args
                if self.p1.x != self.p2.x:
                    ti = solve(x - other.x, t)[0]
                else:
                    ti = solve(y - other.y, t)[0]
                if ti.is_number:
                    return 0 <= ti <= 1
                return None

        # No other known entity can be contained in a Ray
        return False
