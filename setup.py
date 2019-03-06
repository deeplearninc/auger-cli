#!/usr/bin/env python
"""
    Setup file for auger_cli.
"""

import codecs
from os import path
from setuptools import setup, find_packages


VERSION = '0.1.0'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with codecs.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt')) as f:
    REQUIRES = f.readlines()

with open(path.join(here, 'test-requirements.txt')) as f:
    TESTS_REQUIRES = f.readlines()

setup(
    name='auger-cli',
    version=VERSION,
    url='https://github.com/deeplearninc/auger-cli',
    license='MIT',
    author='DeepLearn',
    description='Command line tool for the Auger AI platform.',
    long_description=long_description,
    packages=find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    test_suite='tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=REQUIRES,
    tests_require=TESTS_REQUIRES,
    entry_points={
        'console_scripts': [
            'auger=auger_cli.cli:cli',
        ]
    }
)
