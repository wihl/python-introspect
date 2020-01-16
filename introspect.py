#!/usr/bin/env python
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Import a directory or module containing a hierarchy of Python files
and produce a dict or printout containing all exported classes.
This is useful to populate a types.py file to implement lazy loading
of a complex object hierarchy in Python 3.7+.

This assumes that the hierarchy may contain Google protobuf definitions,
so superfluous 'google_dot' and '*grpc' modules are filtered.
"""


import argparse
import sys
import os
import importlib
import inspect
import pprint as pp

PREFIX='google.ads.google_ads.v2.proto'
DEFAULT_DIR = '/Users/wihl/Projects/Google/google-ads-python/google/ads/google_ads/v2/proto'


def traverse_module(module, depth = 1):
    for name, submod in inspect.getmembers(module, inspect.ismodule):
        if name.startswith(('_','google_dot_','path')):
            continue
        if name == 'sys' or name == 'config' or name == 'collections' or name == 'handlers' or name == 'io':
            continue
        if name.endswith('grpc'):
            continue
        if inspect.isbuiltin(submod):
            continue
        print('---' * depth, name)
        for class_name, _ in inspect.getmembers(submod, inspect.isclass):
            print('   ' * (depth + 1), class_name)
        traverse_module(submod, depth + 1)


def fixed_traverse(module):
    for name, val in inspect.getmembers(module, inspect.ismodule):
        print('---',name)
        for n2, val2 in inspect.getmembers(val, inspect.ismodule):
            print ('---' * 2, n2)
            for n3, val3 in inspect.getmembers(val2, inspect.isclass):
                print ('   ' * 3, n3)


def traverse_dir(directory, to_print):
    """ Traverse a directory of Python modules."""
    if to_print:
        print (f'Starting directiory: {directory}\n')
    else:
        print ('_lazy_class_to_package_map = dict(')
    for root, _, files in os.walk(directory):
        if os.path.basename(root) == '__pycache__':
            continue
        n_dirs = len(root.split(os.sep)) - len(directory.split(os.sep)) + 1
        if to_print:
            print((n_dirs) * '---', os.path.basename(root))
        for file in files:
            if not file.endswith('.py'):
                continue
            if file.endswith(('_grpc.py', 'init__.py')):
                continue
            fullpath = root + os.sep + file
            if to_print:
                print((n_dirs + 1) * '   ' + file)
            # remove trailing .py from file
            fname = file[:-3]
            spec = importlib.util.spec_from_file_location(fname, fullpath)
            foo = importlib.util.module_from_spec(spec)

            try:
                #spec.loader.exec_module(foo)
                is_importable(fullpath)
            except Exception as e:
                print(f"ERROR module={foo}  exception={e}")
                continue

            print(f"Imported {fname}")
            # for class_name, _ in inspect.getmembers(foo, inspect.isclass):
            #     if to_print:
            #         print((n_dirs + 2) * '   ', class_name)
            #     else:
            #         print(f"    {class_name}='{PREFIX+'.'+os.path.basename(root)}.{file[:-3]}',")
    if not to_print:
        print (')')


def is_importable(fullpath):
    """ Test whether the file in the fullpath can be imported. """
    parts = fullpath.split(os.sep)
    fname = parts[-1][:-3]
    my_globals = {}

    x = f"from google.ads.google_ads.v999.proto.{parts[-2]} import {fname}"
    y = f"google.ads.google_ads.v999.proto.{parts[-2]}.{fname}"
    try:
        # exec(x, my_globals)
        importlib.import_module(y)
    except Exception as e:
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Produce a dict of all public values by introspection.')
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument('-m', '--mod', type=str, nargs='?', const=PREFIX,
                        help='Starting module.')
    grp.add_argument('-d', '--dir', type=str, nargs='?',
                        help='Starting directory.')
    parser.add_argument('-p', '--print', action='store_true', required=False,
                        help='Print results (instead of producing a dict)')
    args = parser.parse_args()
    if args.dir:
      if not os.path.isdir(args.dir):
        print(f"directory {args.dir} cannot be found")
        sys.exit()
      traverse_dir(args.dir, args.print)
    elif args.mod:
        module = importlib.import_module(args.mod)
        traverse_module(module)
    else:
        traverse_dir(DEFAULT_DIR, args.print)



