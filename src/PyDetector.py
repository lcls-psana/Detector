#--------------------------------------------------------------------------
# File and Version Information:
#  $Id$
#
# Description:
#  module PyDetector
#--------------------------------------------------------------------------
"""Method detector_factory(src,env) returns instance of the detector data accessor. 

   Method detector_factory(src,env) switches between detector data access objects depending on source parameter.
   Currently implemented detector data access classes:
   \n :py:class:`Detector.AreaDetector`  - access to area detector data
   \n :py:class:`Detector.WFDetector`    - access to waveform detector data
   \n :py:class:`Detector.EvrDetector`   - access to EVR data
   \n :py:class:`Detector.DdlDetector`   - access to DDL data
   \n :py:class:`Detector.EpicsDetector` - access to EPICS data

Usage::

    # Import
    import psana

    # Input parameters
    # str object for data source can be defined using DAQ detector name
    src = 'XppGon.0:Cspad.0' # or its alias 'cspad'
    # The list of available detector names and alieses for data set can be printed by the command like
    # psana -m EventKeys -n 5 exp=xpptut15:run=54

    # env object can be defined from data set
    ds = psana.DataSource('exp=xpptut15:run=54')
    env = ds.env()

    # Create detector object
    det = psana.Detector(src, env)

    # in ipython the list of det methods can be seen using "tab completion" operation - type "det." and click on Tab button.

A set of det object methods depends on type of the returned object, see for example
:py:class:`Detector.AreaDetector`, :py:class:`Detector.WFDetector`, :py:class:`Detector.EvrDetector`, etc.
 
This software was developed for the LCLS project.
If you use all or part of it, please give an appropriate acknowledgment.

@version $Id$

@author Lane, Thomas Joseph - "Sacramentum hoc revelatum est"
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

    PARAMETERS

    source_string : str
        A string identifying a piece of data to access, examples include:
          - 'cspad'                  # a DAQ detector alias
          - 'XppGon.0:Cspad.0'       # a DAQ detector full-name
          - 'DIAG:FEE1:202:241:Data' # an EPICS variable name (or alias)
          - 'EBeam'                  # a BldInfo identifier\n
        The idea is that you should be able to pass something that makes
        sense to you as a human here, and you automatically get the right
        detector object in return.

    env : psana.Env
        The psana environment object associated with the psana.DataSource
        you are interested in (from method DataSource.env()).

    RETURNS

    A psana-python detector object. Try detector(psana.Event) to
    access your data.

    HOW TO GET MORE HELP

    The Detector method returns an object that has methods that
    change depending on the detector type. To see help for a particular
    detector type execute commands similar to the following

    env = DataSource('exp=xpptut15:run=54').env()
    det = Detector('cspad',env)

    and then use the standard ipython "det?" command (and tab completion) to
    see the documentation for that particular detector type.
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

    if isWFDetector(source_string):
        return WFDetector(source_string, env)
    elif isEvrDetector(source_string):
        return EvrDetector(source_string, env)
    elif isAreaDetector(source_string):
        return AreaDetector(source_string, env)
    else:
        raise ValueError('Could not interpret "%s" as any known detector' % source_string)
    
    return

##-----------------------------

def isWFDetector(source_string):
    """
    Returns True if the source is a waveform detector
    """
    # map detector names to their respective detector class implementations
    dettype = gu.det_type_from_source(source_string)
    if dettype == gu.ACQIRIS or dettype == gu.IMP: return True
    return False

##-----------------------------

def isEvrDetector(source_string):
    """
    Returns True if the source is an Evr detector
    """
    # map detector names to their respective detector class implementations
    dettype = gu.det_type_from_source(source_string)
    if dettype == gu.EVR: return True
    return False

##-----------------------------

def isAreaDetector(source_string):
    """
    Returns True if the source is an area detector
    """
    # map detector names to their respective detector class implementations
    dettype = gu.det_type_from_source(source_string)
    if dettype in [gu.CSPAD, gu.CSPAD2X2, gu.PRINCETON, gu.PNCCD,
                   gu.TM6740, gu.OPAL1000, gu.OPAL2000, gu.OPAL4000, gu.OPAL8000,
                   gu.ORCAFL40, gu.EPIX, gu.EPIX10K, gu.EPIX100A, gu.FCCD960,
                   gu.ANDOR, gu.QUARTZ4A150, gu.RAYONIX]: return True
    return False

##-----------------------------

def test1(ntest):
    """Test of the detector_factory(src, env) for AreaDetector and WFDetector classes.
    """
    from time import time
    import psana

    dsname, src                  = 'exp=xpptut15:run=54',  'XppGon.0:Cspad.0'
    if   ntest==2  : dsname, src = 'exp=meca1113:run=376', 'MecTargetChamber.0:Cspad2x2.1'
    elif ntest==3  : dsname, src = 'exp=amob5114:run=403', 'Camp.0:pnCCD.0'
    elif ntest==4  : dsname, src = 'exp=xppi0614:run=74',  'NoDetector.0:Epix100a.0'
    elif ntest==5  : dsname, src = 'exp=sxri0414:run=88',  'SxrEndstation.0:Acqiris.2'
    elif ntest==6  : dsname, src = 'exp=cxii0215:run=49',  'CxiEndstation.0:Imp.1'
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

##-----------------------------

def test2():
    """Test of the detector_factory(src, env) for EvrDetector, DdlDetectorand and EpicsDetector classes.
    """
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

##-----------------------------

if __name__ == '__main__':
    import sys

    try    : ntest = int(sys.argv[1]) if len(sys.argv)>1 else 0
    except : raise ValueError('First input parameter "%s" is expected to be empty or integer test number' % sys.argv[1])
    print 'Test# %d' % ntest

    if len(sys.argv)<2 : test2()
    else               : test1(ntest)

    sys.exit ('Self test is done')

##-----------------------------
