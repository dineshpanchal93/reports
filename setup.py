from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in reports/__init__.py
from reports import __version__ as version

setup(
	name="reports",
	version=version,
	description="All Custom Report",
	author="dineshpanchal432@gmail.com",
	author_email="dineshpanchal432@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
