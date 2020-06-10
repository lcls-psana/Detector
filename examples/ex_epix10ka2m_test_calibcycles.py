#!/usr/bin/env python

import sys
from psana import DataSource, Detector
from Detector.PyDataAccess import get_epix_config_object
from Detector.GlobalUtils import info_ndarr, print_ndarr
from Detector.UtilsEpix10ka import store, GAIN_MODES, GAIN_MODES_IN, config_objects,\
                            get_epix10ka_any_config_object, find_gain_mode

#----------

def argument_parser():

    import argparse
    
    d_dsname  = 'exp=detdaq18:run=40:smd'
    d_detname = 'DetLab.0:Epix10ka2M.0'
    d_prefix  ='./img'
    d_procev  = False
    d_plot    = False
    d_save    = False
    d_skip    = 0
    d_objinfo = True

    scrname = sys.argv[0].rsplit('/')[-1]
    usage = 'E.g.: %s %s # brief info about content' % (scrname, d_dsname)\
          + '\n  or: %s %s -i -e -p -S 5 # skip 5 calib-cycles and plot graphics' % (scrname, d_dsname)\
          + '\n  or: %s %s -e -p -s --detname %s -f %s' % (scrname, d_dsname, d_detname, d_prefix)
    print(usage)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('dsname', type=str, default=d_dsname, help="dataset, default: %s"%d_dsname)
    parser.add_argument('--detname', type=str, default=d_detname, help="detname, default: %s"%d_detname)
    parser.add_argument('-f', '--prefix', type=str, default=d_prefix, help='output file name prefix, default: %s'%d_prefix)
    parser.add_argument('-e', '--procev', default=d_procev, help='process events in loop, default: %s'%d_procev, action='store_true')
    parser.add_argument('-p', '--plot', default=d_plot, help='plot graphiocs, default: %s'%d_plot, action='store_true')
    parser.add_argument('-s', '--save', default=d_save, help='save graphiocs, default: %s'%d_save, action='store_true')
    parser.add_argument('-i', '--objinfo', default=d_objinfo, help='print objcts info, default: %s'%d_objinfo, action='store_false')
    parser.add_argument('-S', '--skip', default=d_skip, type=int, help='skip initial number of calibcycles, default: %d'%d_skip)
    
    args = parser.parse_args()
    print('Arguments: %s\n' % str(args))
    for k,v in vars(args).items() : print('  %12s : %s' % (k, str(v)))

    return args

#----------

args = argument_parser()

DSNAME     = args.dsname
DETNAME    = args.detname
PREFIX     = args.prefix
DO_PLOT    = args.plot
DO_SAVE    = args.save
PROC_EVENT = args.procev
OBJINFO    = args.objinfo
SKIPNCC    = args.skip

if DO_PLOT: 
    import pyimgalgos.Graphics as gr
    fig = gr.figure(figsize=(10,9), title='Image', dpi=80, facecolor='w', edgecolor='w', frameon=True, move=None)
    fig, axim, axcb = gr.fig_img_cbar_axes(fig, win_axim=(0.05,  0.03, 0.87, 0.93), win_axcb=(0.923, 0.03, 0.02, 0.93))

#----------

def info_quad(q):
    print 'quad = cfg.quad(i)', q
    print 'dir(cfg.quad(i))', dir(q)
    print '\n'


def info_elemCfg(e):
    print 'e = cfg.elemCfg(i)', e
    print 'dir(e)', dir(e)
    print 'e.asicMask', e.asicMask()
    print 'e.asicPixelConfigArray\n', e.asicPixelConfigArray()
    print 'e.asics(0)', e.asics(0)
    print 'e.asics_shape', e.asics_shape()
    print 'e.calibPixelConfigArray\n', e.calibPixelConfigArray()
    print 'e.calibrationRowCountPerASIC', e.calibrationRowCountPerASIC()
    print 'e.carrierId0', e.carrierId0()
    print 'e.carrierId1', e.carrierId1()
    print 'e.environmentalRowCountPerASIC', e.environmentalRowCountPerASIC()
    print 'e.numberOfAsics', e.numberOfAsics()
    print 'e.numberOfAsicsPerColumn', e.numberOfAsicsPerColumn()
    print 'e.numberOfAsicsPerRow', e.numberOfAsicsPerRow()
    print 'e.numberOfCalibrationRows', e.numberOfCalibrationRows()
    print 'e.numberOfColumns', e.numberOfColumns()
    print 'e.numberOfEnvironmentalRows', e.numberOfEnvironmentalRows()
    print 'e.numberOfPixelsPerAsicRow', e.numberOfPixelsPerAsicRow()
    print 'e.numberOfReadableRows', e.numberOfReadableRows()
    print 'e.numberOfReadableRowsPerAsic', e.numberOfReadableRowsPerAsic()
    print 'e.numberOfRows', e.numberOfRows()
    print 'e.numberOfRowsPerAsic', e.numberOfRowsPerAsic()
    print '\n'


def info_asic(a):
    print 'a = cfg.elemCfg.asics(i)', a
    print 'dir(a)', dir(a)
    print 'a.Pulser', a.Pulser()
    print 'a.trbit', a.trbit()
    print 'a.pixelDummy', a.pixelDummy()
    print 'a.chipID', a.chipID()
    print 'a.PulserR', a.PulserR()
    print 'a.PixelCB', a.PixelCB()
    print 'a.PulserSync', a.PulserSync()
    print '\n'


def info_config_evr(evr):
    print 'evr = cfg.evr():', evr
    print 'dir(evr):', dir(evr)
    print 'evr.daqCode', evr.daqCode()
    print 'evr.enable', evr.enable()
    print 'evr.runCode', evr.runCode()
    print 'evr.runDelay', evr.runDelay()
    print '\n'


def info_config(cfg):
    print 'cfg:', cfg
    print 'dir(cfg):', dir(cfg)
    print 'cfg.TypeId', cfg.TypeId
    print 'cfg.Version', cfg.Version
    print 'cfg.elemCfg_shape', cfg.elemCfg_shape()
    print 'cfg.numberOfAsics', cfg.numberOfAsics()
    print 'cfg.numberOfCalibrationRows:', cfg.numberOfCalibrationRows()
    print 'cfg.numberOfColumns', cfg.numberOfColumns()
    print 'cfg.numberOfElements', cfg.numberOfElements()
    print 'cfg.numberOfEnvironmentalRows', cfg.numberOfEnvironmentalRows()
    print 'cfg.numberOfReadableRows', cfg.numberOfReadableRows()
    print 'cfg.numberOfRows', cfg.numberOfRows()
    print 'cfg.quad_shape', cfg.quad_shape()
    print 'cfg.elemCfg(0)', cfg.elemCfg(0)
    print 'cfg.quad(0)', cfg.quad(0)
    print '\n'

    info_config_evr(cfg.evr())

    q0 = cfg.quad(0)
    e0 = cfg.elemCfg(0)
    a0 = e0.asics(0)

    info_quad(q0)
    info_elemCfg(e0)
    info_asic(a0)

#----------

def do_work():

    #ds = DataSource('exp=detdaq18:run=14:smd')
    #ds = DataSource('exp=detdaq18:run=18:smd') # good dark calib-cycles: FH, FM, FL, AHL-H, AML_M
    #ds = DataSource('exp=detdaq18:run=27-29:smd')
    #ds = DataSource('exp=detdaq18:run=35-36:smd')
    #ds = DataSource('exp=detdaq18:run=37:smd')
    #ds = DataSource('exp=detdaq18:run=38:smd')
    #ds = DataSource('exp=detdaq18:run=39:smd')
    #ds = DataSource('exp=detdaq18:run=40:smd')
    #det = Detector('DetLab.0:Epix10ka2M.0')
    ds  = DataSource(DSNAME)
    cd  = Detector('ControlData')
    det = Detector(DETNAME)
    
    idx = 0
    #print '=== cd:', dir(cd)
    
    nstep = -1
    for run in ds.runs():
      env = run.env()
      cfg = get_epix_config_object(env, det.source)

      print '\n=== run:', run.run()

      if OBJINFO:
         info_config(cfg)
         #sys.exit('TEST EXIT')

      for nstep_in_run, step in enumerate(run.steps()):
        nstep += 1
        print '%s\nrun: %04d step: %03d/%03d (in run/total)' % (50*'=', run.run(), nstep, nstep_in_run), \
              '    ControlData pvControls, pvLabels, pvMonitors', cd().pvControls(),cd().pvLabels(),cd().pvMonitors() # EMPTY: ,

        if nstep<SKIPNCC : 
            print '    skip calibcycles < %d' % SKIPNCC
            continue

        events = step.events()
        #print 'dir(events)', dir(events)

        nevgood=-1
        for nev,evt in enumerate(events):

          if not PROC_EVENT: continue

          raw = det.raw(evt)
          
          if raw is None:
              print 'Ev:%2d raw is None' % nev
              continue
          else:
              nevgood += 1
              if nevgood%1000: continue
              #if raw.ndim > 2: raw=raw[idx,:]
              msg = 'Ev:%2d ' % nevgood
              for idx in range(16):
                 gmode = find_gain_mode(det,raw[idx,:])
                 msg += ' %d:%s' % (idx,gmode)
              print_ndarr(raw, '%s\n    '%msg)

              if DO_PLOT:
                  idx = 0
                  img = raw[idx,:]
                  imsh, cbar = gr.imshow_cbar(fig, axim, axcb, img, amin=None, amax=None, extent=None,\
                    interpolation='nearest', aspect='auto', origin='upper', orientation='vertical', cmap='inferno')
                  gr.set_win_title(fig, titwin='run: %d  cc: %d' % (run.run(), nstep))
                  gr.draw_fig(fig)
                  gr.show(mode='non-hold')

                  if DO_SAVE:
                      ofname = '%s-%s-r%04d-s%03d-e%04d-seg%02d.png'%\
                           (PREFIX, str(det.name).replace(':','-').replace('.','-'), run.run(), nstep, nevgood, idx)
                      gr.save_fig(fig, fname=ofname, verb=True)
    
        print '%sstep: %03d contains %d/%d good/total events in run' % (10*' ', nstep, nevgood, nev)
    
        if PROC_EVENT and nevgood<0: nstep -= 1

#----------

do_work()

#----------
