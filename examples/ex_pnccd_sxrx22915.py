from pyimgalgos.GlobalUtils import print_ndarr
import os
import sys

from pylab import *
import h5py
import psana

run = 104
myDataSource = psana.DataSource("exp=sxrx22915:run="+str(run))# reads in the data file

pnccd = psana.Detector('Camp.0:pnCCD.1') #picks out the pnccd data
mask = None

fname = "mySparseImages_run"+str(run)+"_oldgain_commod8_100_every5_mask.h5"
if os.path.lexists(fname) :
    sys.exit("File %s already exists... Remove it pls." % fname)

print("Open new file %s" % fname)

f = h5py.File(fname, 'a') #opens the file to write the images to
for evnum,evt in enumerate(myDataSource.events()):

        print('Event %d'%evnum)

        if evnum < 99: continue #skips the first 999 events

        if evnum > 200: break #stops after the indicated number of events

        if evnum%20==1: #selects 1 every 5 events,to be exact,the events 1001,1006,1011,etc
                print evnum                        
                if mask is None:               
                        mask = pnccd.mask(evt, calib=True, status=True)
                        print_ndarr(mask, name='mask for ev %d'%evnum, first=0, last=5)
                nda = pnccd.calib(evt, cmpars=(8,5,500), mask=mask) # does common mode8
                #nda = pnccd.raw(evt)
                print_ndarr(nda, name='raw for ev %d'%evnum, first=0, last=5)

                image  = pnccd.image(evt,nda) #makes the image for this event
                print_ndarr(image, name='img for ev %d'%evnum, first=0, last=5)

                if (None is not image):
                        f.create_dataset(str(evnum), data=array(image,dtype=float))
                else:
                        continue
f.close() 
print("See file %s" % fname)
