
#------------------------------
""" 
Methiods for Epix10kaQuad, Epix10ka2M combined from 4, 16 of Epix10ka panels, respectively.
"""
from __future__ import print_function
from __future__ import division

import logging
logger = logging.getLogger(__name__)
#from Detector.PyDataAccess import get_epix_data_object, get_epix10ka_config_object
from Detector.PyDataAccess import get_epix10ka_any_config_object, get_epix10ka2m_data_object, get_epix_data_object
from Detector.UtilsEpix import id_epix
#------------------------------

#from Detector.UtilsEpix10ka import calib_epix10ka_any
#calib_epix10ka2m   = calib_epix10ka_any
#calib_epix10kaquad = calib_epix10ka_any

#------------------------------

def print_object_dir(o) :
    print('dir(%s):\n  %s' % (str(o), ',\n  '.join([v for v in dir(o) if v[:1]!='_'])))

#------------------------------

def id_epix10ka(co, ielem=0) :
    """Returns Epix10ka2M Id as a string, 
       e.g., 3925999616-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719
       co is psana.Epix.Config10kaQuadV1 or psana.Epix.Config10ka2MV1
    """

    quad_shape = getattr(co, "quad_shape", None)
    eco = co.elemCfg(ielem)
    qco = co.quad() if quad_shape is None else co.quad(ielem//4)

    #print '%s\nQuad:%d element:%d' % (50*'=',iquad, ielem)
    #print 'quad_shape %s' % str(quad_shape)
    #print 'XXXX dco', co
    #print 'XXXX eco', eco
    #print 'XXXX qco', qco
    #print_object_dir(eco)
    #print 'XXXX eco.carrierId0/1:', eco.carrierId0(), eco.carrierId1()  
    #print 'XXXX qco.digitalCardId0/1():', qco.digitalCardId0(), qco.digitalCardId1()   

    fmt2 = '%010d-%010d'
    zeros = fmt2 % (0,0)
    version = '%010d' % (co.Version) if getattr(co, "Version", None) is not None else '%010d' % 0
    carrier = fmt2 % (eco.carrierId0(), eco.carrierId1())\
              if getattr(eco, "carrierId0", None) is not None else zeros
    digital = fmt2 % (qco.digitalCardId0(), qco.digitalCardId1())\
              if getattr(qco, "digitalCardId0", None) is not None else zeros
    #analog  = fmt2 % (qco.analogCardId0(), qco.analogCardId1())\
    #          if getattr(o, "analogCardId0", None) is not None else zeros
    analog  = zeros
    return '%s-%s-%s-%s' % (version, carrier, digital, analog)

#------------------------------

def ids_epix10ka2m(co) :
    """Returns list of epix10ka panel ids for any composite detector config object.
       Works with epix10ka, epix10kaquad, and epix10ka2m
    """
    # looking for epix10kaquad or epix10ka2m
    o = getattr(co, "numberOfElements", None)
    if o is None :
        # try psana.Epix.Config10kaV1
        id = id_epix(co)
        return None if id is None else [id,]
    ids = [id_epix10ka(co, ielem=i) for i in range(co.numberOfElements())]
    return ids

#------------------------------

ids_epix10kaquad = ids_epix10ka2m

#------------------------------
#------------------------------
#------------------------------
#------------------------------

if __name__ == "__main__" :

  import psana
  from pyimgalgos.GlobalUtils import print_ndarr

  EVENTS  = 5

#------------------------------

  def test_config_epix10ka2m(tname) :
    
    ssrc, dsname = ex_source_dsname(tname)
    print('Test: %s\n  dataset: %s\n  source : %s' % (tname, dsname, ssrc))

    ds = psana.DataSource(dsname)
    det = psana.Detector(ssrc)
    env = ds.env()
    evt = next(ds.events())
    src = psana.Source(ssrc)

    #co = env.configStore().get(psana.Epix.Config10kaQuadV1, src)
    #co = env.configStore().get(psana.Epix.Config10ka2MV1, src)
    #confo = env.configStore().get(psana.Epix.Config10kaV1, src)
    #datao = evt.get(psana.Epix.ElementV3, src)
    confo = get_epix10ka_any_config_object(env, src)
    datao = get_epix10ka2m_data_object(evt, src)
    if datao is None : datao = get_epix_data_object(evt, src)

    print('epix10ka2m_config: %s' % str(confo))
    print('epix10ka2m_data  : %s' % str(datao))
    #print_object_dir(confo)

    #epix_name = 'epix-%s' % id_epix10ka(confo, ielem=0)
    #print('epix_name: %s' % epix_name)

    ids = ids_epix10ka2m(confo)
    for i,id in enumerate(ids) : print('elem %2d: %s' % (i,id))

    #print_object_dir(datao)
    print_ndarr(datao.frame(), 'datao.frame()')

#------------------------------

  # See Detector.examples.ex_source_dsname
  def ex_source_dsname(tname) : 
    src, dsn = None, None
    if   tname == '1': src, dsn = 'MecTargetChamber.0:Epix10ka.1',\
                                  '/reg/g/psdm/detector/data_test/types/0033-MecTargetChamber.0-Epix10ka.1.xtc'
    elif tname == '2': src, dsn = 'NoDetector.0:Epix10kaQuad.0',\
                                  '/reg/g/psdm/detector/data_test/types/0032-NoDetector.0-Epix10kaQuad.0.xtc' 
    elif tname == '3': src, dsn = 'NoDetector.0:Epix10ka2M.0',\
                                  '/reg/g/psdm/detector/data_test/types/0034-NoDetector.0-Epix10ka2M.0.xtc'
    elif tname == '4': src, dsn = 'DetLab.0:Epix10ka2M.0',\
                                  '/reg/g/psdm/detector/data_test/types/0035-DetLab.0-Epix10ka2M.0.xtc' # (16, 352, 384)

    else : sys.exit('Non-implemented sample for test number # %s' % tname)
    return src, dsn

#------------------------------

if __name__ == "__main__" :
    import sys

    print(80*'_')
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    if   tname == '1' : test_config_epix10ka2m(tname)
    elif tname == '2' : test_config_epix10ka2m(tname)
    elif tname == '3' : test_config_epix10ka2m(tname)
    elif tname == '4' : test_config_epix10ka2m(tname)
    else : sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit('End of %s' % sys.argv[0])

#------------------------------
