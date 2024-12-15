'''Setup script for PyZoltan.

You can use some environment variables to control the build. Setting CC/CXX
will let you choose a custom compiler (these can also be set in the config file
discussed below). You can also export ZOLTAN or ZOLTAN_INCLUDE/ZOLTAN_LIBRARY.

These are more configuration file options that trump everything. The file is in
~/.compyle/config.py.  The options are:

# MPI options: handy on clusters like a Cray.
MPI_CFLAGS = ['...']  # must be a list.
MPI_LINK = ['...']

# Zoltan options
USE_TRILINOS = 1  # When set to anything, use "-ltrilinos_zoltan".
ZOLTAN = '/path/to_zoltan'  # looks inside this for $ZOLTAN/include/, lib/

# Not needed if using ZOLTAN
ZOLTAN_INCLUDE = 'path/include'  # path to zoltan.h
ZOLTAN_LIBRARY = 'path/lib'  # path to libzoltan.a

'''

import os
from subprocess import check_output
import sys


# This is taken from compyle.ext_module.
def get_config_file_opts():
    '''A global configuration file is used to configure build options
    for compyle and other packages.  This is located in:

    ~/.compyle/config.py

    The file can contain arbitrary Python that is exec'd. The variables defined
    here specify the compile and link args. For example, one may set:

    OMP_CFLAGS = ['-fopenmp']
    OMP_LINK = ['-fopenmp']

    Will use these instead of the defaults that are automatically determined.
    These must be lists.

    '''
    fname = os.path.expanduser(os.path.join('~', '.compyle', 'config.py'))
    opts = {}
    if os.path.exists(fname):
        print('Reading configuration options from %s.' % fname)
        with open(fname) as fp:
            exec(compile(fp.read(), fname, 'exec'), opts)
        opts.pop('__builtins__', None)
    return opts


# NOTE: the configuration options in the file trump everything else!
# These are options from the .compyle/config.py
CONFIG_OPTS = get_config_file_opts()


if len(os.environ.get('COVERAGE', '')) > 0:
    MACROS = [("CYTHON_TRACE", "1"), ("CYTHON_TRACE_NOGIL", "1")]
    COMPILER_DIRECTIVES = {"linetrace": True}
    print("-" * 80)
    print("Enabling linetracing for cython and setting CYTHON_TRACE = 1")
    print("-" * 80)
else:
    MACROS = []
    COMPILER_DIRECTIVES = {}

MODE = 'normal'
if len(sys.argv) >= 2 and \
   ('--help' in sys.argv[1:] or
    sys.argv[1] in ('--help-commands', 'egg_info', '--version',
                    'clean', 'sdist')):
    MODE = 'info'

HAVE_MPI = True
USE_ZOLTAN = True
try:
    import mpi4py
except ImportError:
    HAVE_MPI = False

compiler = 'gcc'
# compiler = 'mpich'
# compiler = 'intel'
if compiler == 'intel':
    extra_compile_args = ['-O3']
else:
    extra_compile_args = []


def get_deps(*args):
    """Given a list of basenames, this checks if a .pyx or .pxd exists
    and returns the list.
    """
    result = []
    for basename in args:
        for ext in ('.pyx', '.pxd'):
            f = basename + ext
            if os.path.exists(f):
                result.append(f)
    return result


def get_zoltan_directory(varname):
    global USE_ZOLTAN
    if varname in CONFIG_OPTS:
        return os.path.expanduser(CONFIG_OPTS[varname])

    d = os.environ.get(varname, '')
    if len(d) == 0:
        USE_ZOLTAN = False
        return ''
    else:
        USE_ZOLTAN = True
    if not os.path.exists(d):
        print("*" * 80)
        print("%s incorrectly set to %s, not using ZOLTAN!" % (varname, d))
        print("*" * 80)
        USE_ZOLTAN = False
        return ''
    return d


def get_mpi_flags():
    """Returns mpi_inc_dirs, mpi_compile_args, mpi_link_args.
    """
    global HAVE_MPI
    mpi_inc_dirs = []
    mpi_compile_args = []
    mpi_link_args = []
    if not HAVE_MPI:
        return mpi_inc_dirs, mpi_compile_args, mpi_link_args
    elif 'MPI_CFLAGS' in CONFIG_OPTS:
        mpi_compile_args = CONFIG_OPTS['MPI_CFLAGS']
        mpi_link_args = CONFIG_OPTS['MPI_LINK']
        mpi_inc_dirs.append(mpi4py.get_include())
    else:
        try:
            mpic = 'mpic++'
            if compiler == 'intel':
                link_args = check_output(
                    [mpic, '-cc=icc', '-link_info'],
                    universal_newlines=True
                ).strip()
                link_args = link_args[3:]
                compile_args = check_output(
                    [mpic, '-cc=icc', '-compile_info'],
                    universal_newlines=True
                ).strip()
                compile_args = compile_args[3:]
            elif compiler == 'mpich':
                link_args = check_output(
                    [mpic, '-link-info'],
                    universal_newlines=True
                ).strip()
                link_args = " ".join(link_args.split()[1:])
                compile_args = check_output(
                    [mpic, '-compile_info'],
                    universal_newlines=True
                ).strip()
                compile_args = " ".join(compile_args.split()[1:])
            else:
                link_args = check_output(
                    [mpic, '--showme:link'],
                    universal_newlines=True
                ).strip()
                compile_args = check_output(
                    [mpic, '--showme:compile'],
                    universal_newlines=True
                ).strip()
        except:  # noqa: E722
            print('-' * 80)
            print("Unable to run mpic++ correctly, skipping parallel build")
            print('-' * 80)
            HAVE_MPI = False
        else:
            mpi_link_args.extend(link_args.split())
            mpi_compile_args.extend(compile_args.split())
            mpi_inc_dirs.append(mpi4py.get_include())

    return mpi_inc_dirs, mpi_compile_args, mpi_link_args


def get_zoltan_args():
    """Returns zoltan_include_dirs, zoltan_library_dirs
    """
    global HAVE_MPI, USE_ZOLTAN
    zoltan_include_dirs, zoltan_library_dirs = [], []
    if not HAVE_MPI:
        return zoltan_include_dirs, zoltan_library_dirs
    # First try with the environment variable 'ZOLTAN'
    zoltan_base = get_zoltan_directory('ZOLTAN')
    inc = lib = ''
    if len(zoltan_base) > 0:
        inc = os.path.join(zoltan_base, 'include')
        lib = os.path.join(zoltan_base, 'lib')
        if not os.path.exists(inc) or not os.path.exists(lib):
            inc = lib = ''

    # try with the older ZOLTAN include directories
    if len(inc) == 0 or len(lib) == 0:
        inc = get_zoltan_directory('ZOLTAN_INCLUDE')
        lib = get_zoltan_directory('ZOLTAN_LIBRARY')

    if not USE_ZOLTAN:
        # Try with default in sys.prefix/{include,lib}, this is what is done
        # by any conda installs of zoltan.
        inc = os.path.join(sys.prefix, 'include')
        lib = os.path.join(sys.prefix, 'lib')
        if os.path.exists(os.path.join(inc, 'zoltan.h')):
            USE_ZOLTAN = True

    if (not USE_ZOLTAN):
        print("*" * 80)
        print("Zoltan Environment variable not set, not using ZOLTAN!")
        print("*" * 80)
        HAVE_MPI = False
    else:
        print('-' * 70)
        print("Using Zoltan from:\n%s\n%s" % (inc, lib))
        print('-' * 70)
        zoltan_include_dirs = [inc]
        zoltan_library_dirs = [lib]

        # PyZoltan includes
        zoltan_cython_include = [os.path.abspath('./pyzoltan/czoltan')]
        zoltan_include_dirs += zoltan_cython_include

    # Not sure we need this but doing so just to be safe.
    import cyarray
    cyarray_include_dirs = [os.path.abspath(os.path.dirname(cyarray.__file__))]
    zoltan_include_dirs += cyarray_include_dirs

    return zoltan_include_dirs, zoltan_library_dirs


def get_parallel_extensions():
    if not HAVE_MPI:
        return []

    if MODE == 'info':
        from distutils.core import Extension
        include_dirs = []
        mpi_inc_dirs, mpi_compile_args, mpi_link_args = [], [], []
        zoltan_include_dirs, zoltan_library_dirs = [], []
    else:
        from Cython.Distutils import Extension
        import numpy
        include_dirs = [numpy.get_include()]
        mpi_inc_dirs, mpi_compile_args, mpi_link_args = get_mpi_flags()
        zoltan_include_dirs, zoltan_library_dirs = get_zoltan_args()

    # We should check again here as HAVE_MPI may be set to False when we try to
    # get the MPI flags and are not successful.
    if not HAVE_MPI:
        return []

    MPI4PY_V2 = False if mpi4py.__version__.startswith('1.') else True
    cython_compile_time_env = {'MPI4PY_V2': MPI4PY_V2}

    zoltan_lib = 'zoltan'
    if 'USE_TRILINOS' in CONFIG_OPTS:
        zoltan_lib = 'trilinos_zoltan'
    elif os.environ.get('USE_TRILINOS', None) is not None:
        zoltan_lib = 'trilinos_zoltan'

    zoltan_modules = [
        Extension(
            name="pyzoltan.core.zoltan",
            sources=["pyzoltan/core/zoltan.pyx"],
            depends=get_deps(
                "pyzoltan/czoltan/czoltan",
                "pyzoltan/czoltan/czoltan_types",
            ),
            include_dirs=include_dirs + zoltan_include_dirs + mpi_inc_dirs,
            library_dirs=zoltan_library_dirs,
            libraries=[zoltan_lib, 'mpi'],
            extra_link_args=mpi_link_args,
            extra_compile_args=mpi_compile_args + extra_compile_args,
            cython_compile_time_env=cython_compile_time_env,
            define_macros=MACROS,
        ),

        Extension(
            name="pyzoltan.core.zoltan_dd",
            sources=["pyzoltan/core/zoltan_dd.pyx"],
            depends=get_deps(
                "pyzoltan/core/carray",
                "pyzoltan/czoltan/czoltan_dd",
                "pyzoltan/czoltan/czoltan_types"
            ),
            include_dirs=include_dirs + zoltan_include_dirs + mpi_inc_dirs,
            library_dirs=zoltan_library_dirs,
            libraries=[zoltan_lib, 'mpi'],
            extra_link_args=mpi_link_args,
            extra_compile_args=mpi_compile_args + extra_compile_args,
            cython_compile_time_env=cython_compile_time_env,
            define_macros=MACROS,
        ),

        Extension(
            name="pyzoltan.core.zoltan_comm",
            sources=["pyzoltan/core/zoltan_comm.pyx"],
            depends=get_deps(
                "pyzoltan/core/carray",
                "pyzoltan/czoltan/zoltan_comm"
            ),
            include_dirs=include_dirs + zoltan_include_dirs + mpi_inc_dirs,
            library_dirs=zoltan_library_dirs,
            libraries=[zoltan_lib, 'mpi'],
            extra_link_args=mpi_link_args,
            extra_compile_args=mpi_compile_args + extra_compile_args,
            cython_compile_time_env=cython_compile_time_env,
            define_macros=MACROS,
        ),
    ]

    return zoltan_modules


def _is_cythonize_default():
    import warnings
    result = True
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            # old_build_ext was introduced in Cython 0.25 and this is when
            # cythonize was made the default.
            from Cython.Distutils import old_build_ext  # noqa: F401
        except ImportError:
            result = False
    return result


def setup_package():
    from setuptools import find_packages, setup
    if MODE == 'info':
        cmdclass = {}
    else:
        from Cython.Distutils import build_ext
        cmdclass = {'build_ext': build_ext}

    # Extract the version information from pysph/__init__.py
    info = {}
    module = os.path.join('pyzoltan', '__init__.py')
    exec(compile(open(module).read(), module, 'exec'), info)

    # The requirements.
    tests_require = ["pytest>=3.0"]
    docs_require = ["sphinx"]

    ext_modules = get_parallel_extensions()
    if MODE != 'info' and _is_cythonize_default():
        # Cython >= 0.25 uses cythonize to compile the extensions. This
        # requires the compile_time_env to be set explicitly to work.
        compile_env = {}
        include_path = set()
        if HAVE_MPI:
            MPI4PY_V2 = False if mpi4py.__version__.startswith('1.') else True
            compile_env.update({'MPI4PY_V2': MPI4PY_V2})

        for mod in ext_modules:
            compile_env.update(mod.cython_compile_time_env or {})
            include_path.update(mod.include_dirs)
        from Cython.Build import cythonize
        ext_modules = cythonize(
            ext_modules, compile_time_env=compile_env,
            include_path=list(include_path),
            compiler_directives=COMPILER_DIRECTIVES,
        )
        if len(ext_modules) == 0:
            raise RuntimeError(
                'There are no extension modules, Nothing to do!'
            )

    setup(name='PyZoltan',
          version=info['__version__'],
          author='PySPH Developers',
          author_email='pysph-dev@googlegroups.com',
          description='Wrapper for the Zoltan data management library',
          long_description=open('README.rst').read(),
          url='http://github.com/pypr/pyzoltan',
          license="BSD",
          keywords="Cython Zoltan Dynamic load balancing",
          packages=find_packages(),
          package_data={
              '': ['*.pxd', '*.rst', '*.txt'],
              'pyzoltan.core.tests': ['mesh.txt'],
          },
          # exclude package data in installation.
          exclude_package_data={
              '': ['Makefile', '*.bat', '*.cfg', '*.rst', '*.sh', '*.yml'],
          },
          ext_modules=ext_modules,
          include_package_data=True,
          cmdclass=cmdclass,
          extras_require={
              "docs": docs_require,
              "tests": tests_require,
              "dev": docs_require + tests_require,
          },
          zip_safe=False,
          platforms=['Linux', 'Mac OS-X', 'Unix', 'Windows'],
          classifiers=[c.strip() for c in """\
            Development Status :: 5 - Production/Stable
            Environment :: Console
            Intended Audience :: Developers
            Intended Audience :: Science/Research
            License :: OSI Approved :: BSD License
            Natural Language :: English
            Operating System :: MacOS :: MacOS X
            Operating System :: Microsoft :: Windows
            Operating System :: POSIX
            Operating System :: Unix
            Programming Language :: Python
            Programming Language :: Python :: 3
            Topic :: Scientific/Engineering
            Topic :: Scientific/Engineering :: Physics
            Topic :: Software Development :: Libraries
            """.splitlines() if len(c.split()) > 0],
          )


if __name__ == '__main__':
    setup_package()
