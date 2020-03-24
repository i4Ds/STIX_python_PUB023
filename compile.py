#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @title        : compile.py
# @description  : compile the code with cython
# @author       : Hualin Xiao
# @date         : Nov. 15, 2019
#   Execute: python3 setup.py build_ext --inplace
#
import glob
from distutils.core import setup
from distutils.extension import Extension
import os
from Cython.Distutils import build_ext
files=glob.glob('stix/core/*py')
files.extend(glob.glob('stix/ui/*py'))
print(files)
modules=[os.path.splitext(x)[0].replace('/','.') for x in files]
ext_modules = []
excluded=['__init__']
for module, fname in zip(modules,files):
    filename=os.path.splitext(os.path.basename(fname))[0] 
    if filename not in excluded:
        print(module, fname)
        ext_modules.append(Extension(module,  [fname]))

for e in ext_modules:
    e.cython_directives = {'language_level': "3"} #all are Python-3
setup(
    name = 'STIX_parser',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
#python3 setup.py build_ext --inplace

