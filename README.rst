PyZoltan: a Python wrapper for the Zoltan library
==================================================

|CI Status|  |Documentation Status|

.. |CI Status| image:: https://github.com/pypr/pyzoltan/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/pypr/pyzoltan/actions/workflows/tests.yml
.. |Documentation Status| image:: https://readthedocs.org/projects/pyzoltan/badge/?version=latest
    :target: https://pyzoltan.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

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

Zoltan itself needs to be already installed. We provide a convenient script
called ``build_zoltan.sh`` that can be used to build Zoltan.

Many of the other dependencies can be installed using pip or conda::

  $ pip install -r requirements.txt

Once this is installed one can install PyZoltan as follows::

  $ pip install pyzoltan

or via the usual ``setup.py`` method::

  $ python setup.py install # or develop


For more installation instructions, especially on how to build Zoltan and
PyZoltan, please see the documentation here: https://pyzoltan.readthedocs.io
