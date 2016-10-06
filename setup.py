import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "MyBooleanNetSimul",
    version = "0.0.4",
    author = "Je-Hoon Song",
    author_email = "song.jehoon@gmail.com",
    description = ( "BooleanNetwork Simulator"),
    license = "BSD",
    keywords = "example documentation tutorial",
    url = "",
    packages=['boolean3', 'boolean3_addon'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
