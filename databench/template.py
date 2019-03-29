import logging
import os
import tornado.template


class Loader(tornado.template.BaseLoader):
    """Template Loader from a list of base directories.

    First match is used.
    """
    def __init__(self, root_directories, **kwargs):
        super(Loader, self).__init__(**kwargs)
        self.roots = [os.path.abspath(root_directory)
                      for root_directory in root_directories]

    def resolve_path(self, name, parent_path=None):
        logging.error('name %s, p %s', name, parent_path)
        for root in self.roots:
            logging.error('root %s', root)
            if parent_path and \
               not parent_path.startswith('<') and \
               not parent_path.startswith('/') and \
               not name.startswith('/') and \
               name[1:3] != ':\':
                logging.error('mergeing %s %s', root, parent_path)
                root = os.path.join(root, parent_path)
            path = os.path.join(root, name)
            if os.path.exists(path):
                logging.error('path %s', path)
                return path
        logging.error('name %s', name)
        return name

    def _create_template(self, name):
        logging.error('before open %s', name)
        with open(name, 'rb') as f:
            template = tornado.template.Template(
                f.read(), name=name, loader=self)
            return template
