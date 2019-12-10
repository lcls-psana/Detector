#!/usr/bin/env python

from __future__ import print_function
import sys
import numpy as np
from time import time

import psana
from Detector.GlobalUtils import print_ndarr
import PSCalib.GlobalUtils as gu

import pyimgalgos.GlobalGraphics as gg
import Detector.UtilsEpix as ue
#import pyimgalgos.Graphics as gr

#------------------------------

def print_object_dir(o) :
    print('dir(%s):\n  %s' % (str(o), ',\n  '.join([v for v in dir(o) if v[:1]!='_'])))

#------------------------------

def test_epix10kaquad_config(tname) :
    #run = tname
    src = psana.Source('NoDetector.0:Epix10kaQuad.0')
    ds  = psana.DataSource('/reg/g/psdm/detector/data_test/types/0032-NoDetector.0-Epix10kaQuad.0.xtc')
    env = ds.env()
    co = env.configStore().get(psana.Epix.Config10kaQuadV1, src)
    #co = env.configStore().get(psana.Epix.Config10kaV1, src)
    #co = env.configStore().get(psana.Epix.Config10ka2MV1, src)

    print('experiment %s' % env.experiment())
    print('src        %s' % str(src)) 
    print('dataset    %s' % str(ds)) 
    print('calibDir:', env.calibDir())

    print_object_dir(co)
    print('co.evr()    ...Epix.PgpEvrConfig:', co.evr())
    print('co.elemCfg(0) ...Epix.Config10ka:', co.elemCfg(0))
    print('co.quad() ...Epix.Config10kaQuad:', co.quad())
    print('co.elemCfg_shape()           [4]:', co.elemCfg_shape())
    print('co.numberOfAsics()            16:', co.numberOfAsics())
    print('co.numberOfCalibrationRows()   4:', co.numberOfCalibrationRows())
    print('co.numberOfColumns()         384:', co.numberOfColumns())
    print('co.numberOfElements()          4:', co.numberOfElements())
    print('co.numberOfEnvironmentalRows() 2:', co.numberOfEnvironmentalRows())
    print('co.numberOfReadableRows()    352:', co.numberOfReadableRows())
    print('co.numberOfRows()            352:', co.numberOfRows())
    print('co.TypeId                    120:', co.TypeId)
    print('co.Version                     1:', co.Version)


    e0co = co.elemCfg(0)
    print_object_dir(e0co)
    print('e0co.asicMask()                       0:', e0co.asicMask())
    print('e0co.asicPixelConfigArray()         arr:\n', e0co.asicPixelConfigArray())
    print('e0co.asics()       Asic10kaConfigV1 obj:', e0co.asics(0))
    print('e0co.asics_shape()                  [4]:', e0co.asics_shape())
    print('e0co.calibPixelConfigArray()        arr:\n', e0co.calibPixelConfigArray())
    print('e0co.calibrationRowCountPerASIC()   2  :', e0co.calibrationRowCountPerASIC())
    print('e0co.carrierId0()                   0  :', e0co.carrierId0())
    print('e0co.carrierId1()                   0  :', e0co.carrierId1())
    print('e0co.environmentalRowCountPerASIC() 1  :', e0co.environmentalRowCountPerASIC())
    print('e0co.numberOfAsics()                4  :', e0co.numberOfAsics())
    print('e0co.numberOfAsicsPerColumn()       2  :', e0co.numberOfAsicsPerColumn())
    print('e0co.numberOfAsicsPerRow()          2  :', e0co.numberOfAsicsPerRow())
    print('e0co.numberOfCalibrationRows()      4  :', e0co.numberOfCalibrationRows())
    print('e0co.numberOfColumns()              384:', e0co.numberOfColumns())
    print('e0co.numberOfEnvironmentalRows()    2  :', e0co.numberOfEnvironmentalRows())
    print('e0co.numberOfPixelsPerAsicRow()     192:', e0co.numberOfPixelsPerAsicRow())
    print('e0co.numberOfReadableRows()         352:', e0co.numberOfReadableRows())
    print('e0co.numberOfReadableRowsPerAsic()  176:', e0co.numberOfReadableRowsPerAsic())
    print('e0co.numberOfRows()                 352:', e0co.numberOfRows())
    print('e0co.numberOfRowsPerAsic()          176:', e0co.numberOfRowsPerAsic())         

    evr = co.evr()
    print_object_dir(evr)

    q0co = co.quad() # psana.Epix.Config10kaQuad
    print_object_dir(q0co)
    print('q0co....')
    print('q0co.digitalCardId0               32772:', q0co.digitalCardId0())         
    print('q0co.digitalCardId1            19705345:', q0co.digitalCardId1())         


    print('id_epix:', ue.id_epix(co))


    nda = np.array(e0co.asicPixelConfigArray()) # shape:(352, 384)
    print_ndarr(nda, 'asicPixelConfigArray')



    sys.exit('TEST EXIT')



def test_further(tname) :

    a    = co.asicPixelConfigArray()
    arr1 = np.ones(a.shape, dtype=np.int32)
    print('asicPixelConfigArray:')

    cbits = np.bitwise_and(a,12)

    print('number of non-zero-status pixels', np.sum(np.select((a!=0,), (arr1,), default=0)))
    print('number of pixels cbits = 0 AUTO ', np.sum(np.select((cbits==0,), (arr1,), default=0)))
    print('number of pixels cbits = 4 FORCE', np.sum(np.select((cbits==4,), (arr1,), default=0)))
    print('number of pixels cbits = 8 LOW  ', np.sum(np.select((cbits==8,), (arr1,), default=0)))
    print('number of pixels cbits =12 HIGH ', np.sum(np.select((cbits==12,), (arr1,), default=0)))

    print_ndarr(a, 'asicPixelConfigArray')
    print('numberOfAsics :', co.numberOfAsics())

    for iasic in range(co.numberOfAsics()) :
        asic = co.asics(iasic)
        print('  ASIC:%d'%iasic,\
              '  trbit:',  asic.trbit(),\
              '  chipID:', asic.chipID())



    #if True :
    if False :
        import pyimgalgos.GlobalGraphics as gg

        img = hnda = co.asicPixelConfigArray()

        #ave, rms = img.mean(), img.std()
        gg.plotImageLarge(img, amp_range=None, figsize=(13,12)) # amp_range=(ave-1*rms, ave+2*rms))
        
        ##-----------------------------

        range_x = (hnda.min(), hnda.max()+1) # (0,(2<<16)-1)
        range_x = (0,16)
        fighi, axhi, hi = gg.hist1d(hnda.flatten(), bins=16, amp_range=range_x,\
                                  weights=None, color=None, show_stat=True, log=True, \
                                  figsize=(6,5), axwin=(0.15, 0.12, 0.78, 0.80), \
                                  title='Image spectrum', xlabel='ADU', ylabel=None, titwin=None)
        gg.show()

    ##-----------------------------
 

    ##-----------------------------
    #sys.exit('TEST EXIT')
    ##-----------------------------

#------------------------------
"""
'MfxEndstation.0:Epix10ka.0'                  trbit  asicPixelConfigArray()
'exp=mfxx32516:run=377' # Dark. Auto H to L   1      0
'exp=mfxx32516:run=368' # Dark. fixed high    1     12
'exp=mfxx32516:run=367' # fixed high          1     12
'exp=mfxx32516:run=365' # fixed low           1      8
'exp=mfxx32516:run=363' # fixed high          1     12
'exp=mfxx32516:run=340' # fixed medium        0     12
'exp=mfxx32516:run=337' # Auto M to L         0      2
'exp=mfxx32516:run=336' # Auto M to L         0      0
"""
#------------------------------

if __name__ == "__main__" :
    tname = sys.argv[1] if len(sys.argv)>1 else '377'
    print('%s\nTest %s' % (80*'_', tname))
    test_epix10kaquad_config(tname)
    print('try mfxx32516 runs: 336-AUTO, 337-AUTO&LOW, 340-HIGH, 363-HIGH, 365-LOW, 367-HIGH, 368-HIGH, 377-AUTO')
    sys.exit ('End of %s' % sys.argv[0])

#------------------------------
