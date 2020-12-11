import psana
import numpy as np
import matplotlib.pyplot as plt

experimentName = 'cxic00318'
runNumber = '123'
detInfo = 'jungfrau4M'

ds = psana.DataSource('exp='+experimentName+':run='+runNumber+':idx')
run = ds.runs().next()
det = psana.Detector(detInfo)
times = run.times()
env = ds.env()

runnum = int(runNumber)

mask = det.mask(runnum, calib=False, status=True, edges=False, central=False, unbond=False, unbondnbrs=False, unbondnbrs8=False)
if mask is not None: print "mask: ", mask.shape

mask = det.mask(runnum, calib=False, status=True, edges=True, central=False, unbond=False, unbondnbrs=False, unbondnbrs8=False)
if mask is not None: print "mask: ", mask.shape

evt = run.event(times[0])
plt.imshow(det.image(evt,mask),vmin=0,vmax=1);plt.show()
