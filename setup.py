#!/usr/bin/env python3

import setuptools
with open("stix/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
      name='StixParser',
      version='1.5',
      description='STIX python data parser',
      author='Hualin Xiao',
      author_email='hualin.xiao@fhnw.ch',
      url='https://github.com/i4Ds/STIX-python-data-parser',
      packages=setuptools.find_packages(),
      install_requires=['numpy','PyQt5','PyQtChart','scipy','pymongo','python-dateutil','xmltodict'],
      package_data={'idb': ['stix/idb/idb.sqlite']},
      scripts=['stix-parser','stix-parser-gui'],
      python_requires='>=3.6'
)

