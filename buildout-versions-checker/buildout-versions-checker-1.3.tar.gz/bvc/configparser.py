"""Config parser for Buildout Versions Checker"""
import re
try:
    from ConfigParser import RawConfigParser
except ImportError:  # Python 3
    from configparser import RawConfigParser

OPERATORS = re.compile(r'[+-<]$')


class VersionsConfigParser(RawConfigParser):
    """
    ConfigParser customized to read and write
    beautiful buildout files.
    """
    optionxform = str

    def write_section(self, fd, section, indentation):
        """
        Write a section of an .ini-format
        and all the keys within.
        """
        string_section = '[%s]\n' % section
        for key, value in self._sections[section].items():
            if key == '__name__':
                continue
            if value is None:
                value = ''
            operator = ''
            key_indentation = indentation
            buildout_operator = OPERATORS.search(key)
            if buildout_operator:
                operator = buildout_operator.group(0)
                key_indentation -= 1
                key = key[:-1]
            key = key.ljust(key_indentation) + operator
            value = str(value).replace('\n', '\n'.ljust(
                key_indentation + 3 + int(bool(operator))))
            string_section += '%s= %s\n' % (key, value)

        fd.write(string_section.encode('utf-8'))

    def write(self, source, indentation=32):
        """
        Write an .ini-format representation of the
        configuration state with a readable indentation.
        """
        with open(source, 'wb') as fd:
            sections = list(self._sections.keys())
            for section in sections[:-1]:
                self.write_section(fd, section, indentation)
                fd.write('\n'.encode('utf-8'))
            self.write_section(fd, sections[-1], indentation)
