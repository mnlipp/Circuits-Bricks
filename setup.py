import os
from setuptools import setup, find_packages
from imp import new_module
from os import path
from posix import getcwd

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = new_module("version")

exec(
    compile(
        open(
            path.join(
                path.dirname(
                    globals().get(
                        "__file__",
                        path.join(getcwd(), "circuits_bricks")
                    )
                ),
                "circuits_bricks/version.py"
            ),
            "r"
        ).read(),
        "circuits_bricks/version.py", "exec"
    ),
    version.__dict__
)

setup(
    name = "circuits-bricks",
    version = version.version,
    author = "Michael N. Lipp",
    author_email = "mnl@mnl.de",
    description = ("General purpose components extending the circuits framework."),
    license = "MIT",
    keywords = "circuits component",
    url = "http://packages.python.org/circuits-bricks",
    long_description=read('pypi-overview.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages("."),
    install_requires = ['circuits>=3.2'],
)
