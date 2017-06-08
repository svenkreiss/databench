#!/usr/bin/env python
"""Databench command line tool. See http://databench.trivial.io for
more info."""

from __future__ import absolute_import, print_function

import argparse
import logging
import os
import ssl
import sys
import tornado

from . import __version__ as DATABENCH_VERSION

from zmq.eventloop import ioloop
ioloop.install()


def main():
    """Entry point to run databench."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(DATABENCH_VERSION))
    parser.add_argument('--log', dest='loglevel', default="INFO",
                        type=str.upper,
                        help=('log level (info, warning, error, critical or '
                              'debug, default info)'))
    parser.add_argument('--no-watch', dest='watch', default=True,
                        action='store_false',
                        help='do not watch and restart when files change')
    parser.add_argument('--host', dest='host',
                        default=os.environ.get('HOST', 'localhost'),
                        help='host address for webserver (default localhost)')
    parser.add_argument('--port', dest='port',
                        type=int, default=int(os.environ.get('PORT', 5000)),
                        help='port for webserver')
    parser.add_argument('--analyses', default=None,
                        help='import path for analyses')
    parser.add_argument('--build', default=False, action='store_true',
                        help='run the build command and exit')
    parser.add_argument('--coverage', default=False,
                        help=argparse.SUPPRESS)

    ssl_args = parser.add_argument_group('SSL')
    ssl_args.add_argument('--ssl-certfile', dest='ssl_certfile',
                          help='SSL certificate file')
    ssl_args.add_argument('--ssl-keyfile', dest='ssl_keyfile',
                          help='SSL key file')
    ssl_args.add_argument('--ssl-port', dest='ssl_port', type=int,
                          default=int(os.environ.get('SSLPORT', 5001)),
                          help='SSL port for webserver')

    args, analyses_args = parser.parse_known_args()

    # coverage
    cov = None
    if args.coverage:
        import coverage
        cov = coverage.Coverage(data_file=args.coverage, data_suffix=True)
        cov.start()

    # this is included here so that is included in coverage
    from .app import App

    # log
    if args.loglevel != 'INFO':
        print('Setting loglevel to {}.'.format(args.loglevel))
    logging.basicConfig(level=getattr(logging, args.loglevel))

    # show versions and setup
    logging.info('Databench {}'.format(DATABENCH_VERSION))
    if args.host in ('localhost', '127.0.0.1'):
        logging.info('Open http://{}:{} in a web browser.'
                     ''.format(args.host, args.port))
    logging.debug('host={}, port={}'.format(args.host, args.port))
    logging.debug('Python {}'.format(sys.version))

    if analyses_args:
        logging.debug('Arguments passed to analyses: {}'.format(analyses_args))

    app = App(args.analyses, cmd_args=analyses_args, debug=args.watch)

    # check whether this is just a quick build
    if args.build:
        logging.info('Build mode: only run build command and exit.')
        app.build()
        if cov:
            cov.stop()
            cov.save()
        return

    # HTTP server
    tornado_app = app.tornado_app()
    tornado_app.listen(args.port, args.host)
    # HTTPS server
    if args.ssl_certfile and args.ssl_keyfile:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(args.ssl_certfile, args.ssl_keyfile)
        ssl_server = tornado.httpserver.HTTPServer(tornado_app,
                                                   ssl_options=ssl_ctx)
        ssl_server.listen(args.ssl_port, args.host)

    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.current().stop()
        if cov:
            cov.stop()
            cov.save()


if __name__ == '__main__':
    main()
