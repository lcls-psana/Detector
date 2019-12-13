from __future__ import print_function

# Example of code for ipython

import psana
nrun = 9 #  9, 11, 12
dsname = 'exp=cxi11216:run=%d' % nrun # (1, 512, 1024)
s_src = 'CxiEndstation.0:Jungfrau.0'
print('Example for\n  dataset: %s\n  source : %s' % (dsname, s_src))

src = psana.Source(s_src)
ds  = psana.DataSource(dsname)
env = ds.env()

r = next(ds.runs())
evt = next(ds.events())

cfg = env.configStore()
co  = cfg.get(psana.Jungfrau.ConfigV1, src)
co2 = cfg.get(psana.Jungfrau.ConfigV2, src)
co3 = cfg.get(psana.Jungfrau.ConfigV3, src)

gm = co.gainMode()
#Out[13]: psana.Jungfrau.GainMode.ForcedGain1

det = psana.Detector(s_src, env)
raw = det.raw(evt)

raw.shape
#Out[8]: (1, 512, 1024)

raw.dtype
#Out[9]: dtype('uint16')

gm.imag
#Out[26]: 0

gm.name
#Out[14]: 'ForcedGain1'

gm.numerator
#Out[24]: 3

gm.denominator
#Out[25]: 1

gm.names
#Out[22]: 
#{'FixedGain1': psana.Jungfrau.GainMode.FixedGain1,
# 'FixedGain2': psana.Jungfrau.GainMode.FixedGain2,
# 'ForcedGain1': psana.Jungfrau.GainMode.ForcedGain1,
# 'ForcedGain2': psana.Jungfrau.GainMode.ForcedGain2,
# 'HighGain0': psana.Jungfrau.GainMode.HighGain0,
# 'Normal': psana.Jungfrau.GainMode.Normal}

gm.values
#Out[25]: 
#{0: psana.Jungfrau.GainMode.Normal,
# 1: psana.Jungfrau.GainMode.FixedGain1,
# 2: psana.Jungfrau.GainMode.FixedGain2,
# 3: psana.Jungfrau.GainMode.ForcedGain1,
# 4: psana.Jungfrau.GainMode.ForcedGain2,
# 5: psana.Jungfrau.GainMode.HighGain0}

ds = DataSource('exp=...:run=12,13,14')
for run in ds.runs():
    for evt in run.events():
      pass

ds = DataSource('exp=...:run=12,13,14')
for run in ds.runs():
    for step in run.steps():
        for evt in step.events():
	  pass

ds = DataSource('exp=...:run=12,13,14')
for step in ds.steps():
    for evt in step.events():
      pass


evt = next(ds.events())
dato = evt.get(psana.Jungfrau.ElementV1, src)

#------------------------------

#def get_jungfrau_data_object(evt, src) :
#    """get jungfrau data object
#    """
#    o = evt.get(psana.Jungfrau.ElementV1, src)
#    if o is not None : return o
#    return None

#def get_jungfrau_config_object(env, src) :
#    cfg = env.configStore()
#    o = cfg.get(psana.Jungfrau.ConfigV1, src)
#    if o is not None : return o
#    return None

#------------------------------
#exp=xcs11116:run=18
#event_keys -d exp=xcs11116:run=18 -m 2
#EventKey(type=psana.Epics.ConfigV1, src='DetInfo(EpicsArch.0:NoDevice.0)')
#EventKey(type=None, src='DetInfo(XcsEndstation.0:Jungfrau.0)', alias='jungfrau1M')

#exp=xcslr6316:run=17
#event_keys -d exp=xcslr6316:run=17 -m 2
#EventKey(type=psana.Epix.Config100aV2, src='DetInfo(XcsEndstation.0:Epix100a.5)', alias='epix_ladm_1')
#EventKey(type=None, src='DetInfo(XcsEndstation.0:Jungfrau.1)', alias='jungfrau512k')

#exp=xcsls3716:run=631
#event_keys -d exp=xcsls3716:run=631 -m 2
#EventKey(type=None, src='DetInfo(XcsEndstation.0:Jungfrau.0)', alias='jungfrau1M')
#EventKey(type=psana.Jungfrau.ConfigV3, src='DetInfo(XcsEndstation.0:Jungfrau.0)', alias='jungfrau1M')

#ds = psana.DataSource('exp=xcsx22015:run=555')
#event_keys -d exp=xcsx22015:run=555 -m 2
#EventKey(type=None, src='DetInfo(XcsEndstation.0:Jungfrau.0)', alias='jungfrau1M')
#EventKey(type=psana.Jungfrau.ConfigV2, src='DetInfo(XcsEndstation.0:Jungfrau.0)', alias='jungfrau1M')

#ds  = psana.DataSource('exp=cxi11216:run=54')
# event_keys -d exp=cxi11216:run=54 -m 2
#EventKey(type=None, src='DetInfo(CxiEndstation.0:Jungfrau.0)', alias='Jungfrau')
#EventKey(type=psana.Jungfrau.ConfigV1, src='DetInfo(CxiEndstation.0:Jungfrau.0)', alias='Jungfrau')

from Detector.PyDataAccess import get_jungfrau_data_object, get_jungfrau_config_object
import psana

ds  = psana.DataSource('exp=xcsls3716:run=631')
src = psana.Source('XcsEndstation.0:Jungfrau.0')
co = ds.env().configStore().get(psana.Jungfrau.ConfigV3, src)
#co = get_jungfrau_config_object(ds.env(), src)

nmodules = co.numberOfModules()
print(('numberOfModules', co.numberOfModules()))
for i in range(nmodules) :
    m = co.moduleConfig(i)
    print(('  firmwareVersion', m.firmwareVersion()))         
    print(('  moduleVersion', m.moduleVersion()))      
    print(('  serialNumber', m.serialNumber())) 

env = ds.env()
exp = env.experiment()
cdir = env.calibDir()
#calibs = env.calibStore()
cs = env.configStore()
keys = cs.keys()
key_jf_data = keys[16]
key_jf_conf = keys[17] # EventKey(type=psana.Jungfrau.ConfigV3, src='DetInfo(XcsEndstation.0:Jungfrau.0)', alias='jungfrau1M')
a = key_jf_conf.alias()    # 'jungfrau1M'
s = key_jf_conf.src()      # DetInfo(XcsEndstation.0:Jungfrau.0)
t = key_jf_conf.type()     # psana.Jungfrau.ConfigV3

s.detName() # 'XcsEndstation'
s.detId() # 0
s.devName() # 'Jungfrau'
s.devId() # 0
detname = '%s-%d-%s-%d' % (s.detName(), s.detId(), s.devName(), s.devId()) # 'XcsEndstation-0-Jungfrau-0'

import psana
ds  = psana.DataSource('exp=cxi11216:run=9')
src = psana.Source('CxiEndstation.0:Jungfrau.0')
co = ds.env().configStore().get(psana.Jungfrau.ConfigV1, src)
#co = get_jungfrau_config_object(ds.env(), src)

import psana
ds  = psana.DataSource('exp=xcsx22015:run=503:smd') # dark runs 503,504,505
src = psana.Source('XcsEndstation.0:Jungfrau.0')
co = ds.env().configStore().get(psana.Jungfrau.ConfigV2, src)
#co = get_jungfrau_config_object(ds.env(), src)

print('Content of Jungfrau.ConfigV1:')

print('numberOfModules         ', co.numberOfModules())
print('numberOfRowsPerModule   ', co.numberOfRowsPerModule())
print('numberOfColumnsPerModule', co.numberOfColumnsPerModule())

print('biasVoltage             ',co.biasVoltage())
print('gainMode                ',co.gainMode())
print('SpeedMode               ',co.SpeedMode())
print('TypeId                  ',co.TypeId)
print('exposureTime            ',co.exposureTime())
print('GainMode                ',co.GainMode())
print('speedMode               ',co.speedMode())
print('Version                 ',co.Version)
print('frameSize               ',co.frameSize())
print('numPixels               ',co.numPixels())
print('triggerDelay            ',co.triggerDelay())          

#------------------------------
#------------------------------
#------------------------------
#------------------------------
