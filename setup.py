from codecs import open
from os import path
import sys
from setuptools import setup


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'mcdc', '_version.py')) as version_file:
    exec(version_file.read())

with open(path.join(here, 'README.md')) as readme_file:
    readme = readme_file.read()

long_description = readme

setup(
    name='mcdc',
    version='0.1.0',
    description='A Neutron transport Monte Carlo code',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ilham Juanda',
    author_email='ijuanda@nd.edu',
    classifers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
    license='BSD-2-Clause',
    python_requires='>=3.6',
    packages=['mcdc'],
    setup_requires=['pytest-runner',],
    tests_require=['pytest'],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
)
