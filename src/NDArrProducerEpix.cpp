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

#include "Detector/NDArrProducerEpix.h"

//-----------------------------

namespace Detector {

typedef NDArrProducerEpix::data_t data_t;

//-----------------------------

NDArrProducerEpix::NDArrProducerEpix(const PSEvt::Source& source, const unsigned& mode, const unsigned& pbits, const float& vdef)
  : NDArrProducerBase(source, mode, pbits, vdef)
  , m_count_ent(0)
  , m_count_msg(0)
{
  //m_as_data = (mode) ? false : true;
  m_as_data = true;
}

//-----------------------------

NDArrProducerEpix::~NDArrProducerEpix ()
{
}

//-----------------------------

void
NDArrProducerEpix::print_warning(const char* msg)
{
  m_count_msg++;
  if (m_count_msg < 11 && m_pbits) {
    MsgLog(name(), warning, "Epix::ElementV1,2 object"
           << " is not available in this run/event for source:" << m_source);
    if (m_count_msg == 10) MsgLog(name(), warning, "STOP PRINT WARNINGS for source:" << m_source);
  }
}

//-----------------------------

ndarray<const data_t, 2> 
NDArrProducerEpix::data_nda_uint16_2(PSEvt::Event& evt, PSEnv::Env& env)
{
  ndarray<const data_t, 2> nda1 = getNDArrForType<Psana::Epix::ElementV1, data_t>(evt, env);
  if ( ! nda1.empty()) return nda1; 

  ndarray<const data_t, 2> nda2 = getNDArrForType<Psana::Epix::ElementV2, data_t>(evt, env);
  if ( ! nda2.empty()) return nda2; 

  print_warning();
  ndarray<data_t, 2> nda;
  return nda; // empty
}

//-----------------------------

void
NDArrProducerEpix::print_config(PSEvt::Event& evt, PSEnv::Env& env)
{
  printConfigFromData(evt);

  if      (printConfigForType<Psana::Epix::ConfigV1>    (evt, env, "ConfigV1"    )) return;
  else if (printConfigForType<Psana::Epix::Config10KV1> (evt, env, "Config10KV1" )) return;
  else if (printConfigForType<Psana::Epix::Config100aV1>(evt, env, "Config100aV1")) return;

  MsgLog(name(), info, "Epix::ConfigV# is not found for source " << m_source);  
}

//-----------------------------

void
NDArrProducerEpix::printConfigFromData(PSEvt::Event& evt) {

  boost::shared_ptr<Psana::Epix::ElementV1> data1 = evt.get(m_source, m_key, &m_src);
  if (data1) {        
      const ndarray<const data_t, 2> data = data1->frame();
      std::stringstream ss; 
      ss << "Epix::ElementV1 at " << m_source;
      ss << "\n  vc           = " << int(data1->vc());
      ss << "\n  lane         = " << int(data1->lane());
      ss << "\n  acqCount     = " << data1->acqCount();
      ss << "\n  frameNumber  = " << data1->frameNumber();
      ss << "\n  ticks        = " << data1->ticks();
      ss << "\n  fiducials    = " << data1->fiducials();
      ss << "\n  frame        = " << data1->frame();
      ss << "\n  excludedRows = " << data1->excludedRows();
      ss << "\n  temperatures = " << data1->temperatures();
      ss << "\n  lastWord     = " << data1->lastWord();
      ss << "\n  data_ndarr:\n"   << data; 
      MsgLog(name(), info, ss.str());
  }

  boost::shared_ptr<Psana::Epix::ElementV2> data2 = evt.get(m_source, m_key, &m_src);
  if (data2) {        
      const ndarray<const data_t, 2> data = data2->frame();
      std::stringstream ss; 
      ss << "Epix::ElementV2 at "      << m_source;
      ss << "\n  vc                = " << int(data2->vc());
      ss << "\n  lane              = " << int(data2->lane());
      ss << "\n  acqCount          = " << data2->acqCount();
      ss << "\n  frameNumber       = " << data2->frameNumber();
      ss << "\n  ticks             = " << data2->ticks();
      ss << "\n  fiducials         = " << data2->fiducials();
      ss << "\n  frame             = " << data2->frame();
      ss << "\n  calibrationRows   = " << data2->calibrationRows();      //New
      ss << "\n  environmentalRows = " << data2->environmentalRows();    //New
      ss << "\n  temperatures      = " << data2->temperatures();
      ss << "\n  lastWord          = " << data2->lastWord();
      ss << "\n  data_ndarr:\n"        << data;  
      MsgLog(name(), info, ss.str());
  }
}
 
//-----------------------------
} // namespace Detector
//-----------------------------
