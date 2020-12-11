from psana import *

ds  = DataSource('exp=detdaq17:run=190:smd')

jungfrau = Detector('jungfrau4M_q2', ds.env())


maxNevents = 100

nEvt = 0
for nEvent,evt in enumerate(ds.events()):
    #if nEvent%size != rank:
    #    continue
    if nEvent>maxNevents:
        break

    print 'jungfrau.raw(evt)', jungfrau.raw(evt)

    print "Ev:%3d should work"%nEvent
    frames = jungfrau.calib(evt)
    print "might not"
    frames = jungfrau.calib(evt, cmpars=(7, 1, 100))
    if frames is None:
        print "Empty frame, bail"
        continue
    if nEvent==0:
        print "doing CM 7, 1, 100"
