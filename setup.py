from distutils.core import setup
 
setup(
    name='databench',
    version='0.0.1',
    packages=['databench', 'scripts'],
    license='LICENSE',
    description='Data analysis tool using Flask, SocketIO and d3.js.',
    long_description=open('README.md').read(),
    author='Sven Kreiss',
    author_email='sk@svenkreiss.com',

    install_requires= [
        'multiprocessing',
    ],

    entry_points={
        'console_scripts': [
            'databench = scripts.exec:main',
        ]
    }
)