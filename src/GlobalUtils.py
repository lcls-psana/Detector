
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
import sys
import os
#import time
#from time import localtime, gmtime, strftime, clock, time, sleep

##-----------------------------
##-----------------------------
##-----------------------------

list_of_detnames = [ \
      "Cspad2x2" \
    , "Cspad" \
    , "pnCCD" \
    , "Princeton" \
    , "Acqiris" \
    , "Tm6740" \
    , "Opal1000" \
    , "Opal2000" \
    , "Opal4000" \
    , "Opal8000" \
    , "Andor" \
    , "OrcaFl40" \
    , "Fccd960" \
    , "Epix100a" \
    , "Epix10k" \
    , "Epix" \
    , "OTHER" \
    ]

map_det_type_to_name = dict(enumerate(list_of_detnames))

map_det_name_to_type = dict(zip(map_det_type_to_name.values(), map_det_type_to_name.keys()))

CSPAD    = map_det_name_to_type["Cspad"]
CSPAD2X2 = map_det_name_to_type["Cspad2x2"]
PNCCD    = map_det_name_to_type["pnCCD"]

##-----------------------------


def string_from_source(source) :
  """Returns string like "CxiDs2.0:Cspad.0" from "Source("DetInfo(CxiDs2.0:Cspad.0)")"
  """
  return str(source).split('(')[2].split(')')[0]

##-----------------------------

def det_name_from_source(source) :
  """Returns detector name like "Cspad" from source like "Source("DetInfo(CxiDs2.0:Cspad.0)")"
  """
  str_src = string_from_source(source)
  return str_src.split(':')[1].split('.')[0]

##-----------------------------

def det_type_from_source(source) :
  detname = det_name_from_source(source)
  return map_det_name_to_type[detname]

##-----------------------------

def det_name_from_type(type) :
    return map_det_type_to_name[type]

##-----------------------------

def det_type_from_name(name) :
    return map_det_name_to_type[name]

##-----------------------------

#import psana

if __name__ == "__main__" :

  #psana.Source('DetInfo(CxiDs2.0:Cspad.0)')

  #print 'dettype_from_source: %s' % source
  print '\nlist_of_detnames:', list_of_detnames

  print '\nmap_det_type_to_name:'
  for t,n in map_det_type_to_name.items() : print '  %2d : %10s' % (t, n)
  print '\nmap_det_name_to_type:'
  for n,t in map_det_name_to_type.items() : print '  %10s : %2d' % (n, t)

##-----------------------------
##-----------------------------
