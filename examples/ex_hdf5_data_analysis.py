#!/usr/bin/env python
"""
Some references:

1. https://confluence.slac.stanford.edu/display/PSDM/psana+python+Setup
2. https://confluence.slac.stanford.edu/display/PCDS/Remote+Visualization
3. https://confluence.slac.stanford.edu/display/PSDM/Data+Access


System setup:
> source conda_setup

To run script use command:
> python ex-data-analysis-h5.py 3
"""
from __future__ import print_function
#------------------------------
import sys
import numpy as np
import h5py
from pyimgalgos.GlobalUtils import print_ndarr

#------------------------------
IFNAME = '/reg/d/psdm/DIA/diamcc14/hdf5/diamcc14-r1791.h5'
OFNAME = 'image-averaged.txt'
EVSKIP = 0
EVENTS = 1000 + EVSKIP

#------------------------------

def access_data_direct() :
    f = h5py.File(IFNAME,'r')

    ebeam_time = f['/Configure:0000/Run:0000/CalibCycle:0000/Bld::BldDataEBeamV7/EBeam/time'][:]
    ebeam_data = f['/Configure:0000/Run:0000/CalibCycle:0000/Bld::BldDataEBeamV7/EBeam/data'][:]
    print_ndarr(ebeam_time, name='ebeam_time', first=0, last=5)
    print_ndarr(ebeam_data, name='ebeam_data', first=0, last=5)

    camera_data  = f['/Configure:0000/Run:0000/CalibCycle:0000/Camera::FrameV1/FeeHxSpectrometer.0:OrcaFl40.0/data'][:]
    camera_image = f['/Configure:0000/Run:0000/CalibCycle:0000/Camera::FrameV1/FeeHxSpectrometer.0:OrcaFl40.0/image'][:]
    camera_time  = f['/Configure:0000/Run:0000/CalibCycle:0000/Camera::FrameV1/FeeHxSpectrometer.0:OrcaFl40.0/time'][:]
    print_ndarr(camera_time,  name='camera_time', first=0, last=5)
    print_ndarr(camera_data,  name='camera_data', first=0, last=5)
    print_ndarr(camera_image, name='camera_image',first=0, last=5)

    f.close()

#------------------------------

def access_data_detector() :
    import psana
    ds = psana.DataSource(IFNAME)
    env = ds.env()
    det_orca  = psana.Detector('FeeHxSpectrometer.0:OrcaFl40.0', env)
    det_ebeam = psana.Detector('EBeam')

    for i, evt in enumerate(ds.events()) :

        if i<EVSKIP : continue
        if i>EVENTS : break

        ebeam = det_ebeam.get(evt)
        print('Event %3d' % i)
        if ebeam is None: continue
        print('Photon energy %.6f' % ebeam.ebeamPhotonEnergy())

        raw = det_orca.raw(evt)
        print_ndarr(raw, name='orca raw',first=0, last=5)
        
        if raw is None : continue
            
        # ===>>> put analyses code here <<<===


#   ebeam.damageMask        ebeam.ebeamEnergyBC1    ebeam.ebeamLTU450       ebeam.ebeamLTUPosY      ebeam.ebeamUndAngX      ebeam.ebeamXTCAVAmpl    
#   ebeam.DamageMask        ebeam.ebeamEnergyBC2    ebeam.ebeamLTUAngX      ebeam.ebeamPhotonEnergy ebeam.ebeamUndAngY      ebeam.ebeamXTCAVPhase   
#   ebeam.ebeamCharge       ebeam.ebeamL3Energy     ebeam.ebeamLTUAngY      ebeam.ebeamPkCurrBC1    ebeam.ebeamUndPosX      ebeam.TypeId            
#   ebeam.ebeamDumpCharge   ebeam.ebeamLTU250       ebeam.ebeamLTUPosX      ebeam.ebeamPkCurrBC2    ebeam.ebeamUndPosY      ebeam.Version  

#------------------------------

from pyimgalgos.GlobalGraphics import plotImageLarge, hist1d, show

def plot_image(img, amp_range=None) :
    axim = plotImageLarge(img, img_range=None, amp_range=amp_range, figsize=(12,10), title='Image', origin='upper', window=(0.05,  0.03, 0.94, 0.94), cmap='inferno')

def plot_hist(arr, nbins=None, amp_range=None, title='Hist') :
    fig, axhi, hi =\
    hist1d(np.array(arr), bins=None, amp_range=None, weights=None, color=None, show_stat=True, log=False,\
           figsize=(6,5), axwin=(0.15, 0.12, 0.78, 0.80), \
           title=title, xlabel=None, ylabel=None, titwin=title)

#------------------------------

def filter_events() :
    import psana
    ds = psana.DataSource(IFNAME)
    env = ds.env()
    det_orca  = psana.Detector('FeeHxSpectrometer.0:OrcaFl40.0', env)
    det_ebeam = psana.Detector('EBeam')

    img_ave = None
    lst_px = []
    lst_py = []

    nev_tot = 0
    nev_sel = 0

    for i, evt in enumerate(ds.events()) :

        if i<EVSKIP : continue
        if i>EVENTS : break

        ebeam = det_ebeam.get(evt)
        print('Event %3d' % i)
        if ebeam is None: continue
        print('Photon energy %.6f' % ebeam.ebeamPhotonEnergy())

        img = det_orca.raw(evt)
        print_ndarr(img, name='orca raw',first=0, last=5)
        
        if img is None : continue
            
        # ===>>> put analyses code here <<<===

        px = ebeam.ebeamUndPosX()
        py = ebeam.ebeamUndPosY()

        lst_px.append(px)
        lst_py.append(py)
        #print('  px, py = %.3f, %.3f' % (px, py))
        nev_tot += 1
        
        if px < -0.01 : continue
        if px >  0.01 : continue
        if py < -0.04 : continue
        if py >  0.03 : continue

        nev_sel += 1

        if img_ave is None : img_ave = np.array(img, dtype=np.double)
        img_ave += img

    np.savetxt(OFNAME, img_ave, fmt='%3i', delimiter=' ', newline='\n')

    print('Selected %d events of total %d' % (nev_sel, nev_tot))
    print('Plot image and histograms')

    mean, std = img_ave.mean(), img_ave.std()
    plot_image(img_ave, amp_range=(mean-1*std, mean+5*std))
    #plot_image(img_ave, amp_range=(0, 6000))

    plot_hist(lst_px, nbins=None, amp_range=None, title='ebeamUndPosX')
    plot_hist(lst_py, nbins=None, amp_range=None, title='ebeamUndPosY')
    show()


#------------------------------

if __name__ == "__main__" :

    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    print('%s\nTest %s' % (80*'_', tname))

    if   tname == '1' : access_data_direct()
    elif tname == '2' : access_data_detector()
    elif tname == '3' : filter_events()

    else : sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit ('End of %s' % sys.argv[0])

#------------------------------
