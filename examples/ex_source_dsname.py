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

    else :
        sys.exit('Non-implemented sample for test number # %d' % ntest)

    return src, dsn

##-----------------------------

if __name__ == "__main__" :

    ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
    print '%s\nExample # %d' % (80*'_', ntest)

    src, dsn = ex_source_dsname(ntest)
    print 'src=%s, dsname=%s' % (src, dsn)

    sys.exit(0)

##-----------------------------
