
#===============
ipython
#===============

import psana
ds = psana.DataSource('/reg/d/psdm/DIA/diamcc14/hdf5/diamcc14-r1791.h5')
env = ds.env()
det_orca  = psana.Detector('FeeHxSpectrometer.0:OrcaFl40.0', env)
det_ebeam = psana.Detector('EBeam')
events = ds.events()

evt = None
ebeam = None
for i, evt in enumerate(ds.events()) : 
    ebeam = det_ebeam.get(evt)
    if ebeam is None: 
        print 'Event %3d: EBeam is None' % i
    else : 
        print 'EBeam object is found in event %d' % i
        break

ebeam.ebeamPhotonEnergy()

# ebeam. <TAB>
