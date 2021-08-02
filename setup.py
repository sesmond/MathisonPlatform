from setuptools import setup, find_packages
setup(
	name="mathison",
	version="1.0",
	description="mathison platform common code",
	author="vincent",
	url="",
	license="LGPL",
	packages=find_packages(where='.', exclude=(), include=('*',)),
	# packages=find_packages()
)
