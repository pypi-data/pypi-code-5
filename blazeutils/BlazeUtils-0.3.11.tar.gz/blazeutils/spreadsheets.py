from __future__ import absolute_import

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import datetime as dt
from decimal import Decimal

try:
    import xlrd
except ImportError:
    xlrd = None

try:
    import xlwt
except ImportError:
    xlwt = None

from .decorators import deprecate


def _xlrd_required():
    if xlrd is None:
        raise ImportError('xlrd library is required to use this function or class')


def _xlwt_required():
    if xlwt is None:
        raise ImportError('xlwt library is required to use this function or class')


def workbook_to_reader(xlwt_wb):
    """
        convert xlwt Workbook instance to an xlrd instance for reading
    """
    _xlrd_required()
    fh = StringIO()
    xlwt_wb.save(fh)
    # prep for reading
    fh.seek(0)
    return xlrd.open_workbook(file_contents=fh.read())

import xlwt


class Writer(object):
    """
        code from : http://panela.blog-city.com/pyexcelerator_xlwt_cheatsheet_create_native_excel_from_pu.htm
    """

    STYLE_FACTORY = {}
    FONT_FACTORY = {}

    def __init__(self, ws=None):
        _xlwt_required()
        self.ws = ws
        self.rownum = 0
        self.colnum = 0

    def set_sheet(self, ws):
        self.ws = ws
        self.rownum = 0
        self.colnum = 0

    def write(self, row, col, data, style=None):
        """
        Write data to row, col of worksheet (ws) using the style
        information.

        Again, I'm wrapping this because you'll have to do it if you
        create large amounts of formatted entries in your spreadsheet
        (else Excel, but probably not OOo will crash).
        """
        ws = self.ws
        if not ws:
            raise Exception('you must use set_sheet() before write()')

        if style:
            if isinstance(style, xlwt.Style.XFStyle):
                s = style
            else:
                s = self.get_style(style)
            ws.write(row, col, data, s)
        else:
            ws.write(row, col, data)

    def write_merge(self, r1, r2, c1, c2, data, style=None):
        """
        Write data to row, col of worksheet (ws) using the style
        information.

        Again, I'm wrapping this because you'll have to do it if you
        create large amounts of formatted entries in your spreadsheet
        (else Excel, but probably not OOo will crash).
        """
        ws = self.ws
        if not ws:
            raise Exception('you must use set_sheet() before write()')

        if style:
            if isinstance(style, xlwt.Style.XFStyle):
                s = style
            else:
                s = self.get_style(style)
            ws.write_merge(r1, r2, c1, c2, data, s)
        else:
            ws.write_merge(r1, r2, c1, c2, data)

    def mwrite(self, col_vals, style=None, nextrow=False):
        for val in col_vals:
            self.awrite(val, style)
        if nextrow:
            self.newrow()

    def awrite(self, data=None, style=None, nextrow=False):
        """
            Auto Write: Similar to write, except that the row and column
            numbers are handled automatically and based on the extra
            parameters to this method.
        """
        self.write(self.rownum, self.colnum, data, style)
        self.colnum += 1
        if nextrow:
            self.newrow()

    def newrow(self):
        self.rownum +=1
        self.colnum = 0

    def get_style(self, style):
        """
        Style is a dict maping key to values.
        Valid keys are: background, format, alignment, border

        The values for keys are lists of tuples containing (attribute,
        value) pairs to set on model instances...
        """
        #print "KEY", style
        style_key = tuple(style.items())
        s = self.STYLE_FACTORY.get(style_key, None)
        if s is None:
            s = xlwt.XFStyle()
            for key, values in style.items():
                if key == "background":
                    p = xlwt.Pattern()
                    for attr, value in values:
                        p.__setattr__(attr, value)
                    s.pattern = p
                elif key == "format":
                    s.num_format_str = values
                elif key == "alignment":
                    a = xlwt.Alignment()
                    for attr, value in values:
                        a.__setattr__(attr, value)
                    s.alignment = a
                elif key == "border":
                    b = xlwt.Formatting.Borders()
                    for attr, value in values:
                        b.__setattr__(attr, value)
                    s.borders = b
                elif key == "font":
                    f = self.get_font(values)
                    s.font = f
            self.STYLE_FACTORY[style_key] = s
        return s

    def get_font(self, values):
        """
        'height' 10pt = 200, 8pt = 160
        """
        font_key = values
        f = self.FONT_FACTORY.get(font_key, None)
        if f is None:
            f = xlwt.Font()
            for attr, value in values:
                f.__setattr__(attr, value)
            self.FONT_FACTORY[font_key] = f
        return f


@deprecate('XlwtHelper has been renamed to Writer')
def XlwtHelper(ws=None):
    return Writer(ws)


class Reader(object):

    def __init__(self, xlrd_wb, sheetnum=0):
        _xlrd_required()
        self.book = xlrd_wb
        self.sheetnum = sheetnum
        self.rownum = 0
        self.colnum = 0
        self.sheet = self.book.sheet_by_index(self.sheetnum)

    @classmethod
    def from_xlwt(cls, xlwt_wb):
        wb = workbook_to_reader(xlwt_wb)
        return cls(wb)

    def cell_value(self, is_date=False):
        try:
            return self.sheet.cell_value(self.rownum, self.colnum)
        finally:
            self.colnum += 1

    def cell_date(self):
        value = self.cell_value()
        date_tuple = xlrd.xldate_as_tuple(value, self.book.datemode)
        return dt.datetime(*date_tuple).date()

    def cell_datetime(self):
        value = self.cell_value()
        date_tuple = xlrd.xldate_as_tuple(value, self.book.datemode)
        return dt.datetime(*date_tuple)

    def cell_decimal(self):
        value = self.cell_value()
        return Decimal(value)

    def next_row(self):
        self.rownum += 1
        self.colnum = 0

