//-----------------------
// This Class's Header --
//-----------------------
#include "Detector/DetectorAccess.h"

//-----------------
// C/C++ Headers --
//-----------------
#include <algorithm> // for fill_n
#include <sstream>  // for stringstream

//-------------------------------
// Collaborating Class Headers --
//-------------------------------
#include "MsgLogger/MsgLogger.h"
// to work with detector data include corresponding 
#include "PSEvt/EventId.h"
#include "PSEvt/Source.h"
#include "PSCalib/CalibParsStore.h"
#include "PSCalib/CalibFileFinder.h"

//-------------------
namespace Detector {

  typedef DetectorAccess::data_t data_t;
  typedef DetectorAccess::image_t image_t;

//----------------
// Constructors --
//----------------
  DetectorAccess::DetectorAccess (const PSEvt::Source& source, boost::shared_ptr<PSEnv::Env> shp_env, const unsigned& pbits)
  : m_calibpars(0)
  , m_geometry(0)
  , m_cmode(0)
  , m_source(source)
  , m_runnum(-1)
  , m_runnum_geo(-1)
  , m_runnum_cmode(-1)
  , m_mode(0)
  , m_pbits(pbits)
  , m_vdef(0)
  , m_nda_prod(0)
  , m_env(*shp_env)
{
  std::stringstream ss; ss << source;
  m_str_src = ss.str();
  m_dettype = ImgAlgos::detectorTypeForSource(m_source);
  m_cgroup  = ImgAlgos::calibGroupForDetType(m_dettype); // for ex: "PNCCD::CalibV1";
  m_calibdir = shp_env->calibDir(); // std::string();

  if(m_pbits) {
      std::stringstream ss;
      ss << "in ctor:" // "SOURCE: " << m_source
  	 << "\nData source  : " << m_str_src
  	 << "\nCalib group  : " << m_cgroup 
  	 << "\nCalib dir    : " << m_calibdir 
         << "\nPrint bits   : " << m_pbits
         << '\n';
      MsgLog(_name_(), info, ss.str());
  }
}

//--------------
// Destructor --
//--------------
DetectorAccess::~DetectorAccess ()
{
  // Does nothing for now
  if(m_geometry) delete m_geometry;
}

//-------------------

void
DetectorAccess::initCalibStore(PSEvt::Event& evt, PSEnv::Env& env)
{
  //const int& runnum = ImgAlgos::getRunNumber(evt);
  //const std::string& calibdir = env.calibDir();
  initCalibStore(env.calibDir(), ImgAlgos::getRunNumber(evt));
}

//-------------------

void
DetectorAccess::initCalibStore(const std::string& calibdir, const int& runnum)
{
  m_calibdir = calibdir;
  initCalibStore(runnum);
}

//-------------------

void
DetectorAccess::initCalibStore(const int& runnum)
{
  if(m_calibpars) {
    if(runnum == m_runnum) return;
    delete m_calibpars;
    m_calibpars = 0;
  }
  m_runnum = runnum;

  if(m_pbits) {
      std::stringstream ss;
      ss << "initCalibStore(...):"
       //<< "\nInstrument  : " << env.instrument()
         << "\nCalib dir   : " << m_calibdir 
         << "\nCalib group : " << m_cgroup 
         << "\nData source : " << m_str_src
         << "\nRun number  : " << m_runnum 
         << "\nPrint bits  : " << m_pbits 
         << '\n';
      
      MsgLog(_name_(), info, ss.str());
  }

  m_calibpars = PSCalib::CalibParsStore::Create(m_calibdir, m_cgroup, m_str_src, m_runnum, m_pbits);
}

//-------------------

void 
DetectorAccess::initGeometry(PSEvt::Event& evt, PSEnv::Env& env)
{
  //const int& runnum = ImgAlgos::getRunNumber(evt);
  //const std::string& calibdir = env.calibDir();
  initGeometry(env.calibDir(), ImgAlgos::getRunNumber(evt));
}

//-------------------

void 
DetectorAccess::initGeometry(const std::string& calibdir, const int& runnum)
{
  m_calibdir = calibdir;
  initGeometry(runnum);
}

//-------------------

void 
DetectorAccess::initGeometry(const int& runnum)
{
  if(m_geometry) {
    if(runnum == m_runnum_geo) return;
    delete m_geometry;
    m_geometry = 0;
  }
  m_runnum_geo = runnum;

  unsigned pbits_cff = (m_pbits & 2) ? 0xffff : 0;
  PSCalib::CalibFileFinder calibfinder(m_calibdir, m_cgroup, pbits_cff);
  std::string fname = calibfinder.findCalibFile(m_str_src, "geometry", runnum);

  if(m_pbits) {
      std::stringstream ss;
      ss << "initGeometry(...):"
       //<< "\nInstrument     : " << env.instrument()
         << "\nCalib dir      : " << m_calibdir 
         << "\nCalib group    : " << m_cgroup 
         << "\nCalib file     : " << fname 
         << "\nData source    : " << m_str_src
         << "\nRun requested  : " << runnum 
         << "\nRun for loaded : " << m_runnum_geo 
         << "\nPrint bits     : " << m_pbits 
         << '\n';
      
      MsgLog(_name_(), info, ss.str());
  }

  if(fname.empty()) return;    

  unsigned pbits_ga = (m_pbits & 4) ? 0xffff : 0;
  m_geometry = new PSCalib::GeometryAccess(fname, pbits_ga);
}

//-------------------

void 
DetectorAccess::initNDArrProducer()
{
  if(!m_nda_prod) m_nda_prod = NDArrProducerStore::Create(m_source, m_mode, m_pbits, m_vdef); // universal access through the factory store
}

//-------------------

//void 
//DetectorAccess::initCommonMode(PSEvt::Event& evt, PSEnv::Env& env)
//{
//  initCommonMode(env.calibDir(), ImgAlgos::getRunNumber(evt));
//}

//-------------------

//void 
//DetectorAccess::initCommonMode(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
//{
//  initCommonMode(shp_env->calibDir(), ImgAlgos::getRunNumber(*shp_evt));
//}

//-------------------

void 
DetectorAccess::initCommonMode(const std::string& calibdir, const int& runnum)
{
  m_calibdir = calibdir;
  initCommonMode(runnum);
}

//-------------------

void 
DetectorAccess::initCommonMode(const int& runnum)
{
  if(m_cmode) {
    if(runnum == m_runnum_cmode) return;
    delete m_cmode;
    m_cmode = 0;
  }

  m_runnum_cmode = runnum;

  const DetectorAccess::common_mode_t*  cmod_pars = this->p_common_mode (runnum); 
  const DetectorAccess::pixel_status_t* status    = this->p_pixel_status(runnum);
  const size_t size = this->size(runnum);

  if(m_pbits) {
      std::stringstream ss;
      ss << "initCommonMode(...):"
       //<< "\nInstrument  : " << shp_env->instrument()
         << "\nData source : " << m_source
         << "\nRun cmode   : " << m_runnum 
         << "\nRun number  : " << m_runnum_cmode 
         << "\nPrint bits  : " << m_pbits 
         << '\n';
      
      MsgLog(_name_(), info, ss.str());
  }

  m_cmode = new ImgAlgos::CommonModeCorrection(m_source, cmod_pars, size, status, m_pbits);
}

//-------------------
//-------------------
//-------------------
//-------------------
//-------------------

const size_t DetectorAccess::ndim(const int& runnum)
{
  initCalibStore(runnum);
  return m_calibpars->ndim();
}

//-------------------

const size_t DetectorAccess::ndim(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return ndim(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------
//-------------------

const size_t DetectorAccess::size(const int& runnum)
{
  initCalibStore(runnum);
  return m_calibpars->size();
}

//-------------------

const size_t DetectorAccess::size(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return size(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------
//-------------------

ndarray<const DetectorAccess::shape_t, 1>
DetectorAccess::shape(const int& runnum)
{
  initCalibStore(runnum);
  return make_ndarray(m_calibpars->shape(), m_calibpars->ndim());
}

//-------------------

ndarray<const DetectorAccess::shape_t, 1>
DetectorAccess::shape(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return shape(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------
//-------------------
//-------------------
//-------------------

const DetectorAccess::pedestals_t*
DetectorAccess::p_pedestals(const int& runnum)
{
  initCalibStore(runnum);
  return m_calibpars->pedestals(); // constants loaded before call to size()
}

//-------------------

const DetectorAccess::pedestals_t*
DetectorAccess::p_pedestals(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return p_pedestals(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

ndarray<const DetectorAccess::pedestals_t, 1> 
DetectorAccess::pedestals(const int& runnum)
{
  initCalibStore(runnum);
  const DetectorAccess::pedestals_t* p = m_calibpars->pedestals(); // constants loaded before call to size()
  return make_ndarray(p, m_calibpars->size());
}

//-------------------

ndarray<const DetectorAccess::pedestals_t, 1> 
DetectorAccess::pedestals(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return pedestals(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------
//-------------------
//-------------------
//-------------------

const DetectorAccess::pixel_rms_t*
DetectorAccess::p_pixel_rms(const int& runnum)
{
  initCalibStore(runnum);
  return m_calibpars->pixel_rms();
}

//-------------------

const DetectorAccess::pixel_rms_t*
DetectorAccess::p_pixel_rms(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return p_pixel_rms(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

ndarray<const DetectorAccess::pixel_rms_t, 1> 
DetectorAccess::pixel_rms(const int& runnum)
{
  initCalibStore(runnum);
  const DetectorAccess::pixel_rms_t* p = m_calibpars->pixel_rms();
  return make_ndarray(p, m_calibpars->size());
}

//-------------------

ndarray<const DetectorAccess::pixel_rms_t, 1> 
DetectorAccess::pixel_rms(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return pixel_rms(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------
//-------------------
//-------------------
//-------------------

const DetectorAccess::pixel_gain_t*
DetectorAccess::p_pixel_gain(const int& runnum)
{
  initCalibStore(runnum);
  return m_calibpars->pixel_gain();
}

//-------------------

const DetectorAccess::pixel_gain_t*
DetectorAccess::p_pixel_gain(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return p_pixel_gain(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

ndarray<const DetectorAccess::pixel_gain_t, 1> 
DetectorAccess::pixel_gain(const int& runnum)
{
  initCalibStore(runnum);
  const DetectorAccess::pixel_gain_t* p = m_calibpars->pixel_gain();
  return make_ndarray(p, m_calibpars->size());
}

//-------------------

ndarray<const DetectorAccess::pixel_gain_t, 1> 
DetectorAccess::pixel_gain(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return pixel_gain(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------
//-------------------
//-------------------
//-------------------

const DetectorAccess::pixel_mask_t*
DetectorAccess::p_pixel_mask(const int& runnum)
{
  initCalibStore(runnum);
  return m_calibpars->pixel_mask();
}

//-------------------

const DetectorAccess::pixel_mask_t*
DetectorAccess::p_pixel_mask(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir =shp_env->calibDir();
  return p_pixel_mask(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

ndarray<const DetectorAccess::pixel_mask_t, 1> 
DetectorAccess::pixel_mask(const int& runnum)
{
  initCalibStore(runnum);
  const DetectorAccess::pixel_mask_t* p = m_calibpars->pixel_mask();
  return make_ndarray(p, m_calibpars->size());
}

//-------------------

ndarray<const DetectorAccess::pixel_mask_t, 1> 
DetectorAccess::pixel_mask(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return pixel_mask(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------
//-------------------
//-------------------
//-------------------

const DetectorAccess::pixel_bkgd_t*
DetectorAccess::p_pixel_bkgd(const int& runnum)
{
  initCalibStore(runnum);
  return m_calibpars->pixel_bkgd();
}

//-------------------

const DetectorAccess::pixel_bkgd_t*
DetectorAccess::p_pixel_bkgd(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return p_pixel_bkgd(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

ndarray<const DetectorAccess::pixel_bkgd_t, 1> 
DetectorAccess::pixel_bkgd(const int& runnum)
{
  initCalibStore(runnum);
  const DetectorAccess::pixel_bkgd_t* p = m_calibpars->pixel_bkgd();
  return make_ndarray(p, m_calibpars->size());
}

//-------------------

ndarray<const DetectorAccess::pixel_bkgd_t, 1> 
DetectorAccess::pixel_bkgd(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return pixel_bkgd(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------
//-------------------
//-------------------
//-------------------

const DetectorAccess::pixel_status_t*
DetectorAccess::p_pixel_status(const int& runnum)
{
  initCalibStore(runnum);
  return m_calibpars->pixel_status();
}

//-------------------

const DetectorAccess::pixel_status_t*
DetectorAccess::p_pixel_status(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return p_pixel_status(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

ndarray<const DetectorAccess::pixel_status_t, 1> 
DetectorAccess::pixel_status(const int& runnum)
{
  initCalibStore(runnum);
  const DetectorAccess::pixel_status_t* p = m_calibpars->pixel_status();
  return make_ndarray(p, m_calibpars->size());
}

//-------------------

ndarray<const DetectorAccess::pixel_status_t, 1> 
DetectorAccess::pixel_status(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return pixel_status(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------
//-------------------
//-------------------
//-------------------

const DetectorAccess::common_mode_t*
DetectorAccess::p_common_mode(const int& runnum)
{
  initCalibStore(runnum);
  return m_calibpars->common_mode();
}

//-------------------

const DetectorAccess::common_mode_t*
DetectorAccess::p_common_mode(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return p_common_mode(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

ndarray<const DetectorAccess::common_mode_t, 1> 
DetectorAccess::common_mode(const int& runnum)
{
  initCalibStore(runnum);
  //std::cout << "TEST cm[0]: " << m_calibpars->common_mode()[0] << "\n";
  //std::cout << "TEST cm[3]: " << m_calibpars->common_mode()[3] << "\n";
  //std::cout << "TEST  size: " << m_calibpars->size(PSCalib::COMMON_MODE) << "\n";
  const DetectorAccess::common_mode_t* p = m_calibpars->common_mode();
  return make_ndarray(p, m_calibpars->size(PSCalib::COMMON_MODE));
}

//-------------------

ndarray<const DetectorAccess::common_mode_t, 1> 
DetectorAccess::common_mode(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return common_mode(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------
//-------------------
//-------------------
//-------------------

const int
DetectorAccess::status(const int& runnum, const int& calibtype) // PSCalib::COMMON_MODE
{
  initCalibStore(runnum);
  return m_calibpars->status((const PSCalib::CALIB_TYPE)calibtype);
}

//-------------------

const int
DetectorAccess::status(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, const int& calibtype) // PSCalib::COMMON_MODE
{
  m_calibdir = shp_env->calibDir();
  return status(ImgAlgos::getRunNumber(*shp_evt), calibtype);
}

//-------------------
//-------------------
//-------------------
//-------------------

ndarray<const int16_t, 1> DetectorAccess::data_int16_1(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initNDArrProducer();
  return m_nda_prod->data_nda_int16_1(*shp_evt, *shp_env);
}

//-------------------

ndarray<const int16_t, 2> DetectorAccess::data_int16_2(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initNDArrProducer();
  return m_nda_prod->data_nda_int16_2(*shp_evt, *shp_env);
}

//-------------------

ndarray<const int16_t, 3> DetectorAccess::data_int16_3(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initNDArrProducer();
  return m_nda_prod->data_nda_int16_3(*shp_evt, *shp_env);
}

//-------------------

ndarray<const int16_t, 4> DetectorAccess::data_int16_4(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initNDArrProducer();
  return m_nda_prod->data_nda_int16_4(*shp_evt, *shp_env);
}

//-------------------

ndarray<const uint16_t, 2> DetectorAccess::data_uint16_2(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initNDArrProducer();
  return m_nda_prod->data_nda_uint16_2(*shp_evt, *shp_env);
}

//-------------------

ndarray<const uint16_t, 3> DetectorAccess::data_uint16_3(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initNDArrProducer();
  return m_nda_prod->data_nda_uint16_3(*shp_evt, *shp_env);
}

//-------------------

ndarray<const uint8_t, 2> DetectorAccess::data_uint8_2(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initNDArrProducer();
  return m_nda_prod->data_nda_uint8_2(*shp_evt, *shp_env);
}

//-------------------
//-------------------
//-------------------
//-------------------

ndarray<const double, 1> DetectorAccess::pixel_coords_x(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return pixel_coords_x(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

ndarray<const double, 1> DetectorAccess::pixel_coords_x(const int& runnum)
{
  initGeometry(runnum);

  const double* pX; 
  const double* pY; 
  const double* pZ; 
  unsigned size;

  if(m_geometry==0) return ndarray<const double, 1>();
  m_geometry -> get_pixel_coords(pX, pY, pZ, size);
  return make_ndarray(pX, size);
}

//-------------------

ndarray<const double, 1> DetectorAccess::pixel_coords_y(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return pixel_coords_y(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

ndarray<const double, 1> DetectorAccess::pixel_coords_y(const int& runnum)
{
  initGeometry(runnum);

  const double* pX; 
  const double* pY; 
  const double* pZ; 
  unsigned size;

  if(m_geometry==0) return ndarray<const double, 1>();
  m_geometry -> get_pixel_coords(pX, pY, pZ, size);
  return make_ndarray(pY, size);
}

//-------------------

ndarray<const double, 1> DetectorAccess::pixel_coords_z(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return pixel_coords_z(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

ndarray<const double, 1> DetectorAccess::pixel_coords_z(const int& runnum)
{
  initGeometry(runnum);

  const double* pX; 
  const double* pY; 
  const double* pZ; 
  unsigned size;

  if(m_geometry==0) return ndarray<const double, 1>();
  m_geometry -> get_pixel_coords(pX, pY, pZ, size);
  return make_ndarray(pZ, size);
}

//-------------------

ndarray<const double, 1> DetectorAccess::pixel_areas(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return pixel_areas(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

ndarray<const double, 1> DetectorAccess::pixel_areas(const int& runnum)
{
  initGeometry(runnum);

  const double* A;
  unsigned   size;

  if(m_geometry==0) return ndarray<const double, 1>();
  m_geometry -> get_pixel_areas(A,size);
  return make_ndarray(A, size);
}

//-------------------

// mbits=0377; // 1-edges; 2-wide central cols; 4-non-bound; 8-non-bound neighbours
ndarray<const int, 1> DetectorAccess::pixel_mask_geo(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, const unsigned& mbits)
{
  m_calibdir = shp_env->calibDir();
  return pixel_mask_geo(ImgAlgos::getRunNumber(*shp_evt), mbits);
}

//-------------------

// mbits=0377; // 1-edges; 2-wide central cols; 4-non-bound; 8-non-bound neighbours
ndarray<const int, 1> DetectorAccess::pixel_mask_geo(const int& runnum, const unsigned& mbits)
{
  initGeometry(runnum);

  const int* mask;
  unsigned   size;

  if(m_geometry==0) return ndarray<const int, 1>();
  m_geometry -> get_pixel_mask(mask, size, std::string(), 0, mbits);
  return make_ndarray(mask, size);
}

//-------------------

ndarray<const unsigned, 1> DetectorAccess::pixel_indexes_x(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return pixel_indexes_x(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

ndarray<const unsigned, 1> DetectorAccess::pixel_indexes_x(const int& runnum)
{
  initGeometry(runnum);

  const unsigned* iX;
  const unsigned* iY; 
  unsigned size;

  //      const std::string ioname = "QUAD:V1";                                                            
  //      const unsigned ioindex = 1;                                                                      
  //      const double pix_scale_size_um = 109.92;                                                         
  //      const int xy0_off_pix[] = {200,200};
  //      geometry.get_pixel_coord_indexes(iX, iY, isize, ioname, ioindex, pix_scale_size_um, xy0_off_pix, do_tilt);

  if(m_geometry==0) return ndarray<const unsigned, 1>();
  m_geometry -> get_pixel_coord_indexes(iX, iY, size); 
  return make_ndarray(iX, size);
}

//-------------------

ndarray<const unsigned, 1> DetectorAccess::pixel_indexes_y(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return pixel_indexes_y(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

ndarray<const unsigned, 1> DetectorAccess::pixel_indexes_y(const int& runnum)
{
  initGeometry(runnum);

  const unsigned* iX;
  const unsigned* iY; 
  unsigned size;

  if(m_geometry==0) return ndarray<const unsigned, 1>();
  m_geometry -> get_pixel_coord_indexes(iX, iY, size); 
  return make_ndarray(iY, size);
}

//-------------------

double DetectorAccess::pixel_scale_size(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  m_calibdir = shp_env->calibDir();
  return pixel_scale_size(ImgAlgos::getRunNumber(*shp_evt));
}

//-------------------

double DetectorAccess::pixel_scale_size(const int& runnum)
{
  initGeometry(runnum);

  if(m_geometry==0) return 1;
  return m_geometry -> get_pixel_scale_size ();
}

//-------------------

ndarray<const image_t, 2>
DetectorAccess::get_image(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, ndarray<const image_t, 1> nda)
{
  m_calibdir = shp_env->calibDir();
  return get_image(ImgAlgos::getRunNumber(*shp_evt), nda);
}

//-------------------

ndarray<const image_t, 2>
DetectorAccess::get_image(const int& runnum, ndarray<const image_t, 1> nda)
{
  initGeometry(runnum);

  const unsigned* iX;
  const unsigned* iY; 
  unsigned isize;

  if(m_geometry==0) return ndarray<const image_t, 2>();
  m_geometry -> get_pixel_coord_indexes(iX, iY, isize);

  //std::cout << "DetectorAccess::get_image isize = " << isize << '\n';
  //std::cout << "iX : "; for(int i=0; i<10; i++) std::cout << ' ' << iX[i]; std::cout << '\n';
  //std::cout << "iY : "; for(int i=0; i<10; i++) std::cout << ' ' << iY[i]; std::cout << '\n';
  //std::cout << "nda: "; for(int i=0; i<10; i++) std::cout << ' ' << nda[i]; std::cout << '\n';

  return PSCalib::GeometryAccess::img_from_pixel_arrays(iX, iY, nda.data(), isize); 
}

//-------------------
//-------------------
//-------------------
//-------------------

void DetectorAccess::print()
{
  initNDArrProducer();
  return m_nda_prod->print();
}

//-------------------

void DetectorAccess::print_config(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initNDArrProducer();
  return m_nda_prod->print_config(*shp_evt, *shp_env);
}

//-------------------

std::string DetectorAccess::str_inst(boost::shared_ptr<PSEnv::Env> shp_env)
{  
  return shp_env->instrument().c_str();
}

//-------------------

/*
  template <typename T>
  void DetectorAccess::apply_common_mode(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, T* nda)
    {
      initCommonMode(shp_evt, shp_env);
      m_cmode -> do_common_mode<T>(nda);
    }

template void DetectorAccess::apply_common_mode<double>  (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, double* nda);
template void DetectorAccess::apply_common_mode<float>   (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, float* nda);
template void DetectorAccess::apply_common_mode<int>     (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, int* nda);
template void DetectorAccess::apply_common_mode<int16_t> (boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, int16_t* nda);
template void DetectorAccess::apply_common_mode<uint16_t>(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, uint16_t* nda);
*/

//-------------------


//-------------------
} // namespace Detector
//-------------------





