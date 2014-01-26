#!/usr/bin/env python

from distutils.core import setup

setup(name='rdlcompiler',
      version='0.1',
      description='',
      author='Paul Roukema',
      author_email='roukemap@gmail.com',
      url='',
      packages=['rdlcompiler', 'rdlcompiler.systemrdl'],
      requires=[ 'enum34']
     )