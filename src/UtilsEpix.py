#------------------------------
"""
:py:class:`UtilsEpix` contains utilities for epix100a detector
==============================================================

Usage::
    from Detector.UtilsEpix import create_directory, alias_for_id,\
         id_for_alias, id_epix, print_object_dir, 

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2018-02-22 by Mikhail Dubrovin
"""

#------------------------------
import os
#import numpy as np
from time import time

import logging
logger = logging.getLogger(__name__)

from Detector.GlobalUtils import print_ndarr #, info_ndarr
from PSCalib.GlobalUtils import load_textfile, save_textfile, file_mode#, create_path, create_directory

CALIB_REPO_EPIX10KA = '/reg/g/psdm/detector/gains/epix10k/panels'
FNAME_PANEL_ID_ALIASES = '%s/.aliases.txt'%CALIB_REPO_EPIX10KA

#------------------------------

def set_file_access_mode(fname, mode=0777) :
    os.chmod(fname, mode)

#------------------------------

def create_directory(dir, mode=0777) :
    """Creates directory and sets its mode"""
    if os.path.exists(dir) :
        logger.debug('Exists: %s mode(oct): %s' % (dir, oct(file_mode(dir))))
    else :
        os.makedirs(dir)
        os.chmod(dir, mode)
        logger.debug('Created:%s, mode(oct)=%s' % (dir, oct(mode)))

#------------------------------

def alias_for_id(panel_id, fname=FNAME_PANEL_ID_ALIASES) :
    """Returns Epix100a/10ka panel short alias for long panel_id, 
       e.g., for panel_id = 3925999616-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719
       returns 0001
    """
    alias_max = 0
    if os.path.exists(fname) :
      #logger.debug('search alias for panel id: %s\n  in file %s' % (panel_id, fname))
      recs = load_textfile(fname).strip('\n').split('\n')
      for r in recs :
        if not r : continue # skip empty records
        fields = r.strip('\n').split(' ')
        if fields[1] == panel_id : 
            logger.debug('found alias %s for panel_id %s\n  in file %s' % (fields[0], panel_id, fname))
            return fields[0]
        ialias = int(fields[0])
        if ialias>alias_max : alias_max = ialias
        #print(fields)
    # if record for panel_id is not found yet, add it to the file and return its alias
    rec = '%04d %s\n' % (alias_max+1, panel_id)
    logger.debug('file "%s" is appended with record:\n%s' % (fname, rec))
    save_textfile(rec, fname, mode='a')
    return '%04d' % (alias_max+1)

#------------------------------

def id_for_alias(alias, fname=FNAME_PANEL_ID_ALIASES) :
    """Returns Epix100a/10ka panel panel_id for specified alias, 
       e.g., for alias = 0001
       returns 3925999616-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719
    """
    logger.debug('search panel id for alias: %s\n  in file %s' % (alias, fname))
    recs = load_textfile(fname).strip('\n').split('\n')
    for r in recs :
        fields = r.strip('\n').split(' ')
        if fields[0] == alias : 
            logger.debug('found panel id %s' % (fields[1]))
            return fields[1]

#------------------------------

def id_epix(config_obj) :
    """Returns Epix100 Id as a string, e.g., 3925999616-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719"""
    o = config_obj
    fmt2 = '%010d-%010d'
    zeros = fmt2 % (0,0)
    version = '%010d' % (o.version()) if getattr(o, "version", None) is not None else '%010d' % 0
    carrier = fmt2 % (o.carrierId0(), o.carrierId1())\
              if getattr(o, "carrierId0", None) is not None else zeros
    digital = fmt2 % (o.digitalCardId0(), o.digitalCardId1())\
              if getattr(o, "digitalCardId0", None) is not None else zeros
    analog  = fmt2 % (o.analogCardId0(), o.analogCardId1())\
              if getattr(o, "analogCardId0", None) is not None else zeros
    return '%s-%s-%s-%s' % (version, carrier, digital, analog)

#------------------------------

def is_trbit_high(co) :
    """from configuration object define if detector works in high gain mode.
    """
    if co.numberOfAsics()>1 : 
        return co.asics(0).trbit()==1

#------------------------------

def time_of_nda(t0_sec, res, cmt='XXX') :
    dt = time()-t0_sec
    print_ndarr(res, '%s : consumed time (sec) = %.6f' % (cmt,dt))
    return res

#------------------------------

def print_object_dir(o) :
    print 'dir(%s):\n  %s' % (str(o), ',\n  '.join([v for v in dir(o) if v[:1]!='_']))

#------------------------------
#------------------------------
#------------------------------

if __name__ == "__main__" :
  def test_alias_for_id(tname) :
     import random
     ranlst = ['%010d'%random.randint(0,1000000) for i in range(5)]
     #panel_id = 3925999616-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719
     panel_id = '-'.join(ranlst)
     alias = alias_for_id(panel_id, fname='./aliases-test.txt')
     print 'alias:', alias

#------------------------------

if __name__ == "__main__" :
    import sys
    print 80*'_'
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    if tname == '1' : test_alias_for_id(tname)
    else : sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit('End of %s' % sys.argv[0])

#------------------------------
