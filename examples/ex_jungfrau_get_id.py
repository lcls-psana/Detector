#!/usr/bin/env python
#----------
import sys
import psana
from Detector.UtilsJungfrau import id_jungfrau, id_jungfrau_from_config
from Detector.PyDataAccess import get_jungfrau_data_object, get_jungfrau_config_object
#----------

def jungfrau_id(dsname, srcname) :

    print 50*'_'
    
    ds  = psana.DataSource(dsname)
    src = psana.Source(srcname)
    env = ds.env()
    
    print('id_jungfrau(env, src, 0)       : %s' % id_jungfrau(env, src, iseg=0))
    print('id_jungfrau(env, src, 1)       : %s' % id_jungfrau(env, src, iseg=1))
    print('id_jungfrau(env, src)          : %s' % id_jungfrau(env, src))
    print('id_jungfrau(env, "Jung")       : %s' % id_jungfrau(env, 'Jung'))
    print('id_jungfrau(env, "Jungfrau")   : %s' % id_jungfrau(env, 'Jungfrau'))
    print('id_jungfrau(env, "jungfrau4M") : %s' % id_jungfrau(env, 'jungfrau4M'))

    if True :
        co = get_jungfrau_config_object(ds.env(), src)
        print('id_jungfrau_from_config(co,0): %s' % id_jungfrau_from_config(co,0))
        print('id_jungfrau_from_config(co,1): %s' % id_jungfrau_from_config(co,1))
        print('id_jungfrau_from_config(co)  : %s' % id_jungfrau_from_config(co))

#----------

def jungfrau_id_guaranteed() :
    # Garanteed data availability example:
    print 50*'_'
    
    # event_keys -d exp=xpptut15:run=410 -m2
    ds  = psana.DataSource('exp=xpptut15:run=410')
    print('id_jungfrau xpptut15:run=410   : %s' % id_jungfrau(ds.env(), 'Jungfrau'))
    
    # event_keys -d exp=xpptut15:run=430 -m2
    ds  = psana.DataSource('exp=xpptut15:run=430')
    print('id_jungfrau xpptut15:run=430   : %s' % id_jungfrau(ds.env(), 'Jungfrau'))

#----------

if __name__ == "__main__" :
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    if   tname=='0' : jungfrau_id_guaranteed()
    elif tname=='1' : jungfrau_id('exp=xpptut15:run=410', 'Jungfrau512k')
    elif tname=='2' : jungfrau_id('exp=xpptut15:run=430', 'Jungfrau1M')
    elif tname=='3' : jungfrau_id('/reg/d/psdm/xpp/xpptut13/scratch/cpo/e968-r0177-s01-c00.xtc','DetLab.0:Jungfrau.2')
    #MISSING DATA
    #elif tname=='1' : jungfrau_id('exp=cxi11216:run=9',    'CxiEndstation.0:Jungfrau.0', )
    #elif tname=='2' : jungfrau_id('exp=xcsx22015:run=503', 'XcsEndstation.0:Jungfrau.0', )
    #elif tname=='3' : jungfrau_id('exp=xcsls3716:run=631', 'XcsEndstation.0:Jungfrau.0', )
    else : sys.exit('Not recognized test name: "%s"' % tname)

#----------
