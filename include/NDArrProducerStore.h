#ifndef DETECTOR_NDARRPRODUCERSTORE_H
#define DETECTOR_NDARRPRODUCERSTORE_H

//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// $Revision$
//------------------------------------------------------------------------

//-----------------
// C/C++ Headers --
//-----------------
#include <iostream>
#include <string>
#include <vector>
//#include <map>
//#include <fstream>  // open, close etc.

//-------------------------------
// Collaborating Class Headers --
//-------------------------------
#include "ndarray/ndarray.h"
#include "MsgLogger/MsgLogger.h"

#include "Detector/NDArrProducerBase.h"
#include "Detector/NDArrProducerCSPAD.h"
#include "Detector/NDArrProducerCSPAD2X2.h"
#include "Detector/NDArrProducerCamera.h"
#include "Detector/NDArrProducerAndor.h"
#include "Detector/NDArrProducerPnccd.h"
#include "Detector/NDArrProducerPrinceton.h"
#include "Detector/NDArrProducerEpix.h"

//#include "ImgAlgos/GlobalMethods.h" // for DETECTOR_TYPE, getRunNumber(evt), detectorTypeForSource, etc.
//#include "PSCalib/GenericCalibPars.h"

//-----------------------------

namespace Detector {

/**
 *  @defgroup Detector package
 *  @brief Package Detector provides access to psana data from python
 */

/// @addtogroup Detector

/**
 *  @ingroup Detector
 *
 *  @brief class NDArrProducerStore has a static factory method Create for CalibPars
 *
 *  This software was developed for the LCLS project. If you use all or 
 *  part of it, please give an appropriate acknowledgment.
 *
 *  @version $Id$
 *
 *  @author Mikhail S. Dubrovin
 *
 *  @see 
 *
 *  @anchor interface
 *  @par<interface> Interface Description
 * 
 *  @li  Includes
 *  @code
 *  #include "Detector/NDArrProducerStore.h"
 *  @endcode
 *
 *  @li Instatiation
 *  \n
 *  Here we assume that code is working inside psana module where evt and env variables are defined through input parameters of call-back methods. 
 *  Code below instateates calibpars object using factory static method Detector::NDArrProducerStore::Create:
 *  @code
 *  PSEvt::Source source("Camp.0:pnCCD.1");
 *  Detector::NDArrProducerBase* nda_prod = NDArrProducerStore::Create(source);
 *  @endcode
 *
 *  @li Access methods
 *  @code
 *  nda_prod->print();
 *  ndarray<const int16_t, 3> nda = nda_prod->data_nda_int16_3(*shp_evt, *shp_env); // for cspad, cspad2x2
 *  ndarray<const uint16_t, 2> nda = nda_prod->data_nda_uint16_2(*shp_evt, *shp_env); // for Camera, pnCCD, Andor, etc 
 *  @endcode
 */

//-----------------------------

class NDArrProducerStore  {


private:
  inline const char* name(){return "NDArrProducerStore";}

public:
  //NDArrProducerStore () {}
  //virtual ~NDArrProducerStore () {}

//-----------------------------
  /**
   *  @brief Regular constructor, which use const std::string& str_src
   *  
   *  @param[in] source    The data source name, ex.: Source("Camp.0:pnCCD.0")
   *  @param[in] mode      Mode of operation, depending on detector, =0 - main mode.
   *  @param[in] pbits     Print control bit-word.
   *  @param[in] vdef      Default intensity value for missing in data pixels.
   */ 
  static Detector::NDArrProducerBase*
  Create ( const PSEvt::Source& source,      //  Camp.0:pnCCD.0
           const unsigned& mode=0,
           const unsigned& pbits=1, 
           const float&    vdef=0)
  {
    // enum DETECTOR_TYPE {OTHER, CSPAD, CSPAD2X2, PNCCD, PRINCETON, ACQIRIS, TM6740, 
    //                     OPAL1000, OPAL2000, OPAL4000, OPAL8000,
    //                     ANDOR, ORCAFL40, FCCD960, EPIX, EPIX100A, EPIX10K};

        ImgAlgos::DETECTOR_TYPE m_dettype = ImgAlgos::detectorTypeForSource(source);  // enumerated detector type defined from source string info
        if (pbits & 1) MsgLog("NDArrProducerStore", info, "Get access to CSPAD data source: " << source);


	if (m_dettype == ImgAlgos::CSPAD)
	  return new NDArrProducerCSPAD(source, mode, pbits, vdef);

	if (m_dettype == ImgAlgos::CSPAD2X2)
	  return new NDArrProducerCSPAD2X2(source, mode, pbits, vdef);

	if (   m_dettype == ImgAlgos::OPAL1000
	    || m_dettype == ImgAlgos::OPAL2000
	    || m_dettype == ImgAlgos::OPAL4000
	    || m_dettype == ImgAlgos::OPAL8000
	    || m_dettype == ImgAlgos::FCCD960
	    || m_dettype == ImgAlgos::TM6740
	    || m_dettype == ImgAlgos::ORCAFL40
           ) 
	  return new NDArrProducerCamera(source, mode, pbits, vdef);

	if (m_dettype == ImgAlgos::ANDOR)
	  return new NDArrProducerAndor(source, mode, pbits, vdef);

	if (m_dettype == ImgAlgos::PNCCD) 
	  return new NDArrProducerPnccd(source, mode, pbits, vdef);

	if (m_dettype == ImgAlgos::PRINCETON) 
	  return new NDArrProducerPrinceton(source, mode, pbits, vdef);

	if (m_dettype == ImgAlgos::EPIX100A) 
	  return new NDArrProducerEpix(source, mode, pbits, vdef);

        MsgLog("NDArrProducerStore", error, "Access to data for source " << source << " is not implemented yet...");  
        abort();

        return NULL;
  }
//-----------------------------

}; // class

} // namespace

#endif // DETECTOR_NDARRPRODUCERSTORE
