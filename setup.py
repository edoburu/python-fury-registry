#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path
import codecs
import os
import re


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError("Unable to find version string.")


setup(
    name='sidn',
    version=find_version('sidn', '__init__.py'),
    author='Diederik van der Boor, Jochem Oosterveen',
    author_email='opensource@edoburu.nl',
    packages=find_packages(),
    description='Python EPP client for SIDN/DRS5',
    long_description=read('README.rst'),
    install_requires=[
        "BeautifulSoup >= 3.2.1",
        "python-dateutil",
    ],
)
