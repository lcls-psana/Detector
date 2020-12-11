
print\
"""example of bare minimum configuration info for epix10ka intensity correction\n\n
"""

import psana
from Detector.GlobalUtils import print_ndarr

ds = psana.DataSource('/reg/g/psdm/detector/data_test/types/0035-DetLab.0-Epix10ka2M.0.xtc')
dco = ds.env().configStore().get(psana.Epix.Config10ka2MV1, psana.Source('DetLab.0:Epix10ka2M.0'))

print 50*'_', '\ndetector config object dco:', dco
print 'number of ASICs  in the detector dco.numberOfAsics     :', dco.numberOfAsics()
print 'number of panels in the detector dco.numberOfElements():', dco.numberOfElements()

for i in range(dco.numberOfElements()):
    print 10*'='
    print 'panel config object pco = dco.elemCfg(%d):'%i
    pco = dco.elemCfg(i)
    print_ndarr(pco.asicPixelConfigArray(),'    pco.asicPixelConfigArray()')
    print '    pco.numberOfAsics():', pco.numberOfAsics()
    for ia in range(pco.numberOfAsics()):
        print '        pco.asics(%d).trbit():'%ia, pco.asics(ia).trbit()

#----
