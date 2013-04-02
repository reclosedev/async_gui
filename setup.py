#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import glob
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'test':
    os.chdir('tests')
    for test in glob.glob('*.py'):
        os.system('python %s' % test)
    sys.exit()

ver = sys.version_info
if ver[0] < 3 and ver[1] < 2:
    install_requires = ['futures']
else:
    install_requires = []

setup(
    name='async_gui',
    packages=[
        'async_gui',
        'async_gui.toolkits',
    ],
    version='0.1.0',
    description='Easy threading and multiprocessing for GUI applications',
    author='Roman Haritonov',
    author_email='reclosedev@gmail.com',
    url='https://github.com/reclosedev/async_gui',
    install_requires=install_requires,
    keywords=['GUI', 'thread', 'coroutine', 'futures', 'async'],
    license='BSD License',
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    long_description=open('README.rst').read() + '\n\n' +
                     open('HISTORY.rst').read(),
)
