"""
===============
=== Purpose ===
===============

Reads a file containing AMF data, converts that data to into a plain (i.e. no
custom objects) python object, and writes the JSON representation of that
object to another file.

Note: due to use of the `pyamf` package, this is a python2 script and is not
compatible with python3.


=================
=== Changelog ===
=================

2017-02-03
  + initial version
"""

# python2 setup
from __future__ import print_function
# standard library
import argparse
import datetime
import json
# third party
import pyamf.remoting


def get_public_members(obj):
  """
  Return public members of the given object.

  Note that "public members" here are defined as all of:
    - not private (i.e. no leading underscores)
    - not constant (i.e. not all caps)
    - not callable (i.e. not a method)
  """

  # tests for necessary conditions (`callable` is a built-in function)
  private = lambda a: a[:1] == '_'
  constant = lambda a: a == a.upper()

  # return members matching all conditions
  accept = lambda a: not private(a) and not constant(a) and not callable(a)
  return [a for a in dir(obj) if accept(a)]


def is_primitive(obj):
  """Return whether the object is a native python type."""

  # test this non-exhaustive list of types
  for t in (type(None), bool, int, float, str, unicode):
    if isinstance(obj, t):
      return True

  # it must be some other type
  return False


def is_list(obj):
  """Return whether the object is list-like."""
  return isinstance(obj, list) or isinstance(obj, tuple)


def is_map(obj):
  """Return whether the object is map-like."""
  return isinstance(obj, dict)


def extract(amf_obj, known_objects=set(), verbose=False):
  """Recursively extract objects from the amf object."""

  # ignore methods
  if callable(amf_obj):
    if verbose:
      print('not calling ' + str(type(amf_obj)))
    return None

  # pass primitive values through unmodified
  if is_primitive(amf_obj):
    return amf_obj

  # recursively iterate over list items
  if is_list(amf_obj):
    return [extract(elem, known_objects, verbose) for elem in amf_obj]

  # recursively iterate over map entries
  if is_map(amf_obj):
    keys = amf_obj.keys()
    results = [(k, extract(amf_obj[k], known_objects, verbose)) for k in keys]
    return dict(results)

  # special handling for python's datetime objects (return as a string)
  if isinstance(amf_obj, datetime.datetime):
    return str(amf_obj)

  # ignore non-pyamf objects
  type_str = str(type(amf_obj))
  if 'pyamf' not in type_str:
    raise Exception('unable to handle ' + type_str)

  # special handling for pyamf objects
  if verbose:
    print('pyamf type', type(amf_obj))

  # ignore objects pevously seen (e.g. circular references)
  obj_id = id(amf_obj)
  if obj_id in known_objects:
    if verbose:
      print(' skipping known pyamf object')
    return None

  # treat the object as a map and iterate over attributes
  known_objects.add(obj_id)
  result = {}
  for attr in get_public_members(amf_obj):
    if verbose:
      print(' ', attr)
    # recursively extract this attribute
    result[attr] = extract(getattr(amf_obj, attr), known_objects, verbose)
  return result


def convert(file_in, file_out, debug=False):
  """Convert the specified AMF file into the specified JSON file."""

  # read binary AMF data
  with open(file_in, 'rb') as f:
    data_in = f.read()

  # decode the AMF data into a pyamf object
  amf_obj = pyamf.remoting.decode(data_in)

  # convert the pyamf object into a plain python object
  py_obj = extract(amf_obj, verbose=debug)
  if debug and type(py_obj) is dict:
    # record the name of the input file for debugging
    py_obj['__source__'] = file_in

  # get the JSON representation of the python object
  data_out = json.dumps(py_obj)

  # save the JSON string to a file
  with open(file_out, 'w') as f:
    f.write(data_out)


if __name__ == '__main__':
  # args and usage
  parser = argparse.ArgumentParser()
  parser.add_argument(
    'amf_file',
    help='amf file (input)'
  )
  parser.add_argument(
    'json_file',
    help='json file (output)'
  )
  parser.add_argument(
    '--debug',
    default=False, action='store_true', help='enable debug output'
  )
  args = parser.parse_args()

  # sanity check
  if args.amf_file == args.json_file:
    raise Exception('input and output files must be different')

  # do the conversion
  convert(args.amf_file, args.json_file, args.debug)
