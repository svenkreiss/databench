from __future__ import unicode_literals

import os
import fnmatch
import logging

# utilities
try:
    from markdown import markdown
except ImportError:
    markdown = None

try:
    from docutils.core import publish_parts as rst
except ImportError:
    rst = None

log = logging.getLogger(__name__)


class Readme(object):
    def __init__(self, directory):
        self.directory = directory

        self._text = None
        self._meta = None

    def _read(self):
        self._meta = {}
        self._text = ''

        if not os.path.exists(self.directory):
            return
        readme_file = [os.path.join(self.directory, n)
                       for n in os.listdir(self.directory)
                       if fnmatch.fnmatch(n.lower(), 'readme.*')]
        readme_file = readme_file[0] if readme_file else None
        log.debug('Readme file name: {}'.format(readme_file))
        if not readme_file:
            return

        with open(readme_file, 'r') as f:
            self._text = f.read()

        if readme_file.lower().endswith('.md'):
            self.extract_md_meta()

            if markdown is not None:
                self._text = markdown(self._text)
            else:
                self._text = (
                    '<p>Install markdown with <b>pip install markdown</b>'
                    ' to render this readme file.</p>'
                ) + self._text

        if readme_file.lower().endswith('.rst'):
            self.extract_rst_meta(self._text)
            if rst is not None:
                self._text = rst(self._text, writer_name='html')['html_body']
            else:
                self._text = (
                    '<p>Install rst rendering with <b>pip install docutils</b>'
                    ' to render this readme file.</p>'
                ) + self._text

    @property
    def text(self):
        if self._text is None:
            self._read()

        return self._text

    @property
    def meta(self):
        if self._text is None:
            self._read()

        return self._meta

    def extract_md_meta(self):
        """
        Searches for lines like:

        <!--
        Title: MyTitle
        Description: hello bla
        logo_url: /path/to/logo.png
        build: gulp
        -->
        """
        possible_fields = ['title', 'description', 'logo_url', 'build', 'watch']

        for l in self._text.split('\n'):
            if ': ' not in l:
                continue

            p = l.partition(': ')
            if p[0].lower() not in possible_fields:
                continue

            self._meta[p[0].lower()] = p[2]

        return self

    def extract_rst_meta(self):
        """
        Searches for lines like:

        .. title: MyTitle
        .. description: hello bla
        .. logo_url: /path/to/logo.png
        .. build: gulp
        """
        possible_fields = ['title', 'description', 'logo_url', 'build', 'watch']

        for l in self._text.split('\n'):
            if not l.startswith('..') or ': ' not in l:
                continue

            # remove the leading '.. '
            l = l[3:]

            p = l.partition(': ')
            if p[0].lower() not in possible_fields:
                continue

            self._meta[p[0].lower()] = p[2]

        return self