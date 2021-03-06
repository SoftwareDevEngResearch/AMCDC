from codecs import open
from os import path
import setuptools


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as readme_file:
    readme = readme_file.read()

long_description = readme

setuptools.setup(
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
    packages=['mcdc', 'mcdc.examples', 'mcdc.tests_tmp',
              'mcdc.examples.slabs',
              'mcdc.examples.slabs.beam_source',
              'mcdc.examples.slabs.eig_alpha',
              'mcdc.examples.slabs.eig_k',
              'mcdc.examples.slabs.multi_source',
              'mcdc.examples.slabs.uniform_source'],
    setup_requires=['pytest-runner',],
    tests_require=['pytest'],
)
