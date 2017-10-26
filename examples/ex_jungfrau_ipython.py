
# Example of code for ipython

import psana
nrun = 9 #  9, 11, 12
dsname = 'exp=cxi11216:run=%d' % nrun # (1, 512, 1024)
s_src = 'CxiEndstation.0:Jungfrau.0'
print 'Example for\n  dataset: %s\n  source : %s' % (dsname, s_src)

src = psana.Source(s_src)
ds  = psana.DataSource(dsname)
env = ds.env()

r = ds.runs().next()
evt = ds.events().next()

cfg = env.configStore()
co = cfg.get(psana.Jungfrau.ConfigV1, src)

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

ds = DataSource('exp=...:run=12,13,14')
for run in ds.runs():
    for step in run.steps():
        for evt in step.events():

ds = DataSource('exp=...:run=12,13,14')
for step in ds.steps():
    for evt in step.events():


evt = ds.events().next()
dato = evt.get(psana.Jungfrau.ElementV1, src)

#------------------------------

def get_jungfrau_data_object(evt, src) :
    """get jungfrau data object
    """
    o = evt.get(psana.Jungfrau.ElementV1, src)
    if o is not None : return o
    return None

def get_jungfrau_config_object(env, src) :
    cfg = env.configStore()
    o = cfg.get(psana.Jungfrau.ConfigV1, src)
    if o is not None : return o
    return None

#------------------------------

import psana
ds  = psana.DataSource('exp=cxi11216:run=9')
src = psana.Source('CxiEndstation.0:Jungfrau.0')

import psana
ds  = psana.DataSource('exp=xcsx22015:run=503:smd') # dark runs 503,504,505
src = psana.Source('XcsEndstation.0:Jungfrau.0')

env = ds.env()
#co = env.configStore().get(psana.Jungfrau.ConfigV1, src)
co = env.configStore().get(psana.Jungfrau.ConfigV2, src)

print 'Content of Jungfrau.ConfigV1:'

print 'numberOfModules         ', co.numberOfModules()
print 'numberOfRowsPerModule   ', co.numberOfRowsPerModule()
print 'numberOfColumnsPerModule', co.numberOfColumnsPerModule()

print 'biasVoltage             ',co.biasVoltage()
print 'gainMode                ',co.gainMode()
print 'SpeedMode               ',co.SpeedMode()
print 'TypeId                  ',co.TypeId
print 'exposureTime            ',co.exposureTime()
print 'GainMode                ',co.GainMode()
print 'speedMode               ',co.speedMode()
print 'Version                 ',co.Version
print 'frameSize               ',co.frameSize()
print 'numPixels               ',co.numPixels()
print 'triggerDelay            ',co.triggerDelay()          

#------------------------------
#------------------------------
#------------------------------
#------------------------------
