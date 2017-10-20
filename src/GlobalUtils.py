#------------------------------------------------------------------------

"""
:py:class:`GlobalUtils` contains global utilities
=================================================

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Author Mikhail Dubrovin
"""

#--------------------------------

import numpy as np

#------------------------------

def print_ndarr(nda, name='', first=0, last=5) :
    if nda is None : print '%s: %s' % (name, nda)
    elif isinstance(nda, tuple) : print_ndarr(np.array(nda), 'print_ndarr: ndarray from tuple: %s' % name)
    elif isinstance(nda, list)  : print_ndarr(np.array(nda), 'print_ndarr: ndarray from list: %s' % name)
    elif not isinstance(nda, np.ndarray) :
                     print '%s: %s' % (name, type(nda))
    else           : print '%s:  shape:%s  size:%d  dtype:%s %s...' % \
         (name, str(nda.shape), nda.size, nda.dtype, nda.flatten()[first:last])

#------------------------------

def divide_protected(num, den, vsub_zero=0) :
    """Returns result of devision of numpy arrays num/den with substitution of value vsub_zero for zero den elements.
    """
    pro_num = np.select((den!=0,), (num,), default=vsub_zero)
    pro_den = np.select((den!=0,), (den,), default=1)
    return pro_num / pro_den

#------------------------------

