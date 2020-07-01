"""

WARNING! NON-EXISTENT DIR: /reg/d/psdm/XCS/xcslr0016/calib/Epix100a::CalibV1/XcsEndstation.0:Epix100a.2/geometry

DCFileName attributes:
  env      : psana.Env()
  src      : XcsEndstation.0:Epix100a.2
  src_name : DetInfo(XcsEndstation.0:Epix100a.2)
  dettype  : epix100a
  detid    : 3925999620-0996579585-0553648138-1232098304-1221641739-2650251521-3976200215
  detname  : epix100a-3925999620-0996579585-0553648138-1232098304-1221641739-2650251521-3976200215
  file name: epix100a-3925999620-0996579585-0553648138-1232098304-1221641739-2650251521-3976200215.h5
  calibdir : /reg/d/psdm/XCS/xcslr0016/calib

  file path: /reg/d/psdm/XCS/xcslr0016/calib/epix100a/epix100a-3925999620-0996579585-0553648138-1232098304-1221641739-2650251521-3976200215.h5
  repo path: /reg/d/psdm/detector/calib/epix100a/epix100a-3925999620-0996579585-0553648138-1232098304-1221641739-2650251521-3976200215.h5

ERROR: DCType corrupted file structure - group "/pixel_status/1519529114-end" does not contain key "begin", keys: "[u'data', u'tsprod', u'version']"

epix_1:
  local: "/reg/d/psdm/XCS/xcslr0016/calib/epix100a/epix100a-3925999620-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719.h5"
  repo : "/reg/d/psdm/detector/calib/epix100a/epix100a-3925999620-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719.h5"

epix_2:
  local: "/reg/d/psdm/XCS/xcslr0016/calib/epix100a/epix100a-3925999620-0996579585-0553648138-1232098304-1221641739-2650251521-3976200215.h5"
  repo : "/reg/d/psdm/detector/calib/epix100a/epix100a-3925999620-0996579585-0553648138-1232098304-1221641739-2650251521-3976200215.h5"

epix_3:
  local: "/reg/d/psdm/XCS/xcslr0016/calib/epix100a/epix100a-3925999620-0998779393-0117440522-1794137088-1745668107-2398940417-2046820376.h5"
  repo : "/reg/d/psdm/detector/calib/epix100a/epix100a-3925999620-0998779393-0117440522-1794137088-1745668107-2398940417-2046820376.h5"

epix_4:
  local: /reg/d/psdm/XCS/xcslr0016/calib/epix100a/epix100a-3925999620-0998275585-0385875978-1232100352-0416335371-2654033921-1056964631.h5
  repo : /reg/d/psdm/detector/calib/epix100a/epix100a-3925999620-0998275585-0385875978-1232100352-0416335371-2654033921-1056964631.h5

"""
from __future__ import print_function


rnum = 400

from psana import *
ds = DataSource('exp=xcslr0016:run=%d' % rnum)
det2 = Detector('epix_4')
#det2.set_print_bits(01777)
print(det2.coords_x(rnum))
print(det2.gain(rnum))
print(det2.pedestals(rnum))
#print(det2.status(rnum))
