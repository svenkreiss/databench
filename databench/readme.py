from __future__ import unicode_literals

import fnmatch
import io
import logging
import os
import re
import tornado.autoreload

# utilities
try:
    from markdown import markdown
except ImportError:  # pragma: no cover
    markdown = None  # pragma: no cover

try:
    from docutils.core import publish_parts as rst
except ImportError:  # pragma: no cover
    rst = None  # pragma: no cover

log = logging.getLogger(__name__)


class Readme(object):
    """Readme reader and meta data extractor.

    Supports markdown (``.md``) and restructured text (``.rst``).

    :param directory:
        Path to a directory containing a readme file.

    :param bool watch:
        Whether to watch for changes in the readme file.
    """
    def __init__(self, directory, watch=True):
        self.directory = directory

        self._text = None
        self._html = None
        self.watch = watch

    def _read(self, encoding='utf8', encoding_errors='ignore'):
        self._text = ''
        self._html = ''

        if not os.path.exists(self.directory):
            return
        readme_file = [os.path.join(self.directory, n)
                       for n in os.listdir(self.directory)
                       if fnmatch.fnmatch(n.lower(), 'readme.*')]
        readme_file = readme_file[0] if readme_file else None
        if not readme_file:
            return

        log.debug('Readme file name: {}'.format(readme_file))
        if self.watch:
            tornado.autoreload.watch(readme_file)

        with io.open(readme_file, 'r',
                     encoding=encoding, errors=encoding_errors) as f:
            self._text = f.read()

        if readme_file.lower().endswith('.md'):
            if markdown is not None:
                self._html = markdown(self._text)

                # remove first html comment
                self._text = re.sub('<!\-\-.*\-\->', '', self._text,
                                    count=1, flags=re.DOTALL)
            else:
                self._html = (
                    '<p>Install markdown with <b>pip install markdown</b>'
                    ' to render this readme file.</p>'
                ) + self._text  # pragma: no cover

        if readme_file.lower().endswith('.rst'):
            if rst is not None:
                self._html = rst(self._text,
                                 writer_name='html')['html_body']
            else:
                self._html = (
                    '<p>Install rst rendering with <b>pip install docutils</b>'
                    ' to render this readme file.</p>'
                ) + self._text  # pragma: no cover

    @property
    def text(self):
        if self._text is None:
            self._read()

        return self._text

    @property
    def html(self):
        if self._html is None:
            self._read()

        return self._html
