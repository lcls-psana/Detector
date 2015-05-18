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

#include "Detector/NDArrProducerCamera.h"

//-----------------------------

namespace {  
  void printFrameCoord(std::ostream& str, const Psana::Camera::FrameCoord& coord) {
    str << "(" << coord.column() << ", " << coord.row() << ")";
  }  
}

//-----------------------------
namespace Detector {

  //typedef NDArrProducerCamera::data_t data_t;

//-----------------------------

NDArrProducerCamera::NDArrProducerCamera(const PSEvt::Source& source, const unsigned& mode, const unsigned& pbits, const float& vdef)
  : NDArrProducerBase(source, mode, pbits, vdef)
  , m_count_evt(0)
  , m_count_msg(0)
{
  m_as_data         = (mode&1) ? true  : false;
  m_subtract_offset = (mode)   ? false : true; 
}

//-----------------------------

NDArrProducerCamera::~NDArrProducerCamera ()
{
}

//-----------------------------

void
NDArrProducerCamera::print_warning(const char* msg)
{
  m_count_msg++;
  if (m_count_msg < 11 && m_pbits) {
    MsgLog(name(), warning, "Psana::Camera::FrameV1 for data type" << msg 
           << " is not available in this run/event for source:" << m_source);
    if (m_count_msg == 10) MsgLog(name(), warning, "STOP PRINT WARNINGS for source:" << m_source);
  }
}

//-----------------------------

ndarray<const uint16_t, 2> 
NDArrProducerCamera::data_nda_uint16_2(PSEvt::Event& evt, PSEnv::Env& env)
{
  ndarray<const uint16_t, 2> nda = getNDArrForType16<Psana::Camera::FrameV1, uint16_t>(evt, env);
  if ( ! nda.empty()) return nda; 

  print_warning("uint16_t");
  return nda;
}

//-----------------------------

ndarray<const uint8_t, 2> 
NDArrProducerCamera::data_nda_uint8_2(PSEvt::Event& evt, PSEnv::Env& env)
{
  ndarray<const uint8_t, 2> nda = getNDArrForType8<Psana::Camera::FrameV1, uint8_t>(evt, env);
  if ( ! nda.empty()) return nda; 

  print_warning("uint8_t");
  return nda;
}
//-----------------------------

void
NDArrProducerCamera::print_config(PSEvt::Event& evt, PSEnv::Env& env)
{
  boost::shared_ptr<Psana::Camera::FrameFexConfigV1> frmConfig = env.configStore().get(m_source);
  if (frmConfig) {
    WithMsgLog(name(), info, str) {
      str << "Camera::FrameFexConfigV1:";
      str << "\n  forwarding = " << frmConfig->forwarding();
      str << "\n  forward_prescale = " << frmConfig->forward_prescale();
      str << "\n  processing = " << frmConfig->processing();
      str << "\n  roiBegin = ";
      ::printFrameCoord(str, frmConfig->roiBegin());
      str << "\n  roiEnd = ";
      ::printFrameCoord(str, frmConfig->roiEnd());
      str << "\n  threshold = " << frmConfig->threshold();
      str << "\n  number_of_masked_pixels = " << frmConfig->number_of_masked_pixels();
      const ndarray<const Psana::Camera::FrameCoord, 1>& masked_pixels = frmConfig->masked_pixel_coordinates();
      for (unsigned i = 0; i < masked_pixels.shape()[0]; ++ i) {
        str << "\n    ";
        ::printFrameCoord(str, masked_pixels[i]);
      }
    }
  }
  else MsgLog(name(), info, "Camera::FrameFexConfigV1 object is not found for source " << m_source);  

  //------------

  boost::shared_ptr<Psana::Camera::FrameV1> frmData = evt.get(m_source);
  if (frmData) {
    WithMsgLog(name(), info, str) {
      str << "Camera::FrameV1:"
          << "\n  width =" << frmData->width()
          << "\n  height=" << frmData->height()
          << "\n  depth =" << frmData->depth()
          << "\n  offset=" << frmData->offset() ;
    }
  }
  else MsgLog(name(), info, "Camera::FrameV1 object is not found for source " << m_source);  
}

//-----------------------------
} // namespace Detector
//-----------------------------
