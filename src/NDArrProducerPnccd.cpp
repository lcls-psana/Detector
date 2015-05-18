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

#include "Detector/NDArrProducerPnccd.h"

//-----------------------------

namespace Detector {

typedef NDArrProducerPnccd::data_t data_t;

//-----------------------------

NDArrProducerPnccd::NDArrProducerPnccd(const PSEvt::Source& source, const unsigned& mode, const unsigned& pbits, const float& vdef)
  : NDArrProducerBase(source, mode, pbits, vdef)
  , m_count_ent(0)
  , m_count_msg(0)
{
  //m_as_data = (mode) ? false : true;
  m_as_data = true;
}

//-----------------------------

NDArrProducerPnccd::~NDArrProducerPnccd ()
{
}

//-----------------------------

void
NDArrProducerPnccd::print_warning(const char* msg)
{
  m_count_msg++;
  if (m_count_msg < 11 && m_pbits) {
    MsgLog(name(), warning, "PNCCD::FramesV1 object"
           << " is not available in this run/event for source:" << m_source);
    if (m_count_msg == 10) MsgLog(name(), warning, "STOP PRINT WARNINGS for source:" << m_source);
  }
}

//-----------------------------

ndarray<const data_t, 3> 
NDArrProducerPnccd::data_nda_uint16_3(PSEvt::Event& evt, PSEnv::Env& env)
{
  ndarray<const data_t, 3> nda = getNDArrForType<Psana::PNCCD::FramesV1, data_t>(evt, env);
  if ( ! nda.empty()) return nda; 

  print_warning();
  return nda; // empty
}

//-----------------------------

void
NDArrProducerPnccd::print_config(PSEvt::Event& evt, PSEnv::Env& env)
{
  boost::shared_ptr<Psana::PNCCD::ConfigV1> config1 = env.configStore().get(m_source);
  if (config1.get()) {    
      WithMsgLog(name(), info, str) {
        str << "PNCCD::ConfigV1:";
        str << "\n  numLinks = " << config1->numLinks();
        str << "\n  payloadSizePerLink = " << config1->payloadSizePerLink();
      }    
      return;
  }

  boost::shared_ptr<Psana::PNCCD::ConfigV2> config2 = env.configStore().get(m_source);
  if (config2.get()) {    
      WithMsgLog(name(), info, str) {
        str << "PNCCD::ConfigV2:";
        str << "\n  numLinks = "             << config2->numLinks();
        str << "\n  payloadSizePerLink = "   << config2->payloadSizePerLink();
        str << "\n  numChannels = "          << config2->numChannels();
        str << "\n  numRows = "              << config2->numRows();
        str << "\n  numSubmoduleChannels = " << config2->numSubmoduleChannels();
        str << "\n  numSubmoduleRows = "     << config2->numSubmoduleRows();
        str << "\n  numSubmodules = "        << config2->numSubmodules();
        str << "\n  camexMagic = "           << config2->camexMagic();
        str << "\n  info = "                 << config2->info();
        str << "\n  timingFName = "          << config2->timingFName();
      } 
      return;
  }

  MsgLog(name(), info, "PNCCD::ConfigV# is not found for source " << m_source);  
}

//-----------------------------
} // namespace Detector
//-----------------------------
