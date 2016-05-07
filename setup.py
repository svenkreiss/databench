from setuptools import setup


# extract version from __init__.py
with open('databench/__init__.py', 'r') as f:
    version_line = [l for l in f if l.startswith('__version__')][0]
    VERSION = version_line.split('=')[1].strip()[1:-1]


setup(
    name='databench',
    version=VERSION,
    packages=['databench', 'databench.analyses_packaged',
              'databench_py', 'databench_py.singlethread'],
    license='MIT',
    description='Realtime data analysis tool.',
    long_description=open('README.rst').read(),
    author='Sven Kreiss',
    author_email='me@svenkreiss.com',
    url='https://github.com/svenkreiss/databench',

    include_package_data=True,

    install_requires=[
        'tornado>=4.3',
        'pyzmq>=4.3.1',
    ],
    entry_points={
        'console_scripts': [
            'databench = databench.cli:main',
            'scaffold-databench = databench.scaffold:main',
        ]
    },

    extras_require={
        'markup': [
            'markdown>=2.6.5',
            'docutils>=0.12',
        ],
        'tests': [
            'flake8>=2.5.4',
            'hacking>=0.11.0',
            'nose>=1.3.4',
            'coverage>=4.1b2',
            'requests>=2.9.1',
            'websocket-client>=0.35.0',
        ],
    },

    tests_require=[
        'nose>=1.3.4',
    ],
    test_suite='nose.collector',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
