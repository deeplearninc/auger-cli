#!/usr/bin/env python
"""
    Setup file for auger_cli.
"""

import codecs
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install


VERSION = '0.1.9'

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

class VerifyVersionCommand(install):
    """Verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG', '')

        if not tag.endswith(VERSION, 1):
            info = "Git tag: {0} does not match the version of auger-cli: {1}".format(
                tag, VERSION
            )
            sys.exit(info)

setup(
    name='auger-cli',
    version=VERSION,
    url='https://github.com/deeplearninc/auger-cli',
    license='MIT',
    author='Auger AI',
    description='Command line tool for the Auger AI platform.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    test_suite='tests',
    python_requires='>=3',
    keywords='augerai auger ai machine learning automl deeplearn api sdk',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        "Intended Audience :: System Administrators",
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Programming Language :: Python :: 3 :: Only"
    ],
    install_requires=[
        'click>=6.7',
        'click-spinner>=0.1',
        'auger-hub-api-client==0.5.6',
        'pandas==0.23.4',
        'ruamel.yaml'
    ],
    setup_requires=[
        'flake8==3.4.1'
    ],
    tests_require=[
        'coverage==4.4.1',
        'vcrpy==1.11.1',
        'mock==2.0.0'
    ],
    cmdclass={
        'verify': VerifyVersionCommand
    },
    entry_points={
        'console_scripts': [
            'auger=auger_cli.cli:cli',
        ]
    }
)
