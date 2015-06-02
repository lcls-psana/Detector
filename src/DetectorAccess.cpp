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
DetectorAccess::DetectorAccess (const PSEvt::Source& source, const unsigned& pbits)
  : m_calibpars(0)
  , m_geometry(0)
  , m_source(source)
  , m_runnum(-1)
  , m_runnum_geo(-1)
  , m_mode(0)
  , m_pbits(pbits)
  , m_vdef(0)
  , m_nda_prod(0)
{
  std::stringstream ss; ss << source;
  m_str_src = ss.str();
  m_dettype = ImgAlgos::detectorTypeForSource(m_source);
  m_cgroup  = ImgAlgos::calibGroupForDetType(m_dettype); // for ex: "PNCCD::CalibV1";
  m_calibdir = std::string();

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
}

//-------------------

const size_t DetectorAccess::ndim(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initCalibStore(*shp_evt, *shp_env);
  return m_calibpars->ndim();
}

//-------------------

const size_t DetectorAccess::size(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initCalibStore(*shp_evt, *shp_env);
  return m_calibpars->size();
}

//-------------------

ndarray<const DetectorAccess::shape_t, 1>
DetectorAccess::shape(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initCalibStore(*shp_evt, *shp_env);
  return make_ndarray(m_calibpars->shape(), m_calibpars->ndim());
}

//-------------------

ndarray<const DetectorAccess::pedestals_t, 1> 
DetectorAccess::pedestals(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initCalibStore(*shp_evt, *shp_env);
  const DetectorAccess::pedestals_t* p = m_calibpars->pedestals(); // constants loaded before call to size()
  return make_ndarray(p, m_calibpars->size());
}

//-------------------

ndarray<const DetectorAccess::pixel_rms_t, 1> 
DetectorAccess::pixel_rms(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initCalibStore(*shp_evt, *shp_env);
  const DetectorAccess::pixel_rms_t* p = m_calibpars->pixel_rms();
  return make_ndarray(p, m_calibpars->size());
}

//-------------------

ndarray<const DetectorAccess::pixel_gain_t, 1> 
DetectorAccess::pixel_gain(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initCalibStore(*shp_evt, *shp_env);
  const DetectorAccess::pixel_gain_t* p = m_calibpars->pixel_gain();
  return make_ndarray(p, m_calibpars->size());
}

//-------------------

ndarray<const DetectorAccess::pixel_mask_t, 1> 
DetectorAccess::pixel_mask(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initCalibStore(*shp_evt, *shp_env);
  const DetectorAccess::pixel_mask_t* p = m_calibpars->pixel_mask();
  return make_ndarray(p, m_calibpars->size());
}

//-------------------

ndarray<const DetectorAccess::pixel_bkgd_t, 1> 
DetectorAccess::pixel_bkgd(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initCalibStore(*shp_evt, *shp_env);
  const DetectorAccess::pixel_bkgd_t* p = m_calibpars->pixel_bkgd();
  return make_ndarray(p, m_calibpars->size());
}

//-------------------

ndarray<const DetectorAccess::pixel_status_t, 1> 
DetectorAccess::pixel_status(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initCalibStore(*shp_evt, *shp_env);
  const DetectorAccess::pixel_status_t* p = m_calibpars->pixel_status();
  return make_ndarray(p, m_calibpars->size());
}

//-------------------

ndarray<const DetectorAccess::common_mode_t, 1> 
DetectorAccess::common_mode(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initCalibStore(*shp_evt, *shp_env);
  //std::cout << "TEST cm[0]: " << m_calibpars->common_mode()[0] << "\n";
  //std::cout << "TEST cm[3]: " << m_calibpars->common_mode()[3] << "\n";
  //std::cout << "TEST  size: " << m_calibpars->size(PSCalib::COMMON_MODE) << "\n";
  const DetectorAccess::common_mode_t* p = m_calibpars->common_mode();
  return make_ndarray(p, m_calibpars->size(PSCalib::COMMON_MODE));
}

//-------------------

const int
DetectorAccess::status(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, const int& calibtype) // PSCalib::COMMON_MODE
{
  initCalibStore(*shp_evt, *shp_env);
  return m_calibpars->status((const PSCalib::CALIB_TYPE)calibtype);
}

//-------------------
//-------------------
//-------------------
//-------------------

void 
DetectorAccess::initCalibStore(PSEvt::Event& evt, PSEnv::Env& env)
{
  int runnum = ImgAlgos::getRunNumber(evt);
  if(runnum == m_runnum) return;
  m_runnum = runnum;

  if(m_calibpars) delete m_calibpars;

  m_calibdir = env.calibDir();

  if(m_pbits) {
      std::stringstream ss;
      ss << "in initCalibStore(...):"
         << "\nInstrument  : " << env.instrument()
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
//-------------------

void 
DetectorAccess::initGeometry(PSEvt::Event& evt, PSEnv::Env& env)
{
  int runnum = ImgAlgos::getRunNumber(evt);

  if(m_geometry) {
    if(runnum == m_runnum_geo) return;
    delete m_geometry;
    m_geometry = 0;
  }

  m_calibdir = env.calibDir();

  unsigned pbits_cff = (m_pbits & 2) ? 0xffff : 0;
  PSCalib::CalibFileFinder calibfinder(m_calibdir, m_cgroup, pbits_cff);
  std::string fname = calibfinder.findCalibFile(m_str_src, "geometry", runnum);

  if(m_pbits) {
      std::stringstream ss;
      ss << "in initGeometry(...):"
         << "\nInstrument     : " << env.instrument()
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
  m_runnum_geo = runnum;
}

//-------------------
//-------------------

void 
DetectorAccess::initNDArrProducer()
{
  if(!m_nda_prod) m_nda_prod = NDArrProducerStore::Create(m_source, m_mode, m_pbits, m_vdef); // universal access through the factory store
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

ndarray<const double, 1> DetectorAccess::pixel_coords_x(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initGeometry(*shp_evt, *shp_env);

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
  initGeometry(*shp_evt, *shp_env);

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
  initGeometry(*shp_evt, *shp_env);

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
  initGeometry(*shp_evt, *shp_env);

  const double* A;
  unsigned   size;

  if(m_geometry==0) return ndarray<const double, 1>();
  m_geometry -> get_pixel_areas(A,size);
  return make_ndarray(A, size);
}

//-------------------

ndarray<const int, 1> DetectorAccess::pixel_mask_geo(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initGeometry(*shp_evt, *shp_env);

  const int* mask;
  unsigned   size;
  unsigned   mbits=0377; // 1-edges; 2-wide central cols; 4-non-bound; 8-non-bound neighbours

  if(m_geometry==0) return ndarray<const int, 1>();
  m_geometry -> get_pixel_mask(mask, size, std::string(), 0, mbits);
  return make_ndarray(mask, size);
}

//-------------------

ndarray<const unsigned, 1> DetectorAccess::pixel_indexes_x(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env)
{
  initGeometry(*shp_evt, *shp_env);
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
  initGeometry(*shp_evt, *shp_env);

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
  initGeometry(*shp_evt, *shp_env);

  if(m_geometry==0) return 1;
  return m_geometry -> get_pixel_scale_size ();
}

//-------------------

ndarray<const image_t, 2>
DetectorAccess::get_image(boost::shared_ptr<PSEvt::Event> shp_evt, boost::shared_ptr<PSEnv::Env> shp_env, ndarray<const image_t, 1> nda)
{
  initGeometry(*shp_evt, *shp_env);

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
} // namespace Detector
//-------------------





