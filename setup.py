import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

import circuits_bricks

setup(
    name = "circuits-bricks",
    version = circuits_bricks.__version__,
    author = "Michael N. Lipp",
    author_email = "mnl@mnl.de",
    description = ("General purpose components extending the circuits framework."),
    license = "MIT",
    keywords = "circuits component",
    url = "http://packages.python.org/circuits-bricks",
    packages=['circuits_bricks', 'tests'],
    package_data={'circuits_bricks': ['*.properties'],
                  'tests': ['*.properties']},
    long_description=read('pypi-overview.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ],
)