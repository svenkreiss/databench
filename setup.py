from setuptools import setup

import re

# extract version from __init__.py
with open('databench/__init__.py', 'r') as f:
    INIT = f.read()
    VERSION = re.finditer('__version__ = \"(.*?)\"', INIT).next().group(1)

setup(
    name='databench',
    version=VERSION,
    packages=['databench', 'databench_py', 'analyses_packaged'],
    license='MIT',
    description='Data analysis tool using Flask, WebSockets and d3.js.',
    long_description=open('README.rst').read(),
    author='Sven Kreiss',
    author_email='me@svenkreiss.com',
    url='https://github.com/svenkreiss/databench',

    include_package_data=True,

    install_requires=[
        'Flask>=0.10.1',
        'Flask-Sockets>=0.1',
        'Flask-Markdown>=0.3',
        'Jinja2>=2.7.2',
        'MarkupSafe>=0.23',
        'Werkzeug>=0.9.4',
        'jinja2-highlight>=0.5.1',
        'pyzmq>=4.3.1',
    ],
    entry_points={
        'console_scripts': [
            'databench = databench.cli:main',
            'scaffold-databench = databench.scaffold:main',
        ]
    },

    tests_require=[
        'nose',
        'requests',
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
