from __future__ import print_function
import sys
import os
from psana import *
#import Image
import numpy as np
#from PSCalib.GeometryAccess import img_from_pixel_arrays
 
ds = DataSource('exp=%s:run=%d:stream=0,1,2,3,4,5,6,7,8'% ("meca6013", 184))
env = ds.env()
sourceName = "MecTargetChamber.0"
expFolder = "/reg/d/psdm/mec/"
detectorNameOffset = 19
src = [sourceName+':'+'Cspad.0']+[sourceName+':'+'Cspad2x2.1']+[sourceName+':'+'Cspad2x2.2']+[sourceName+':'+'Cspad2x2.3']+[sourceName+':'+'Cspad2x2.4']+[sourceName+':'+'Cspad2x2.5']
#src = [sourceName+':'+'Cspad2x2.1']+[sourceName+':'+'Cspad2x2.2']+[sourceName+':'+'Cspad2x2.3']+[sourceName+':'+'Cspad2x2.4']+[sourceName+':'+'Cspad2x2.5']
#src = [sourceName+':'+'Cspad2x2.1']
print(src)

cspaddetectors = {}
for det in src:
    cspaddetectors[det] = Detector(det, env)
 
x = ds.events()
evt = next(x)
for det in src:
    detectorname = det[det.find(sourceName)+detectorNameOffset:]
    calibframe = cspaddetectors[det].raw(evt)
    if not calibframe is None:
        cropframe = cspaddetectors[det].image(evt, calibframe)
        #cropframe = cspaddetectors[det].raw(evt)
        print(det)
        print(cropframe)
