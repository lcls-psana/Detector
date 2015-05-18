//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// Author List:
//      Mikhail S. Dubrovin
//
//------------------------------------------------------------------------

//---------------
// -- Headers --
//---------------

#include "Detector/NDArrProducerBase.h"

//-----------------------------
namespace Detector {

  //typedef NDArrProducerBase::data_t data_t;

//-----------------------------

NDArrProducerBase::NDArrProducerBase(const PSEvt::Source& source, const unsigned& mode, const unsigned& pbits, const float& vdef)
  : m_source(source)
  , m_key(std::string())
  , m_mode(mode)
  , m_vdef(vdef)
  , m_pbits(pbits)
  , m_count_msg(0)
{
  std::stringstream ss; ss << source;
  m_str_src = ss.str();
  m_dettype = ImgAlgos::detectorTypeForSource(m_source);

  if (m_pbits) print();  
}

//-----------------------------

NDArrProducerBase::NDArrProducerBase(const std::string& str_src, const unsigned& mode, const unsigned& pbits, const float& vdef)
{
  NDArrProducerBase(PSEvt::Source(str_src), mode, pbits, vdef);
}

//-----------------------------

NDArrProducerBase::~NDArrProducerBase ()
{
}

//-----------------------------
//-----------------------------

/*
ndarray<data_t,3>  
NDArrProducerBase::getNDArr(PSEvt::Event& evt, PSEnv::Env& env)
{
  return make_ndarray<data_t>(2,4,8);
}
*/

//-----------------------------

void
NDArrProducerBase::print()
{
  MsgLog(name(), info, "\n  Input parameters:"
         << "\n  source        : " << m_source
         << "\n  str_src       : " << m_str_src
         << "\n  key           : " << m_key      
         << "\n  mode          : " << m_mode      
         << "\n  vdef          : " << m_vdef
         << "\n  pbits         : " << m_pbits
         << "\n  dettype       : " << m_dettype
         << "\n  detector      : " << ImgAlgos::stringForDetType(m_dettype)
	 );
}
//-----------------------------

void
NDArrProducerBase::print_config(PSEvt::Event& evt, PSEnv::Env& env)
{
  MsgLog(name(), info, "Default method print_config(evt,env) should be re-implemented in derived class");
}

//-----------------------------

void
NDArrProducerBase::print_def(const char* method)
{
  MsgLog(name(), info, "Default method: " << method << " should be re-implemented in derived class"); 
}

//-----------------------------
} // namespace Detector
//-----------------------------
