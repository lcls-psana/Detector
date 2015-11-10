#--------------------------------------------------------------------------
# File and Version Information:
#  $Id$
#
# Description:
#  class PyDetector
#--------------------------------------------------------------------------
""" 
This software was developed for the LCLS project.
If you use all or part of it, please give an appropriate acknowledgment.

----------------------------------------

Notes on progress 11/9 TJL & CPO
-- BLD returns DDL detector, some discussion if this should be
   easier to access.

Notes on progress 11/2 TJL & CPO
-- We settled on a source-matching pattern by eliminating support for
   psana.Source in the Detector interface and adopting Mikhail's
   matching system
-- For next time: start with BLD
-- We are going to implement Detector classes for
   > BLD
   > EPICS
-- Should EPICS be one detector, or should there be one detector
   per EPICS PV?
     > Pros of 1 per PV: seamless for user (no knowledge of EPCIS)
     > Pros of 1 detector: better performance for tab completes


Notes on progress 10/20 TJL & CPO
-- Major outstanding problem is figuring out how to map Source names to their 
   corresponding Detector class implementations
-- We are going to implement Detector classes for
   > BLD
   > EPICS
   > EVR (in progress)
-- All ToDo's below still outstanding


Notes on progress 10/14

To Do:
-- rename Detector.Pydetector to AreaDetector

(factory)
-- Fix matching of source objects so it works nicely
   (leaning towards strings, alt option is to reveal
    detector/device ID numbers in C++, one route
    is to cp the Event.keys() transfer of the DetInfo
    object from C++ to Python)
-- write smart DetInfo/BldInfo/EPICS matching code that
   takes a string and finds out which one to use, we
   can distinguish between DetInfo and BldInfo by the
   number of fields the user pases in their string

To Think About:
-- How should tab completion work (heirarchies, and how does this 
   dictate restraints on the Detector interface implementation?
-- Should EPICS be one detector, or should there be one detector
   per EPICS PV?
     > Pros of 1 per PV: seamless for user (no knowledge of EPCIS)
     > Pros of 1 detector: better performance for tab completes

"""
#------------------------------
__version__ = "$Revision$"
##-----------------------------

import _psana
import PSCalib.GlobalUtils as gu

from Detector.DdlDetector   import DdlDetector
from Detector.EpicsDetector import EpicsDetector
from Detector.AreaDetector  import AreaDetector
from Detector.WFDetector    import WFDetector
from Detector.EvrDetector   import EvrDetector

# the following function is renamed psana.Detector in the
# psana __init__.py file

def detector_factory(source_string, env):
    """
    Create a python Detector from a string identifier.

    Parameters
    ----------
    source_string : str
        A string identifing a peice of data to access, examples include:
          > 'cspad'              # a DAQ alias for a CSPAD camera
          > 'XppGon.0:Cspad.0'   # a DAQ source string
          > 'evr0'               # the EVR event code read out
          > 'EBeam'              # a BldInfo identifier
        The idea is that you should be able to pass something that makes
        sense to you as a human here, and you automatically get the right
        detector object in return.

    env : psana.Env
        The psana environment object associated with the psana.DataSource
        you are interested in.

    Returns
    -------
    detector : Detector.PyDetector
        A psana-python detector object. Try detector(psana.Event) to
        access your data.
    """

    # check to see if the source_string is in the Bld, which is a
    # reserved set of names
    if source_string in gu.bld_names:
        # make a DDL detector and return it
        return DdlDetector( 'BldInfo(' + source_string + ')' )


    # see if the source_string is an epics PV name
    epics = env.epicsStore()
    if source_string in epics.names(): # both names & aliases
        return EpicsDetector(source_string, env)


    # check to see if it is an alias
    amap = env.aliasMap()
    alias_src = amap.src(source_string) # string --> DAQ-style psana.Src
                
    # if it is an alias, look up the full name
    if amap.alias(alias_src) != '':         # alias found
        source_string = str(alias_src)


    # map detector names to their respective detector class implementations
    dettype = gu.det_type_from_source(source_string)

    if dettype == gu.ACQIRIS or dettype == gu.IMP:
        return WFDetector(source_string, env)
    elif dettype == gu.EVR:
        return EvrDetector(source_string, env)
    elif dettype in [gu.CSPAD, gu.CSPAD2X2, gu.PRINCETON, gu.PNCCD,
                     gu.TM6740, gu.OPAL1000, gu.OPAL2000, gu.OPAL4000, gu.OPAL8000,
                     gu.ORCAFL40, gu.EPIX, gu.EPIX10K, gu.EPIX100A, gu.FCCD960,
                     gu.ANDOR, gu.QUARTZ4A150, gu.RAYONIX]:
        return AreaDetector(source_string, env)

    else:
        raise ValueError('Could not interpret "%s" as any known detector' % source_string)
    
    return

##-----------------------------

def test1():

    import sys
    from time import time
    import psana

    ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
    print 'Test # %d' % ntest
    dsname, src                  = 'exp=cxif5315:run=169', psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
    if   ntest==2  : dsname, src = 'exp=meca1113:run=376', psana.Source('DetInfo(MecTargetChamber.0:Cspad2x2.1)')
    elif ntest==3  : dsname, src = 'exp=amob5114:run=403', psana.Source('DetInfo(Camp.0:pnCCD.0)')
    elif ntest==4  : dsname, src = 'exp=xppi0614:run=74',  psana.Source('DetInfo(NoDetector.0:Epix100a.0)')
    elif ntest==5  : dsname, src = 'exp=sxri0414:run=88',  psana.Source('DetInfo(SxrEndstation.0:Acqiris.2)')
    elif ntest==6  : dsname, src = 'exp=cxii0215:run=49',  psana.Source('DetInfo(CxiEndstation.0:Imp.1)')
    print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

    ds = psana.DataSource(dsname)
    env = ds.env()
    cls = env.calibStore()
    eviter = ds.events()
    evt = eviter.next()
    rnum = evt.run()

    for key in evt.keys() : print key

    det = detector_factory(src, env)

    try :
        nda = det.pedestals(rnum)
        print '\nnda:\n', nda
        print 'nda.dtype: %s nda.shape: %s' % (nda.dtype, nda.shape)
    except :
        print 'WARNING: det.pedestals(rnum) is not available for dataset: %s and source : %s' % (dsname, src) 

    try :
        t0_sec = time()
        nda = det.raw(evt)
        print '\nConsumed time to get raw data (sec) =', time()-t0_sec
        print 'nda:\n', nda.flatten()[0:10]
    except :
        print 'WARNING: det.raw(evt) is not available for dataset: %s and source : %s' % (dsname, src) 

    sys.exit ('Self test is done')


def test2():
    # test EVR names
    import psana

    #ds = psana.DataSource('exp=amoj5415:run=43')
    ds = psana.DataSource('exp=xpptut15:run=54')
    env = ds.env()

    names = ['cspad',
             'XppGon.0:Cspad.0',
             'evr0',
             'NoDetector.0:Evr.0',
             'FEEGasDetEnergy',
             'EBeam',
             #'DIAG:FEE1:202:241:Data',
             #'XTCAV_yag_status',
             #'badname',
             ]

    for name in names:
        evrdet = detector_factory(name, env)
        print name, '-->', type(evrdet)

        for evt in ds.events():
            print evrdet(evt)
            break

    return 

if __name__ == '__main__':
    test2()

