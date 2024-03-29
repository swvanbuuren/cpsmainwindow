#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='cpsmainwindow',
    version='0.1',
    author='Sietze van Buuren',
    author_email='s.van.buuren@gmail.com',
    packages=find_packages(),
    url='https://github.com/swvanbuuren/cpsmainwindow',
    license='LICENSE',
    description='A classic main window implementation for PySide',
    long_description=open('README.md').read(),
    install_requires=['PySide2',
                      'shiboken2']
)
