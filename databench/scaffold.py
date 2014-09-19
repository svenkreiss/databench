#!/usr/bin/env python

"""Command line tool to scaffold a new analysis environment."""

import os
import argparse
from databench.analyses_packaged.scaffold.analysis \
    import __file__ as analysis_src_file


def check_folders(name):
    """Only checks and asks questions. Nothing is written to disk."""

    if os.getcwd().endswith('analyses'):
        correct = raw_input('You are in an analyses folder. This will create '
                            'another analyses folder inside this one. Do '
                            'you want to continue? (y/N)')
        if correct != 'y':
            return False

    if not os.path.exists(os.getcwd()+'/analyses'):
        correct = raw_input('This is the first analysis here. Do '
                            'you want to continue? (y/N)')
        if correct != 'y':
            return False

    if os.path.exists(os.getcwd()+'/analyses/'+name):
        correct = raw_input('An analysis with this name exists already. Do '
                            'you want to continue? (y/N)')
        if correct != 'y':
            return False

    return True


def create_analyses(name, py_native):
    """If it does not exist already, it creates the top level analyses folder
    and it's __init__.py file."""

    if not os.path.exists(os.getcwd()+'/analyses'):
        os.system("mkdir analyses")

    if not os.path.exists(os.getcwd()+'/analyses/__init__.py'):
        with open('analyses/__init__.py', 'w') as f:
            f.write('"""Analyses folder created by `scaffold-databench`. '
                    'Modify me.\n\nSources: '
                    '[github.com/username/project]'
                    '(http://github.com/username/project)"""\n\n')
            f.write('__version__ = "0.0.1"\n')
            f.write('__author__ = "Change Me Please <change@meplease.com>"\n')
            f.write('\n')

    if py_native:
        with open('analyses/__init__.py', 'r') as f:
            existing = f.readlines()
        if 'import '+name+'.analysis\n' in existing:
            print 'WARNING: analysis is already imported in __init__.py.'
        else:
            with open('analyses/__init__.py', 'a') as fa:
                fa.write('import '+name+'.analysis\n')


def copy_scaffold_file(src, dest, name):
    if os.path.exists(dest):
        print 'WARNING: file '+dest+' exists alread. Skipping.'
        return

    with open(src, 'r') as f:
        lines = f.readlines()

    if not lines:
        print 'FATAL: source '+src+' is empty.'
        raise

    # replace
    lines = [l.replace('scaffold', name) for l in lines]
    lines = [l.replace('Scaffold', name.title()) for l in lines]

    with open(dest, 'w') as f:
        for l in lines:
            f.write(l)


def create_analysis(name, py_native):
    """Create analysis files."""

    # analysis folder
    folder = os.getcwd()+'/analyses/'+name
    if not os.path.exists(folder):
        os.system('mkdir '+folder)
    else:
        print 'WARNING: analysis folder '+folder+' already exists.'

    # __init__.py
    if py_native:
        os.system('touch '+folder+'/__init__.py')

    # copy all other files
    for f in ['analysis.py', 'index.html', 'README.md', 'thumbnail.png']:
        src = analysis_src_file.replace('analysis.pyc', f)
        copy_scaffold_file(src, folder+'/'+f, name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('analysis_name',
                        help='Name of the analysis to be created.')
    args = parser.parse_args()

    if not check_folders(args.analysis_name):
        return

    py_native = args.analysis_name.split('_')[-1] not in [
        'py', 'pyspark', 'spark', 'go', 'lua', 'julia', 'r'
    ]

    create_analyses(args.analysis_name, py_native)
    create_analysis(args.analysis_name, py_native)
    print("Done.")


if __name__ == "__main__":
    main()
