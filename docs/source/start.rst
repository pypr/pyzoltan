==============================
Getting started with PyZoltan
==============================


PyZoltan is as the name suggests, is a Python wrapper for the Zoltan_
data management library.

In PyZoltan, we wrap the specific routines and objects that we wish to
use. The following features of Zoltan are currently supported:

- Dynamic load balancing using geometric algorithms
- Unstructured point-to-point communication
- Distributed data directories

.. _Zoltan: http://www.cs.sandia.gov/Zoltan/

Installation
-------------

PyZoltan requires the following:

- numpy
- cyarray_
- Cython_
- mpi4py_
- Zoltan_


.. _mpi4py: http://mpi4py.scipy.org/
.. _Cython: https://cython.org
.. _cyarray: https://github.com/pypr/cyarray

These dependencies can be installed using pip::

  $ pip install -r requirements.txt

Once this is installed one can install PyZoltan as follows::

  $ pip install pyzoltan

or via the usual ``setup.py`` method::

  $ python setup.py install # or develop


Building and linking PyZoltan on OSX/Linux
-------------------------------------------

We've provided a simple Zoltan build script in the repository.  This works on
Linux and OS X but not on Windows.  It can be used as::

    $ ./build_zoltan.sh INSTALL_PREFIX

where the ``INSTALL_PREFIX`` is where the library and includes will be
installed.  You may edit and tweak the build to suit your installation.
However, this script is what we use to build Zoltan on our continuous
integration servers.

After Zoltan is build, set the environment variable ``ZOLTAN`` to point to the
``INSTALL_PREFIX`` that you used above::

    $ export ZOLTAN=$INSTALL_PREFIX

Note that replace ``$INSTALL_PREFIX`` with the directory you specified above.
After this, follow the instructions to build PySPH. The PyZoltan wrappers will
be compiled and available.

.. note::

    The installation will use ``$ZOLTAN/include`` and ``$ZOLTAN/lib`` to find
    the actual directories, if these do not work for your particular
    installation for whatever reason, set the environment variables
    ``ZOLTAN_INCLUDE`` and ``ZOLTAN_LIBRARY`` explicitly without setting up
    ``ZOLTAN``. If you used the above script, this would be::

        $ export ZOLTAN_INCLUDE=$INSTALL_PREFIX/include
        $ export ZOLTAN_LIBRARY=$INSTALL_PREFIX/lib


Installing mpi4py and Zoltan on OS X
--------------------------------------


In order to build/install mpi4py_ one first has to install the MPI library.
This is easily done with Homebrew_ as follows (you need to have ``brew``
installed for this but that is relatively easy to do)::

    $ sudo brew install open-mpi

After this is done, one can install mpi4py by hand.  First download mpi4py
from `here <https://pypi.python.org/pypi/mpi4py>`_. Then run the following
(modify these to suit your XCode installation and version of mpi4py)::

    $ cd /tmp
    $ tar xvzf ~/Downloads/mpi4py-1.3.1.tar.gz
    $ cd mpi4py-1.3.1
    $ export MACOSX_DEPLOYMENT_TARGET=10.7
    $ export SDKROOT=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.7.sdk/
    $ python setup.py install

Change the above environment variables to suite your SDK version. If this
installs correctly, mpi4py should be available. You can now build Zoltan, (the
script to do this is in the pyzoltan sources) ::

    $ cd pyzoltan
    $ ./build_zoltan.sh ~/zoltan # Replace ~/zoltan with what you want
    $ export ZOLTAN=~/zoltan

You should be set now and should be able to build/install pyzoltan as::

  $ python setup.py install
  # or
  $ python setup.py develop

.. _Homebrew: http://brew.sh/
