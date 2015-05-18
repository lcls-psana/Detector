#ifndef DETECTOR_NDARRPRODUCERPNCCD_H
#define DETECTOR_NDARRPRODUCERPNCCD_H

//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// Description:
//	Class NDArrProducerPnccd
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
#include "psddl_psana/pnccd.ddl.h"

//-----------------------------

namespace Detector {

/// @addtogroup Detector

/**
 *  @ingroup Detector
 *
 *  @brief Produces ndarray<TOUT,3> from pnCCD camera raw data.
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

class NDArrProducerPnccd : public NDArrProducerBase {
public:

  /// Data type for detector image 
  typedef uint16_t data_t;

  const static size_t   Segs   = 4; 
  //const static size_t   Rows   = 512; 
  //const static size_t   Cols   = 512; 
  //const static size_t   FrSize = Rows*Cols; 
  //const static size_t   Size   = Segs*Rows*Cols; 

  // Constructor
  NDArrProducerPnccd(const PSEvt::Source& source, const unsigned& mode=0, const unsigned& pbits=0, const float& vdef=0);

  // Destructor
  virtual ~NDArrProducerPnccd();

  /// Interface method
  virtual ndarray<const data_t, 3> data_nda_uint16_3(PSEvt::Event& evt, PSEnv::Env& env);

  /// Print configuration data
  virtual void print_config(PSEvt::Event& evt, PSEnv::Env& env);

  //protected:

private:

  bool          m_as_data;
  long          m_count_ent;
  long          m_count_msg;

  // Copy constructor and assignment are disabled by default
  NDArrProducerPnccd ( const NDArrProducerPnccd& );
  NDArrProducerPnccd& operator = ( const NDArrProducerPnccd& );

  inline const char* name(){return "NDArrProducerPnccd";}

  void print_warning(const char* msg="");

//-----------------------------

  /**
   * @brief Get pnccd four frames from Psana::PNCCD::FramesV1 data object and copy them in the ndarray<TOUT, 3> out_ndarr
   * Returns false if data is missing.
   */

  template <typename TFRAME, typename TOUT>
  ndarray<const data_t, 3> 
  getNDArrForType(PSEvt::Event& evt, PSEnv::Env& env) {

      m_count_ent ++;

      boost::shared_ptr<TFRAME> frames1 = evt.get(m_source, m_key, &m_src);
      if (frames1) {

	  const unsigned* shape_data = (frames1->frame(0)).data().shape();
        
          ndarray<TOUT, 3> nda_out = make_ndarray<TOUT>(Segs, shape_data[0], shape_data[1]);
          typename ndarray<TOUT, 3>::iterator it_out = nda_out.begin(); 

          std::stringstream str; 

          if(m_pbits & 2) str << "  numLinks = " << frames1->numLinks();

          for (unsigned i = 0 ; i != frames1->numLinks(); ++ i) {
          
              const Psana::PNCCD::FrameV1& frame = frames1->frame(i);          
              const ndarray<const data_t, 2> data = frame.data();

              if(m_pbits & 2) {      
                str << "\n  Frame #" << i;          
                str << "\n    specialWord = " << frame.specialWord();
                str << "\n    frameNumber = " << frame.frameNumber();
                str << "\n    timeStampHi = " << frame.timeStampHi();
                str << "\n    timeStampLo = " << frame.timeStampLo();          
                str << "\n    frame size  = " << data.shape()[0] << 'x' << data.shape()[1];
              }      

              // Copy frame from data to output ndarray with changing type
              for ( ndarray<const data_t, 2>::iterator it=data.begin(); it!=data.end(); ++it, ++it_out) {
                  *it_out = (TOUT)*it;
              }
          }

          if(m_pbits & 2) { str << "\n    nda_out:\n" << nda_out; MsgLog(name(), info, str.str()); }

          return nda_out;
      }

      ndarray<TOUT,3> nda;
      return nda;
  }

//-----------------------------
//-----------------------------

}; // class 

} // namespace Detector

#endif // DETECTOR_NDARRPRODUCERPNCCD_H
