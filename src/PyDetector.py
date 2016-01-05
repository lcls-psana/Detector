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

TJL To Do
---------
- IPIMB
- explicitly check types?
- gas det (maybe)
- hook in psgeom to AreaDetector
"""
#------------------------------
__version__ = "$Revision$"
##-----------------------------

import _psana
import re
import Detector.DetectorTypes as dt
from Detector.EpicsDetector import EpicsDetector

def det_and_dev_from_string(source_string):
    """
    Interpret a string like 'DetInfo(CxiDs2.0:Cspad.0)' in terms of:
    
        detector_type --> 'CxiDs2'
        detector_id   --> 0
        device_type   --> 'Cspad'
        device_id     --> 0

    Returns
    -------
    detector_type: str
    detector_id:   int
    device_type:   str
    device_id:     int
    """
    m = re.search('(\w+).(\d)\:(\w+).(\d)', source_string)
    if not m:
        raise ValueError('Could not interpret source string: "%s", '
                         'check your formatting and alias list' % source_string)
    mg = m.groups()
    return mg[0], int(mg[1]), mg[2], int(mg[3])


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

    # > see if the source_string is an epics PV name
    epics = env.epicsStore()
    if source_string in epics.names(): # both names & aliases
        return EpicsDetector(source_string, env)


    # > see if the source_string is an alias
    amap = env.aliasMap()
    alias_src = amap.src(source_string) # string --> DAQ-style psana.Src
                
    # if it is an alias, look up the full name
    if amap.alias(alias_src) != '':         # alias found
        source_string = str(alias_src)


    # > look up what Detector class we should use
    if source_string in dt.bld_info.keys(): # if source is a BldInfo...
        dettype = dt.bld_info[source_string]

    else:                                   # assume source is a DetInfo...
        _, _, device_type, _ = det_and_dev_from_string(source_string)
        if device_type in dt.detectors.keys():
            dettype = dt.detectors[device_type]
        else:
            raise KeyError('Unknown DetInfo device type: %s (source: %s)'
                           '' % (device_type, source_string))


    # > create an instance of the determined detector type & return it
    det_instance = dettype(source_string, env)

    return det_instance


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
             'dev.0:det.0',
             'notadet',
             #'DIAG:FEE1:202:241:Data',
             #'XTCAV_yag_status',
             #'badname',
             ]

    for name in names:
        det = detector_factory(name, env)
        print name, '-->', type(det)

        for evt in ds.events():
            print det(evt)
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
