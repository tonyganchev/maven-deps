#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup, find_packages
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


# prerequisite - python 2-compatible pyparsing module.
#
# pip uninstall pyparsing
# pip install -Iv https://pypi.python.org/packages/source/p/pyparsing/pyparsing-1.5.7.tar.gz#md5=9be0fcdcc595199c646ab317c1d9a709
# pip install pydot
setup(name='mavendeps',
      version=mavendeps.__version__,
      url='https://www.github.com/tonyganchev/maven-deps/',
      description='Library for transforming Maven dependency graphs coming from FuseSource\'s maven-graph-plugin',
      author='Tony Ganchev',
      author_email='tony.ganchev@gmail.com',
      license='The MIT License (MIT)',
      long_description=open("README.md").read(),
      tests_require=['tox'],
      cmdclass={'test': Tox},
      # package_data_dirs=['mavendeps/samples'],
      # scripts=['mavendeps/samples/reduce_karaf_codebase_deps.py',
      #          'mavendeps/samples/reduce_karaf_sample_deps.py'],
      packages=['mavendeps'],
      include_package_data=True,
      platforms='any',
      classifiers=[
          'Programming Language :: Python',
          'Development Status :: 4 - Beta',
          'Natural Language :: English',
          'Environment :: CLI Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: The MIT License (MIT)',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      keywords=[])
