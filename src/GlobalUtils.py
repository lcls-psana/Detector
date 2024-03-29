
"""
:py:class:`GlobalUtils` contains global utilities
=================================================

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Author Mikhail Dubrovin
"""
import sys
import numpy as np


def info_ndarr(nda, name='', first=0, last=5):
    _name = '%s '%name if name!='' else name
    s = ''
    gap = '\n' if (last-first)>10 else ' '
    if nda is None : s = '%s%s' % (_name, nda)
    elif isinstance(nda, tuple): s += info_ndarr(np.array(nda), 'ndarray from tuple: %s' % name)
    elif isinstance(nda, list) : s += info_ndarr(np.array(nda), 'ndarray from list: %s' % name)
    elif not isinstance(nda, np.ndarray):
                     s = '%s%s' % (_name, type(nda))
    else: s = '%sshape:%s size:%d dtype:%s%s%s%s'%\
               (_name, str(nda.shape), nda.size, nda.dtype, gap, str(nda.ravel()[first:last]).rstrip(']'),\
                ('...]' if nda.size>last else ']'))
    return s


def print_ndarr(nda, name='', first=0, last=5):
    print(info_ndarr(nda, name, first, last))


def divide_protected(num, den, vsub_zero=0):
    """Returns result of devision of numpy arrays num/den with substitution of value vsub_zero for zero den elements.
    """
    pro_num = np.select((den!=0,), (num,), default=vsub_zero)
    pro_den = np.select((den!=0,), (den,), default=1)
    return pro_num / pro_den


def info_command_line_parameters(parser):
    """Prints input arguments and optional parameters"""
    opts = {}
    args = None
    defs = None

    from optparse import OptionParser
    if isinstance(parser, OptionParser):
      (popts, pargs) = parser.parse_args()
      args = pargs                             # list of positional arguments
      opts = vars(popts)                       # dict of options
      defs = vars(parser.get_default_values()) # dict of default options
    else: # ArgumentParser
      args = parser.parse_args()  # Namespace
      opts = vars(args)           # dict
      defs = vars(parser.parse_args([]))

    s = 'Command: ' + ' '.join(sys.argv)\
      + '\n  Optional parameters:'\
      + '\n    <key>      <value>              <default>\n'

    for k,v in opts.items():
        vdef = defs[k]
        if k in ('dirmode', 'filemode'):
            v = oct(v)
            vdef = oct(vdef)
        s += '    %s %s %s\n' % (k.ljust(10), str(v).ljust(20), str(vdef).ljust(20))
    return s


def info_command_line():
    return ' '.join(sys.argv)


def info_kwargs(fmt='%10s: %s', separator='\n', **kwargs):
    return separator.join(fmt%(k,str(v)) for k,v in kwargs.items())


def selected_record(n):
    return n<5\
       or (n<50 and not n%10)\
       or (n<500 and not n%100)\
       or (not n%1000)

# EOF
