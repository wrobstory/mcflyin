# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='mcflyin',
    version='0.0.1',
    description='Time traveling Pandas.',
    author='Rob Story',
    author_email='wrobstory@gmail.com',
    license='MIT License',
    url='https://github.com/wrobstory/mcflyin',
    keywords='data analysis',
    classifiers=['Development Status :: 3 - Alpha',
                 'Programming Language :: Python :: 2.7',
                 'License :: OSI Approved :: MIT License'],
    packages=['mcflyin'],
    package_data={'': ['*.js',
                       'templates/*.html',
                       'templates/*.js',
                       'templates/*.txt']}
)
