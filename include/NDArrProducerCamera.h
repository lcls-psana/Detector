#ifndef DETECTOR_NDARRPRODUCERCAMERA_H
#define DETECTOR_NDARRPRODUCERCAMERA_H

//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// Description:
//	Class NDArrProducerCamera
//
//------------------------------------------------------------------------

//----------------------
// Base Class Headers --
//----------------------
#include "Detector/NDArrProducerBase.h"

//-----------------
// C/C++ Headers --
//-----------------
#include <stdint.h>  // uint8_t, uint32_t, etc.
#include <algorithm> // for fill_n
#include <sstream>  // for stringstream
#include <boost/shared_ptr.hpp>

//-------------------------------
// Collaborating Class Headers --
//-------------------------------
//#include "Detector/GlobalMethods.h"
#include "psddl_psana/camera.ddl.h"

//-----------------------------

namespace Detector {

/// @addtogroup Detector

/**
 *  @ingroup Detector
 *
 *  @brief Produces ndarray<TOUT,2> from Camera raw data for specified TOUT.
 *
 *  @note This software was developed for the LCLS project.  If you use all or 
 *  part of it, please give an appropriate acknowledgment.
 *
 *  @version $Id$
 *
 *  @author Mikhail S. Dubrovin
 *
 *  @see NDArrProducerBase, NDArrProducerStore
 */

//-----------------------------

class NDArrProducerCamera : public NDArrProducerBase {
public:

  /// Data types
  //typedef uint16_t data16_t;
  //typedef uint8_t  data8_t;

  // Constructor
  NDArrProducerCamera(const PSEvt::Source& source, const unsigned& mode=0, const unsigned& pbits=0, const float& vdef=0);

  // Destructor
  virtual ~NDArrProducerCamera();

  /// Interface method
  virtual ndarray<const uint8_t, 2>  data_nda_uint8_2 (PSEvt::Event& evt, PSEnv::Env& env);
  virtual ndarray<const uint16_t, 2> data_nda_uint16_2(PSEvt::Event& evt, PSEnv::Env& env);

  /// Print configuration data
  virtual void print_config(PSEvt::Event& evt, PSEnv::Env& env);


  //protected:

private:

  bool          m_as_data;
  bool          m_subtract_offset;
  long          m_count_evt;
  long          m_count_msg;

  // Copy constructor and assignment are disabled by default
  NDArrProducerCamera ( const NDArrProducerCamera& );
  NDArrProducerCamera& operator = ( const NDArrProducerCamera& );

  inline const char* name(){return "NDArrProducerCamera";}
  void print_warning(const char* msg);

//-----------------------------

  template <typename T>
  ndarray<T,2> getNDArrDefault (const unsigned& rows=10, const unsigned& cols=10) {
    ndarray<T,2> nda = make_ndarray<T>(rows,cols);
    std::fill(nda.begin(), nda.end(), T(m_vdef));
    return nda;
  }

//-----------------------------
  /**
   * @brief Process event for frame type TFRAME uint16_t data, requested output type TOUT
   * Returns false if data is missing.
   */
  template <typename TFRAME, typename TOUT>
  ndarray<const TOUT, 2> 
  getNDArrForType16(PSEvt::Event& evt, PSEnv::Env& env)
  {
      boost::shared_ptr<TFRAME> frame = evt.get(m_source, m_key, &m_src);
      if (frame.get()) {

          TOUT offset = (m_subtract_offset) ? (TOUT)frame->offset() : 0;
    
          const ndarray<const uint16_t, 2>& data16 = frame->data16();
          if (not data16.empty()) {

              if(m_as_data) return frame->data16();

              if(m_pbits & 4) MsgLog(name(), info, "getNDArrForType16(...): Get image as ndarray<const uint16_t,2>,"
                                                          <<" frame offset=" << offset);
              ndarray<TOUT, 2> data_out = make_ndarray<TOUT>(frame->height(), frame->width());
              typename ndarray<TOUT, 2>::iterator oit;
              typename ndarray<const uint16_t, 2>::iterator dit;
              // This loop consumes ~5 ms/event for Opal1000 camera with 1024x1024 image size 
              
              if(m_dettype == ImgAlgos::FCCD960) { 
                // Do special processing for FCCD960 gain factor bits
                for(dit=data16.begin(), oit=data_out.begin(); dit!=data16.end(); ++dit, ++oit) { 

                  uint16_t code = *dit;
                  //std::cout << "  xx:" << (code>>14);
                  switch ((code>>14)&03) {
                    default :
                    case  0 : *oit = TOUT( code&017777 );      break; // gain 8 - max gain in electronics - use factor 1 
                    case  1 : *oit = TOUT((code&017777) << 2); break; // gain 2 - use factor 4
                    case  3 : *oit = TOUT((code&017777) << 3); break; // gain 1 - use factor 8
                  }
                }
              }
              else {
                for(dit=data16.begin(), oit=data_out.begin(); dit!=data16.end(); ++dit, ++oit) { *oit = TOUT(*dit) - offset; }
              }
              
              return data_out;
          }
      }

      ndarray<TOUT,2> nda; // empty ndarray
      return nda; // getNDArrDefault<TOUT>();
  }


//-----------------------------
  /**
   * @brief Process event for frame type TFRAME uint8_t data, requested output type TOUT
   * Returns false if data is missing.
   */
  template <typename TFRAME, typename TOUT>
  ndarray<const TOUT, 2> 
  getNDArrForType8(PSEvt::Event& evt, PSEnv::Env& env)
  {
      boost::shared_ptr<TFRAME> frame = evt.get(m_source, m_key, &m_src);
      if (frame.get()) {

          TOUT offset = (m_subtract_offset) ? (TOUT)frame->offset() : 0;
    
          const ndarray<const uint8_t, 2>& data8 = frame->data8();
          if (not data8.empty()) {
	      if(m_as_data) return data8;              

              if(m_pbits & 4) MsgLog(name(), info, "getNDArrForType8(...): Get image as ndarray<const uint8_t,2>, subtract offset=" << offset);
              ndarray<TOUT, 2> data_out = make_ndarray<TOUT>(frame->height(), frame->width());
              typename ndarray<TOUT, 2>::iterator oit;
              typename ndarray<const uint8_t, 2>::iterator dit;
              for(dit=data8.begin(), oit=data_out.begin(); dit!=data8.end(); ++dit, ++oit) { *oit = TOUT(*dit) - offset; }
              
              return data_out;
          }
      }

      ndarray<TOUT,2> nda; // empty ndarray
      return nda;
  }

//-----------------------------

}; // class 

} // namespace Detector

#endif // DETECTOR_NDARRPRODUCERCAMERA_H
