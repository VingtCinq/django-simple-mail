#!/usr/bin/env python
import os
import simple_mail
from setuptools import setup, find_packages


README = os.path.join(os.path.dirname(__file__), 'README.rst')

# When running tests using tox, README.md is not found
try:
    with open(README) as file:
        long_description = file.read()
except Exception:
    long_description = ''


setup(
    name='django_simple_mail',
    version=simple_mail.__version__,
    description='A simple and customizable email template built for Django',
    long_description=long_description,
    url='https://github.com/charlesthk/django-simple-mail',
    author='Charles TISSIER',
    author_email='charles@vingtcinq.io',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.9',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='python django mail html template',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'html2text>=2018.1.9',
        'premailer>=3.2.0',
        'Pillow>=5.2.0',
        'django-imagekit>=4.0.2'
    ],
    # test_suite='tests',
)
