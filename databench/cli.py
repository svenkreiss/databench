#!/usr/bin/env python
"""Databench command line tool. See http://databench.trivial.io for
more info."""

from __future__ import absolute_import, print_function

from . import __version__ as DATABENCH_VERSION
import argparse
import logging
import os
import ssl
import sys
import tornado


def main(**kwargs):
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
    if not kwargs:
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
                          default=int(os.environ.get('SSLPORT', 0)),
                          help='SSL port for webserver')

    args, analyses_args = parser.parse_known_args()

    # coverage
    cov = None
    if args.coverage:
        import coverage
        cov = coverage.Coverage(data_file=args.coverage, data_suffix=True)
        cov.start()

    # this is included here so that is included in coverage
    from .app import App, SingleApp

    # log
    logging.basicConfig(level=getattr(logging, args.loglevel))
    if args.loglevel != 'INFO':
        logging.info('Set loglevel to {}.'.format(args.loglevel))

    # show versions and setup
    logging.info('Databench {}'.format(DATABENCH_VERSION))
    if args.host in ('localhost', '127.0.0.1'):
        logging.info('Open http://{}:{} in a web browser.'
                     ''.format(args.host, args.port))
    logging.debug('host={}, port={}'.format(args.host, args.port))
    logging.debug('Python {}'.format(sys.version))

    if analyses_args:
        logging.debug('Arguments passed to analyses: {}'.format(analyses_args))

    if not kwargs:
        app = App(args.analyses, cli_args=analyses_args, debug=args.watch)
    else:
        app = SingleApp(cli_args=analyses_args, debug=args.watch, **kwargs)

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
    if args.ssl_port:
        if args.ssl_certfile and args.ssl_keyfile:
            ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_ctx.load_cert_chain(args.ssl_certfile, args.ssl_keyfile)
        else:
            # use Tornado's self signed certificates
            module_dir = os.path.dirname(tornado.__file__)
            ssl_ctx = {
                'certfile': os.path.join(module_dir, 'test', 'test.crt'),
                'keyfile': os.path.join(module_dir, 'test', 'test.key'),
            }

        logging.info('Open https://{}:{} in a web browser.'
                     ''.format(args.host, args.ssl_port))
        tornado_app.listen(args.ssl_port, ssl_options=ssl_ctx)

    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.current().stop()
        if cov:
            cov.stop()
            cov.save()


def run(analysis, path=None, name=None, info=None, **kwargs):
    """Run a single analysis.

    :param Analysis analysis: Analysis class to run.
    :param str path: Path of analysis. Can be `__file__`.
    :param str name: Name of the analysis.
    :param dict info: Optional entries are ``version``, ``title``,
        ``readme``, ...
    :param dict static: Map[url regex, root-folder] to serve static content.
    """
    kwargs.update({
        'analysis': analysis,
        'path': path,
        'name': name,
    })
    main(**kwargs)


if __name__ == '__main__':
    main()
