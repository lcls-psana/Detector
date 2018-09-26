####!/usr/bin/env python
#--------------------------------
import sys
import psana
from Detector.UtilsJungfrau import id_jungfrau, id_jungfrau_from_config
#--------------------------------

print 50*'_'

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 3

# get detector and dataset names for jungfrau config objects of version V1, V2, and V3
srcname, dsname =\
  ('CxiEndstation.0:Jungfrau.0', 'exp=cxi11216:run=9')    if ntest == 1 else\
  ('XcsEndstation.0:Jungfrau.0', 'exp=xcsx22015:run=503') if ntest == 2 else\
  ('XcsEndstation.0:Jungfrau.0', 'exp=xcsls3716:run=631')

ds  = psana.DataSource(dsname)
src = psana.Source(srcname)
env = ds.env()

print('id_jungfrau(env, src, 0)       : %s' % id_jungfrau(env, src, iseg=0))
print('id_jungfrau(env, src, 1)       : %s' % id_jungfrau(env, src, iseg=1))
print('id_jungfrau(env, src)          : %s' % id_jungfrau(env, src))
print('id_jungfrau(env, "Jung")       : %s' % id_jungfrau(env, 'Jung'))
print('id_jungfrau(env, "jungfrau1M") : %s' % id_jungfrau(env, 'jungfrau1M'))
print('id_jungfrau(env, "Jungfrau")   : %s' % id_jungfrau(env, 'Jungfrau'))

#--------------------------------

if False :
    from Detector.PyDataAccess import get_jungfrau_data_object, get_jungfrau_config_object
    co = get_jungfrau_config_object(ds.env(), src)
    print('id_jungfrau_from_config(co,0): %s' % id_jungfrau_from_config(co,0))
    print('id_jungfrau_from_config(co,1): %s' % id_jungfrau_from_config(co,1))
    print('id_jungfrau_from_config(co)  : %s' % id_jungfrau_from_config(co))

#--------------------------------
# Garanteed data availability example:
print 50*'_'

# event_keys -d exp=xpptut15:run=410 -m2
# EventKey(type=psana.Jungfrau.ConfigV3, src='DetInfo(MfxEndstation.0:Jungfrau.1)', alias='Jungfrau512k')
ds  = psana.DataSource('exp=xpptut15:run=410')
print('id_jungfrau xpptut15:run=410   : %s' % id_jungfrau(ds.env(), 'Jungfrau'))

# event_keys -d exp=xpptut15:run=430 -m2
# EventKey(type=psana.Jungfrau.ConfigV3, src='DetInfo(MfxEndstation.0:Jungfrau.0)', alias='Jungfrau1M')
ds  = psana.DataSource('exp=xpptut15:run=430')
print('id_jungfrau xpptut15:run=430   : %s' % id_jungfrau(ds.env(), 'Jungfrau'))

#--------------------------------
