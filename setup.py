#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name="arkosctl",
    version="0.3",
    install_requires=[
        "click==6.0",
        "pyarkosclient>=0.3"
    ],
    description="arkOS command-line interface",
    author='CitizenWeb',
    author_email='info@citizenweb.io',
    url='https://arkos.io/',
    license='GPLv3',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['arkosctl = arkosctl:main'],
    }
)
