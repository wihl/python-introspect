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
"""Import a directory containing a hierarchy of Python files
and produce a dict containing all exported elements.
"""


import argparse
import sys
import os
import importlib
import inspect
import pprint as pp

PREFIX='google.ads.google_ads.v2.'

def traverse(module, depth = 1):
    for name, submod in inspect.getmembers(module, inspect.ismodule):
        if name.startswith(('_','google_dot_','path')):
            continue
        if name == 'sys':
            continue
        if name.endswith('grpc'):
            continue
        if inspect.isbuiltin(submod):
            continue
        print('---' * depth, name)
        for class_name, _ in inspect.getmembers(submod, inspect.isclass):
            print('   ' * (depth + 1), class_name)
        traverse(submod, depth + 1)

def fixed_traverse(module):
    for name, val in inspect.getmembers(module, inspect.ismodule):
        print('---',name)
        for n2, val2 in inspect.getmembers(val, inspect.ismodule):
            print ('---' * 2, n2)
            for n3, val3 in inspect.getmembers(val2, inspect.isclass):
                print ('   ' * 3, n3)

def show_dir(directory):
    try:
        print ('_lazy_class_to_package_map = dict(')
        for root, dirs, files in os.walk(directory):
            if os.path.basename(root) == '__pycache__':
                continue
            path = root.split(os.sep)
            #  print((len(path) - 1) * '---', os.path.basename(root))
            for file in files:
                if not file.endswith('.py'):
                    continue
                if file.endswith(('_grpc.py', 'init__.py')):
                    continue
                fullpath = root + os.sep + file
                # print(fullpath)
                # remove trailing .py from file
                spec = importlib.util.spec_from_file_location(file[:-3],fullpath)
                foo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(foo)
                for class_name, _ in inspect.getmembers(foo, inspect.isclass):
                    print(f"    {class_name}='{PREFIX+os.path.basename(root)}.{file[:-3]}',")
        print (')')


    except:
        print ('exception occurred')
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Produce a dict of all public values by introspection.')
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument('-m', '--mod', type=str,
                        required=False, help='Starting module.',
                        default='google.ads.google_ads.v2.proto')
    # XXX: Obviously the default will change
    grp.add_argument('-d', '--dir', type=str,
                        required=False, help='Starting directory.',
                        default='/usr/local/google/home/davidwihl/Projects/ads/python/google-ads-python/google/ads/google_ads/v2/proto/')
    args = parser.parse_args()

    show_dir(args.dir)
