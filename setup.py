# *********************************************************************************************
# Copyright (C) 2017 Joel Becker,  Jillian Anderson, Steve McColl and Dr. John McLevey
#
# This file is part of the labutils package developed for Dr John McLevey's Networks Lab
# at the University of Waterloo.
#
# labutils is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License along with tidyextractors.
# If not, see <http://www.gnu.org/licenses/>.
# *********************************************************************************************

"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
import pip
from os import path
from codecs import open
from setuptools import setup, find_packages
from pip.req import parse_requirements


here = path.abspath(path.dirname(__file__))

# !!! Update version here!
version_string = '0.0.1'

# Parse requirements
# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('./requirements.txt', session=pip.download.PipSession())

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='labutils',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version_string,

    description='Utilities for NetLab developers and researchers.',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/networks-lab/labutils/',
    download_url='https://github.com/networks-lab/labutils/archive/{}.tar.gz'.format(version_string),


    # Author details
    author='networks-lab',
    author_email='john.mclevey@uwaterloo.ca',

    # Choose your license
    license='GPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 1 - Planning',

        # Indicate who your project is intended for
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Sociology',
        'Topic :: Utilities'

    ],

    # What does your project relate to?
    keywords='matching dataframes fusion pandas recordlinkage',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=reqs,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # If there are test_data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #     'sample': ['package_data.dat'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place test_data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['test_data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)
