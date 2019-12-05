import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='stix_parser',
    version='1.3',
    description='STIX python data parser',
    url='https://github.com/i4Ds/STIX-python-data-parser',
    packages=setuptools.find_packages(),
    data_files=[('idb', ['stix_parser/data/idb/idb.sqlite'])
                ('tls_filename',['stix_parser/data/SPICE/kernels/lsk/naif0012.tls']),
                ('sclk_filename',['stix_parser/data/SPICE/kernels/sclk/solo_ANC_soc-sclk_20000101_V01.tsc'])],
    install_requires=['numpy', 'PyQt5', 'PyQtChart', 'scipy', 'pymongo', 'python-dateutil',
                      'xmltodict', 'spiceypy','qtconsole'],
    extras_require={
            'dev':  ["pytest", "pycodestyle", "pydocstyle",  "flake8"],
    },

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
