# -*- coding: utf-8 -*-
import string

import common
import utils


class InputPrompt(object):
  """An object that encapsulates the abstraction of an
  user-defined input prompt.
  """

  def __init__(
    self,
    prompt_msg_items,
    input_output_map,
    value_func=None,
    validator=None,
    err_msg=None
  ):
    self.prompt_msg_core = ' '.join(
      [
        '{0}) {1}'.format(string.letters[i], item)
        for i, item in enumerate(prompt_msg_items)
      ]
    )
    self.input_output_map = input_output_map
    self.value_func = value_func or utils.SELF_LAMBDA
    self.validator = validator
    self.err_msg = err_msg

  def prompt(self):
    while True:
      try:
        print '\n{0}Please enter: {1}{2}'.format(
            common.TerminalColors.WARNING,
            self.prompt_msg_core,
            common.TerminalColors.CLEAR
        )

        raw_val = raw_input(
          '{0}>> {1}'.format(
            common.TerminalColors.GREEN,
            common.TerminalColors.CLEAR
          )
        )
        print '\n'

        if raw_val in self.input_output_map:
          return self.input_output_map[raw_val]

        val = self.value_func(raw_val)

        if self.validator:
          return self.validator.parse_and_validate(val)
      except ValueError:
        if self.err_msg:
          print '{0}{1}{2}'.format(
            common.TerminalColors.FAIL,
            self.err_msg,
            common.TerminalColors.CLEAR
          )