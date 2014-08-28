from distutils.core import setup

import re

# extract version from __init__.py
with open('databench/__init__.py', 'r') as f:
    INIT = f.read()
    VERSION = re.finditer('__version__ = \"(.*?)\"', INIT).next().group(1)

setup(
    name='databench',
    version=VERSION,
    packages=['databench', 'databench_py', 'scripts', 'analyses_packaged'],
    license='LICENSE',
    description='Data analysis tool using Flask, WebSockets and d3.js.',
    long_description=open('README.md').read(),
    author='Sven Kreiss',
    author_email='me@svenkreiss.com',

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
            'databench = scripts.exec:main',
            'scaffold-databench = scripts.scaffold:main',
        ]
    }
)
