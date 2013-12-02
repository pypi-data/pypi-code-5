import texttable
import os


class Formatter(object):
    def table(self, headers, rows):
        height, width = os.popen('stty size', 'r').read().split()

        table = texttable.Texttable(max_width=width)
        table.set_cols_dtype(['t' for h in headers])
        table.add_rows([headers] + rows)
        table.set_deco(table.HEADER)
        table.set_chars(['-', '|', '+', '-'])

        return table.draw()
