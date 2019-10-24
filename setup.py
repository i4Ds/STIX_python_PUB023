#!/usr/bin/env python3
import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
      name='stix_parser',
      version='1.4',
      description='STIX python data parser',
      author='Hualin Xiao',
      author_email='hualin.xiao@fhnw.ch',
      url='https://github.com/i4Ds/STIX-python-data-parser',
      packages=setuptools.find_packages(),
      data_files=[('idb',['stix_parser/idb/idb.sqlite'])],
      install_requires=['numpy','PyQt5','PyQtChart','scipy','pymongo','python-dateutil','xmltodict'],
       entry_points={
        'console_scripts': [
            'stix-parser= stix_parser.apps.parser:main',
            'stix-quicklook= stix_parser.apps.stix_quicklook:main',
        ],
        'gui_scripts': [
            'stix-parser-gui= stix_parser.apps.stix_parser_gui:main',
        ]
    },
      python_requires='>=3.6'
)

