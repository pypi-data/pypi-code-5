# -*- coding: utf-8 -*-
import utils


class RecursiveTransformer(object):
  """An object that applies recursive transformation to a data structure."""

  def __init__(self, type_to_action_map):
    self.type_to_action_map = type_to_action_map or {}

  def get_transformer(self, obj):
    return self.type_to_action_map.get(
      type(obj),
      dict(
        value_func=utils.SELF_LAMBDA,
        args=[],
        kwargs={}
      )
    )

  def _transform(self, obj):
    if isinstance(obj, dict):
      return dict(
        (
          key,
          self.transform(value)
        )
        for key, value in obj.iteritems()
      )

    if isinstance(obj, list):
      return [
        self.transform(value) for value in obj
      ]

    return obj

  def transform(self, obj):
    transformer = self.get_transformer(obj)
    value_func = transformer['value_func']
    args = transformer['args']
    kwargs = transformer['kwargs']
    return value_func(self._transform(obj), *args, **kwargs)