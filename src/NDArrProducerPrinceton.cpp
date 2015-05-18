//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// Author:
//      Mikhail S. Dubrovin
//
//------------------------------------------------------------------------

//---------------
// -- Headers --
//---------------

#include "Detector/NDArrProducerPrinceton.h"

//-----------------------------

namespace Detector {

typedef NDArrProducerPrinceton::data_t data_t;

//-----------------------------

NDArrProducerPrinceton::NDArrProducerPrinceton(const PSEvt::Source& source, const unsigned& mode, const unsigned& pbits, const float& vdef)
  : NDArrProducerBase(source, mode, pbits, vdef)
  , m_count_ent(0)
  , m_count_msg(0)
{
  //m_as_data = (mode) ? false : true;
  m_as_data = true;
}

//-----------------------------

NDArrProducerPrinceton::~NDArrProducerPrinceton ()
{
}

//-----------------------------

void
NDArrProducerPrinceton::print_warning(const char* msg)
{
  m_count_msg++;
  if (m_count_msg < 11 && m_pbits) {
    MsgLog(name(), warning, "Princeton::FramesV1,2, Pimax::FrameV1 object"
           << " is not available in this run/event for source:" << m_source);
    if (m_count_msg == 10) MsgLog(name(), warning, "STOP PRINT WARNINGS for source:" << m_source);
  }
}

//-----------------------------

ndarray<const data_t, 2> 
NDArrProducerPrinceton::data_nda_uint16_2(PSEvt::Event& evt, PSEnv::Env& env)
{
  ndarray<const data_t, 2> nda1 = getNDArrForType<Psana::Princeton::FrameV1, data_t>(evt, env);
  if ( ! nda1.empty()) return nda1; 

  ndarray<const data_t, 2> nda2 = getNDArrForType<Psana::Princeton::FrameV2, data_t>(evt, env);
  if ( ! nda2.empty()) return nda2; 

  ndarray<const data_t, 2> nda3 = getNDArrForType<Psana::Pimax::FrameV1, data_t>(evt, env);
  if ( ! nda3.empty()) return nda3; 

  print_warning();
  ndarray<data_t, 2> nda;
  return nda; // empty
}

//-----------------------------

void
NDArrProducerPrinceton::print_config(PSEvt::Event& evt, PSEnv::Env& env)
{

    boost::shared_ptr<Psana::Princeton::ConfigV1> config1 = env.configStore().get(m_source);
    if (config1.get()) {    
      WithMsgLog(name(), info, str) {
        str << "Princeton::ConfigV1:";
        str << "\n  width = " << config1->width();
        str << "\n  height = " << config1->height();
        str << "\n  orgX = " << config1->orgX();
        str << "\n  orgY = " << config1->orgY();
        str << "\n  binX = " << config1->binX();
        str << "\n  binY = " << config1->binY();
        str << "\n  exposureTime = " << config1->exposureTime();
        str << "\n  coolingTemp = " << config1->coolingTemp();
        str << "\n  readoutSpeedIndex = " << config1->readoutSpeedIndex();
        str << "\n  readoutEventCode = " << config1->readoutEventCode();
        str << "\n  delayMode = " << config1->delayMode();
        str << "\n  frameSize = " << config1->frameSize();
        str << "\n  numPixels = " << config1->numPixels();
      }
      return;
    }
    
    
    boost::shared_ptr<Psana::Princeton::ConfigV2> config2 = env.configStore().get(m_source);
    if (config2.get()) {
      WithMsgLog(name(), info, str) {
        str << "Princeton::ConfigV2:";
        str << "\n  width = " << config2->width();
        str << "\n  height = " << config2->height();
        str << "\n  orgX = " << config2->orgX();
        str << "\n  orgY = " << config2->orgY();
        str << "\n  binX = " << config2->binX();
        str << "\n  binY = " << config2->binY();
        str << "\n  exposureTime = " << config2->exposureTime();
        str << "\n  coolingTemp = " << config2->coolingTemp();
        str << "\n  gainIndex = " << config2->gainIndex();
        str << "\n  readoutSpeedIndex = " << config2->readoutSpeedIndex();
        str << "\n  readoutEventCode = " << config2->readoutEventCode();
        str << "\n  delayMode = " << config2->delayMode();
        str << "\n  frameSize = " << config2->frameSize();
        str << "\n  numPixels = " << config2->numPixels();
      }    
      return;
    }
    
    
    boost::shared_ptr<Psana::Princeton::ConfigV3> config3 = env.configStore().get(m_source);
    if (config3.get()) {    
      WithMsgLog(name(), info, str) {
        str << "Princeton::ConfigV3:";
        str << "\n  width = " << config3->width();
        str << "\n  height = " << config3->height();
        str << "\n  orgX = " << config3->orgX();
        str << "\n  orgY = " << config3->orgY();
        str << "\n  binX = " << config3->binX();
        str << "\n  binY = " << config3->binY();
        str << "\n  exposureTime = " << config3->exposureTime();
        str << "\n  coolingTemp = " << config3->coolingTemp();
        str << "\n  gainIndex = " << config3->gainIndex();
        str << "\n  readoutSpeedIndex = " << config3->readoutSpeedIndex();
        str << "\n  exposureEventCode = " << config3->exposureEventCode();
        str << "\n  numDelayShots = " << config3->numDelayShots();
        str << "\n  frameSize = " << config3->frameSize();
        str << "\n  numPixels = " << config3->numPixels();
      } 
      return;
    }

    boost::shared_ptr<Psana::Princeton::ConfigV4> config4 = env.configStore().get(m_source);
    if (config4) {
      WithMsgLog(name(), info, str) {
        str << "Princeton::ConfigV4:";
        str << "\n  width = " << config4->width();
        str << "\n  height = " << config4->height();
        str << "\n  orgX = " << config4->orgX();
        str << "\n  orgY = " << config4->orgY();
        str << "\n  binX = " << config4->binX();
        str << "\n  binY = " << config4->binY();
        str << "\n  maskedHeight = " << config4->maskedHeight();
        str << "\n  kineticHeight = " << config4->kineticHeight();
        str << "\n  vsSpeed = " << config4->vsSpeed();
        str << "\n  exposureTime = " << config4->exposureTime();
        str << "\n  coolingTemp = " << config4->coolingTemp();
        str << "\n  gainIndex = " << int(config4->gainIndex());
        str << "\n  readoutSpeedIndex = " << int(config4->readoutSpeedIndex());
        str << "\n  exposureEventCode = " << config4->exposureEventCode();
        str << "\n  numDelayShots = " << config4->numDelayShots();
        str << "\n  frameSize = " << config4->frameSize();
        str << "\n  numPixels = " << config4->numPixels();
      }
      return;
    }
  
    boost::shared_ptr<Psana::Princeton::ConfigV5> config5 = env.configStore().get(m_source);
    if (config5) {
      WithMsgLog(name(), info, str) {
        str << "Princeton::ConfigV5:";
        str << "\n  width = " << config5->width();
        str << "\n  height = " << config5->height();
        str << "\n  orgX = " << config5->orgX();
        str << "\n  orgY = " << config5->orgY();
        str << "\n  binX = " << config5->binX();
        str << "\n  binY = " << config5->binY();
        str << "\n  exposureTime = " << config5->exposureTime();
        str << "\n  coolingTemp = " << config5->coolingTemp();
        str << "\n  gainIndex = " << config5->gainIndex();
        str << "\n  readoutSpeedIndex = " << config5->readoutSpeedIndex();
        str << "\n  maskedHeight = " << config5->maskedHeight();
        str << "\n  kineticHeight = " << config5->kineticHeight();
        str << "\n  vsSpeed = " << config5->vsSpeed();
        str << "\n  infoReportInterval = " << config5->infoReportInterval();
        str << "\n  exposureEventCode = " << config5->exposureEventCode();
        str << "\n  numDelayShots = " << config5->numDelayShots();
        str << "\n  frameSize = " << config5->frameSize();
        str << "\n  numPixels = " << config5->numPixels();
      }
      return;
    }

    boost::shared_ptr<Psana::Pimax::ConfigV1> config1_pimax = env.configStore().get(m_source);
    if (config1_pimax) {    
      WithMsgLog(name(), info, str) {
        str << "Pimax::ConfigV1:";
        str << "\n  width = " << config1_pimax->width();
        str << "\n  height = " << config1_pimax->height();
        str << "\n  orgX = " << config1_pimax->orgX();
        str << "\n  orgY = " << config1_pimax->orgY();
        str << "\n  binX = " << config1_pimax->binX();
        str << "\n  binY = " << config1_pimax->binY();
        str << "\n  exposureTime = " << config1_pimax->exposureTime();
        str << "\n  coolingTemp = " << config1_pimax->coolingTemp();
        str << "\n  readoutSpeed = " << config1_pimax->readoutSpeed();
        str << "\n  gainIndex = " << config1_pimax->gainIndex();
        str << "\n  intensifierGain = " << config1_pimax->intensifierGain();
        str << "\n  gateDelay = " << config1_pimax->gateDelay();
        str << "\n  gateWidth = " << config1_pimax->gateWidth();
        str << "\n  maskedHeight = " << config1_pimax->maskedHeight();
        str << "\n  kineticHeight = " << config1_pimax->kineticHeight();
        str << "\n  vsSpeed = " << config1_pimax->vsSpeed();
        str << "\n  infoReportInterval = " << config1_pimax->infoReportInterval();
        str << "\n  exposureEventCode = " << config1_pimax->exposureEventCode();
        str << "\n  numIntegrationShots = " << config1_pimax->numIntegrationShots();
        str << "\n  frameSize = " << config1_pimax->frameSize();
        str << "\n  numPixelsX = " << config1_pimax->numPixelsX();
        str << "\n  numPixelsY = " << config1_pimax->numPixelsY();
        str << "\n  numPixels = " << config1_pimax->numPixels();
      }    
      return;
    }
  
    MsgLog(name(), info, "Princeton::ConfigV# is not found for source " << m_source);  
}

//-----------------------------
} // namespace Detector
//-----------------------------
