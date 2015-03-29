#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def getpath(filepath = None):
    """Get absolute filepath from string or iterable."""

    import os

    here = os.path.abspath(os.path.dirname(__file__))

    if not filepath:
        return here
    elif isinstance(filepath, basestring):
        return os.path.join(here, filepath)
    elif isinstance(filepath, (tuple, list)):
        return os.path.join(here, os.path.sep.join(filepath))
    else:
        raise RuntimeError("Invalid filepath given")

def install():
    """Setuptools based installation script."""

    import setuptools
    import setuptools.command.install

    class NemoaCustomInstall(setuptools.command.install.install):
        """Customized setuptools install command."""

        def run(self):
            setuptools.command.install.install.run(self)

            # run post installation script
            import subprocess
            import sys

            subprocess.call([sys.executable, __file__, 'postinstall'])

    def getfile(filepath = None):
        """Get the content from a file."""

        import codecs

        path = getpath(filepath)

        with codecs.open(path, encoding = 'utf-8') as file_handler:
            content = file_handler.read()

        return content

    def getvars(filepath = None):
        """Get all __VARIABLE__ from given file."""

        import io
        import re

        # get file content
        path = getpath(filepath)
        with io.open(path, encoding = 'utf8') as file_handler:
            content = file_handler.read()

        # parse variables with regular expressions
        key_regex = """__([a-zA-Z][a-zA-Z0-9]*)__"""
        val_regex = """['\"]([^'\"]*)['\"]"""
        regex = r"^[ ]*%s[ ]*=[ ]*%s" % (key_regex, val_regex)
        variables = {}
        for match in re.finditer(regex, content, re.M):
            key = str(match.group(1))
            val = str(match.group(2))
            variables[key] = val

        return variables

    pkg = {
        'name': 'qdeep',
        'descfile': 'DESCRIPTION.rst',
        'libdir': 'lib',
        'keywords': 'nemoa dataanalysis classification dbn rbm',
        'install_requires': [
            'nemoa',
            'pyside',
            'pyqtgraph'],
        'extras_require': {},
        'classifiers': [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering',
            'Operating System :: OS Independent',
            'License :: OSI Approved :: GPLv3',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4' ],
        'entry_points': {
            'gui_scripts' : ['qdeep = qdeep:main']}
        }

    # prepare dynamic package variables
    srcfile = (pkg['libdir'], pkg['name'], '__init__.py')
    for key, val in getvars(srcfile).items(): pkg[key] = val
    pkg['long_description'] = getfile(pkg['descfile'])
    pkg['package_dir'] = { '': pkg['libdir'] }
    pkg['cmdclass'] = { 'install': NemoaCustomInstall }
    pkg['packages'] = setuptools.find_packages(pkg['libdir'])

    # install nemoa lib
    setuptools.setup(
        name             = pkg['name'],
        version          = pkg['version'],
        description      = pkg['description'],
        url              = pkg['url'],
        author           = pkg['author'],
        author_email     = pkg['email'],
        license          = pkg['license'],
        keywords         = pkg['keywords'],
        package_dir      = pkg['package_dir'],
        packages         = pkg['packages'],
        classifiers      = pkg['classifiers'],
        long_description = pkg['long_description'],
        install_requires = pkg['install_requires'],
        extras_require   = pkg['extras_require'],
        entry_points     = pkg['entry_points'],
        cmdclass         = pkg['cmdclass'],
        zip_safe         = True,
        include_package_data = True )

def postinstall():
    """Post installation script."""

    import appdirs

    def copytree(src, tgt):

        import glob
        import os
        import shutil

        print('copying %s -> %s' % (src, tgt))

        for srcsdir in glob.glob(os.path.join(src, '*')):
            tgtsdir = os.path.join(tgt, os.path.basename(srcsdir))

            if os.path.exists(tgtsdir):
                shutil.rmtree(tgtsdir)

            try:
                shutil.copytree(srcsdir, tgtsdir)

            # directories are the same
            except shutil.Error as e:
                print('directory not copied. Error: %s' % e)

            # any error saying that the directory doesn't exist
            except OSError as e:
                print('directory not copied. Error: %s' % e)

        return True

    print('running postinstall')

    # copy application data
    site_src_base = getpath('data')
    site_tgt_base = appdirs.site_data_dir(
        appname = 'nemoa', appauthor = 'Froot')
    site_tgt_base = getpath(site_tgt_base)
    copytree(site_src_base, site_tgt_base)

if __name__ == '__main__':

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'postinstall':
        postinstall()
    else:
        install()
