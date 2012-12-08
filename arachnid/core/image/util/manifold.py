# This file was automatically generated by SWIG (http://www.swig.org).
# Version 1.3.31
#
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import _manifold
import new
new_instancemethod = new.instancemethod
try:
    _swig_property = property
except NameError:
    pass # Python < 2.2 doesn't have 'property'.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'PySwigObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static) or hasattr(self,name):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types




def select_subset_csr(*args):
  """
    This SWIG wrapper function selects a subset of rows 
    	(and columns) from a CSR sparse matrix.

    	:Parameters:

    	data : array
    		   In/out 1D array of distances
    	col_ind :array
    		 	 In/out 1D array column indicies
    	row_ptr : array
    		   	  In/out 1D array row pointers
    	selected : array
    			   Input 1D array of selected rows
    	
    	:Returns:
    	
    	n : int
    		Number of sparse elements
    	
    """
  return _manifold.select_subset_csr(*args)

def self_tuning_gaussian_kernel_csr(*args):
  """
    This SWIG wrapper function calculates a self-tuning gaussin kernel over
    	a sparse matrix in CSR format.

    	:Parameters:

    	sdist : array
    		    Output 1D array of distances
    	data : array
    		   Input 1D array of distances
    	col_ind :array
    		 	 Input 1D array column indicies
    	row_ptr : array
    		   	  Input 1D array row pointers
    	
    """
  return _manifold.self_tuning_gaussian_kernel_csr(*args)

def normalize_csr(*args):
  """
    This SWIG wrapper function normalizes a sparse matrix in CSR format.

    	:Parameters:

    	sdist : array
    		    Output 1D array of distances
    	data : array
    		   Input 1D array of distances
    	col_ind :array
    		 	 Input 1D array column indicies
    	row_ptr : array
    		   	  Input 1D array row pointers
    	
    """
  return _manifold.normalize_csr(*args)

def push_to_heap(*args):
  """
    This SWIG wrapper function heaps sorts a partial distance matrix.

    	:Parameters:

    	dist2 : array
    		   Input 2D array of distances
    	data : array
    		   Output 1D array of distances
    	col_ind :array
    		 	 Output 1D array column indicies
    	offset : int
    			 Offset for the column index
    	k : int
    		Number of neighbors
    	
    """
  return _manifold.push_to_heap(*args)

def finalize_heap(*args):
  """
    This SWIG wrapper function creates a sparse matrix from a heap sorted
    	distance matrix.

    	:Parameters:

    	data : array
    		   Output 1D array of distances
    	col_ind :array
    		 	 Output 1D array column indicies
    	k : int
    		Number of neighbors
    	
    """
  return _manifold.finalize_heap(*args)

def knn_reduce(*args):
  """
    This SWIG wrapper function calculates a self-tuning gaussin kernel over
    	a sparse matrix in CSR format.

    	:Parameters:
    	
    	data : array
    		   Input 1D array of distances
    	col_ind :array
    		 	 Input 1D array column indicies
    	row_ind : array
    		   	  Input 1D array row indicies
    	sdata : array
    		   Output 1D array of distances
    	scol_ind :array
    		 	 Output 1D array column indicies
    	srow_ind : array
    		   	  Output 1D array row indicies
    	d : int
    		Difference between old and new number of neighbors
    	k : int
    		New number of neighbors
    	
    """
  return _manifold.knn_reduce(*args)

def knn_mutual(*args):
  """
    This SWIG wrapper function calculates a self-tuning gaussin kernel over
    	a sparse matrix in CSR format.

    	:Parameters:
    	
    	data : array
    		   In/out 1D array of distances
    	col_ind :array
    		 	 In/out 1D array column indicies
    	row_ind : array
    		   	  In/out 1D array row indicies
    	k : int
    		New number of neighbors
    	
    	:Returns:
    	
    	n : int
    		Number of sparse values
    	
    """
  return _manifold.knn_mutual(*args)
