
if True:
  from psana import *
  #setOption('psana.calib-dir','/reg/neh/home/cpo/junk/calib')
  ds = DataSource('exp=meclv8018:run=76:stream=0,1,2,3,4,5,6,7,8')
  env = ds.env()
  det = Detector("MecTargetChamber.0:Epix100a.0", accept_missing=True)
  it = ds.events()
  evt = it.next()
  frame = det.image(evt)
  print frame
  
  
