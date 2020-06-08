#!/usr/bin/env python

import sys
from psana import DataSource, Detector
from Detector.PyDataAccess import get_epix_config_object
from Detector.GlobalUtils import info_ndarr, print_ndarr
from Detector.UtilsEpix10ka import store, GAIN_MODES, GAIN_MODES_IN, config_objects,\
                            get_epix10ka_any_config_object, find_gain_mode

PREFIX = './img'
DO_PLOT = False # False #True
DO_SAVE = False # False

if DO_PLOT: 
    import pyimgalgos.Graphics as gr
    fig = gr.figure(figsize=(10,9), title='Image', dpi=80, facecolor='w', edgecolor='w', frameon=True, move=None)
    fig, axim, axcb = gr.fig_img_cbar_axes(fig, win_axim=(0.05,  0.03, 0.87, 0.93), win_axcb=(0.923, 0.03, 0.02, 0.93))

#----------
"""
dir(quad) ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'acqToAsicR0Delay', 'adc', 'adcPipelineDelay', 'adc_shape', 'asicAcqForce', 'asicAcqLToPPmatL', 'asicAcqValue', 'asicAcqWidth', 'asicAnaEn', 'asicDigEn', 'asicPPmatForce', 'asicPPmatToReadout', 'asicPPmatValue', 'asicR0Force', 'asicR0ToAsicAcq', 'asicR0Value', 'asicR0Width', 'asicRoClkForce', 'asicRoClkHalfT', 'asicRoClkValue', 'asicSyncForce', 'asicSyncValue', 'baseClockFrequency', 'dcdcEn', 'ddrVttEn', 'digitalCardId0', 'digitalCardId1', 'enableAutomaticRunTrigger', 'numberOf125MhzTicksPerRunTrigger', 'scopeADCThreshold', 'scopeADCsamplesToSkip', 'scopeChanAwaveformSelect', 'scopeChanBwaveformSelect', 'scopeEnable', 'scopeTraceLength', 'scopeTrigChan', 'scopeTrigDelay', 'scopeTrigEdge', 'scopeTrigHoldoff', 'scopeTrigMode', 'scopeTrigOffset', 'testChannel', 'testData', 'testDataMask', 'testPattern', 'testRequest', 'testSamples', 'testTimeout', 'trigSrcSel', 'vguardDac']
"""
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


"""
dir(elemCfg.asics(0)) ['ColumnStart', 'ColumnStop', 'CompEnOn', 'CompEn_lowBit', 'CompEn_topTwoBits', 'CompTH_DAC', 'DM1', 'DM1en', 'DM2', 'DM2en', 'DelCCKreg', 'DelEXEC', 'FELmode', 'Filter_DAC', 'Hrtest', 'Monost', 'Monost_Pulser', 'OCB', 'PP_OCB_S2D', 'Pbit', 'PixelCB', 'Preamp', 'Pulser', 'PulserR', 'PulserSync', 'Pulser_DAC', 'RO_Monost', 'RO_rst_en', 'RowStart', 'RowStop', 'S2D', 'S2D0_DAC', 'S2D0_GR', 'S2D0_tcDAC', 'S2D1_DAC', 'S2D1_GR', 'S2D1_tcDAC', 'S2D2_DAC', 'S2D2_GR', 'S2D2_tcDAC', 'S2D3_DAC', 'S2D3_GR', 'S2D3_tcDAC', 'S2D_DAC_Bias', 'S2D_tcomp', 'SLVDSbit', 'Sab_test', 'TPS_DAC', 'TPS_GR', 'TPS_MUX', 'TPS_tcDAC', 'TPS_tcomp', 'VREF_DAC', 'Vld1_b', 'VrefLow', '__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'atest', 'chipID', 'emph_bc', 'emph_bd', 'fastPP_enable', 'is_en', 'pixelDummy', 'tc', 'test', 'testBE', 'testLVDTransmitter', 'trbit']
"""
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
    ds = DataSource('exp=detdaq18:run=40:smd')

    cd  = Detector('ControlData')
    det = Detector('DetLab.0:Epix10ka2M.0')
    
    idx = 0
    #print '=== cd:', dir(cd)
    
    nstep = -1
    for run in ds.runs():
      env = run.env()
      cfg = get_epix_config_object(env, det.source)

      print '=== run:', run.run()
      info_config(cfg)

      #====================
      #sys.exit('TEST EXIT')
      #====================

      for nstep_in_run, step in enumerate(run.steps()):
        nstep += 1
        print '%s\nrun: %04d step: %03d/%03d (in run/total)' % (50*'=', run.run(), nstep, nstep_in_run), \
              '    ControlData pvControls, pvLabels, pvMonitors', cd().pvControls(),cd().pvLabels(),cd().pvMonitors() # EMPTY: ,
        nevgood=-1
        for nev,evt in enumerate(step.events()):
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
    
        print 'step %03d contains %d/%d good/total events in file' % (nstep, nevgood, nev)
    
        if nevgood<0: nstep -= 1
    
#----------

do_work()

#----------
