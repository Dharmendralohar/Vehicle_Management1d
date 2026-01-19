from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in insurance_erp/__init__.py
from insurance_erp import __version__ as version

setup(
	name="insurance_erp",
	version=version,
	description="Vehicle Insurance Policy Management System",
	author="Insurance Solutions Inc",
	author_email="admin@example.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
