"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

import os
from setuptools import setup
from glob import glob

APP = ['src/main.py']
DATA_FILES = [('resources', glob('src/resources/*', recursive=True))]
OPTIONS = {
    'argv_emulation': False,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    py_modules=[x.replace('.py', '') for x in glob('src/[!main]*.py')],
)
