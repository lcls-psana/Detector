#ifndef DETECTOR_NDARRPRODUCERANDOR_H
#define DETECTOR_NDARRPRODUCERANDOR_H

//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// Description:
//	Class NDArrProducerAndor
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
#include <sstream>   // for stringstream
#include <boost/shared_ptr.hpp>

//-------------------------------
// Collaborating Class Headers --
//-------------------------------
//#include "Detector/GlobalMethods.h"
#include "psddl_psana/andor.ddl.h"

//-----------------------------

namespace Detector {

/// @addtogroup Detector

/**
 *  @ingroup Detector
 *
 *  @brief Produces ndarray<TOUT,2> from Andor camera raw data.
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

class NDArrProducerAndor : public NDArrProducerBase {
public:

  /// Data type for detector image 
  typedef uint16_t data_t;

  // Constructor
  NDArrProducerAndor(const PSEvt::Source& source, const unsigned& mode=0, const unsigned& pbits=0, const float& vdef=0);

  // Destructor
  virtual ~NDArrProducerAndor();

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
  NDArrProducerAndor ( const NDArrProducerAndor& );
  NDArrProducerAndor& operator = ( const NDArrProducerAndor& );

  inline const char* name(){return "NDArrProducerAndor";}
  void print_warning(const char* msg="");

//-----------------------------
  /**
   * @brief Returns ndarray with data for requested output type TOUT
   * Returns empty ndarray<TOUT,2> if data is missing.
   */

  template <typename TFRAME, typename TOUT>
  const ndarray<const TOUT, 2>
  getNDArrForType(PSEvt::Event& evt, PSEnv::Env& env) {

      m_count_ent ++;

      boost::shared_ptr<TFRAME> frame1 = evt.get(m_source, m_key, &m_src);
      if (frame1) {

          const ndarray<const data_t, 2>& nda_data = frame1->data();

          if(m_pbits & 2) { 
              MsgLog(name(), info, "Andor::FrameV# data for entry:" << m_count_ent << ":\n");
              for (int i=0; i<10; ++i) cout << " " << nda_data[0][i]; cout << "\n"; 
          }      

          // Return ndarray directly from data
          if(m_as_data) return nda_data; 

          // Copy ndarray from data with type changing
          ndarray<TOUT,2> nda_out( nda_data.shape() );
          typename ndarray<TOUT,2>::iterator it_out = nda_out.begin(); 
          for ( ndarray<const data_t, 2>::iterator it=nda_data.begin(); it!=nda_data.end(); ++it, ++it_out) {
              *it_out = (TOUT)*it;
          }

          if(m_pbits & 2) {for (int i=0; i<10; ++i) cout << " " << nda_out[0][i]; cout << "\n"; }      
 
          return nda_out;
      }

      ndarray<TOUT,2> nda;
      return nda;
  }

//-----------------------------

}; // class 

} // namespace Detector

#endif // DETECTOR_NDARRPRODUCERANDOR_H
