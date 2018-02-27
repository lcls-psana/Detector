####!/usr/bin/env python

import sys
import numpy as np
from time import time

import psana
from Detector.GlobalUtils import print_ndarr
import PSCalib.GlobalUtils as gu

import pyimgalgos.GlobalGraphics as gg
#import pyimgalgos.Graphics as gr

#------------------------------

def test_epix10ka_config(tname) :
    run = tname
    dsname =  'exp=mfxx32516:run=%s' % run
    s_src = 'MfxEndstation.0:Epix10ka.0'
    src = psana.Source(s_src)
    runnum = int(run)

    ds  = psana.DataSource(dsname)
    env = ds.env()
    cfg = env.configStore()
    co = env.configStore().get(psana.Epix.Config10kaV1, src)

    print 'experiment %s' % env.experiment()
    print 'run        %d' % runnum
    print 'dataset    %s' % (dsname) 
    print 'calibDir:', env.calibDir()

    print 'asicAcq                0:', co.asicAcq()
    print 'asicAcqControl         0:', co.asicAcqControl()
    print 'asicAcqLToPPmatL       200:', co.asicAcqLToPPmatL()
    print 'asicAcqWidth           10000:', co.asicAcqWidth()
    print 'asicGR                 0:', co.asicGR()
    print 'asicGRControl          0:', co.asicGRControl()
    print_ndarr(co.asicPixelConfigArray(), 'asicPixelConfigArray   ')
    print 'asicPpbe               0:', co.asicPpbe()
    print 'asicPpbeControl        0:', co.asicPpbeControl()
    print 'asicPpmat              1:', co.asicPpmat()
    print 'asicPpmatControl       1:', co.asicPpmatControl()
    print 'asicPPmatToReadout     0:', co.asicPPmatToReadout()
    print 'asicR0                 0:', co.asicR0()
    print 'asicR0ClkControl       0:', co.asicR0ClkControl()
    print 'asicR0Control          0:', co.asicR0Control()
    print 'asicR0ToAsicAcq        10000:', co.asicR0ToAsicAcq()
    print 'asicR0Width            30:', co.asicR0Width()
    print 'asicRoClk              0:', co.asicRoClk()
    print 'asicRoClkHalfT         5:', co.asicRoClkHalfT()
    print 'asics                  obj:', co.asics(0)
    print 'asics_shape            [4]:', co.asics_shape()         
    print 'adcReadsPerPixel       1:', co.adcReadsPerPixel() 
    print 'adcStreamMode          0:', co.adcStreamMode()   
    print 'enableAutomaticRunTrigger 0:', co.enableAutomaticRunTrigger()
    print 'dacSetting   0:', co.dacSetting()
    print 'evrDaqCode   40:', co.evrDaqCode()
    print 'evrRunCode   40:', co.evrRunCode()
    print 'R0Mode       1:', co.R0Mode()
    print 'scopeArmMode 2:', co.scopeArmMode()
    print 'usePgpEvr    1:', co.usePgpEvr()

    for iasic in range(co.numberOfAsics()) :
        asic = co.asics(iasic)
        print 'ASIC:%d' % iasic,
        print '  trbit: ',  asic.trbit()
        print '  chipID: ',  asic.chipID()



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
    print '%s\nTest %s' % (80*'_', tname)
    test_epix10ka_config(tname)
    sys.exit ('End of %s' % sys.argv[0])

#------------------------------
