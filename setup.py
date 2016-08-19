"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='SafeAPI',

    version='0.0.5',

    description='A python wrapper around the Safe Launcher API.',
    long_description=long_description,

    url='https://github.com/hintofbasil/PySafeAPI',

    author='hintofbasil',
    author_email='william@hutcheson.org.uk',

    # TODO
    #license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # TODO
        #'License :: OSI Approved :: MIT License',

        # TODO test Python 3
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='Maidsafe Safe API',

    packages=find_packages(exclude=['examples', 'tests']),

    install_requires=['requests']
)
