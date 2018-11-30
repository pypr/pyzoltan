PyZoltan: a Python wrapper for the Zoltan library
==================================================


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
- cyarray
- Cython
- mpi4py_
- Zoltan_


.. _mpi4py: http://mpi4py.scipy.org/

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
integration servers on Travis-CI_ and Shippable_.

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
