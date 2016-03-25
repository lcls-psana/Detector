
#--------------------------------------------------------------------------
# File and Version Information:
#  $Id$
#
# Description:
#  file GlobalUtils.py
#------------------------------------------------------------------------

"""Contains Global Utilities

This software was developed for the SIT project.  If you use all or 
part of it, please give an appropriate acknowledgment.

@see RelatedModule

@version $Id$

@author Mikhail S. Dubrovin
"""

#------------------------------
#  Module's version from SVN --
#------------------------------
__version__ = "$Revision$"
# $Source$

#--------------------------------
#  Imports of standard modules --
#--------------------------------
import numpy as np

def print_ndarr(nda, name='', first=0, last=5) :
    if nda is None : print '%s: %s' % (name, nda)
    elif isinstance(nda, tuple) : print_ndarr(np.array(nda), 'ndarray from tuple: %s' % name)
    elif isinstance(nda, list)  : print_ndarr(np.array(nda), 'ndarray from list: %s' % name)
    elif not isinstance(nda, np.ndarray) :
                     print '%s: %s' % (name, type(nda))
    else           : print '%s:  shape:%s  size:%d  dtype:%s %s...' % \
         (name, str(nda.shape), nda.size, nda.dtype, nda.flatten()[first:last])

#------------------------------

def table_from_cspad_ndarr(nda_cspad) :
    """returns table of 2x1s shaped as (8*185, 4*388) in style of Cheetah
       generated from cspad array with size=(32*185*388) ordered as in data, shape does not matter. 
    """
    quads, nsegq, rows, cols = 4, 8, 185, 388
    nda = np.array(nda_cspad)
    nda.shape = (quads, nsegq, rows, cols)
    return np.hstack([np.vstack([nda[q,s,:] for s in range(nsegq)]) for q in range(quads)])

#------------------------------
#------------------------------
#------------------------------
