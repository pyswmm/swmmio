import os
from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSION = '0.3.2.dev'
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
      version = VERSION,
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
