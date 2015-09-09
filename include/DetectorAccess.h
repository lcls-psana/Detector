#ifndef DETECTOR_DETECTORACCESS_H
#define DETECTOR_DETECTORACCESS_H

//--------------------------------------------------------------------------
// File and Version Information:
// 	$Id$
//
// Description:
//	Class DetectorAccess
//
//------------------------------------------------------------------------

//-----------------
// Headers --
//-----------------

#include <string>
#include <cstddef>  // for size_t

#include <PSEvt/Event.h>
#include <PSEnv/Env.h>

#include "ndarray/ndarray.h"
#include <boost/shared_ptr.hpp>

#include "ImgAlgos/GlobalMethods.h" // for DETECTOR_TYPE, getRunNumber(evt), etc.
#include "PSCalib/CalibPars.h"
#include "Detector/NDArrProducerStore.h"
//#include "Detector/NDArrProducerCSPAD.h"
#include "PSCalib/GeometryAccess.h"
#include "ImgAlgos/CommonModeCorrection.h"

//-------------------
namespace Detector {

/**
 *  @defgroup Detector package 
 *  @brief Package Detector contains classes to call c++ classes/methods from python.
 *
 */

/// @addtogroup Detector

/**
 *  @ingroup Detector
 *
 *  @brief Class helps to get data/calibrations associated with detector.
 *
 *  This software was developed for the LCLS project.  If you use all or 
 *  part of it, please give an appropriate acknowledgment.
 *
 *  @version \$Id$
 *
 *  @author Mikhail S. Dubrovin
 */

class DetectorAccess {
 public:

  typedef PSCalib::GeometryAccess::image_t    image_t;
  typedef uint16_t data_t;

  typedef PSCalib::CalibPars::shape_t         shape_t;

  typedef PSCalib::CalibPars::pedestals_t     pedestals_t;
  typedef PSCalib::CalibPars::pixel_rms_t     pixel_rms_t;
  typedef PSCalib::CalibPars::pixel_gain_t    pixel_gain_t;
  typedef PSCalib::CalibPars::pixel_mask_t    pixel_mask_t;
  typedef PSCalib::CalibPars::pixel_bkgd_t    pixel_bkgd_t;
  typedef PSCalib::CalibPars::pixel_status_t  pixel_status_t;
  typedef PSCalib::CalibPars::common_mode_t   common_mode_t;

  //typedef NDArrProducerCSPAD::data_t          data_i16_t;  

  // Constructor
  DetectorAccess (const PSEvt::Source& source, boost::shared_ptr<PSEnv::Env> shp_env, const unsigned& pbits=0x1) ; // 0xffff
  
  // Destructor
  virtual ~DetectorAccess () ;

  const size_t                    ndim        (const int& runnum);
  const size_t                    size        (const int& runnum);
  ndarray<const shape_t,1>        shape       (const int& runnum);

  const size_t                    ndim        (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  const size_t                    size        (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const shape_t,1>        shape       (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);

  const pedestals_t*            p_pedestals   (const int& runnum);
  const pixel_rms_t*            p_pixel_rms   (const int& runnum);
  const pixel_gain_t*           p_pixel_gain  (const int& runnum);
  const pixel_mask_t*           p_pixel_mask  (const int& runnum);
  const pixel_bkgd_t*           p_pixel_bkgd  (const int& runnum);
  const pixel_status_t*         p_pixel_status(const int& runnum);
  const common_mode_t*          p_common_mode (const int& runnum);

  const pedestals_t*            p_pedestals   (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  const pixel_rms_t*            p_pixel_rms   (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  const pixel_gain_t*           p_pixel_gain  (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  const pixel_mask_t*           p_pixel_mask  (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  const pixel_bkgd_t*           p_pixel_bkgd  (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  const pixel_status_t*         p_pixel_status(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  const common_mode_t*          p_common_mode (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);

  ndarray<const pedestals_t,1>    pedestals   (const int& runnum);
  ndarray<const pixel_rms_t,1>    pixel_rms   (const int& runnum);
  ndarray<const pixel_gain_t,1>   pixel_gain  (const int& runnum);
  ndarray<const pixel_mask_t,1>   pixel_mask  (const int& runnum);
  ndarray<const pixel_bkgd_t,1>   pixel_bkgd  (const int& runnum);
  ndarray<const pixel_status_t,1> pixel_status(const int& runnum);
  ndarray<const common_mode_t,1>  common_mode (const int& runnum);

  ndarray<const pedestals_t,1>    pedestals   (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const pixel_rms_t,1>    pixel_rms   (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const pixel_gain_t,1>   pixel_gain  (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const pixel_mask_t,1>   pixel_mask  (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const pixel_bkgd_t,1>   pixel_bkgd  (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const pixel_status_t,1> pixel_status(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const common_mode_t,1>  common_mode (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);

  const int status(const int& runnum, const int& calibtype);  
  const int status(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, const int& calibtype);  

//-------------------

  ndarray<const int16_t, 1>  data_int16_1(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const int16_t, 2>  data_int16_2(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const int16_t, 3>  data_int16_3(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const int16_t, 4>  data_int16_4(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);

  //ndarray<const uint16_t, 1> data_uint16_1(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const uint16_t, 2> data_uint16_2(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const uint16_t, 3> data_uint16_3(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  //ndarray<const uint16_t, 4> data_uint16_4(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);

  //ndarray<const uint8_t, 1>  data_uint8_1(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const uint8_t, 2>  data_uint8_2(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  //ndarray<const uint8_t, 3>  data_uint8_3(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  //ndarray<const uint8_t, 4>  data_uint8_4(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);

//-------------------

  ndarray<const double, 1>   pixel_coords_x (const int& runnum);
  ndarray<const double, 1>   pixel_coords_y (const int& runnum);
  ndarray<const double, 1>   pixel_coords_z (const int& runnum);
  ndarray<const double, 1>   pixel_areas    (const int& runnum);
  ndarray<const int, 1>      pixel_mask_geo (const int& runnum, const unsigned& mbits=0377);
  ndarray<const unsigned, 1> pixel_indexes_x(const int& runnum);
  ndarray<const unsigned, 1> pixel_indexes_y(const int& runnum);
  double                    pixel_scale_size(const int& runnum);

  ndarray<const double, 1>   pixel_coords_x (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const double, 1>   pixel_coords_y (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const double, 1>   pixel_coords_z (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const double, 1>   pixel_areas    (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const int, 1>      pixel_mask_geo (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, const unsigned& mbits=0377);
  ndarray<const unsigned, 1> pixel_indexes_x(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  ndarray<const unsigned, 1> pixel_indexes_y(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  double                    pixel_scale_size(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);

//-------------------

  ndarray<const image_t, 2> get_image(const int& runnum, ndarray<const image_t, 1> nda);
  ndarray<const image_t, 2> get_image(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, ndarray<const image_t, 1> nda);

//-------------------

//  template <typename T>
//  void apply_common_mode(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, T* nda);

//-------------------

  // Returns instrument as string
  std::string str_inst(boost::shared_ptr<PSEnv::Env> shp_env);  

  //inline void setEnv(boost::shared_ptr<PSEnv::Env> shp_env) {m_env = *shp_env;}
  inline void setMode (const unsigned& mode) {m_mode = mode;}
  inline void setPrintBits (const unsigned& pbits) {m_pbits = pbits;}
  inline void setDefaultValue (const float& vdef) {m_vdef = vdef;}

//-------------------

  void print();
  void print_config(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);

//-------------------
//-------------------
//-------------------
//-------------------

 private:

  ImgAlgos::DETECTOR_TYPE  m_dettype;          // numerated detector type source
  PSCalib::CalibPars*      m_calibpars;        // pointer to calibration store
  PSCalib::GeometryAccess* m_geometry;         // pointer to GeometryAccess object
  ImgAlgos::CommonModeCorrection* m_cmode;     // pointer to CommonModeCorrection object
  PSEvt::Source            m_source;
  std::string              m_str_src;
  std::string              m_cgroup;
  int                      m_runnum;
  int                      m_runnum_geo;
  int                      m_runnum_cmode;
  unsigned                 m_mode; 
  unsigned                 m_pbits; 
  float                    m_vdef; 
  std::string              m_calibdir;


  //NDArrProducerCSPAD*     m_nda_prod;  // direct access
  NDArrProducerBase*       m_nda_prod;   // factory store access
  PSEnv::Env&              m_env;

  inline const char* _name_() {return "DetectorAccess";}

  void initCalibStore(const int& runnum);
  void initCalibStore(const std::string& calibdir, const int& runnum);
  void initCalibStore(PSEvt::Event& evt, PSEnv::Env& env);

  void initGeometry(const int& runnum);
  void initGeometry(const std::string& calibdir, const int& runnum);
  void initGeometry(PSEvt::Event& evt, PSEnv::Env& env);

  void initCommonMode(const int& runnum);
  void initCommonMode(const std::string& calibdir, const int& runnum);
  //void initCommonMode(PSEvt::Event& evt, PSEnv::Env& env);
  //void initCommonMode(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env);
  void initNDArrProducer();

//-------------------
 
 public:
 
   template <typename T>
   void common_mode_apply(const int& runnum, T* arr)
       {
         initCommonMode(runnum);
         m_cmode -> do_common_mode<T>(arr);
       }

   template <typename T>
   void common_mode_apply(const std::string& calibdir, const int& runnum, T* arr)
       {
         m_calibdir = calibdir;  
         common_mode_apply<T>(runnum, arr);
       }
   
   void common_mode_double(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, ndarray<double, 1> nda)
      { common_mode_apply<double>(shp_env->calibDir(), ImgAlgos::getRunNumber(*shp_evt), nda.data()); }

   void common_mode_double(const int& runnum, ndarray<double, 1> nda)
      { common_mode_apply<double>(runnum, nda.data()); }

   void common_mode_float(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, ndarray<float, 1> nda)
      { common_mode_apply<float>(shp_env->calibDir(), ImgAlgos::getRunNumber(*shp_evt), nda.data()); }

   void common_mode_float(const int& runnum, ndarray<float, 1> nda)
      { common_mode_apply<float>(runnum, nda.data()); }

//-------------------
}; // class
//-------------------
} // namespace
//-------------------

#endif // DETECTOR_DETECTORACCESS_H
