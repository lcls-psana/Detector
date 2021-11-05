#!/usr/bin/env python
from __future__ import print_function

import sys
import numpy as np
from psana import Detector, DataSource
from Detector.PyDataAccess import get_epix_data_object
from Detector.GlobalUtils import info_ndarr
from Detector.UtilsEpix10kaCalib import proc_dark_block
#from Detector.UtilsCalib import proc_dark_block

SCRNAME = sys.argv[0].rsplit('/')[-1]
USAGE = '%s -e mfxc00118 -d epix10k2M -r191 -N1000 -K0' % SCRNAME

d_detname = 'epix10k2M'
d_expname = 'mfxc00118'
d_run     = 191
d_events  = 1000
d_evskip  = 0
d_nrecs   = 1000

import argparse
parser = argparse.ArgumentParser(usage=USAGE, description='%s - averaging of epix10ka calibration rows'%SCRNAME)
parser.add_argument('-d', '--detname', default=d_detname, type=str, help='detector name, def=%s' % d_detname)
parser.add_argument('-e', '--expname', default=d_expname, type=str, help='experiment name, def=%s' % d_expname)
parser.add_argument('-r', '--run',     default=d_run,     type=int, help='run number, def=%s' % d_run)
parser.add_argument('-N', '--events',  default=d_events,  type=int, help='maximal number of events, def=%s' % d_events)
parser.add_argument('-K', '--evskip',  default=d_evskip,  type=int, help='number of events to skip in the beginning of run, def=%s' % d_evskip)
parser.add_argument('--nrecs',         default=d_nrecs,   type=int, help='maximal number of records in the data block, def=%s' % d_nrecs)

args = parser.parse_args()
print('parser.parse_args: %s' % str(args))

def save_ndarray(nda, fname, cmt='nda'):
    print(info_ndarr(nda, cmt))
    print('save in file %s' % fname)
    np.save(fname, nda)

M14 =  0x3fff
nrec = -1
shape_block = [args.nrecs,] + list((16, 4, 384))
block=np.zeros(shape_block, dtype=np.int16)

ds = DataSource('exp=%s:run=%d:smd' % (args.expname, args.run))
det = Detector(args.detname)
for run in ds.runs():
  for nev,evt in enumerate(run.events()):

    if nev < args.evskip:
        print('Ev:%6d skip, nev < --evskip=%d' % (nev, args.evskip))
        continue

    if nev > args.events:
        print('Ev:%6d break, nev > --events=%d' % (nev, args.events))
        break

    raw = det.raw(evt)
    if raw is not None:
      #print(info_ndarr(raw,'raw')) #raw shape:(16, 352, 384)
      odata = get_epix_data_object(evt, det.source)
      crows = odata.calibrationRows() #calibrows shape:(16, 4, 384)

      nrec += 1
      if not(nev<args.nrecs): break

      if nrec<10\
      or not(nrec%10): print(info_ndarr(crows, 'Ev:%04d rec:%04d raw & M14' % (nev,nrec)))
      block[nrec]=crows # & M14


print('Ev:%04d nrec:%04d' % (nev, nrec))

kwa = {'exp':args.expname, 'det':args.detname}

list_med = []
list_rms = []

for i in range(block.shape[1]):
    print('== panel:%d' % i)
    med, rms, status = proc_dark_block(block[:nrec,i,:], **kwa)
    print(info_ndarr(med,      '  med')) #shape=(4, 384)
    print(info_ndarr(med[0,:], '  med[0,:]'))
    print(info_ndarr(med[1,:], '  med[1,:]'))
    print(info_ndarr(rms[0,:], '  rms[0,:]'))
    print(info_ndarr(rms[1,:], '  rms[1,:]'))

    print('  minimum of med[0,:]: %.3f' %np.amin(med[0,:]))
    print('  minimum of med[1,:]: %.3f' %np.amin(med[1,:]))
    print('  maximum of med[0,:]: %.3f' %np.amax(med[0,:]))
    print('  maximum of med[1,:]: %.3f' %np.amax(med[1,:]))
    print('  medium  of rms[0,:]: %.3f' %np.median(rms[0,:]))
    print('  medium  of rms[1,:]: %.3f' %np.median(rms[1,:]))
    print('  maximum of rms[0,:]: %.3f' %np.amax(rms[0,:]))
    print('  maximum of rms[1,:]: %.3f' %np.amax(rms[1,:]))

    list_med.append(med)
    list_rms.append(rms)

prefix = 'calibrows-%s-r%04d-%s' % (args.expname, args.run, args.detname.replace('.','-').replace(':','-'))

save_ndarray(np.stack(list_med), '%s-ave.npy'%prefix, cmt='nda_med')
save_ndarray(np.stack(list_rms), '%s-rms.npy'%prefix, cmt='nda_rms')

# EOF
