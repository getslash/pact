import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "pact", "__version__.py")) as version_file:
    exec(version_file.read()) # pylint: disable=W0122

_INSTALL_REQUIRES = [
    'flux',
    'Logbook>=0.12.2',
    'waiting',
]

setup(name="pact",
      classifiers=[
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          ],
      description="Promises library in Python",
      license="BSD3",
      author="Rotem Yaari",
      author_email="vmalloc@gmail.com",
      version=__version__,  # pylint: disable=undefined-variable
      packages=find_packages(exclude=["tests"]),

      url="https://github.com/getslash/pact",

      install_requires=_INSTALL_REQUIRES,
      scripts=[],
      namespace_packages=[]
     )
