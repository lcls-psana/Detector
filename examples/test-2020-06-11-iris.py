import sys
ROOT_DIR = ".."
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
import os
import time
import numpy as np
import six
import itertools
import h5py as h5
from mpi4py import MPI # module required to use MPI
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import pysingfel as ps
import pysingfel.gpu as pg
from pysingfel.util import asnumpy, xp
beam = ps.Beam(ROOT_DIR+'/input/beam/amo86615.beam')
det = ps.Epix10kDetector(geom=ROOT_DIR+'/input/lcls/xcslt4017/Epix10ka2M::CalibV1/XcsEndstation.0:Epix10ka2M.0/geometry/7-end.data',run_num=7,beam=beam)
const = det.pedestals[1]
particle = ps.Particle()
particle.read_pdb(ROOT_DIR+'/input/pdb/2CEX.pdb', ff='WK')
experiment = ps.SPIExperiment(det, beam, particle)
img_stack = experiment.generate_image_stack()
import psana
import numpy as np
import time
import matplotlib.pyplot as plt
from Detector.UtilsEpix10ka import find_gain_mode
experimentName = 'xcslt4017'
runNumber = '357'
detInfo = 'epix10ka2m'
ds = psana.DataSource('exp='+experimentName+':run='+runNumber+':idx')
run = ds.runs().next()
det = psana.Detector(detInfo)
times = run.times()
env = ds.env()
for i in times:
    evt = run.event(i)
    raw = det.raw(evt)
    gm = find_gain_mode(det, raw) # returns string name of the gain mode
    #print gm
    #calib = det.calib(evt, cmpars=(0, 2, 100), nda_raw=const)
    calib = det.calib(evt, nda_raw=const)
    img1 = det.image(evt, calib)
    img2 = experiment.generate_image()
    plt.subplot(1, 2, 1)
    plt.imshow(img1, norm=LogNorm())
    plt.subplot(1, 2, 2)
    plt.imshow(img2, norm=LogNorm())
    plt.colorbar()
    plt.show()
    exit()
