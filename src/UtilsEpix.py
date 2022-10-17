
"""
:py:class:`UtilsEpix` contains utilities for epix100a detector
==============================================================

Usage::
    #from PSCalib.UtilsPanelAlias import alias_for_id, id_for_alias # moved out of this module
    from Detector.UtilsEpix import id_epix, is_trbit_high
    id = id_epix(config_obj)
    s = is_trbit_high(co)

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2018-02-22 by Mikhail Dubrovin
"""

from __future__ import print_function
from PSCalib.UtilsPanelAlias import alias_for_id, id_for_alias # keep it here for b/w compatability

from Detector.dir_root import os, DIR_ROOT, DIR_LOG_AT_START
CALIB_REPO_EPIX10KA = os.path.join(DIR_ROOT, 'detector/gains/epix10k/panels')  # '$DIR_ROOT/detector/gains/epix10k/panels'
FNAME_PANEL_ID_ALIASES = '%s/.aliases.txt'%CALIB_REPO_EPIX10KA

def id_epix(config_obj):
    """Returns Epix100 Id as a string, e.g., 3925999616-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719"""
    o = config_obj
    fmt2 = '%010d-%010d'
    zeros = fmt2 % (0,0)
    version = '%010d' % (o.version()) if getattr(o, "version", None) is not None else '%010d' % 0
    carrier = fmt2 % (o.carrierId0(), o.carrierId1())\
              if getattr(o, "carrierId0", None) is not None else zeros
    digital = fmt2 % (o.digitalCardId0(), o.digitalCardId1())\
              if getattr(o, "digitalCardId0", None) is not None else zeros
    analog  = fmt2 % (o.analogCardId0(), o.analogCardId1())\
              if getattr(o, "analogCardId0", None) is not None else zeros
    return '%s-%s-%s-%s' % (version, carrier, digital, analog)


def is_trbit_high(co):
    """from configuration object define if detector works in high gain mode."""
    if co.numberOfAsics()>1:
        return co.asics(0).trbit()==1

# EOF
