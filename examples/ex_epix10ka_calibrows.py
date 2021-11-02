#!/usr/bin/env python
from __future__ import print_function

import numpy as np
from psana import Detector, DataSource
from Detector.PyDataAccess import get_epix_data_object
from Detector.GlobalUtils import info_ndarr
#from Detector.UtilsCalib import proc_dark_block
from Detector.UtilsEpix10kaCalib import proc_dark_block

exp = 'xpplw2619'
runnum = 11
detname = 'XppGon.0:Epix10ka2M.0'

M14 =  0x3fff
nrecs=100
nrec = -1
shape_block = [nrecs,] + list((16, 4, 384))
block=np.zeros(shape_block,dtype=np.int16)

ds = DataSource('exp=%s:run=%d:smd' % (exp, runnum))
det = Detector(detname)
for run in ds.runs():
  for nev,evt in enumerate(run.events()):
    raw = det.raw(evt)
    if raw is not None:
      #print(info_ndarr(raw,'raw')) #raw shape:(16, 352, 384)
      odata = get_epix_data_object(evt, det.source)
      crows = odata.calibrationRows() #calibrows shape:(16, 4, 384)

      nrec += 1
      if not(nev<nrecs): break

      if nrec<10\
      or not(nrec%10): print(info_ndarr(crows, 'Ev:%04d rec:%04d raw & M14' % (nev,nrec)))
      block[nrec]=crows # & M14


print('Ev:%04d nrec:%04d' % (nev, nrec))

kwa = {'exp':exp, 'det':detname}

med_list = []

for i in range(block.shape[1]):
    print('== panel:%d' % i)
    med, rms, status = proc_dark_block(block[:nrec,i,:], **kwa)
    print(info_ndarr(med, ' med')) #shape=(4, 384)
    print(info_ndarr(med[0,:], '   med[0,:]'))
    print(info_ndarr(med[1,:], '   med[1,:]'))
    print(info_ndarr(rms[0,:], '   rms[0,:]'))
    print(info_ndarr(rms[1,:], '   rms[1,:]'))

    print('minimum of med[0,:]:', np.amin(med[0,:]))
    print('minimum of med[1,:]:', np.amin(med[1,:]))
    print('maximum of med[0,:]:', np.amax(med[0,:]))
    print('maximum of med[1,:]:', np.amax(med[1,:]))
    print('medium  of rms[0,:]:', np.median(rms[0,:]))
    print('medium  of rms[1,:]:', np.median(rms[1,:]))
    print('maximum of rms[0,:]:', np.amax(rms[0,:]))
    print('maximum of rms[1,:]:', np.amax(rms[1,:]))

    med_list.append(med)

med_nda = np.stack(med_list)
fname = 'calibrows-%s-r%04d-%s.npy' % (exp, runnum, detname.replace('.','-').replace(':','-'))
print(info_ndarr(med_nda, 'med_nda'))
print('save in file %s' % fname)
np.save(fname, med_nda)

# EOF
