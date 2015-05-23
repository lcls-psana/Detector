
#include <boost/python.hpp>
#include "Detector/DetectorAccess.h"

#include <cstddef>  // for size_t

//-------------------
using namespace Detector;

typedef DetectorAccess::image_t image_t;
typedef DetectorAccess::data_t  data_t;

typedef Detector::DetectorAccess::pedestals_t     pedestals_t;    // float
typedef Detector::DetectorAccess::pixel_rms_t     pixel_rms_t;    // float
typedef Detector::DetectorAccess::pixel_gain_t    pixel_gain_t;   // float
typedef Detector::DetectorAccess::pixel_mask_t    pixel_mask_t;   // uint16_t
typedef Detector::DetectorAccess::pixel_bkgd_t    pixel_bkgd_t;   // float
typedef Detector::DetectorAccess::pixel_status_t  pixel_status_t; // uint16_t
typedef Detector::DetectorAccess::common_mode_t   common_mode_t;  // double

typedef Detector::DetectorAccess::shape_t         shape_t;        // double

//typedef Detector::DetectorAccess::data_i16_t      data_i16_t;     // int16_t

//-------------------

// Create function pointer to each overloaded DetectorAccess::calib method
ndarray<const pedestals_t, 1>    (DetectorAccess::*peds_1)  (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pedestals;
ndarray<const pixel_rms_t, 1>    (DetectorAccess::*prms_1)  (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pixel_rms;
ndarray<const pixel_gain_t, 1>   (DetectorAccess::*pgain_1) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pixel_gain;
ndarray<const pixel_mask_t, 1>   (DetectorAccess::*pmask_1) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pixel_mask;
ndarray<const pixel_bkgd_t, 1>   (DetectorAccess::*pbkgd_1) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pixel_bkgd;
ndarray<const pixel_status_t, 1> (DetectorAccess::*pstat_1) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pixel_status;
ndarray<const common_mode_t, 1>  (DetectorAccess::*pcmod_1) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::common_mode;

ndarray<const shape_t, 1>        (DetectorAccess::*pshape_1)(boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::shape;
const size_t                     (DetectorAccess::*psize_1) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::size;
const size_t                     (DetectorAccess::*pndim_1) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::ndim;

const int                        (DetectorAccess::*pstatus) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>, const int& ) = &DetectorAccess::status;

//-------------------

ndarray<const int16_t, 1>     (DetectorAccess::*pdata_1) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::data_int16_1;
ndarray<const int16_t, 2>     (DetectorAccess::*pdata_2) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::data_int16_2;
ndarray<const int16_t, 3>     (DetectorAccess::*pdata_3) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::data_int16_3;
ndarray<const int16_t, 4>     (DetectorAccess::*pdata_4) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::data_int16_4;

ndarray<const uint16_t, 2>    (DetectorAccess::*pdata_5) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::data_uint16_2;
ndarray<const uint16_t, 3>    (DetectorAccess::*pdata_6) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::data_uint16_3;

ndarray<const uint8_t, 2>     (DetectorAccess::*pdata_7) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::data_uint8_2;

//-------------------

ndarray<const double, 1>     (DetectorAccess::*pgeo_1) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pixel_coords_x;
ndarray<const double, 1>     (DetectorAccess::*pgeo_2) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pixel_coords_y;
ndarray<const double, 1>     (DetectorAccess::*pgeo_3) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pixel_coords_z;

ndarray<const double, 1>     (DetectorAccess::*pgeo_4) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pixel_areas;
ndarray<const int, 1>        (DetectorAccess::*pgeo_5) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pixel_mask_geo;

ndarray<const unsigned, 1>   (DetectorAccess::*pgeo_6) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pixel_indexes_x;
ndarray<const unsigned, 1>   (DetectorAccess::*pgeo_7) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pixel_indexes_y;

double                       (DetectorAccess::*pgeo_8) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::pixel_scale_size;


//-------------------

ndarray<const image_t, 2> (DetectorAccess::*img_0) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>, ndarray<const image_t, 1>) = &DetectorAccess::get_image;
//ndarray<const float, 2> (DetectorAccess::*img_1) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>, ndarray<const float, 1>&) = &DetectorAccess::get_image_float;
//ndarray<const double, 2> (DetectorAccess::*img_2) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>, ndarray<const double, 1>&) = &DetectorAccess::get_image_double;
//ndarray<const int16_t, 2> (DetectorAccess::*img_3) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>, ndarray<const int16_t, 1>&) = &DetectorAccess::get_image_int16;
//ndarray<const uint16_t, 2>  (DetectorAccess::*img_4) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>, ndarray<const uint16_t, 1>&) = &DetectorAccess::get_image_uint16;

//-------------------

void (DetectorAccess::*set_1) (const unsigned&) = &DetectorAccess::setMode;
void (DetectorAccess::*set_2) (const unsigned&) = &DetectorAccess::setPrintBits;
void (DetectorAccess::*set_3) (const float&)    = &DetectorAccess::setDefaultValue;


void (DetectorAccess::*print_1) () = &DetectorAccess::print;
void (DetectorAccess::*print_2) (boost::shared_ptr<PSEvt::Event>, boost::shared_ptr<PSEnv::Env>) = &DetectorAccess::print_config;

//-------------------
//ndarray<double,3> (DetectorAccess::*calib_2) (ndarray<data_t,3>) = &DetectorAccess::calib;
//-------------------

// BOOST wrapper to create detector_ext module that contains the DetectorAccess
// python class that calls the C++ DetectorAccess methods
// NB: The name of the python module (detector_ext) MUST match the name given in
// PYEXTMOD in the SConscript

BOOST_PYTHON_MODULE(detector_ext)
{    
  using namespace boost::python;

  boost::python::class_<DetectorAccess>("DetectorAccess", init<const PSEvt::Source, const unsigned&>())
    .def("pedestals",       peds_1)
    .def("pixel_rms",       prms_1)
    .def("pixel_gain",      pgain_1)
    .def("pixel_mask",      pmask_1)
    .def("pixel_bkgd",      pbkgd_1)
    .def("pixel_status",    pstat_1)
    .def("common_mode",     pcmod_1)
    .def("shape",           pshape_1)
    .def("size",            psize_1)
    .def("ndim",            pndim_1)
    .def("status",          pstatus)
    .def("data_int16_1",    pdata_1)
    .def("data_int16_2",    pdata_2)
    .def("data_int16_3",    pdata_3)
    .def("data_int16_4",    pdata_4)
    .def("data_uint16_2",   pdata_5)
    .def("data_uint16_3",   pdata_6)
    .def("data_uint8_2",    pdata_7)
    .def("pixel_coords_x",  pgeo_1)
    .def("pixel_coords_y",  pgeo_2)
    .def("pixel_coords_z",  pgeo_3)
    .def("pixel_areas",     pgeo_4)
    .def("pixel_mask_geo",  pgeo_5)
    .def("pixel_indexes_x", pgeo_6)
    .def("pixel_indexes_y", pgeo_7)
    .def("pixel_scale_size",pgeo_8)
    .def("get_image",       img_0)
    .def("set_mode",        set_1)
    .def("set_print_bits",  set_2)
    .def("set_def_value",   set_3)
    .def("print_members",   print_1)
    .def("print_config",    print_2)
    .def("inst",            &DetectorAccess::str_inst);
}

//-------------------
