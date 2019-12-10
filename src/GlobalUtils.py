#------------------------------

"""
:py:class:`GlobalUtils` contains global utilities
=================================================

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Author Mikhail Dubrovin
"""
from __future__ import print_function

#------------------------------

import sys
import numpy as np

#------------------------------

def info_ndarr(nda, name='', first=0, last=5) :
    s = ''
    if nda is None : s = '%s: %s' % (name, nda)
    elif isinstance(nda, tuple) : s += info_ndarr(np.array(nda), 'ndarray from tuple: %s' % name)
    elif isinstance(nda, list)  : s += info_ndarr(np.array(nda), 'ndarray from list: %s' % name)
    elif not isinstance(nda, np.ndarray) :
                     s = '%s: %s' % (name, type(nda))
    else : s = '%s:  shape:%s  size:%d  dtype:%s %s...'%\
               (name, str(nda.shape), nda.size, nda.dtype, nda.flatten()[first:last])
    return s

#------------------------------

def print_ndarr(nda, name='', first=0, last=5) :
    if nda is None : print('%s: %s' % (name, nda))
    elif isinstance(nda, tuple) : print_ndarr(np.array(nda), 'print_ndarr: ndarray from tuple: %s' % name)
    elif isinstance(nda, list)  : print_ndarr(np.array(nda), 'print_ndarr: ndarray from list: %s' % name)
    elif not isinstance(nda, np.ndarray) :
                     print('%s: %s' % (name, type(nda)))
    else           : print('%s:  shape:%s  size:%d  dtype:%s %s...' % \
         (name, str(nda.shape), nda.size, nda.dtype, nda.flatten()[first:last]))

#------------------------------

def divide_protected(num, den, vsub_zero=0) :
    """Returns result of devision of numpy arrays num/den with substitution of value vsub_zero for zero den elements.
    """
    pro_num = np.select((den!=0,), (num,), default=vsub_zero)
    pro_den = np.select((den!=0,), (den,), default=1)
    return pro_num / pro_den

#------------------------------

def info_command_line_parameters(parser) :
    """Prints input arguments and optional parameters"""
    (popts, pargs) = parser.parse_args()
    args = pargs                             # list of positional arguments
    opts = vars(popts)                       # dict of options
    defs = vars(parser.get_default_values()) # dict of default options

    s = 'Command: ' + ' '.join(sys.argv)+\
        '\n  Argument list: %s\n  Optional parameters:\n' % str(args)+\
        '    <key>      <value>              <default>\n'
    for k,v in opts.items() :
        s += '    %s %s %s\n' % (k.ljust(10), str(v).ljust(20), str(defs[k]).ljust(20))
    return s

#------------------------------
#------------------------------
#------------------------------

