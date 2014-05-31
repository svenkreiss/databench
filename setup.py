from distutils.core import setup

setup(
    name='databench',
    version='0.0.4',
    packages=['databench', 'scripts', 'analyses_packaged'],
    license='LICENSE',
    description='Data analysis tool using Flask, SocketIO and d3.js.',
    long_description=open('README.md').read(),
    author='Sven Kreiss',
    author_email='sk@svenkreiss.com',

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
    },

    data_files=[
        ('databench/static/', ['databench.js', 'favicon.ico', 'main.css']),

        ('databench/static/bootstrap-3.1.1-dist/css', ['bootstrap.css','bootstrap.min.css','bootstrap-theme.css','bootstrap-theme.min.css']),
        ('databench/static/bootstrap-3.1.1-dist/js', ['bootstrap.js','bootstrap.min.js']),
        ('databench/static/bootstrap-3.1.1-dist/fonts', ['glyphicons-halflings-regular.eot','glyphicons-halflings-regular.svg','glyphicons-halflings-regular.ttf','glyphicons-halflings-regular.woff']),

        ('databench/static/d3', ['d3.v3.min.js']),
        ('databench/static/jquery', ['jquery-2.1.1.min.js']),
        ('databench/static/mpld3', ['mpld3.v0.2.js']),
        ('databench/static/socket.io', ['socket.io.min.js']),

        ('databench/templates', ['base.html','index.html']),
    ]
)
