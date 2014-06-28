"""Databench module."""

__version__ = "0.2.10"

# Need to make sure monkey.patch_all() is applied before any 'import threading',
# but cannot raise error because building the Sphinx documentation also suffers
# from this problem, but there it can be ignored.
import sys
if 'threading' in sys.modules:
    print 'WARNING: The threading module needs to be patched before use. ' \
          'Do "import databench" before any "import threading".'
import gevent.monkey; gevent.monkey.patch_all()

from databench.analysis import LIST_ALL, Analysis
from databench.signals import Signals
from databench.app import run
