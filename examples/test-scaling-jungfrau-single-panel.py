from psana import *
from time import time


def test_mpi():
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    #ds = MPIDataSource('exp=cxix1000021:run=5')
    #det = Detector('jungfrau4M')

    #ds = MPIDataSource('exp=xcsx1003522:run=38')
    ds = MPIDataSource('exp=xcsx1003522:run=35-38')
    det = Detector('XcsEndstation.0:Jungfrau.1')
    ds.break_after(100*size)
    for nevt,evt in enumerate(ds.events()):
        raw = det.raw(evt) # prefetch the data from disk
        if raw is None: continue
        t0_sec = time()
        calib = det.calib(evt)
        print('rank',rank,'event',nevt,'time',time()-t0_sec)


def test_nompi():

    #ds = MPIDataSource('exp=cxix1000021:run=5')
    #det = Detector('jungfrau4M')

    ds = DataSource('exp=xcsx1003522:run=38')
    det = Detector('XcsEndstation.0:Jungfrau.1')
    #ds.break_after(100*size)

    nevt = -1
    for istep,step in enumerate(ds.steps()):
      for ievt,evt in enumerate(step.events()):
        raw = det.raw(evt) # prefetch the data from disk
        if raw is None: continue
        nevt += 1
        t0_sec = time()
        calib = det.calib(evt)
        print('nevt:', nevt,  'step:', istep, 'ievt:', ievt, 'time:',  time()-t0_sec)

#test_mpi()
test_nompi()
