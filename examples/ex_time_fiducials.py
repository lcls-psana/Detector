
""" Example shows how to
    1. get EventId and associated to data time in sec, nsec, fiducials
    2. convert time_sec to the string of time-stamp like 2015-10-14T15:44:03
    3. make string of time-stamp for current time
    4. construct EventTime object for idx mode

    Usage: python Detector/examples/ex_time_fiducials.py
"""
##-----------------------------

import psana

from time import strftime, localtime

ds = psana.DataSource('exp=amoj5415:run=49')

for i, evt in enumerate(ds.events()) :
    if i>10 : break
    #for key in evt.keys() : print key
    evtid = evt.get(psana.EventId)
    tsec, tnsec = evtid.time()
    fid = evtid.fiducials()

    tstamp_data = strftime('%Y-%m-%dT%H:%M:%S', localtime(tsec))
    tstamp_now  = strftime('%Y-%m-%dT%H:%M:%S', localtime())

    print '%s\nEvent# %3d t[sec]=%10d  t[nsec]=%9d  fid=%5d  tstamp(data): %s  tstamp(now): %s'%\
          (127*'_', i, tsec, tnsec, fid, tstamp_data, tstamp_now)

    et = psana.EventTime(int((tsec<<32)|tnsec),fid)
    print 'EventTime: t[sec]=%10d  t[nsec]=%9d  fid=%5d' % (et.seconds(), et.nanoseconds(), et.fiducial()) #, et.time

##-----------------------------
