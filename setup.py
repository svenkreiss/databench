from distutils.core import setup

setup(
    name='databench',
    version='0.1.0',
    packages=['databench', 'scripts', 'analyses_packaged'],
    license='LICENSE',
    description='Data analysis tool using Flask, SocketIO and d3.js.',
    long_description=open('README.md').read(),
    author='Sven Kreiss',
    author_email='sk@svenkreiss.com',

    include_package_data = True,

    install_requires=[
        'Flask>=0.10.1',
        'Flask-SocketIO>=0.3.7',
        'Jinja2>=2.7.2',
        'MarkupSafe>=0.23',
        'Werkzeug>=0.9.4',
        'gevent>=1.0.1',
        'gevent-socketio>=0.3.6',
        'gevent-websocket>=0.9.3',
        'greenlet>=0.4.2',
        'itsdangerous>=0.24',
        'wsgiref>=0.1.2',
    ],

    entry_points={
        'console_scripts': [
            'databench = scripts.exec:main',
        ]
    }
)
