#!/usr/bin/env python

from setuptools import setup


with open('README.md', 'r') as f:
    readme = f.read()


setup(
    name='drf-redis_tokens',
    version='0.1.0',
    packages=['drf_redis_tokens'],
    license='MIT',
    author='Mikaeil Orfanian',
    description='Django REST Framework user auth using multiple tokens stored in Redis',
    author_email='mokt@outlook.com',
    long_description=readme,
    install_requires=['passlib', 'djangorestframework'],
    include_package_data=True,
    url='https://bitbucket.org/to_reforge/djforge-redis-tokens',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
