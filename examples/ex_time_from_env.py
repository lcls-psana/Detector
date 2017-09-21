from psana import *
ds = DataSource('exp=xpptut15:run=54:smd')
o = ds.env().configStore().get(EventId) # get XtcEventId object
# XtcEventId(run=54, time=2015-09-24 11:36:07.207250226-07, fiducials=131071, ticks=0, vector=0, control=132)

print 'object:', o
print 'o.time():', o.time()

