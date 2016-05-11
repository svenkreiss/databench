from __future__ import absolute_import

from .dummypi.analysis import Dummypi
from .scaffold.analysis import Scaffold

analyses = [
    ('dummypi', Dummypi),
    ('scaffold', Scaffold),
]
