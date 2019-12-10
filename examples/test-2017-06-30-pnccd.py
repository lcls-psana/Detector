from __future__ import print_function

#==============================
# event_keys -d exp=sxrx22915:run=16
# EventKey(type=psana.PNCCD.FullFrameV1, src='DetInfo(Camp.0:pnCCD.1)', alias='pnccd')
# EventKey(type=psana.PNCCD.FramesV1, src='DetInfo(Camp.0:pnCCD.1)', alias='pnccd')
#
#

# /reg/neh/home/philiph/psana/sxrx20915/fooCalib/PNCCD::CalibV1/Camp.0:pnCCD.1/
# /reg/neh/home/philiph/psana/sxrx20915/oneCalib/PNCCD::CalibV1/Camp.0:pnCCD.1/
#==============================

import numpy
import sys

from psana import *
from pyimgalgos.GlobalUtils import print_ndarr


#from mpi4py import MPI
#comm = MPI.COMM_WORLD
#rank = comm.Get_rank()
#size = comm.Get_size()

rank = 0

calibType = eval(sys.argv[1])
if calibType==0:
    if rank==0:
        print("skip global gain by pointing to local calib with PAH correction")
    setOption('psana.calib-dir',
              '/reg/neh/home/philiph/psana/sxrx20915/fooCalib')

if calibType==1:
    if rank==0:
        print("skip global gain by pointing to local calib with identity gain correction")
    setOption('psana.calib-dir',
              '/reg/neh/home/philiph/psana/sxrx20915/oneCalib')

if calibType==2:
    if rank==0:
        print("use global gain")

#run = 160
##ds  = DataSource('exp=sxrx20915:run=%d:smd' %(run))
run = 16
ds  = DataSource('exp=sxrx22915:run=%d:smd' %(run))


d = Detector('pnccd')
#d = Detector('Camp.0:pnCCD.1')
#d.set_print_bits(0177777)
#d.do_reshape_2d_to_3d(flag=False) 

for nevent,evt in enumerate(ds.events()):

    if nevent==3:
        break

    print('%s\nEvent %4d' % (50*'_', nevent))
    #frame = d.calib(evt)
    #print_ndarr(frame, name='frame')

    print_ndarr(d.gain(evt), name='gain', first=0, last=5)
    #print_ndarr(d.pedestals(evt), name='pedestals')
    #print_ndarr(d.status(evt), name='status')
    #print_ndarr(d.common_mode(evt), name='common_mode')


