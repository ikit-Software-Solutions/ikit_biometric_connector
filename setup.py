# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in ikit_biometric_connector/__init__.py
from ikit_biometric_connector import __version__ as version

setup(
	name='ikit_biometric_connector',
	version=version,
	description='Ikit Biometric Connector',
	author='IKIT',
	author_email='sales@ikit.solutions',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
