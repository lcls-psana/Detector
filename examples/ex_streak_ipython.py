from __future__ import print_function

# event_keys -d exp=detdaq17:run=121
#EventKey(type=psana.Camera.FrameV1, src='DetInfo(DetLab.0:StreakC7700.0)', alias='visar')

#dsname = 'exp=detdaq17:run=121'
import psana
ds = psana.DataSource('/reg/g/psdm/detector/data_test/types/0030-DetLab.0-StreakC7700.0.xtc')
for nevt,evt in enumerate(ds.events()):
    print(list(evt.keys()))
    break


import psana
dsname = '/reg/g/psdm/detector/data_test/types/0030-DetLab.0-StreakC7700.0.xtc'
s_src = 'DetLab.0:StreakC7700.0'
print('Example for\n  dataset: %s\n  source : %s' % (dsname, s_src))

src = psana.Source(s_src)
ds  = psana.DataSource(dsname)
env = ds.env()
cfg = env.configStore()
co  = cfg.get(psana.Streak.ConfigV1, src)

print('co.Column_Pixels:', co.Column_Pixels) # 1344
print('co.Row_Pixels   :', co.Row_Pixels) # 1024
# this how you get the time calibration for the x-axis

arr = co.calibTimesInSeconds()



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
