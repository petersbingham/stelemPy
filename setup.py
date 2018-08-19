# -*- coding: utf-8 -*-

from distutils.core import setup
import os
import shutil
shutil.copy('README.md', 'stelempy/README.md')

dir_setup = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_setup, 'stelempy', 'release.py')) as f:
    # Defines __version__
    exec(f.read())

setup(name='stelempy',
      version=__version__,
      description='Python package to find and quantify stable elements over a number of sets.',
      author="Peter Bingham",
      author_email="petersbingham@hotmail.co.uk",
      packages=['stelempy'],
      package_data={'stelempy': ['tests/*', 'README.md']}
     )
