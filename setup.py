#!/usr/bin/env python
import setuptools


def _get_version():
    with open('aceso/__init__.py') as f:
        for line in f:
            if line.find("__version__") >= 0:
                version = line.split("=")[1].strip()
                version = version.strip('"')
                version = version.strip("'")
                continue
    return version


def _get_long_description():
    with open('README.md', 'r') as f:
        desc = f.read()
    return desc


def _get_install_requires():
    # TODO: Implement this function to read from requirements.txt.
    pass

setuptools.setup(
    name='aceso',
    version=_get_version(),
    description='''
        Lightweight package to calculate 2SFCA and other measures of spatial accessibility
        '''.strip(),
    long_description=_get_long_description(),
    long_description_content_type='text/markdown',
    url='http://github.com/tetraptych/aceso',
    keywords=['geospatial', 'geo', 'gis', '2SFCA', 'gravity', 'access', 'catchment-area'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    author='Brian Lewis',
    author_email='brianburkelewis@gmail.com',
    license='MIT',
    packages=['aceso'],
    install_requires=[
        'numpy>=1.11.0',
    ],
    python_requires='>=2.7'
)
