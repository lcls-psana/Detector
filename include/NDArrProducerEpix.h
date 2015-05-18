#ifndef DETECTOR_NDARRPRODUCERPEPIX_H
#define DETECTOR_NDARRPRODUCERPEPIX_H

//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// Description:
//	Class NDArrProducerEpix
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
#include "psddl_psana/epix.ddl.h"

//-----------------------------

namespace Detector {

/// @addtogroup Detector

/**
 *  @ingroup Detector
 *
 *  @brief Produces ndarray<TOUT,2> from Epix camera raw data.
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

class NDArrProducerEpix : public NDArrProducerBase {
public:

  /// Data type for detector image 
  typedef uint16_t data_t;

  // Constructor
  NDArrProducerEpix(const PSEvt::Source& source, const unsigned& mode=0, const unsigned& pbits=0, const float& vdef=0);

  // Destructor
  virtual ~NDArrProducerEpix();

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
  NDArrProducerEpix ( const NDArrProducerEpix& );
  NDArrProducerEpix& operator = ( const NDArrProducerEpix& );

  inline const char* name(){return "NDArrProducerEpix";}

  void print_warning(const char* msg="");
  void printConfigFromData(PSEvt::Event& evt);

//-----------------------------

  /**
   * @brief Prints Epix configuration parameters. 
   * Returns false if configuration is missing.
   */

  template <typename T>
    bool printConfigForType(PSEvt::Event& evt, PSEnv::Env& env, const std::string& objname=std::string("ConfigV1")) {

          boost::shared_ptr<T> config1 = env.configStore().get(m_source);
          if (config1.get()) {    
              WithMsgLog(name(), info, str) {
                str << "Epix::" << objname;
                str << "\n  version                  = " << config1->version();
                str << "\n  digitalCardId0           = " << config1->digitalCardId0();
                str << "\n  digitalCardId1           = " << config1->digitalCardId1();
                str << "\n  analogCardId0            = " << config1->analogCardId0();
                str << "\n  analogCardId1            = " << config1->analogCardId1();
                //str << "\n  lastRowExclusions        = " << config1->lastRowExclusions(); //missing in Epix100a
                str << "\n  numberOfAsicsPerRow      = " << config1->numberOfAsicsPerRow();
                str << "\n  numberOfAsicsPerColumn   = " << config1->numberOfAsicsPerColumn();
                str << "\n  numberOfRowsPerAsic      = " << config1->numberOfRowsPerAsic();
                str << "\n  numberOfPixelsPerAsicRow = " << config1->numberOfPixelsPerAsicRow();
                str << "\n  baseClockFrequency       = " << config1->baseClockFrequency();
                str << "\n  asicMask                 = " << config1->asicMask();
                str << "\n  numberOfRows             = " << config1->numberOfRows();
                str << "\n  numberOfColumns          = " << config1->numberOfColumns();
                str << "\n  numberOfAsics            = " << config1->numberOfAsics();  
              }    
            return true;
          }
	  return false;
  }


//-----------------------------

  /**
   * @brief Get Epix frame from Psana::Epix::FramesV1 data object and copy them in the ndarray<TOUT, 2> nda_out
   * Returns false if data is missing.
   */

  template <typename TFRAME, typename TOUT>
  ndarray<const data_t, 2> 
  getNDArrForType(PSEvt::Event& evt, PSEnv::Env& env) {

      m_count_ent ++;

      boost::shared_ptr<TFRAME> frame = evt.get(m_source, m_key, &m_src);

      if (frame.get()) {

          // Get reference to data ndarray 
          const ndarray<const data_t,2>& nda_data = frame->frame(); 

          if(m_as_data) return nda_data;

          // Create and initialize the array of the same shape as data, but for all 2x1...
          ndarray<TOUT,2> nda_out(nda_data.shape());
          //std::fill(nda_out.begin(), nda_out.end(), TOUT(0));    
 
          // Pixel-to-pixel copy of data ndarray to output ndarray with type conversion:
          typename ndarray<TOUT,2>::iterator it_out = nda_out.begin(); 
          for ( ndarray<const data_t,2>::iterator it=nda_data.begin(); it!=nda_data.end(); ++it, ++it_out) {
              *it_out = (TOUT)*it;
          } 

          return nda_out;
      }

      ndarray<TOUT,2> nda;
      return nda;
  }

//-----------------------------
//-----------------------------

}; // class 

} // namespace Detector

#endif // DETECTOR_NDARRPRODUCEREPIX_H
