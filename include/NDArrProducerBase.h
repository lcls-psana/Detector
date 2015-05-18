#ifndef DETECTOR_NDARRPRODUCERBASE_H
#define DETECTOR_NDARRPRODUCERBASE_H

//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// $Revision$
//------------------------------------------------------------------------

//-----------------
// C/C++ Headers --
//-----------------
//#include <iostream>
//#include <string>
//#include <map>
#include <stdint.h> // for uint8_t, uint16_t etc.

//-------------------------------
// Collaborating Class Headers --
//-------------------------------

#include "ImgAlgos/GlobalMethods.h" // for DETECTOR_TYPE, getRunNumber(evt), detectorTypeForSource, etc.
#include "ndarray/ndarray.h"
#include "PSEvt/Event.h"
#include "PSEnv/Env.h"
#include "PSEvt/Source.h"
#include "MsgLogger/MsgLogger.h"
//#include "PSEvt/EventId.h"

//-----------------------------

namespace Detector {


/// @addtogroup Detector

/**
 *  @ingroup Detector
 *
 *  @brief Abstract base class defining interface to access raw data as ndarray.
 *
 *  This software was developed for the LCLS project. If you use all or 
 *  part of it, please give an appropriate acknowledgment.
 *
 *  @see NDArrProducerCSPAD, NDArrProducerStore
 *
 *  @version $Id$
 *
 *  @author Mikhail S. Dubrovin
 *
 */

//----------------

class NDArrProducerBase  {
public:

  //typedef unsigned  shape_t;
  //typedef int16_t   data_int16_t;
  //typedef uint16_t  data_uint16_t;
  //typedef float     data_float_t;

  // Constructor
  NDArrProducerBase(const PSEvt::Source& source, const unsigned& mode=0, const unsigned& pbits=0, const float& vdef=0);

  // Constructor
  NDArrProducerBase(const std::string& str_src, const unsigned& mode=0, const unsigned& pbits=0, const float& vdef=0);

  // Destructor
  virtual ~NDArrProducerBase();

  // NOTE: THE METHOD DECLARED AS virtual <type> <method>() = 0; (equal to 0) IS PURE VIRTUAL, NEEDS TO BE IMPLEMENTED IN DERIVED CLASS

  virtual ndarray<const int16_t, 1>  data_nda_int16_1(PSEvt::Event& evt, PSEnv::Env& env)  { print_def("data_nda_int16_1"); return make_ndarray<int16_t>(1); }
  virtual ndarray<const int16_t, 2>  data_nda_int16_2(PSEvt::Event& evt, PSEnv::Env& env)  { print_def("data_nda_int16_2"); return make_ndarray<int16_t>(1,1); } 
  virtual ndarray<const int16_t, 3>  data_nda_int16_3(PSEvt::Event& evt, PSEnv::Env& env)  { print_def("data_nda_int16_3"); return make_ndarray<int16_t>(1,1,1); } 
  virtual ndarray<const int16_t, 4>  data_nda_int16_4(PSEvt::Event& evt, PSEnv::Env& env)  { print_def("data_nda_int16_4"); return make_ndarray<int16_t>(1,1,1,1); } 
				     								                 
  //virtual ndarray<const uint16_t, 1> data_nda_uint16_1(PSEvt::Event& evt, PSEnv::Env& env) { print_def("data_nda_uint16_1"); return make_ndarray<uint16_t>(1); } 
  virtual ndarray<const uint16_t, 2> data_nda_uint16_2(PSEvt::Event& evt, PSEnv::Env& env) { print_def("data_nda_uint16_2"); return make_ndarray<uint16_t>(1,1); }
  virtual ndarray<const uint16_t, 3> data_nda_uint16_3(PSEvt::Event& evt, PSEnv::Env& env) { print_def("data_nda_uint16_3"); return make_ndarray<uint16_t>(1,1,1); } 
  //virtual ndarray<const uint16_t, 4> data_nda_uint16_4(PSEvt::Event& evt, PSEnv::Env& env) { print_def("data_nda_uint16_4"); return make_ndarray<uint16_t>(1,1,1,1); }

  //virtual ndarray<const uint8_t, 1> data_nda_uint8_1(PSEvt::Event& evt, PSEnv::Env& env) { print_def("data_nda_uint8_1"); return make_ndarray<uint8_t>(1); } 
  virtual ndarray<const uint8_t, 2> data_nda_uint8_2(PSEvt::Event& evt, PSEnv::Env& env) { print_def("data_nda_uint8_2"); return make_ndarray<uint8_t>(1,1); }
  //virtual ndarray<const uint8_t, 3> data_nda_uint8_3(PSEvt::Event& evt, PSEnv::Env& env) { print_def("data_nda_uint8_3"); return make_ndarray<uint8_t>(1,1,1); } 
  //virtual ndarray<const uint8_t, 4> data_nda_uint8_4(PSEvt::Event& evt, PSEnv::Env& env) { print_def("data_nda_uint8_4"); return make_ndarray<uint8_t>(1,1,1,1); }

  /// Returns the pointer to array with data
  //virtual const int16_t* data_int16();

  /// Print member data
  virtual void print();

  /// Print configuration data
  virtual void print_config(PSEvt::Event& evt, PSEnv::Env& env);

protected:

  std::string   m_str_src;        // i.e. CxiDs1.0:Cspad.0   
  PSEvt::Source m_source;         // Data source set from config file
  Pds::Src      m_src;
  std::string   m_key;            // empty string for raw data  
  unsigned      m_mode;
  float         m_vdef;
  unsigned      m_pbits;

  ImgAlgos::DETECTOR_TYPE m_dettype;  // numerated detector type defined from source string info

private:

  long          m_count_msg;

  inline const char* name(){return "NDArrProducerBase";}
  void print_def(const char* name);

}; // class

} // namespace 

#endif // DETECTOR_NDARRPRODUCERBASE_H
