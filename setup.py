# Standard library imports
import os
import ast

# Third party imports
from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))

def get_version(module='swmmio'):
    """Get version."""
    with open(os.path.join(HERE, module, '__init__.py'), 'r') as f:
        data = f.read()
    lines = data.split('\n')
    for line in lines:
        if line.startswith('VERSION_INFO'):
            version_tuple = ast.literal_eval(line.split('=')[-1].strip())
            version = '.'.join(map(str, version_tuple))
            break
    return version

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


AUTHOR_NAME = 'Adam Erispaha'
AUTHOR_EMAIL = 'aerispaha@gmail.com'

install_requires = [
    'Pillow',
    'numpy',
    'pandas',
    'pyshp',
    'geojson',
    ]

tests_require = [
    'pytest',
]

setup(name = 'swmmio',
      version = get_version(),
      description = 'Tools for reading, writing, visualizing, and versioning EPA SWMM5 models.',
      author = AUTHOR_NAME,
      url = 'https://github.com/aerispaha/swmmio',
      author_email = AUTHOR_EMAIL,
      packages = find_packages(exclude = ('tests')),
      entry_points = {
        "console_scripts": ['swmmio_run = swmmio.run_models.run:run_simple']
        },
      install_requires = install_requires,
      tests_require = tests_require,
      long_description = read('README.rst'),
      include_package_data = True,
      platforms = "OS Independent",
      license = "MIT License",
      classifiers = [
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
      ]
)
