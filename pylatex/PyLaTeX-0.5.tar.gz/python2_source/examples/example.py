#!/usr/bin/python

from __future__ import absolute_import
import numpy as np

from pylatex import Document, Section, Subsection, Table, Math, TikZ, Axis, \
    Plot
from pylatex.numpy import Matrix
from pylatex.utils import italic

doc = Document()
section = Section(u'Yaay the first section, it can even be ' + italic(u'italic'))

section.append(u'Some regular text')

math = Subsection(u'Math that is incorrect', data=[Math(data=[u'2*3', u'=', 9])])

section.append(math)
table = Table(u'rc|cl')
table.add_hline()
table.add_row((1, 2, 3, 4))
table.add_hline(1, 2)
table.add_empty_row()
table.add_row((4, 5, 6, 7))

table = Subsection(u'Table of something', data=[table])

section.append(table)

a = np.array([[100, 10, 20]]).T
M = np.matrix([[2, 3, 4],
               [0, 0, 1],
               [0, 0, 2]])

math = Math(data=[Matrix(M), Matrix(a), u'=', Matrix(M*a)])
equation = Subsection(u'Matrix equation', data=[math])

section.append(equation)

tikz = TikZ()

axis = Axis(options=u'height=6cm, width=6cm, grid=major')

plot1 = Plot(name=u'model', func=u'-x^5 - 242')
coordinates = [
    (-4.77778, 2027.60977),
    (-3.55556, 347.84069),
    (-2.33333, 22.58953),
    (-1.11111, -493.50066),
    (0.11111, 46.66082),
    (1.33333, -205.56286),
    (2.55556, -341.40638),
    (3.77778, -1169.24780),
    (5.00000, -3269.56775),
]

plot2 = Plot(name=u'estimate', coordinates=coordinates)

axis.append(plot1)
axis.append(plot2)

tikz.append(axis)

plot_section = Subsection(u'Random graph', data=[tikz])

section.append(plot_section)

doc.append(section)

doc.generate_pdf()
