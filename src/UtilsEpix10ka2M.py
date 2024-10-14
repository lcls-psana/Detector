
"""
Methiods for Epix10kaQuad, Epix10ka2M combined from 4, 16 of Epix10ka panels, respectively.
"""
from __future__ import print_function
from __future__ import division

import logging
logger = logging.getLogger(__name__)
from Detector.PyDataAccess import get_epix10ka_any_config_object, get_epix10ka2m_data_object, get_epix_data_object
from Detector.UtilsEpix import id_epix
import numpy as np

def print_object_dir(o):
    print('dir(%s):\n  %s' % (str(o), ',\n  '.join([v for v in dir(o) if v[:1]!='_'])))


def id_epix10ka(co, ielem=0):
    """Returns Epix10ka2M Id as a string,
       e.g., 3925999616-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719
       co is psana.Epix.Config10kaQuadV1 or psana.Epix.Config10ka2MV1
    """
    quad_shape = getattr(co, "quad_shape", None)
    eco = co.elemCfg(ielem)
    qco = co.quad() if quad_shape is None else co.quad(ielem//4)

    fmt2 = '%010d-%010d'
    zeros = fmt2 % (0,0)
    version = '%010d' % (co.Version) if getattr(co, "Version", None) is not None else '%010d' % 0
    carrier = fmt2 % (eco.carrierId0(), eco.carrierId1())\
              if getattr(eco, "carrierId0", None) is not None else zeros
    digital = fmt2 % (qco.digitalCardId0(), qco.digitalCardId1())\
              if getattr(qco, "digitalCardId0", None) is not None else zeros
    analog  = zeros
    return '%s-%s-%s-%s' % (version, carrier, digital, analog)


def ids_epix10ka2m(co):
    """Returns list of epix10ka panel ids for any composite detector config object.
       Works with epix10ka, epix10kaquad, and epix10ka2m
    """
    # looking for epix10kaquad or epix10ka2m
    o = getattr(co, "numberOfElements", None)
    if o is None:
        # try psana.Epix.Config10kaV1
        id = id_epix(co)
        return None if id is None else [id,]
    ids = [id_epix10ka(co, ielem=i) for i in range(co.numberOfElements())]
    return ids

def id_epix10ka2m_for_env_det(env, det):
    #print(dir(det))
    #print('det has source:', hasattr(det, 'source'))
    co = get_epix10ka_any_config_object(env, det.source) if hasattr(det, 'source') else None
    return str(id_epix10ka2m(co)) if co is not None else None

def id_epix10ka2m(co):
    return '_'.join(ids_epix10ka2m(co))

ids_epix10kaquad = ids_epix10ka2m
id_epix10kaquad = id_epix10ka2m


def table_nxn_epix10ka_from_ndarr(nda):
    """returns table of epix10ka panels shaped as (nxn)
       generated from epix10ka array shaped as (N, 352, 384) in data.
    """
    gapv = 20
    segsize = 352*384
    a = np.array(nda) # make a copy

    if a.size == segsize:
       a.shape = (352,384)
       return a

    elif a.size == 4*segsize:
       logger.warning('quad panels are stacked as [(3,2),(1,0)]')
       sh = a.shape = (4,352,384)
       return np.vstack([np.hstack([a[3],a[2]]), np.hstack([a[1],a[0]])])
       #sh = a.shape = (2,2*352,384)
       #return np.hstack([a[q,:] for q in range(sh[0])])

    elif a.size == 16*segsize:
       sh = a.shape = (4,4*352,384)
       return np.hstack([a[q,:] for q in range(sh[0])])

    elif a.size == 7*4*segsize:
       logger.warning('quad panels are stacked as [(3,2),(1,0)]')
       agap = np.zeros((gapv,2*384))
       sh = a.shape = (7,4,352,384)
       return np.vstack([np.vstack([np.hstack([a[g,3],a[g,2]]), np.hstack([a[g,1],a[g,0]]), agap]) for g in range(7)])
       #sh = a.shape = (7,2,2*352,384)
       #return np.vstack([np.vstack([np.hstack([a[g,q,:] for q in range(2)]), agap]) for g in range(7)])

    elif a.size == 7*16*segsize:
       agap = np.zeros((gapv,4*384))
       sh = a.shape = (7,4,4*352,384)
       return np.vstack([np.vstack([np.hstack([a[g,q,:] for q in range(4)]), agap]) for g in range(7)])

    else:
       from psana.pyalgos.generic.NDArrUtils import reshape_to_2d
       return reshape_to_2d(a)



if __name__ == "__main__":

  import psana
  from pyimgalgos.GlobalUtils import print_ndarr

  EVENTS  = 5


  def test_config_epix10ka2m(tname):

    ssrc, dsname = ex_source_dsname(tname)
    print('Test: %s\n  dataset: %s\n  source: %s' % (tname, dsname, ssrc))

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
    if datao is None: datao = get_epix_data_object(evt, src)

    print('epix10ka2m_config: %s' % str(confo))
    print('epix10ka2m_data : %s' % str(datao))
    #print_object_dir(confo)

    ids = ids_epix10ka2m(confo)
    for i,id in enumerate(ids): print('elem %2d: %s' % (i,id))

    #print_object_dir(datao)
    print_ndarr(datao.frame(), 'datao.frame()')


  # See Detector.examples.ex_source_dsname
  def ex_source_dsname(tname):
    src, dsn = None, None
    if   tname == '1': src, dsn = 'MecTargetChamber.0:Epix10ka.1',\
                                  '/reg/g/psdm/detector/data_test/types/0033-MecTargetChamber.0-Epix10ka.1.xtc'
    elif tname == '2': src, dsn = 'NoDetector.0:Epix10kaQuad.0',\
                                  '/reg/g/psdm/detector/data_test/types/0032-NoDetector.0-Epix10kaQuad.0.xtc'
    elif tname == '3': src, dsn = 'NoDetector.0:Epix10ka2M.0',\
                                  '/reg/g/psdm/detector/data_test/types/0034-NoDetector.0-Epix10ka2M.0.xtc'
    elif tname == '4': src, dsn = 'DetLab.0:Epix10ka2M.0',\
                                  '/reg/g/psdm/detector/data_test/types/0035-DetLab.0-Epix10ka2M.0.xtc' # (16, 352, 384)

    else: sys.exit('Non-implemented sample for test number # %s' % tname)
    return src, dsn


if __name__ == "__main__":
    import sys

    print(80*'_')
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    if   tname == '1': test_config_epix10ka2m(tname)
    elif tname == '2': test_config_epix10ka2m(tname)
    elif tname == '3': test_config_epix10ka2m(tname)
    elif tname == '4': test_config_epix10ka2m(tname)
    else: sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit('End of %s' % sys.argv[0])

# EOF
