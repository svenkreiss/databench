from setuptools import setup

import re
import sys

# workaround: nosetests don't exit cleanly with older
# python version (<=2.6 and even <2.7.4)
try:
    import multiprocessing
except ImportError:
    pass


# extract version from __init__.py
with open('databench/__init__.py', 'r') as f:
    INIT = f.read()
    VERSION = re.finditer('__version__ = \"(.*?)\"', INIT).next().group(1)


INSTALL_REQUIRES = [
    'Flask>=0.10.1',
    'Flask-Sockets>=0.1',
    'Flask-Markdown>=0.3',
    'Jinja2>=2.7.2',
    'MarkupSafe>=0.23',
    'Werkzeug>=0.9.4',
    'pyzmq>=4.3.1',
    'zipstream>=1.0.4',
]


major, minor1, minor2, release, serial = sys.version_info
if major <= 2 and minor1 < 7:
    # add argparse dependency for python < 2.7
    INSTALL_REQUIRES.append('argparse>=1.2.1')
    # pin for Python 2.6 compatibility; later versions are not compatible
    INSTALL_REQUIRES.append('jinja2-highlight==0.5.1')
    INSTALL_REQUIRES.append('Markdown<2.5.0')
else:
    # also pin this, because 0.6.1 seems broken
    INSTALL_REQUIRES.append('jinja2-highlight==0.5.1')


setup(
    name='databench',
    version=VERSION,
    packages=['databench', 'databench_py', 'databench_py.singlethread'],
    license='MIT',
    description='Data analysis tool using Flask, WebSockets and d3.js.',
    long_description=open('README.rst').read(),
    author='Sven Kreiss',
    author_email='me@svenkreiss.com',
    url='https://github.com/svenkreiss/databench',

    include_package_data=True,

    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': [
            'databench = databench.cli:main',
            'scaffold-databench = databench.scaffold:main',
        ]
    },

    tests_require=[
        'nose>=1.3.4',
        'coverage>=3.7.1',
        'requests>=2.4.1',
        'websocket-client>=0.18.0',
    ],
    test_suite='nose.collector',

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ]
)
