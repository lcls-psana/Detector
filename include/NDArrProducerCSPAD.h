#ifndef DETECTOR_NDARRPRODUCERCSPAD_H
#define DETECTOR_NDARRPRODUCERCSPAD_H

//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// Description:
//	Class NDArrProducerCSPAD
//
//------------------------------------------------------------------------

#include "Detector/NDArrProducerBase.h"

//-----------------
// C/C++ Headers --
//-----------------
#include <stdint.h>  // uint8_t, uint32_t, etc.
#include <algorithm> // for fill_n
#include <sstream>  // for stringstream
#include <boost/shared_ptr.hpp>

//----------------------
// Base Class Headers --
//----------------------

//-------------------------------
// Collaborating Class Headers --
//-------------------------------
//#include "Detector/GlobalMethods.h"
#include "psddl_psana/cspad.ddl.h"

//------------------------------------
// Collaborating Class Declarations --
//------------------------------------

//		---------------------
// 		-- Class Interface --
//		---------------------

namespace Detector {

/// @addtogroup Detector

/**
 *  @ingroup Detector
 *
 *  @brief Produces ndarray<T,3> from CSPAD raw data.
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

  class NDArrProducerCSPAD : public NDArrProducerBase {
public:

  typedef int16_t data_t;

  const static uint32_t NQuadsMax   = 4;
  const static uint32_t N2x1InQuad  = 8;
  const static uint32_t NRows2x1    = 185;
  const static uint32_t NCols2x1    = 388;
  const static uint32_t Size2x1     = NRows2x1 * NCols2x1;
  const static uint32_t N2x1InCSPAD = NQuadsMax * N2x1InQuad;

  // Constructor
  NDArrProducerCSPAD(const PSEvt::Source& source, const unsigned& mode=0, const unsigned& pbits=0, const float& vdef=0);

  // Destructor
  virtual ~NDArrProducerCSPAD();

  void getConfigPars(PSEnv::Env& env);
  ndarray<data_t,3> getNDArr(PSEvt::Event& evt, PSEnv::Env& env);


  // Interface method
  virtual ndarray<const int16_t, 3> data_nda_int16_3(PSEvt::Event& evt, PSEnv::Env& env) { return getNDArr(evt, env); };

  //protected:

private:

  bool          m_as_data;
  uint32_t      m_numSect;
  long          m_count_evt;
  long          m_count_cfg;
  long          m_count_msg;
  uint32_t      m_roiMask [NQuadsMax];

  ndarray<data_t,3> m_nda_def;

  // Copy constructor and assignment are disabled by default
  NDArrProducerCSPAD ( const NDArrProducerCSPAD& );
  NDArrProducerCSPAD& operator = ( const NDArrProducerCSPAD& );

  inline const char* name(){return "NDArrProducerCSPAD";}

//-----------------------------

  /**
   * @brief Gets m_roiMask[q], m_numSect, m_src,etc from the Psana::CsPad::ConfigV# object.
   */

  template <typename TCFG>
  bool getConfigParsForType(PSEnv::Env& env) {
        boost::shared_ptr<TCFG> cfg = env.configStore().get(m_source, &m_src);
        if (cfg.get()) {
            for (uint32_t q=0; q<NQuadsMax; ++q) {
              m_roiMask[q] = cfg->roiMask(q);
            }
            m_count_cfg ++;
            m_numSect = cfg->numSect();
            return true;
        }
        return false;
  }

//-----------------------------
  /**
   * @brief Returns raw data ndarray shaped as data [32,185,388]
   * Returns empty (default) ndarray if data is missing
   */
  template <typename TDATA, typename TELEM, typename TOUT>
  ndarray<TOUT,3> getNDArrFullForType (PSEvt::Event& evt, const float& vdef=0) {
      boost::shared_ptr<TDATA> shp = evt.get(m_source, m_key, &m_src); // get m_src here
      
      if (shp.get()) {

            // Create and initialize the array of full cspad shape [32,185,388]
            const unsigned shape[] = {N2x1InCSPAD, NRows2x1, NCols2x1};
            ndarray<TOUT,3> nda_out(shape);
            std::fill(nda_out.begin(), nda_out.end(), TOUT(vdef));    
	    
            //typename ndarray<TOUT,3>::iterator it_out = nda_out.begin(); 
            //TOUT* it_out = nda_out.data();
	    
            uint32_t numQuads = shp->quads_shape()[0];

            for (uint32_t q=0; q<numQuads; ++q) {
                const TELEM& el = shp->quads(q);      
                const ndarray<const data_t,3>& nda_quad = el.data();

		uint32_t qnum = el.quad(); 
                uint32_t mask = m_roiMask[qnum];

                uint32_t ind2x1_in_quad=0;
                for(uint32_t sect=0; sect < N2x1InQuad; sect++) {
                    bool sectIsOn = mask & (1<<sect);
                    if( !sectIsOn ) continue;

                    int ind2x1_in_det = qnum*N2x1InQuad + sect;             
                    //std::memcpy(&nda_out[ind2x1_in_det][0][0], &nda_quad[ind2x1_in_quad][0][0], Size2x1*sizeof(T));

		    // Copy with type conversion:
		    const data_t* p_sect = &nda_quad[ind2x1_in_quad][0][0];
		    TOUT*          p_out = &nda_out[ind2x1_in_det][0][0];
		    for(unsigned i=0; i<Size2x1; ++i) {
                      p_out[i]=(TOUT)p_sect[i];
		    }
                    ind2x1_in_quad++;
                }
            }
            return nda_out;

      } // if (shp.get())

      return m_nda_def; // empty ndarray
  }

//-----------------------------
  /**
   * @brief Returns raw data ndarray shaped as data [N,185,388]
   * Returns empty (default) ndarray if data is missing
   */
  template <typename TDATA, typename TELEM, typename TOUT>
  ndarray<TOUT,3> getNDArrAsDataForType(PSEvt::Event& evt) {
      boost::shared_ptr<TDATA> shp = evt.get(m_source, m_key, &m_src); // get m_src here
      
      if (shp.get()) {

            uint32_t numQuads = shp->quads_shape()[0];
	    unsigned n2x1InData=0; 
            for (uint32_t q=0; q<numQuads; ++q) n2x1InData += (shp->quads(q)).data().shape()[0];     	    
	    std::cout << "n2x1InData=" << n2x1InData << '\n';
	    std::cout << "m_numSect =" << m_numSect << '\n';
	    
            // Create and initialize the array of the same shape as data [N,185,388]
            const unsigned shape[] = {n2x1InData, NRows2x1, NCols2x1};
            ndarray<TOUT,3> nda_as_data(shape);
	    
            typename ndarray<TOUT,3>::iterator it_out = nda_as_data.begin(); 
            //TOUT* it_out = nda_as_data.data();
	    
            for (uint32_t q=0; q<numQuads; ++q) {
                const TELEM& el = shp->quads(q);      
                const ndarray<const data_t,3>& nda_quad = el.data();
                // pixel-by-pixel copy of quad data ndarray to output ndarray with type conversion:
                for (ndarray<const data_t,3>::iterator it=nda_quad.begin(); it!=nda_quad.end(); ++it, ++it_out) {
                  *it_out = (TOUT)*it;
                }
            }
            return nda_as_data;

      } // if (shp.get())

      return m_nda_def; // empty ndarray
  }

//-----------------------------
  /**
   * @brief Returns raw data ndarray shaped as requested
   * Returns empty (default) ndarray if data is missing
   */
  template <typename TDATA, typename TELEM, typename TOUT>
  ndarray<TOUT,3> getNDArrForType (PSEvt::Event& evt) {

   if (m_as_data) return getNDArrAsDataForType<TDATA, TELEM, TOUT>(evt);
   else           return getNDArrFullForType<TDATA, TELEM, TOUT>(evt, m_vdef);
  }

//-----------------------------

}; // class 

} // namespace Detector

#endif // DETECTOR_NDARRPRODUCERCSPAD_H
