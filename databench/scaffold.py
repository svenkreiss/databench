"""Command line tool to scaffold a new analysis environment."""

import argparse
from future.builtins import input
import logging
import os
import shutil

log = logging.getLogger(__name__)


def check_folders(name):
    """Only checks and asks questions. Nothing is written to disk."""

    if os.getcwd().endswith('analyses'):
        correct = input('You are in an analyses folder. This will create '
                        'another analyses folder inside this one. Do '
                        'you want to continue? (y/N)')
        if correct != 'y':
            return False

    if not os.path.exists(os.path.join(os.getcwd(), 'analyses')):
        correct = input('This is the first analysis here. Do '
                        'you want to continue? (y/N)')
        if correct != 'y':
            return False

    if os.path.exists(os.path.join(os.getcwd(), 'analyses', name)):
        correct = input('An analysis with this name exists already. Do '
                        'you want to continue? (y/N)')
        if correct != 'y':
            return False

    return True


def create_analyses(name, kernel=None):
    """Create an analysis with given name and suffix.

    If it does not exist already, it creates the top level analyses folder
    and it's __init__.py and index.yaml file.
    """

    if not os.path.exists(os.path.join(os.getcwd(), 'analyses')):
        os.system("mkdir analyses")

    # __init__.py
    init_path = os.path.join(os.getcwd(), 'analyses', '__init__.py')
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            pass

    # index.yaml
    index_path = os.path.join(os.getcwd(), 'analyses', 'index.yaml')
    if not os.path.exists(index_path):
        with open(index_path, 'w') as f:
            f.write('title: Analyses\n')
            f.write('description: A short description.\n')
            f.write('version: 0.1.0\n')
            f.write('\n')
            f.write('analyses:\n')

    if kernel is None:
        with open(index_path, 'a') as f:
            f.write('  # automatically inserted by scaffold-databench\n')
            f.write('  - name: {}\n'.format(name))
            f.write('    title: {}\n'.format(name.title()))
            f.write('    description: A new analysis.\n')
            f.write('    watch:\n')
            f.write('      - {}/*.js\n'.format(name))
            f.write('      - {}/*.html\n'.format(name))


def copy_scaffold_file(src, dest, name, scaffold_name):
    if os.path.exists(dest):
        log.warning('File {} exists already. Skipping.'.format(dest))
        return

    # binary copy for unknown file endings
    if not any(src.endswith(e)
               for e in ('.py', '.js', '.html', '.md', '.rst')):
        log.info('Binary copy {} to {}.'.format(src, dest))
        shutil.copyfile(src, dest)
        return

    # text file copy
    log.info('Copy {} to {}.'.format(src, dest))
    with open(src, 'r') as f:
        lines = f.readlines()

    # replace
    lines = [l.replace(scaffold_name, name) for l in lines]
    lines = [l.replace(scaffold_name.title(), name.title()) for l in lines]

    with open(dest, 'w') as f:
        for l in lines:
            f.write(l)


def create_analysis(name, kernel, src_dir, scaffold_name):
    """Create analysis files."""

    # analysis folder
    folder = os.path.join(os.getcwd(), 'analyses', name)
    if not os.path.exists(folder):
        os.makedirs(folder)
    else:
        log.warning('Analysis folder {} already exists.'.format(folder))

    # copy all other files
    for f in os.listdir(src_dir):
        if f in ('__pycache__',) or \
           any(f.endswith(ending) for ending in ('.pyc',)):
            continue
        copy_scaffold_file(os.path.join(src_dir, f),
                           os.path.join(folder, f),
                           name, scaffold_name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name',
                        help='Name of the analysis to be created.')
    parser.add_argument('--kernel', default=None,
                        help='Language kernel.',
                        choices=('py', 'pypsark', 'go'))
    parser.add_argument('-y', dest='yes', default=False, action='store_true',
                        help='Answer all questions with yes. Be careful.')
    args = parser.parse_args()

    if not (args.yes or check_folders(args.name)):
        return

    # sanitize analysis name
    if '-' in args.name:
        parser.error('Analysis names with dashes are not supported '
                     '(because they are not supported in Python names). '
                     'Abort.')
        return

    # this is a hack to obtain the src directory
    import databench.analyses_packaged.scaffold
    src_dir = os.path.dirname(databench.analyses_packaged.__file__)

    if args.kernel in ('py', 'pyspark'):
        scaffold_name = 'scaffold_py'
    else:
        scaffold_name = 'scaffold'
    src_dir = os.path.join(src_dir, scaffold_name)

    create_analyses(args.name, args.kernel)
    create_analysis(args.name, args.kernel, src_dir, scaffold_name)
    log.info("Done.")
