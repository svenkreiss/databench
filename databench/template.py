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
        print(name, parent_path)
        for root in self.roots:
            print('root', root)
            if parent_path and \
               not parent_path.startswith('<') and \
               not parent_path.startswith('/') and \
               not name.startswith('/'):
                root = os.path.join(root, parent_path)
            path = os.path.join(root, name)
            if os.path.exists(path):
                print('path', path)
                return path
        print('name', name)
        return name

    def _create_template(self, name):
        print('before open', name)
        with open(name, 'rb') as f:
            template = tornado.template.Template(
                f.read(), name=name, loader=self)
            return template
