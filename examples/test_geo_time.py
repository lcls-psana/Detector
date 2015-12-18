
#------------
# In ipython
# %time x  = det.coords_x(evt)
# %time ix = det.indexes_x(evt)
#------------

from time import time

import psana
ds = psana.DataSource('exp=xpptut15:run=54')
env = ds.env()
evt = ds.events().next()
det = psana.Detector('XppGon.0:Cspad.0', env)

for i in range(10) :
    t0_sec = time()
    det.coords_x(evt)
    print 'Ccmmand#%2d consumed astro time = %9.6f sec' % (i, time()-t0_sec)

#------------
