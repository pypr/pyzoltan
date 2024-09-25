# cython: language_level=3, embedsignature=True
# distutils: language=c++

"""Wrapper for the Zoltan Distributed Directory and routines"""
cimport mpi4py.MPI as mpi
if MPI4PY_V2:
   from mpi4py.libmpi cimport MPI_Comm
else:
   from mpi4py.mpi_c cimport MPI_Comm

from cyarray.carray cimport UIntArray, IntArray

from pyzoltan.czoltan.czoltan_dd cimport *
from pyzoltan.czoltan.czoltan_types cimport ZOLTAN_ID_TYPE, ZOLTAN_ID_PTR


cdef class Zoltan_DD:
    # Pointer to the Zoltan DD
    cdef Zoltan_DD_Directory* dd

    # MPI communicator
    cdef MPI_Comm comm
