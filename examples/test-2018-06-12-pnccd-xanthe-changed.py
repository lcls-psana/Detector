import psana
from pylab import *
myDataSource = psana.MPIDataSource('exp=sxrx22915:run=104:smd')
myPnccdDetectorObject = psana.Detector('pnccd')
myEnumeratedEvents = enumerate(myDataSource.events())
eventNumber,thisEvent = next(myEnumeratedEvents)
eventNumber
myPnccdDetectorObject.image(thisEvent)


nda = myPnccdDetectorObject.calib(thisEvent, cmpars=(8,5,500))
myImage = myPnccdDetectorObject.image(thisEvent, nda)

print myImage
