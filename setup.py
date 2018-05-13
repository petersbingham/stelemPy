# -*- coding: utf-8 -*-

from distutils.core import setup
import shutil
shutil.copy('README.md', 'stelempy/README.md')

setup(name='stelempy',
      version='0.11',
      description='Python package to find and quantify stable elements over a number of sets.',
      author="Peter Bingham",
      author_email="petersbingham@hotmail.co.uk",
      packages=['stelempy'],
      package_data={'stelempy': ['tests/*', 'README.md']}
     )
