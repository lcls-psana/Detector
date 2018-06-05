from psana import *
import time
import sys
ds = DataSource('exp=diamcc14:run=1740:smd')
#xtcav = Detector('XTCAV_Images')

#from Detector.AreaDetector import AreaDetector    
#spec = AreaDetector('XrayTransportDiagnostic.20:Opal1000.0', ds.env(), pbits=1)

spec = Detector('SXR_Spectrometer')
#spec = Detector('XrayTransportDiagnostic.20:Opal1000.0')
#spec = Detector('Opal1000')

for i,evt in enumerate(ds.events()) :
    # xtcavraw = xtcav.raw(evt)
    # if xtcavraw is None:
    #     print 'xtcav none'
    #     continue
    specraw = spec.raw(evt)
    if i>50: sys.exit('THE END after %d events' % i)
    if specraw is None:
        print 'spec none'
        continue
    print specraw.shape
    sys.exit('THE END after %d events' % i)








from psana import *
ds = DataSource('exp=diamcc14:run=1740:smd')
di = DetInfo('SXR_Spectrometer')
di.det

#------------------------------

source_string = 'XrayTransport.20:Opal1000.0'
source_string = 'DetInfo(CxiDs2.0:Cspad.0)'

import re
source_string = 'DetInfo(XrayTransportDiagnostic.2:Opal1000.0)'
source_string = 'DetInfo(XrayTransportDiagnostic.20:Opal1000.0)'
print 'XXX: DetInfo source_string = ', source_string
m = re.search('(\w+).(\d+)\:(\w+).(\d+)', source_string)
print 'XXX: DetInfo m = re.search: ', m
print 'XXX: m.groups():', m.groups()

#------------------------------
