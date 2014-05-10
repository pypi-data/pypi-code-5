# -*- coding: utf-8 -*-
import os


SELF_LAMBDA = lambda x: x


def list_to_indexed_dict(listobj, value_func=None, start_index=0):
  """Transforms a list into a integer-indexed dict.

  Example:

    ['a', 'b', 'c', 'd']

    =>

    {
      0: 'a',
      1: 'b',
      2: 'c',
      3: 'd'
    }
  """
  value_func = value_func or SELF_LAMBDA

  return dict(
    (index + start_index, value_func(value))
    for index, value in enumerate(listobj)
  )


def list_to_indexed_compound_dict(listobj, value_func=None, start_index=0):
  """Transforms a list into a integer-indexed dict, where each
  value in the original list is wraped in another dict and is accessible
  at its `value` key.

  Example:

    ['a', 'b', 'c', 'd']

    =>

    {
      0: {
        value: 'a'
      },
      'b': {
        value: 'b'
      },
      'c': {
        value: 'c'
      },
      'd': {
        value: 'd'
      }
    }
  """
  value_func = value_func or SELF_LAMBDA

  return list_to_indexed_dict(
    listobj,
    value_func=lambda value: dict(value=value_func(value)),
    start_index=start_index
  )


def dict_to_indexed_dict(dictobj, value_func=None, start_index=0):
  """Transforms a dict into another integer-indexed dict.

  Example:

    {'a': 'apple, 'b': 'bananna', 'c': 'coconut' }

    =>

    {
      0:  {
            'key': 'a',
            'value': 'apple'
          },
      1:  {
            'key': 'b',
            'value': 'bananna'
          },
      2:  {
            'key': 'c',
            'value': 'coconut'
          }
    }
  """
  value_func = value_func or SELF_LAMBDA

  return dict(
    (
      index + start_index,
      dict(
        key=key,
        value=value_func(value)
      )
    )
    for index, (key, value) in enumerate(dictobj.iteritems())
  )


def grab_deep(obj, key, targets=None):
  """Gets the leaf elements in a nested
  list/dict structure.

  Example:

  input: 
  {
    'a': {
      'food': [
        'apple'
      ],
      'transportation': [
        'airplane',
        'aircraft'
      ]
    }
  }

  output:
  ['apple', 'airplane', 'aircraft']
  """
  if isinstance(obj, dict):
    if key in obj:
      grab_deep(obj[key], key, targets)
    else:
      for _, value in obj.iteritems():
        grab_deep(value, key, targets)
  elif isinstance(obj, list):
    for value in obj:
      grab_deep(value, key, targets)
  else:
    targets.append(obj)

  return targets


def get_deep(value, path, default=None):
  """Given a dot-separated path to a `dict` object, get the value specified
  at the path.

  Raises a `KeyError` if the search fails, or returns the default value
  if it is specified.
  """
  paths = path.split('.')
  current_path = paths.pop(0)
  if isinstance(value, dict):
    try:
      return get_deep(value[current_path], '.'.join(paths), default=default)
    except KeyError as e:
      if default:
        return default
      else:
        raise e
  else:
    if value:
      if not current_path:
        return value
      else:
        raise KeyError(current_path)
    else:
      raise KeyError(current_path)


def get_deep_with_leap(value, path, leap, path_func=None, default=None):
  """Given a dot-separated path to a `dict` object, where the nested layers
  of the object are interwined with a specified key, get the value specified
  at the path.

  Example:

    Given the following input value, where the nested dicts
    are interwined with keys of letters and the word 'value'.
    Here, the 'value' key is the `leap`.
    input = \
    {
      'a': {
        'value': {
          'b': {
            'value': {
              'c': {
                'value': 'coconut'
              }
            }
          }
        }
      }
    }

    get_deep_with_leap(input, 'a.b.c', 'value')

    output: 'coconut'

  Raises a `KeyError` if the search fails, or returns the default value
  if it is specified.
  """
  path_func = path_func or SELF_LAMBDA
  paths = path.split('.')
  current_path = paths.pop(0)

  if isinstance(value, dict):
    if not current_path:
      return value

    try:
      return get_deep_with_leap(
        value[path_func(current_path)][leap],
        '.'.join(paths),
        leap,
        path_func=path_func,
        default=default
      )
    except KeyError as e:
      if default:
        return default
      else:
        raise e
    except Exception as e:
      if default:
        return default
      else:
        raise e
  else:
    # For a leaf item:
    # 1.
    #   a) If the item exists and there's no current path,
    #      then it's the desired leaf item. 
    #   b) If the item exists and there is a current path,
    #      then that means the specified path is invalid.
    # 2.
    #   If the item does not exist, then the path is invalid.
    if value:
      if not current_path:
        return value
      else:
        raise KeyError(current_path)
    else:
      raise KeyError(current_path)


def clear_screen():
  """Clears the screen."""
  os.system('clear')