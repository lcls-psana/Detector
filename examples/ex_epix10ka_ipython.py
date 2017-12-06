
# event_keys -d exp=mfxx32516:run=5
# shape=(352, 384)
# Example of code for ipython

import psana
ds = psana.DataSource('exp=mfxx32516:run=5')
det = psana.Detector('MfxEndstation.0:Epix10ka.0') # 'Epix10ka'
for i, evt in enumerate(ds.events()) :
    if i>100 : break
    raw = det.raw(evt)
    if raw is None:
        print i, 'none'
        continue
    else:
        print i, raw.shape

#------------------------------

import psana
nrun = 5
dsname = 'exp=mfxx32516:run=%d' % nrun
s_src = 'MfxEndstation.0:Epix10ka.0'
print 'Example for\n  dataset: %s\n  source : %s' % (dsname, s_src)

src = psana.Source(s_src)
ds  = psana.DataSource(dsname)
env = ds.env()

r = ds.runs().next()
#evt = ds.events().next()

evt=None
for i, evt in enumerate(ds.events()) :    
    if evt is None : print 'Event %4d is None' % i
    else :  
        print 'Event %4d is NOT None' % i 
        break
        

cfg = env.configStore()
co = cfg.get(psana.Epix.Config10kaV1, src)

print 'analogCardId0():', co.analogCardId0()
print 'analogCardId1():', co.analogCardId1()
print 'asicMask()     :', co.asicMask()     

det = psana.Detector(s_src, env)
raw = det.raw(evt)

raw.shape #Out[8]: ((352, 384)

raw.dtype #Out[9]: dtype('uint16')


evt = ds.events().next()
dato = evt.get(psana.Jungfrau.ElementV1, src)

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
do = env.configStore().get(psana.Epix.ElementV3, src)

co = cfg.get(psana.Epix.Config10kaV1, src)

print 'Content of psana.Epix.Config10kaV1:'

print 'acqToAsicR0Delay :', co.acqToAsicR0Delay()
print 'adcClkHalfT      :', co.adcClkHalfT()      
print 'adcPipelineDelay :', co.adcPipelineDelay() 
print 'adcPipelineDelay0:', co.adcPipelineDelay0()
print 'adcPipelineDelay1:', co.adcPipelineDelay1()
print 'adcPipelineDelay2:', co.adcPipelineDelay2()
print 'adcPipelineDelay3:', co.adcPipelineDelay3()
print 'adcReadsPerPixel :', co.adcReadsPerPixel() 
print 'adcStreamMode    :', co.adcStreamMode()    
print 'analogCardId0    :', co.analogCardId0()    
print 'analogCardId1    :', co.analogCardId1()    
print 'asicAcq          :', co.asicAcq()          
print 'asicAcqControl   :', co.asicAcqControl()   
print 'asicAcqLToPPmatL :', co.asicAcqLToPPmatL() 
print 'asicAcqWidth     :', co.asicAcqWidth()     
print 'asicGR           :', co.asicGR()           
print 'asicGRControl    :', co.asicGRControl()    

co.acqToAsicR0Delay
co.adcClkHalfT      
co.adcPipelineDelay 
co.adcPipelineDelay0
co.adcPipelineDelay1
co.adcPipelineDelay2
co.adcPipelineDelay3
co.adcReadsPerPixel 
co.adcStreamMode    
co.version     
co.analogCardId0                    
co.analogCardId1                    
co.asicAcq                          
co.asicAcqControl                   
co.asicAcqLToPPmatL                 
co.asicAcqWidth                     
co.asicGR                           
co.asicGRControl                    
co.asicMask                         
co.asicPixelConfigArray 
co.asicPpbe             
co.asicPpbeControl      
co.asicPpmat            
co.asicPpmatControl     
co.asicPPmatToReadout   
co.asicR0               
co.asicR0ClkControl     
co.asicR0Control        
co.asicR0ToAsicAcq            
co.asicR0Width                
co.asicRoClk                  
co.asicRoClkHalfT             
co.asics                      
co.asics_shape                
co.baseClockFrequency         
co.calibPixelConfigArray      
co.calibrationRowCountPerASIC 
co.carrierId0                    
co.carrierId1                    
co.dacSetting                    
co.digitalCardId0                
co.digitalCardId1                
co.enableAutomaticRunTrigger     
co.environmentalRowCountPerASIC  
co.epixRunTrigDelay              
co.evrDaqCode                    
co.evrRunCode                      
co.evrRunTrigDelay                 
co.numberOf125MhzTicksPerRunTrigger
co.numberOfAsics                   
co.numberOfAsicsPerColumn          
co.numberOfAsicsPerRow             
co.numberOfCalibrationRows         
co.numberOfColumns                 
co.numberOfEnvironmentalRows       
co.numberOfPixelsPerAsicRow    
co.numberOfReadableRows        
co.numberOfReadableRowsPerAsic 
co.numberOfRows                
co.numberOfRowsPerAsic         
co.prepulseR0Delay             
co.prepulseR0En                
co.prepulseR0Width
co.R0Mode         
co.scopeADCsameplesToSkip    
co.scopeADCThreshold         
co.scopeArmMode              
co.scopeChanAwaveformSelect  
co.scopeChanBwaveformSelect  
co.scopeEnable               
co.scopeTraceLength          
co.scopeTrigChan             
co.scopeTrigEdge             
co.scopeTrigHoldoff     
co.scopeTrigOffset      
co.SyncDelay            
co.SyncMode             
co.SyncWidth            
co.testPatternEnable    
co.TypeId               
co.usePgpEvr            
co.Version              
co.version  



#------------------------------
#------------------------------
#------------------------------
