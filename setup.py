import os
from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSION = '0.1.5'  # also update __init__.py
AUTHOR_NAME = 'Adam Erispaha'
AUTHOR_EMAIL = 'aerispaha@gmail.com'

install_requires = [
    'pillow==3.0.0',
    'matplotlib',
    'numpy',
    'pandas',
    'pyshp',
    'geojson'
    ]

setup(name='swmmio',
      version=VERSION,
      description='Tools for reading, writing, visualizing, and versioning EPA SWMM5 models.',
      author=AUTHOR_NAME,
      url='https://github.com/aerispaha/swmmio',
      author_email=AUTHOR_EMAIL,
      packages=find_packages(exclude=('tests')),
      install_requires=install_requires,
      long_description=read('README.rst'),
      platforms="OS Independent",
      license="MIT License",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
      ]
)
