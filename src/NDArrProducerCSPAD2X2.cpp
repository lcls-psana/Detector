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

#include "Detector/NDArrProducerCSPAD2X2.h"

//-----------------------------

namespace Detector {

typedef NDArrProducerCSPAD2X2::data_t data_t;

//-----------------------------

NDArrProducerCSPAD2X2::NDArrProducerCSPAD2X2(const PSEvt::Source& source, const unsigned& mode, const unsigned& pbits, const float& vdef)
  : NDArrProducerBase(source, mode, pbits, vdef)
  , m_count_ent(0)
  , m_count_msg(0)
{
  //m_as_data = (mode) ? false : true;
  m_as_data = true;
}

//-----------------------------

NDArrProducerCSPAD2X2::~NDArrProducerCSPAD2X2 ()
{
}

//-----------------------------

void
NDArrProducerCSPAD2X2::print_warning(const char* msg)
{
  m_count_msg++;
  if (m_count_msg < 11 && m_pbits) {
    MsgLog(name(), warning, "CsPad2x2::ElementV1 object"
           << " is not available in this run/event for source:" << m_source);
    if (m_count_msg == 10) MsgLog(name(), warning, "STOP PRINT WARNINGS for source:" << m_source);
  }
}

//-----------------------------

ndarray<const data_t,3> 
NDArrProducerCSPAD2X2::data_nda_int16_3(PSEvt::Event& evt, PSEnv::Env& env)
{
  ndarray<const data_t,3> nda1 = getNDArrForType<Psana::CsPad2x2::ElementV1, data_t>(evt, env);
  if ( ! nda1.empty()) return nda1; 

  print_warning();
  ndarray<data_t,3> nda;
  return nda; // empty
}

//-----------------------------

void
NDArrProducerCSPAD2X2::print_config(PSEvt::Event& evt, PSEnv::Env& env)
{
  printConfigFromData(evt);

  boost::shared_ptr<Psana::CsPad2x2::ConfigV1> config1 = env.configStore().get(m_source);
  if (config1) {    
    WithMsgLog(name(), info, str) {
      str << "CsPad2x2::ConfigV1:";
      str << "\n  concentratorVersion = " << config1->concentratorVersion();
      str << "\n  protectionEnable = " << config1->protectionEnable();
      str << "\n  protectionThreshold:";
      str << "\n    adcThreshold= " << config1->protectionThreshold().adcThreshold()
          << "\n    pixelCountThreshold= " << config1->protectionThreshold().pixelCountThreshold();
      str << "\n  inactiveRunMode = " << config1->inactiveRunMode();
      str << "\n  activeRunMode = " << config1->activeRunMode();
      str << "\n  tdi = " << config1->tdi();
      str << "\n  payloadSize = " << config1->payloadSize();
      str << "\n  badAsicMask1 = " << config1->badAsicMask();
      str << "\n  asicMask = " << config1->asicMask();
      str << "\n  numAsicsRead = " << config1->numAsicsRead();
      str << "\n  roiMask = " << config1->roiMask();
      str << "\n  numAsicsStored = " << config1->numAsicsStored();
      const Psana::CsPad2x2::ConfigV1QuadReg& quad = config1->quad();
      str << "\n  quad:";
      str << "\n    shiftSelect = " << quad.shiftSelect();
      str << "\n    edgeSelect = " << quad.edgeSelect();
      str << "\n    readClkSet = " << quad.readClkSet();
      str << "\n    readClkHold = " << quad.readClkHold();
      str << "\n    dataMode = " << quad.dataMode();
      str << "\n    prstSel = " << quad.prstSel();
      str << "\n    acqDelay = " << quad.acqDelay();
      str << "\n    intTime = " << quad.intTime();
      str << "\n    digDelay = " << quad.digDelay();
      str << "\n    ampIdle = " << quad.ampIdle();
      str << "\n    injTotal = " << quad.injTotal();
      str << "\n    rowColShiftPer = " << quad.rowColShiftPer();
      str << "\n    ampReset = " << quad.ampReset();
      str << "\n    digCount = " << quad.digCount();
      str << "\n    digPeriod = " << quad.digPeriod();
      str << "\n    PeltierEnable = " << quad.PeltierEnable();
      str << "\n    kpConstant = " << quad.kpConstant();
      str << "\n    kiConstant = " << quad.kiConstant();
      str << "\n    kdConstant = " << quad.kdConstant();
      str << "\n    humidThold = " << quad.humidThold();
      str << "\n    setPoint = " << quad.setPoint();
      str << "\n    digitalPots = " << quad.dp().pots();
      str << "\n    readOnly = shiftTest: " << quad.ro().shiftTest() << " verstion: " << quad.ro().version();
      str << "\n    gainMap = " << quad.gm().gainMap();
    }
    return;
  }

  boost::shared_ptr<Psana::CsPad2x2::ConfigV2> config2 = env.configStore().get(m_source);
  if (config2) {
    WithMsgLog(name(), info, str) {
      str << "CsPad2x2::ConfigV2:";
      str << "\n  concentratorVersion = " << config2->concentratorVersion();
      str << "\n  protectionEnable = " << config2->protectionEnable();
      str << "\n  protectionThreshold:";
      str << "\n    adcThreshold= " << config2->protectionThreshold().adcThreshold()
          << "\n    pixelCountThreshold= " << config2->protectionThreshold().pixelCountThreshold();
      str << "\n  inactiveRunMode = " << config2->inactiveRunMode();
      str << "\n  activeRunMode = " << config2->activeRunMode();
      str << "\n  runTriggerDelay = " << config2->runTriggerDelay();
      str << "\n  tdi = " << config2->tdi();
      str << "\n  payloadSize = " << config2->payloadSize();
      str << "\n  badAsicMask1 = " << config2->badAsicMask();
      str << "\n  asicMask = " << config2->asicMask();
      str << "\n  numAsicsRead = " << config2->numAsicsRead();
      str << "\n  roiMask = " << config2->roiMask();
      str << "\n  numAsicsStored = " << config2->numAsicsStored();
      const Psana::CsPad2x2::ConfigV2QuadReg& quad = config2->quad();
      str << "\n  quad:";
      str << "\n    shiftSelect = " << quad.shiftSelect();
      str << "\n    edgeSelect = " << quad.edgeSelect();
      str << "\n    readClkSet = " << quad.readClkSet();
      str << "\n    readClkHold = " << quad.readClkHold();
      str << "\n    dataMode = " << quad.dataMode();
      str << "\n    prstSel = " << quad.prstSel();
      str << "\n    acqDelay = " << quad.acqDelay();
      str << "\n    intTime = " << quad.intTime();
      str << "\n    digDelay = " << quad.digDelay();
      str << "\n    ampIdle = " << quad.ampIdle();
      str << "\n    injTotal = " << quad.injTotal();
      str << "\n    rowColShiftPer = " << quad.rowColShiftPer();
      str << "\n    ampReset = " << quad.ampReset();
      str << "\n    digCount = " << quad.digCount();
      str << "\n    digPeriod = " << quad.digPeriod();
      str << "\n    biasTuning = " << quad.biasTuning();
      str << "\n    pdpmndnmBalance = " << quad.pdpmndnmBalance();
      str << "\n    PeltierEnable = " << quad.PeltierEnable();
      str << "\n    kpConstant = " << quad.kpConstant();
      str << "\n    kiConstant = " << quad.kiConstant();
      str << "\n    kdConstant = " << quad.kdConstant();
      str << "\n    humidThold = " << quad.humidThold();
      str << "\n    setPoint = " << quad.setPoint();
      str << "\n    digitalPots = " << quad.dp().pots();
      str << "\n    readOnly = shiftTest: " << quad.ro().shiftTest() << " verstion: " << quad.ro().version();
      str << "\n    gainMap = " << quad.gm().gainMap();
    }
    return;
  }

  MsgLog(name(), info, "CsPad2x2::ConfigV1,2 is not found for source " << m_source);  
}

//-----------------------------

void
NDArrProducerCSPAD2X2::printConfigFromData(PSEvt::Event& evt) {

  boost::shared_ptr<Psana::CsPad2x2::ElementV1> elem1 = evt.get(m_source, m_key);
  if (elem1) {
    WithMsgLog(name(), info, str) {
      str << "CsPad2x2::ElementV1:";
      str << "\n  virtual_channel = " << elem1->virtual_channel() ;
      str << "\n  lane = " << elem1->lane() ;
      str << "\n  tid = " << elem1->tid() ;
      str << "\n  acq_count = " << elem1->acq_count() ;
      str << "\n  op_code = " << elem1->op_code() ;
      str << "\n  quad = " << elem1->quad() ;
      str << "\n  seq_count = " << elem1->seq_count() ;
      str << "\n  ticks = " << elem1->ticks() ;
      str << "\n  fiducials = " << elem1->fiducials() ;
      str << "\n  frame_type = " << elem1->frame_type() ;

      str << "\n    sb_temp = " << elem1->sb_temp();

      const ndarray<const int16_t, 3>& data = elem1->data();
      str << "\n    common_mode = [ ";
      for (unsigned i = 0; i != data.shape()[2]; ++ i) {
          str << elem1->common_mode(i) << ' ';
      }
      str << "]";
      str << "\n    data = " << data;
    }
  }
}
 
//-----------------------------
} // namespace Detector
//-----------------------------
