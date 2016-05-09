#!/usr/bin/env python

"""Command line tool to scaffold a new analysis environment."""

import argparse
import os
import shutil

# for Python 2 compatibility
try:
    input = raw_input
except NameError:
    pass


def check_folders(name):
    """Only checks and asks questions. Nothing is written to disk."""

    if os.getcwd().endswith('analyses'):
        correct = input('You are in an analyses folder. This will create '
                        'another analyses folder inside this one. Do '
                        'you want to continue? (y/N)')
        if correct != 'y':
            return False

    if not os.path.exists(os.getcwd() + '/analyses'):
        correct = input('This is the first analysis here. Do '
                        'you want to continue? (y/N)')
        if correct != 'y':
            return False

    if os.path.exists(os.getcwd() + '/analyses/' + name):
        correct = input('An analysis with this name exists already. Do '
                        'you want to continue? (y/N)')
        if correct != 'y':
            return False

    return True


def create_analyses(name, suffix):
    """Create an analysis with given name and suffix.

    If it does not exist already, it creates the top level analyses folder
    and it's __init__.py file.
    """

    if not os.path.exists(os.getcwd() + '/analyses'):
        os.system("mkdir analyses")

    if not os.path.exists(os.getcwd() + '/analyses/__init__.py'):
        with open('analyses/__init__.py', 'w') as f:
            f.write("'''Automatically created by `scaffold-databench`.'''\n\n")
            f.write("__version__ = '0.1.0'\n")
            f.write("\n")

    if not suffix:
        with open('analyses/__init__.py', 'r') as f:
            existing = f.readlines()
        if 'from .{} import analysis as {}_a\n'.format(name, name) in existing:
            print('WARNING: analysis is already imported in __init__.py.')
        else:
            with open('analyses/__init__.py', 'a') as fa:
                fa.write('from .{} import analysis as {}_a\n'
                         ''.format(name, name))


def copy_scaffold_file(src, dest, name):
    if os.path.exists(dest):
        print('WARNING: file {} exists alread. Skipping.'.format(dest))
        return

    # binary copy for unknown file endings
    if not any(src.endswith(e) for e in ('.py', '.html', '.md', '.rst')):
        print('binary copy {} to {}'.format(src, dest))
        shutil.copyfile(src, dest)
        return

    print('copy {} to {}'.format(src, dest))
    with open(src, 'r') as f:
        lines = f.readlines()

    if not lines:
        print('FATAL: source {} is empty.'.format(src))
        raise

    # scaffold name
    scaffold_name = src.rsplit('/', 2)[-2]

    # replace
    lines = [l.replace(scaffold_name, name) for l in lines]
    lines = [l.replace(scaffold_name.title(), name.title()) for l in lines]

    with open(dest, 'w') as f:
        for l in lines:
            f.write(l)


def create_analysis(name, suffix, src_dir):
    """Create analysis files."""

    # analysis folder
    folder = os.getcwd() + '/analyses/' + name
    if not os.path.exists(folder):
        os.makedirs(folder)
    else:
        print('WARNING: analysis folder {} already exists.'.format(folder))

    # __init__.py
    if not suffix:
        os.system('touch {}/__init__.py'.format(folder))

    # copy all other files
    for f in ['analysis.py', 'index.html', 'README.md', 'thumbnail.png']:
        copy_scaffold_file(os.path.join(src_dir, f),
                           os.path.join(folder, f),
                           name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('analysis_name',
                        help='Name of the analysis to be created.')
    parser.add_argument('-y', dest='yes', default=False, action='store_true',
                        help='Answer all questions with yes. Be careful.')
    args = parser.parse_args()

    if not (args.yes or check_folders(args.analysis_name)):
        return

    suffix = args.analysis_name.split('_')[-1]
    if suffix not in ['py', 'pyspark', 'spark', 'go', 'lua', 'julia', 'r']:
        suffix = None

    # sanitize analysis name
    if '-' in args.analysis_name:
        print('Analysis names with dashes are not supported '
              '(because they are not supported in Python module names). '
              'Abort.')
        return

    # this is a hack to obtain the src directory
    import databench.analyses_packaged.scaffold.analysis
    src_file = databench.analyses_packaged.scaffold.analysis.__file__
    src_dir = src_file[:src_file.rfind('/')]

    if suffix in ['py', 'pyspark']:
        src_dir += '_py'

    create_analyses(args.analysis_name, suffix)
    create_analysis(args.analysis_name, suffix, src_dir)
    print("Done.")


if __name__ == "__main__":
    main()
