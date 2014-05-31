# -*- coding: utf-8 -*-
"""Program entry point."""
from optparse import OptionParser
import sys

from nifty_handler import NiftyHandler
from validators import NiftyCmdlineOptionsValidator
import version


def main():
  parser = OptionParser(
    description='A nifty and interactive command-line tool ' \
      'for efficient management and execution of '\
      'commands grouped in hierarchical structures.',
    usage='usage: %prog filename -c COMMAND [options]',
    version='%prog' + ' %s' % version.__VERSION__
  )

  parser.add_option(
    '-c',
    '--command',
    dest='command',
    help='The shell command used for execution'
  )
  parser.add_option(
    '-r',
    '--arguments',
    dest='arguments',
    default=None,
    help='Additional arguments used for execution'
  )
  parser.add_option(
    '-a',
    '--all',
    dest='all',
    action='store_true',
    default=False,
    help='Execute all targets'
  )
  parser.add_option(
    '-l',
    '--list',
    dest='list',
    action='store_true',
    default=False,
    help='Flatten the hierarchy and list all the targets'
  )
  parser.add_option(
    '-i',
    '--interval',
    dest='interval',
    type=int,
    default=0,
    help='Interval in seconds between each execution'
  )

  options, args = parser.parse_args()

  try:
    NiftyCmdlineOptionsValidator().validate((options, args))
  except ValueError as err:
    sys.exit('%s. See \'nifty --help\'' % err.message)

  nifty_handler = NiftyHandler.create_from_yaml(args[0], options)

  if options.list:
    nifty_handler.list()
  else:
    nifty_handler.run()


if __name__ == '__main__':
  main()