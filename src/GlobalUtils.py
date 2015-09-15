
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
import numpy as np
#import time
#from time import localtime, gmtime, strftime, clock, time, sleep

##-----------------------------
##-----------------------------
##-----------------------------
#Enumerated type of detectors

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

CSPAD     = map_det_name_to_type["Cspad"]
CSPAD2X2  = map_det_name_to_type["Cspad2x2"]
PNCCD     = map_det_name_to_type["pnCCD"]
PRINCETON = map_det_name_to_type["Princeton"]
ACQIRIS   = map_det_name_to_type["Acqiris"]
TM6740    = map_det_name_to_type["Tm6740"]
OPAL1000  = map_det_name_to_type["Opal1000"]
OPAL2000  = map_det_name_to_type["Opal2000"]
OPAL4000  = map_det_name_to_type["Opal4000"]
OPAL8000  = map_det_name_to_type["Opal8000"]
ANDOR     = map_det_name_to_type["Andor"]
ORCAFL40  = map_det_name_to_type["OrcaFl40"]
FCCD960   = map_det_name_to_type["Fccd960"]
EPIX100A  = map_det_name_to_type["Epix100a"]
EPIX10K   = map_det_name_to_type["Epix10k"]
EPIX      = map_det_name_to_type["Epix"]
OTHER     = map_det_name_to_type["OTHER"]

##-----------------------------
# Enumerated calibration types. Should be in the same order like in PSCalib::CalibPars
# enum CALIB_TYPE { PEDESTALS=0, PIXEL_STATUS, PIXEL_RMS, PIXEL_GAIN, PIXEL_MASK, PIXEL_BKGD, COMMON_MODE };

PEDESTALS    = 0
PIXEL_STATUS = 1
PIXEL_RMS    = 2
PIXEL_GAIN   = 3
PIXEL_MASK   = 4
PIXEL_BKGD   = 5
COMMON_MODE  = 6
##-----------------------------
# Enumerated calibration constant status. Should be in the same order like in pdscalibdata::NDArrIOV1.h
# enum STATUS { LOADED=1, DEFAULT, UNREADABLE, UNDEFINED };

LOADED     = 1
DEFAULT    = 2
UNREADABLE = 3
UNDEFINED  = 4

##-----------------------------

def string_from_source_v2(source) :
  """Returns string like "CxiDs2.0:Cspad.0" from "Source('DetInfo(CxiDs2.0:Cspad.0)')" or "Source('DsaCsPad')"
  """
  str_in_quotes = str(source).split('"')[1]
  str_split = str_in_quotes.split('(') 
  return str_split[1].rstrip(')') if len(str_split)>1 else str_in_quotes

##-----------------------------

def string_from_source(source) :
  """Returns string like "CxiDs2.0:Cspad.0" from "Source('DetInfo(CxiDs2.0:Cspad.0)')"
  """
  #return str(source).split('(')[2].split(')')[0]
  return string_from_source_v2(source)

##-----------------------------

def det_name_from_source(source) :
  """Returns detector name like "Cspad" from source like "Source('DetInfo(CxiDs2.0:Cspad.0)')"
  """
  str_src = string_from_source_v2(source)
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
##-----------------------------
##-----------------------------
##-----------------------------

def merge_masks(mask1=None, mask2=None) :
    """Merging masks using rule: (0,1,0,1)^(0,0,1,1) = (0,0,0,1) 
    """
    if mask1 is None : return mask2
    if mask2 is None : return mask1

    shape1 = mask1.shape
    shape2 = mask2.shape

    if shape1 != shape2 :
        if len(shape1) > len(shape2) : mask2.shape = shape1
        else                         : mask1.shape = shape2

    return np.logical_and(mask1, mask2)

##-----------------------------

def print_ndarr(nda, name='', first=0, last=5) :
    if nda is None : print '%s\n%s: %s' % (80*'_', name, nda)
    elif isinstance(nda, tuple) : print_ndarr(np.array(nda), 'ndarray from tuple: %s' % name)
    elif isinstance(nda, list)  : print_ndarr(np.array(nda), 'ndarray from list: %s' % name)
    elif not isinstance(nda, np.ndarray) :
                     print '%s\n%s: %s' % (80*'_', name, type(nda))
    else           : print '%s\n%s:  shape:%s  size:%d  dtype:%s %s...' % \
         (80*'_', name, str(nda.shape), nda.size, nda.dtype, nda.flatten()[first:last])

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

  print 'string_from_source_v2 for src: %s' % string_from_source_v2('Source("DetInfo(CxiDs2.0:Cspad.0)")')

  print 'string_from_source_v2 for alias: %s' % string_from_source_v2('Source("DsaCsPad")')

##-----------------------------
##-----------------------------
