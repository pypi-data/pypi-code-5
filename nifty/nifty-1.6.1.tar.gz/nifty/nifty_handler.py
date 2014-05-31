# -*- coding: utf-8 -*-
"""The core of logic, display and user interactions handling."""
import pprint
import subprocess
import sys
import time
import yaml

import common
from input_prompt import InputPrompt
from recursive_transformer import RecursiveTransformer
import utils
from validators import NiftyHandlerInputValidator
from validators import PositiveIntegerValidator


class TargetsNotFoundError(Exception):
  """Raised when no target(s) are found during one step."""
  pass


class NiftyHandler(object):
  """Responsible for handling the logic, display
  and user interactions of the application.
  """

  def __init__(
    self,
    config_obj,
    config_path,
    options
  ):
    self.config_path = config_path
    self.options = options
    self.formatted_config = RecursiveTransformer(
      {
        dict: {
          'value_func': utils.dict_to_indexed_dict,
          'args': [],
          'kwargs': dict(start_index=1)
        },
        list: {
          'value_func': utils.list_to_indexed_compound_dict,
          'args': [],
          'kwargs': dict(start_index=1)
        }
      }
    ).transform(config_obj)
    self.input_prompt = InputPrompt(
      prompt_msg_items=[
        'One or more paths (e.g. \'1.2, 3.4.5\')',
        '\"all\"',
        '\"exit\"'
      ],
      input_output_map={
        'all': common.Inputs.ALL,
        'exit': common.Inputs.EXIT
      },
      validator=NiftyHandlerInputValidator(),
      err_msg='Please enter one or more valid target(s)'
    )

  @classmethod
  def create_from_yaml(cls, config_path, options):
    with open(config_path) as config:
      try:
        config_obj = yaml.load(config.read())
      except yaml.parser.ParserError:
        sys.exit(
          ('The format of "{0}" is invalid.\n'
          'Please refer to the Nifty documentation for the structure of '
          'well-formed config files.').format(config_path)
        )

    return cls(config_obj, config_path, options)

  def _pretty_print_item(self, obj, lvl=0):
    padding = ''.join(['\t' for _ in xrange(lvl)])
    padding += ' '

    for index, key_val_pair in obj.iteritems():
      # For an inner target, display the item at `key` because that's
      # the title of the sub-group.
      # For a leaf target, display the item at `value` because that's
      # the value of the target.
      item = key_val_pair.get('key') or key_val_pair.get('value')
      print "{0}{1}[{2}]{3} {4}".format(
        padding,
        common.TerminalColors.BLUE,
        index,
        common.TerminalColors.CLEAR,
        item
      )
      if isinstance(key_val_pair['value'], dict):
        self._pretty_print_item(key_val_pair['value'], lvl=lvl+1)

  def pretty_print(self):
    self._pretty_print_item(self.formatted_config)

  def list(self):
    assert self.options.list

    targets = []
    targets = utils.grab_deep(self.formatted_config, 'value', targets)

    print 'Listing all the targets:\n'
    print '\t'+ '\n\t'.join(
      [
        '{0}[{1}]{2} {3}'.format(
          common.TerminalColors.BLUE,
          i,
          common.TerminalColors.CLEAR,
          target
        )
        for i, target in enumerate(targets, start=1)
      ]
    )

  def run(self):
    targets = []

    if self.options.all or self.options.list:
      targets = utils.grab_deep(self.formatted_config, 'value', targets)
    else:
      targets = self.step()

    message = 'Going to execute the following {0} item(s) with the command '\
      '{1}{2}{3}{4}:\n'.format(
        len(targets),
        common.TerminalColors.BLUE,
        self.options.command,
        common.TerminalColors.CLEAR,
        ' with the arguments {0}{1}{2}'.format(
          common.TerminalColors.BLUE,
          self.options.arguments,
          common.TerminalColors.CLEAR
        ) if self.options.arguments else ''
      )

    print message
    print '\t'+ '\n\t'.join(
      [
        '{0}[{1}]{2} {3}'.format(
          common.TerminalColors.BLUE,
          i+1,
          common.TerminalColors.CLEAR,
          target
        )
        for i, target in enumerate(targets)
      ]
    )
    print '\n'
    print '{0}{1}{2}\n'.format(
      common.TerminalColors.BLUE,
      '-'.join(['' for _ in xrange(len(message))]),
      common.TerminalColors.CLEAR
    )

    for target in targets:
      subprocess.call('%s %s' % (self.options.command, target), shell=True)
      time.sleep(self.options.interval)

  def step(self):
    targets = []
    self._step(self.formatted_config, targets)
    return targets

  def _step(self, obj, targets):
    while True:
      utils.clear_screen()
      print 'From config file: %s\n' % self.config_path
      self._pretty_print_item(obj)

      try:
        input_val = self.input_prompt.prompt()

        if input_val == common.Inputs.ALL:
          targets = utils.grab_deep(obj, 'value', targets)
          return
        elif input_val == common.Inputs.EXIT:
          sys.exit()

        paths = input_val

        # Single path.
        if len(paths) == 1:
          path = paths[0]
          target = utils.get_deep_with_leap(
            obj,
            path,
            leap='value',
            path_func=int,
            default=''
          )

          # If no valid target found, then re-try.
          if not target:
            raise TargetsNotFoundError()

          # If target is not leaf, then step into the next level.
          # Else, get the value of the target.
          if isinstance(target, dict):
            self._step(target, targets)
          else:
            targets = utils.grab_deep(target, 'value', targets)
        else:
          # Multiple paths found. For each path, get its targets.
          for path in paths:
            target = utils.get_deep_with_leap(
              obj,
              path,
              leap='value',
              path_func=int,
              default=''
            )

            # No valid target found for this path, continue to next one.
            if not target:
              continue

            targets = utils.grab_deep(target, 'value', targets)
        break
      except (TargetsNotFoundError, KeyError):
        pass