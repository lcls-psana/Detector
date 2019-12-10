#--------------------
""" Manual script to fake actual offset calibration timestamp with earlier one. 
    For list of the panels of specified epix10ka detector in dataset
    creates references with past timestamp to the offset files in relative future, e.g.:
    ln -s /reg/g/psdm/detector/gains/epix10k/panels/.../offset/epix10ka_*_20181129124822_xcsx35617_r0544_offset_AML.dat
          /reg/g/psdm/detector/gains/epix10k/panels/.../offset/epix10ka_*_20180101000000_xcsx35617_r0544_offset_AML.dat
"""
from __future__ import print_function
#--------------------

import os
import psana

from Detector.UtilsEpix import CALIB_REPO_EPIX10KA
from Detector.PyDataAccess import get_epix10ka_any_config_object
from Detector.UtilsEpix10ka2M import ids_epix10ka2m

#--------------------

DIR_REPO = CALIB_REPO_EPIX10KA # '/reg/g/psdm/detector/gains/epix10k/panels' # global repo
                               # '/reg/neh/home/dubrovin/LCLS/con-detector/work' # local repo
TS_PTRN = '20181129124822'     # time stamp of later file
TS_SUBS = '20180101000000'     # time stamp of the reference
DO_REF  = False # True 

psana.setOption('psana.calib-dir', '/reg/neh/home/dubrovin/LCLS/con-detector/calib/')
#psana.setOption('psana.calib-dir', '/reg/d/psdm/XCS/xcsx35617/calib')

dsname, src = 'exp=xcsx35617:run=528',  'XcsEndstation.0:Epix10ka2M.0' # FH, FM, ... all
#return 'exp=xcsx35617:run=394',  'XcsEndstation.0:Epix10ka2M.0' # FH
#return 'exp=xcsx35617:run=419',  'XcsEndstation.0:Epix10ka2M.0' # AML
#return 'exp=xcsx35617:run=414',  'XcsEndstation.0:Epix10ka2M.0' # AHL

#--------------------

ds  = psana.DataSource(dsname)
env = ds.env()
source = psana.Source(src)

confo = get_epix10ka_any_config_object(env, source)

print('experiment %s' % env.experiment())
#print 'run        %d' % runnum
print('dataset    %s' % (dsname)) 
print('calibDir:', env.calibDir())

ids = ids_epix10ka2m(confo)
for i,id in enumerate(ids) : 
    print('elem %2d: %s' % (i,id))
    path = '%s/%s/offset' % (DIR_REPO, id)
    print('  path:', path)

    for fname in os.listdir(path) :
        if TS_PTRN in fname : fname_ref = fname.replace(TS_PTRN, TS_SUBS)
        cmd = 'ln -s %s/%s %s/%s' % (path, fname, path, fname_ref)
        #cmd = 'rm %s/%s' % (path, fname_ref)
        print('   cmd:', cmd)

        if DO_REF: os.system(cmd)

#--------------------
