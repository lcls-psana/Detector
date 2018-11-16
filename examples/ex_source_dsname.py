#!/usr/bin/env python

import sys

##-----------------------------

def ex_source_dsname(ntest) : 
    """returns source and dataset name/file"""

    src, dsn= None, None 

    if   ntest == 1 : # (32, 185, 388)
        src, dsn = ':Cspad.0', '/reg/g/psdm/detector/data_test/types/0003-CxiDs2.0-Cspad.0-fiber-data.xtc'

    elif ntest == 2 : # (185, 388, 2)
        src, dsn = ':Cspad2x2.1', '/reg/g/psdm/detector/data_test/types/0004-MecTargetChamber.0-Cspad.0-three-quads.xtc'

    elif ntest == 3 : # (4, 512, 512)
        #src, dsn = ':pnCCD.0', '/reg/g/psdm/detector/data_test/types/0010-Camp.0-pnCCD.0.xtc'
        src, dsn = ':pnCCD.1', '/reg/g/psdm/detector/data_test/types/0008-Camp.0-pnCCD.1.xtc'
        #src, dsn = ':pnCCD.0', '/reg/g/psdm/detector/data_test/types/0009-pnccdFront.xtc'

    elif ntest == 4 : # (704, 768)
        src, dsn = ':Epix100a.0', '/reg/g/psdm/detector/data_test/types/0007-NoDetector.0-Epix100a.0.xtc'

    elif ntest == 5 : # (1024, 1024)
        src, dsn = ':Opal1000.1', '/reg/g/psdm/detector/data_test/types/0013-SxrBeamline.0-Opal1000.1.xtc'

    elif ntest == 6 : # (1024, 1024)
        src, dsn = ':Opal8000.1', '/reg/g/psdm/detector/data_test/types/0015-Opal8000_FrameV1.xtc'

    elif ntest == 7 : # (512, 512)
        src, dsn = ':Andor.0', '/reg/g/psdm/detector/data_test/types/0013-SxrEndstation.0-Andor.0.xtc'

    elif ntest == 8 : # (2, 512, 512)
        src, dsn = ':DualAndor.0', '/reg/g/psdm/detector/data_test/types/0006-SxrEndstation.0-DualAndor.0.xtc'

    elif ntest == 9 : # (2, 2048, 2048)
        src, dsn = ':DualAndor.0', '/reg/g/psdm/detector/data_test/types/0005-SxrEndstation.0-DualAndor.0.xtc'

    elif ntest == 10: # (500, 1152)
        src, dsn = ':Fccd.0', '/reg/g/psdm/detector/data_test/types/0015-SxrEndstation.0-Fccd.0.xtc'

    elif ntest == 11: # (1300, 1340)
        #src, dsn = ':Princeton.0', '/reg/g/psdm/detector/data_test/types/0015-Princeton_FrameV2.xtc'
        src, dsn = ':Princeton.0', '/reg/g/psdm/detector/data_test/types/0012-XcsBeamline.0-Princeton.0.xtc'

    elif ntest == 12: # (2048, 2048)
        src, dsn = ':OrcaFl40.0', '/reg/g/psdm/detector/data_test/types/0015-Orca_ConfigV1.xtc'

    elif ntest == 13: # (480, 640)
        src, dsn = ':Tm6740.0', '/reg/g/psdm/detector/data_test/types/0015-Pulnix_TM6740ConfigV2.xtc'

    elif ntest == 14: # (2048, 2048)
        #src, dsn = ':Quartz4A150.0', '/reg/g/psdm/detector/data_test/types/0015-Quartz-ConfigV2.xtc'
        src, dsn = ':Quartz4A150.0', '/reg/g/psdm/detector/data_test/types/0016-CxiEndstation.0-Quartz4A150.0.xtc'

    elif ntest == 15: # (512, 512)
        src, dsn = ':Timepix.0', '/reg/g/psdm/detector/data_test/types/0015-Timepix-ConfigV3.xtc'

    elif ntest == 16: # (1024, 1024)
        src, dsn = ':Pimax.0', '/reg/g/psdm/detector/data_test/types/0015-Pimax_FrameV1.xtc'

    elif ntest == 17: # (4096, 4096)
        src, dsn = ':Fli.0', '/reg/g/psdm/detector/data_test/types/0015-Fli_ConfigV1.xtc'

    elif ntest == 18: # (384, 384)
        src, dsn = ':Rayonix.0', '/reg/g/psdm/detector/data_test/types/0011-XppEndstation.0-Rayonix.0.xtc'

    elif ntest == 19: # (1920, 1920)
        src, dsn = ':Rayonix.0', '/reg/g/psdm/detector/data_test/types/0017-MfxEndstation.0-Rayonix.0.xtc'

    elif ntest == 20: # (1, 512, 1024)
        src, dsn = ':Jungfrau.0', '/reg/g/psdm/detector/data_test/types/0024-CxiEndstation.0-Jungfrau.0.xtc'

    elif ntest == 21: # (2160, 2560)
        src, dsn = ':Zyla.0', '/reg/g/psdm/detector/data_test/types/0025-XppEndstation.0-Zyla.0.xtc'

    elif ntest == 22: # (2, 512, 1024)
        src, dsn = ':Jungfrau.0', 'exp=xcsx22015:run=513'

    elif ntest == 31: # psana.Jungfrau.ConfigV1
        src, dsn = 'CxiEndstation.0:Jungfrau.0', 'exp=cxi11216:run=9'

    elif ntest == 32: # psana.Jungfrau.ConfigV2
        src, dsn = 'XcsEndstation.0:Jungfrau.0', 'exp=xcsx22015:run=503'

    elif ntest == 33: # psana.Jungfrau.ConfigV3
        src, dsn = 'XcsEndstation.0:Jungfrau.0', 'exp=xcsls3716:run=631'

    elif ntest == 34:
        src, dsn = ':Pixis.0', '/reg/g/psdm/detector/data_test/types/0026-MecTargetChamber.0-Pixis.1.xtc'

    elif ntest == 35:
        src, dsn = 'DetLab.0:Uxi.0', '/reg/g/psdm/detector/data_test/types/0027-DetLab.0-Uxi.0.xtc'

    elif ntest == 36:
        src, dsn = 'DetLab.0:Uxi.0', '/reg/g/psdm/detector/data_test/types/0027-DetLab.0-Uxi.0.xtc'

    elif ntest == 37:
        src, dsn = 'NoDetector.0:Epix10ka2M.0', '/reg/g/psdm/detector/data_test/types/0028-NoDetector.0-Epix10ka2M.0.xtc'

    elif ntest == 38:
        src, dsn = 'SxrEndstation.0:Archon.0', '/reg/g/psdm/detector/data_test/types/0029-SxrEndstation.0-Archon.0.xtc'

    elif ntest == 39:
        src, dsn = 'DetLab.0:StreakC7700.0', '/reg/g/psdm/detector/data_test/types/0030-DetLab.0-StreakC7700.0.xtc'

    elif ntest == 40:
        src, dsn = 'MecTargetChamber.0-Epix10ka.1', '/reg/g/psdm/detector/data_test/types/0033-MecTargetChamber.0-Epix10ka.1.xtc'

    else :
        sys.exit('Non-implemented sample for test number # %d' % ntest)

    return src, dsn


##-----------------------------

if __name__ == "__main__" :
  def test_dataset(ntest) :
    import psana
    src, dsn = ex_source_dsname(ntest)
    print 'src=%s, dsname=%s' % (src, dsn)
    ds = psana.DataSource(dsn)
    for nevt,evt in enumerate(ds.events()):
        print evt.keys()
        break

##-----------------------------

if __name__ == "__main__" :
    ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
    print '%s\nExample # %d' % (80*'_', ntest)
    test_dataset(ntest)    
    sys.exit(0)

##-----------------------------
