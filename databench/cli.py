#!/usr/bin/env python
"""Databench command line tool. See http://databench.trivial.io for
more info."""

import argparse
import logging
import os
import random
# import signal
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
    parser.add_argument('--log', dest='loglevel', default="WARNING",
                        help='log level (INFO and DEBUG enable '
                             'autoreload)')
    parser.add_argument('--host', dest='host',
                        default=os.environ.get('HOST', 'localhost'),
                        help='host address for webserver (default localhost)')
    parser.add_argument('--port', dest='port',
                        type=int, default=int(os.environ.get('PORT', 5000)),
                        help='port for webserver')
    parser.add_argument('--with-coverage', dest='with_coverage',
                        default=False, action='store_true',
                        help=argparse.SUPPRESS)
    args = parser.parse_args()

    # coverage
    cov = None
    if args.with_coverage:
        import coverage
        cov = coverage.coverage(
            data_suffix=str(int(random.random() * 999999.0)),
            source=['databench'],
        )
        cov.start()

    # this is included here so that is included in coverage
    from .app import App

    # log
    if args.loglevel != 'WARNING':
        print('Setting loglevel to {}.'.format(args.loglevel))
    logging.basicConfig(level=getattr(logging, args.loglevel))

    logging.info('Python {}'.format(sys.version))
    logging.info('Databench {}'.format(DATABENCH_VERSION))
    logging.info('host={}, port={}'.format(args.host, args.port))

    # handle external signal to terminate nicely (used in tests)
    def sig_handler(signum, stack):
        print('exit program')
        if cov:
            cov.stop()
            cov.save()
        sys.exit(0)
    # signal.signal(signal.SIGTERM, sig_handler)
    # not supported on Windows:
    # if hasattr(signal, 'SIGUSR1'):
    #     signal.signal(signal.SIGUSR1, sig_handler)

    app = App().tornado_app(
        debug=args.loglevel not in ('WARNING', 'ERROR', 'CRITICAL')
    )
    app.listen(args.port, args.host)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
