#------------------------------
"""
:py:class:`UtilsEpix` contains utilities for epix100a and epix10ka detectors
============================================================================

    Epix gain range coding ????

    bit: 15,14,...,0   Gain range, ind
          0, 0         Normal,       0
          0, 1         ForcedGain1,  1
          1, 1         FixedGain2,   2

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2018-02-22 by Mikhail Dubrovin
"""
#------------------------------

def id_epix(config_obj) :
    """Returns Epix100 Id as a string, e.g., 3925999616-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719"""

    o = config_obj
    fmt2 = '%010d-%010d'
    zeros = fmt2 % (0,0)
    version = '%010d' % (o.version()) if getattr(o, "version", None) is not None else '%010d' % 0
    carrier = fmt2 % (o.carrierId0(), o.carrierId1())\
              if getattr(o, "carrierId0", None) is not None else zeros
    digital = fmt2 % (o.digitalCardId0(), o.digitalCardId1())\
              if getattr(o, "digitalCardId0", None) is not None else zeros
    analog  = fmt2 % (o.analogCardId0(), o.analogCardId1())\
              if getattr(o, "analogCardId0", None) is not None else zeros
    return '%s-%s-%s-%s' % (version, carrier, digital, analog)

#------------------------------

if __name__ == "__main__" :
  def do_test() :
    import psana
    
    nrun = 377
    dsname = 'exp=mfxx32516:run=%d' % nrun
    s_src = 'MfxEndstation.0:Epix10ka.0'
    #s_src1 = 'MfxEndstation.0:Epix10ka.1'
    print 'Example for\n  dataset: %s\n  source : %s' % (dsname, s_src)

    ds = psana.DataSource(dsname)
    det = psana.Detector(s_src) # 'Epix10ka_0'
    det = psana.Detector('MfxEndstation.0:Epix10ka.1') # 'Epix10ka_1'

    env = ds.env()
    evt = ds.events().next()
    src = psana.Source(s_src)

    confo = env.configStore().get(psana.Epix.Config10kaV1, src)
    datao = evt.get(psana.Epix.ElementV3, src)

    epix_name = 'epix-%s' % id_epix(confo)
    print('epix_name: %s' % epix_name)

#------------------------------

if __name__ == "__main__" :
    do_test()

#------------------------------
