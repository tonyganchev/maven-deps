#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys
import mavendeps

__author__ = 'Tony Ganchev'


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


setup(name='mavendeps',
      version=mavendeps.__version__,
      url='https://www.github.com/tonyganchev/maven-deps/',
      description='Library for transforming Maven dependency graphs coming from FuseSource\'s maven-graph-plugin',
      author='Tony Ganchev',
      author_email='tony.ganchev@gmail.com',
      license='The MIT License (MIT)',
      long_description='''
          The library provides engineers with a way to filter out and style a
          maven dependency graph generated using the FuseSource maven graph
          plugin. This allows for the investigation of complex build
          dependency webs to figure out a specific issue or for presentation
          purposes.
      ''',
      tests_require=['tox'],
      cmdclass={'test': Tox},
      packages=['mavendeps'],
      include_package_data=True,
      platforms='any',
      classifiers=[
          'Programming Language :: Python',
          'Development Status :: 5 - Production/Stable',
          'Natural Language :: English',
          'Environment :: CLI Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: The MIT License (MIT)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Visualization',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      keywords=[])
