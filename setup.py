import os
from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))

VERSION = '0.1.0'  # also update __init__.py
AUTHOR_NAME = 'Adam Erispaha'
AUTHOR_EMAIL = 'aerispaha@gmail.com'

install_requires = [
    'pillow',
    'matplotlib',
    'numpy',
    'pickle',
    'pandas',
    ]

setup(name='swmmio',
      version=VERSION,
      description='Tools for reading, writing, visualizing, and versioning EPA SWMM5 models.',
      author=AUTHOR_NAME,
      url='https://github.com/aerispaha/swmmio',
      author_email=AUTHOR_EMAIL,
      packages=['swmmio', 'version_control', 'utils', 'run_models',
                'reporting', 'graphics', 'defs', 'vendor'],
      install_requires=install_requires,
      long_description=read('README.md'),
      platforms="OS Independent",
      license="MIT License",
      classifiers=[
          'Development Status :: 3 - Alpha',
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Intended Audience :: Developers :: Civil Engineers",
          "Topic :: Engineering :: Graphics",
      ]
)
