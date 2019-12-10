from __future__ import print_function

# event_keys -d exp=detdaq17:run=121
#EventKey(type=psana.Camera.FrameV1, src='DetInfo(DetLab.0:StreakC7700.0)', alias='visar')

import psana
ds = psana.DataSource('/reg/g/psdm/detector/data_test/types/0030-DetLab.0-StreakC7700.0.xtc')
for nevt,evt in enumerate(ds.events()):
    print(evt.keys())
    break

import psana
#dsname = 'exp=sxrx35317:run=1'
dsname = '/reg/g/psdm/detector/data_test/types/0029-SxrEndstation.0-Archon.0.xtc'
s_src = 'SxrEndstation.0:Archon.0' # 'rixs0'
print('Example for\n  dataset: %s\n  source : %s' % (dsname, s_src))

src = psana.Source(s_src)
ds  = psana.DataSource(dsname)
env = ds.env()
cfg = env.configStore()
co  = cfg.get(psana.Archon.ConfigV3, src)

# co.at                  co.biasVoltage         co.exposureEventCode   co.MaxConfigLineLength co.numPixelsY          co.readoutMode         co.stm1                
# co.batches             co.config              co.horizontalBinning   co.MaxConfigLines      co.pixels              co.sensorLines         co.Switch              
# co.bias                co.config_shape        co.idleSweepCount      co.nonIntegrationTime  co.power               co.sensorPixels        co.TypeId              
# co.biasChan            co.configSize          co.integrationTime     co.numPixels           co.preFrameSweepCount  co.sensorTaps          co.Version             
# co.BiasChannelId       co.configVersion       co.lines               co.numPixelsX          co.ReadoutMode         co.st                  co.verticalBinning

print('co.horizontalBinning() :', co.horizontalBinning())
print('co.verticalBinning()   :', co.verticalBinning())
print('co.numPixels()         :', co.numPixels())
print('co.numPixelsX()        :', co.numPixelsX())
print('co.numPixelsY()        :', co.numPixelsY())
print('co.pixels()            :', co.pixels())
print('co.sensorLines()       :', co.sensorLines())
print('co.sensorPixels()      :', co.sensorPixels())
print('co.sensorTaps()        :', co.sensorTaps())
print('co.st()                :', co.st())
print('co.TypeId              :', co.TypeId)
print('co.Version             :', co.Version)
print('co.lines()             :', co.lines())
print('co.MaxConfigLineLength :', co.MaxConfigLineLength)
print('co.MaxConfigLines      :', co.MaxConfigLines)
print('co.config_shape()      :', co.config_shape())
print('co.configSize()        :', co.configSize())
print('co.BiasChannelId       :', co.BiasChannelId)
print('co.biasVoltage         :', co.biasVoltage)
print('co.biasChan()          :', co.biasChan())          

events = ds.events()
evt = next(events)
frame = evt.get(psana.Camera.FrameV1, src)
data = frame.data16()

from pyimgalgos.GlobalUtils import print_ndarr
print_ndarr(data, name='data', first=0, last=5)

evt=None
for i, evt in enumerate(ds.events()) :    
    if evt is None : print('Event %4d is None' % i)
    else :  
        print('Event %4d is NOT None' % i) 
        break

frame = evt.get(psana.Camera.FrameV1, src)
data = frame.data16()
print_ndarr(data, name='data', first=0, last=5)

#raw = det.raw(evt)
