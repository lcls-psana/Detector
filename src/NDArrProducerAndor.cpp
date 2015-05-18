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

#include "Detector/NDArrProducerAndor.h"

//-----------------------------

namespace Detector {

typedef NDArrProducerAndor::data_t data_t;

//-----------------------------

NDArrProducerAndor::NDArrProducerAndor(const PSEvt::Source& source, const unsigned& mode, const unsigned& pbits, const float& vdef)
  : NDArrProducerBase(source, mode, pbits, vdef)
  , m_count_ent(0)
  , m_count_msg(0)
{
  //m_as_data = (mode) ? false : true;
  m_as_data = true;
}

//-----------------------------

NDArrProducerAndor::~NDArrProducerAndor ()
{
}

//-----------------------------

void
NDArrProducerAndor::print_warning(const char* msg)
{
  m_count_msg++;
  if (m_count_msg < 11 && m_pbits) {
    MsgLog(name(), warning, "Andor::FrameV1 object"
           << " is not available in this run/event for source:" << m_source);
    if (m_count_msg == 10) MsgLog(name(), warning, "STOP PRINT WARNINGS for source:" << m_source);
  }
}

//-----------------------------

ndarray<const data_t, 2> 
NDArrProducerAndor::data_nda_uint16_2(PSEvt::Event& evt, PSEnv::Env& env)
{
  ndarray<const data_t, 2> nda = getNDArrForType<Psana::Andor::FrameV1, data_t>(evt, env);
  if ( ! nda.empty()) return nda; 

  print_warning();
  return nda; // empty
}

//-----------------------------

void
NDArrProducerAndor::print_config(PSEvt::Event& evt, PSEnv::Env& env)
{
  boost::shared_ptr<Psana::Andor::ConfigV1> config1 = env.configStore().get(m_source);
  if (config1) {
    WithMsgLog(name(), info, str) {
      str << "Andor::ConfigV1:";
      str << "\n  width = " << config1->width();
      str << "\n  height = " << config1->height();
      str << "\n  orgX = " << config1->orgX();
      str << "\n  orgY = " << config1->orgY();
      str << "\n  binX = " << config1->binX();
      str << "\n  binY = " << config1->binY();
      str << "\n  exposureTime = " << config1->exposureTime();
      str << "\n  coolingTemp = " << config1->coolingTemp();
      str << "\n  fanMode = " << int(config1->fanMode());
      str << "\n  baselineClamp = " << int(config1->baselineClamp());
      str << "\n  highCapacity = " << int(config1->highCapacity());
      str << "\n  gainIndex = " << int(config1->gainIndex());
      str << "\n  readoutSpeedIndex = " << config1->readoutSpeedIndex();
      str << "\n  exposureEventCode = " << config1->exposureEventCode();
      str << "\n  numDelayShots = " << config1->numDelayShots();
      str << "\n  frameSize = " << config1->frameSize();
      str << "\n  numPixels = " << config1->numPixels();
    }
  }
  else MsgLog(name(), info, "Andor::ConfigV1 is not found for source " << m_source);  

  boost::shared_ptr<Psana::Andor::FrameV1> frame1 = evt.get(m_source, m_key, &m_src);
  if (frame1) {
    const ndarray<const data_t, 2>& nda_data = frame1->data();
    WithMsgLog(name(), info, str) {
      str << "Andor::FrameV1"
      	  << "\n  shotIdStart = " << frame1->shotIdStart()
      	  << "\n  readoutTime = " << frame1->readoutTime()
      	  << "\n  temperature = " << frame1->temperature()
      	  << "\n  data:";
      for (int i=0; i<10; ++i) str << " " << nda_data[0][i]; str << " ..."; 
    }
  }
  else MsgLog(name(), info, "Andor::FrameV1 is not found for source " << m_source);  
}

//-----------------------------
} // namespace Detector
//-----------------------------
