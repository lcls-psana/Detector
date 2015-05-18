#ifndef DETECTOR_NDARRPRODUCERPRINCETON_H
#define DETECTOR_NDARRPRODUCERPRINCETON_H

//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// Description:
//	Class NDArrProducerPrinceton
//
//------------------------------------------------------------------------

//----------------------
// Base Class Headers --
//----------------------
#include "Detector/NDArrProducerBase.h"

//-----------------
// C/C++ Headers --
//-----------------
//#include <stdint.h>  // uint8_t, uint32_t, etc.
//#include <algorithm> // for fill_n
//#include <sstream>   // for stringstream
//#include <boost/shared_ptr.hpp>

//-------------------------------
// Collaborating Class Headers --
//-------------------------------
//#include "Detector/GlobalMethods.h"
#include "psddl_psana/princeton.ddl.h"
#include "psddl_psana/pimax.ddl.h"

//-----------------------------

namespace Detector {

/// @addtogroup Detector

/**
 *  @ingroup Detector
 *
 *  @brief Produces ndarray<TOUT,2> from Princeton camera raw data.
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

class NDArrProducerPrinceton : public NDArrProducerBase {
public:

  /// Data type for detector image 
  typedef uint16_t data_t;

  // Constructor
  NDArrProducerPrinceton(const PSEvt::Source& source, const unsigned& mode=0, const unsigned& pbits=0, const float& vdef=0);

  // Destructor
  virtual ~NDArrProducerPrinceton();

  /// Interface method
  virtual ndarray<const data_t, 2> data_nda_uint16_2(PSEvt::Event& evt, PSEnv::Env& env);

  /// Print configuration data
  virtual void print_config(PSEvt::Event& evt, PSEnv::Env& env);

  //protected:

private:

  bool          m_as_data;
  long          m_count_ent;
  long          m_count_msg;

  // Copy constructor and assignment are disabled by default
  NDArrProducerPrinceton ( const NDArrProducerPrinceton& );
  NDArrProducerPrinceton& operator = ( const NDArrProducerPrinceton& );

  inline const char* name(){return "NDArrProducerPrinceton";}

  void print_warning(const char* msg="");

//-----------------------------

  /**
   * @brief Get Princeton frame from Psana::Princeton::FramesV1 data object and copy them in the ndarray<TOUT, 2> nda_out
   * Returns false if data is missing.
   */

  template <typename TFRAME, typename TOUT>
  ndarray<const data_t, 2> 
  getNDArrForType(PSEvt::Event& evt, PSEnv::Env& env) {

      m_count_ent ++;

      boost::shared_ptr<TFRAME> frame = evt.get(m_source, m_key, &m_src);

      if (frame.get()) {

          // Get reference to data ndarray 
          const ndarray<const data_t,2>& nda_data = frame->data(); 

          if(m_as_data) return nda_data;

          // Create and initialize the array of the same shape as data, but for all 2x1...
          ndarray<TOUT,2> nda_out(nda_data.shape());
          //std::fill(nda_out.begin(), nda_out.end(), TOUT(0));    
 
          // Pixel-to-pixel copy of data ndarray to output ndarray with type conversion:
          typename ndarray<TOUT,2>::iterator it_out = nda_out.begin(); 
          for ( ndarray<const data_t,2>::iterator it=nda_data.begin(); it!=nda_data.end(); ++it, ++it_out) {
              *it_out = (TOUT)*it;
          } 

          //if(m_pbits & 1 && m_count_ent < 2) MsgLog(name(), info, " I/O data type: " << strOfDataTypeAndSize<data_t>());
          //if(m_pbits & 8) MsgLog(name(), info, stringOf2DArrayData<data_t>(frame->data(), std::string(" data: ")));

          return nda_out;
      }

      ndarray<TOUT,2> nda;
      return nda;
  }

//-----------------------------
//-----------------------------

}; // class 

} // namespace Detector

#endif // DETECTOR_NDARRPRODUCERPRINCETON_H
