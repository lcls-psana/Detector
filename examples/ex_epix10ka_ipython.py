from __future__ import print_function

# event_keys -d exp=mfxx32516:run=5
# shape=(352, 384)
# Example of code for ipython

import psana
ds = psana.DataSource('exp=mfxx32516:run=377')
det = psana.Detector('MfxEndstation.0:Epix10ka.0') # 'Epix10ka'
for i, evt in enumerate(ds.events()) :
    if i>100 : break
    raw = det.raw(evt)
    if raw is None:
        print(i, 'none')
        continue
    else:
        print(i, raw.shape)

#------------------------------

import psana
nrun = 5
dsname = 'exp=mfxx32516:run=%d' % nrun
s_src = 'MfxEndstation.0:Epix10ka.0'
print('Example for\n  dataset: %s\n  source : %s' % (dsname, s_src))

src = psana.Source(s_src)
ds  = psana.DataSource(dsname)
env = ds.env()

r = next(ds.runs())
#evt = ds.events().next()

evt=None
for i, evt in enumerate(ds.events()) :    
    if evt is None : print('Event %4d is None' % i)
    else :  
        print('Event %4d is NOT None' % i) 
        break
        

cfg = env.configStore()
co = cfg.get(psana.Epix.Config10kaV1, src)

print('analogCardId0():', co.analogCardId0())
print('analogCardId1():', co.analogCardId1())
print('asicMask()     :', co.asicMask())     

det = psana.Detector(s_src, env)
raw = det.raw(evt)

raw.shape #Out[8]: ((352, 384)

raw.dtype #Out[9]: dtype('uint16')


evt = next(ds.events())
dato = evt.get(psana.Epix.ElementV3, src)

#------------------------------

def get_jungfrau_data_object(evt, src) :
    """get jungfrau data object
    """
    o = evt.get(psana.Epix.ElementV3, src)
    if o is not None : return o
    return None

def get_jungfrau_config_object(env, src) :
    cfg = env.configStore()
    o = cfg.get(psana.Epix.Config10kaV1, src)
    if o is not None : return o
    return None

#------------------------------

env = ds.env()
confo = env.configStore().get(psana.Epix.Config10kaV1, src)

cfg = env.configStore()
confo = cfg.get(psana.Epix.Config10kaV1, src)

print('Content of psana.Epix.Config10kaV1:')

print('acqToAsicR0Delay :', co.acqToAsicR0Delay())
print('adcClkHalfT      :', co.adcClkHalfT())      
print('adcPipelineDelay :', co.adcPipelineDelay()) 
print('adcPipelineDelay0:', co.adcPipelineDelay0())
print('adcPipelineDelay1:', co.adcPipelineDelay1())
print('adcPipelineDelay2:', co.adcPipelineDelay2())
print('adcPipelineDelay3:', co.adcPipelineDelay3())
print('adcReadsPerPixel :', co.adcReadsPerPixel()) 
print('adcStreamMode    :', co.adcStreamMode())    
print('analogCardId0    :', co.analogCardId0())    
print('analogCardId1    :', co.analogCardId1())    
print('asicAcq          :', co.asicAcq())          
print('asicAcqControl   :', co.asicAcqControl())   
print('asicAcqLToPPmatL :', co.asicAcqLToPPmatL()) 
print('asicAcqWidth     :', co.asicAcqWidth())     
print('asicGR           :', co.asicGR())           
print('asicGRControl    :', co.asicGRControl())    

#------------------------------

import psana

nrun = 377
dsname = 'exp=mfxx32516:run=%d' % nrun
s_src = 'MfxEndstation.0:Epix10ka.0'
#s_src1 = 'MfxEndstation.0:Epix10ka.1'
print('Example for\n  dataset: %s\n  source : %s' % (dsname, s_src))

ds = psana.DataSource(dsname)
#det = psana.Detector(s_src) # 'Epix10ka_0'
#det = psana.Detector(s_src) # 'Epix10ka_1'

env = ds.env()
evt = next(ds.events())
src = psana.Source(s_src)
cfg = env.configStore()

co = cfg.get(psana.Epix.Config10kaV1, src)
da = evt.get(psana.Epix.ElementV3, src)

asic = co.asics(0)

#------------------------------
"""
psana.Epix.Config10kaV1 :

  co.acqToAsicR0Delay                 co.asicMask                         co.calibPixelConfigArray            co.numberOfCalibrationRows          co.scopeEnable                       
  co.adcClkHalfT                      co.asicPixelConfigArray             co.calibrationRowCountPerASIC       co.numberOfColumns                  co.scopeTraceLength                  
  co.adcPipelineDelay                 co.asicPpbe                         co.carrierId0                       co.numberOfEnvironmentalRows        co.scopeTrigChan                     
  co.adcPipelineDelay0                co.asicPpbeControl                  co.carrierId1                       co.numberOfPixelsPerAsicRow         co.scopeTrigEdge                     
  co.adcPipelineDelay1                co.asicPpmat                        co.dacSetting                       co.numberOfReadableRows             co.scopeTrigHoldoff                  
  co.adcPipelineDelay2                co.asicPpmatControl                 co.digitalCardId0                   co.numberOfReadableRowsPerAsic      co.scopeTrigOffset                  
  co.adcPipelineDelay3                co.asicPPmatToReadout               co.digitalCardId1                   co.numberOfRows                     co.SyncDelay                        
  co.adcReadsPerPixel                 co.asicR0                           co.enableAutomaticRunTrigger        co.numberOfRowsPerAsic              co.SyncMode                         
  co.adcStreamMode                    co.asicR0ClkControl                 co.environmentalRowCountPerASIC     co.prepulseR0Delay                  co.SyncWidth                        
  co.analogCardId0                    co.asicR0Control                    co.epixRunTrigDelay                 co.prepulseR0En                     co.testPatternEnable                
  co.analogCardId1                    co.asicR0ToAsicAcq                  co.evrDaqCode                       co.prepulseR0Width                  co.TypeId                           
  co.asicAcq                          co.asicR0Width                      co.evrRunCode                       co.R0Mode                           co.usePgpEvr                        
  co.asicAcqControl                   co.asicRoClk                        co.evrRunTrigDelay                  co.scopeADCsameplesToSkip           co.Version                          
  co.asicAcqLToPPmatL                 co.asicRoClkHalfT                   co.numberOf125MhzTicksPerRunTrigger co.scopeADCThreshold                co.version                          
  co.asicAcqWidth                     co.asics                            co.numberOfAsics                    co.scopeArmMode                                                         
  co.asicGR                           co.asics_shape                      co.numberOfAsicsPerColumn           co.scopeChanAwaveformSelect                                             
  co.asicGRControl                    co.baseClockFrequency               co.numberOfAsicsPerRow              co.scopeChanBwaveformSelect        

#------------------------------

asic(0) :

            asic.atest              asic.FELmode            asic.RO_rst_en          asic.S2D_tcomp           
            asic.chipID             asic.Filter_DAC         asic.RowStart           asic.Sab_test            
            asic.ColumnStart        asic.Hrtest             asic.RowStop            asic.SLVDSbit            
            asic.ColumnStop         asic.is_en              asic.S2D                asic.tc                  
            asic.CompEn_lowBit      asic.Monost             asic.S2D0_DAC           asic.test                
            asic.CompEn_topTwoBits  asic.Monost_Pulser      asic.S2D0_GR            asic.testBE             
            asic.CompEnOn           asic.OCB                asic.S2D0_tcDAC         asic.testLVDTransmitter 
            asic.CompTH_DAC         asic.Pbit               asic.S2D1_DAC           asic.TPS_DAC            
            asic.DelCCKreg          asic.PixelCB            asic.S2D1_GR            asic.TPS_GR             
            asic.DelEXEC            asic.pixelDummy         asic.S2D1_tcDAC         asic.TPS_MUX            
            asic.DM1                asic.PP_OCB_S2D         asic.S2D2_DAC           asic.TPS_tcDAC          
            asic.DM1en              asic.Preamp             asic.S2D2_GR            asic.TPS_tcomp          
            asic.DM2                asic.Pulser             asic.S2D2_tcDAC         asic.trbit              
            asic.DM2en              asic.Pulser_DAC         asic.S2D3_DAC           asic.Vld1_b             
            asic.emph_bc            asic.PulserR            asic.S2D3_GR            asic.VREF_DAC           
            asic.emph_bd            asic.PulserSync         asic.S2D3_tcDAC         asic.VrefLow            
            asic.fastPP_enable      asic.RO_Monost          asic.S2D_DAC_Bias                        
"""
#------------------------------
#------------------------------
