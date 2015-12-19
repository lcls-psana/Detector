
"""
This file contains static declartions of the known & interpretable detector
types.
"""

from Detector.DdlDetector   import DdlDetector
from Detector.EpicsDetector import EpicsDetector
from Detector.AreaDetector  import AreaDetector
from Detector.WFDetector    import WFDetector
from Detector.EvrDetector   import EvrDetector
from Detector.IpimbDetector import IpimbDetector


def no_device_exception(*args):
    raise TypeError('Detector device is `NoDevice`, which means the'
                    'data are not interpretable.')



# list of all known DetInfo sources and their types
#  > names (keys) should be in all caps
#  > detector types (values) should be implemented class objects
#    originally from pdsdata/xtc/src/DetInfo.cc 
#    copied 11/30/15

detectors = {
    "NoDevice"    : no_device_exception, # raises an error
    "Evr"         : EvrDetector,
    "Acqiris"     : WFDetector,
    "Opal1000"    : AreaDetector,
    "Tm6740"      : AreaDetector,
    "pnCCD"       : AreaDetector,
    "Princeton"   : AreaDetector,
    "Fccd"        : AreaDetector,
    "Ipimb"       : DdlDetector, # to be updated
    "Encoder"     : DdlDetector,
    "Cspad"       : AreaDetector,
    "AcqTDC"      : DdlDetector,
    "Xamps"       : AreaDetector,
    "Cspad2x2"    : AreaDetector,
    "Fexamp"      : AreaDetector,
    "Gsc16ai"     : DdlDetector,
    "Phasics"     : AreaDetector,
    "Timepix"     : AreaDetector,
    "Opal2000"    : AreaDetector,
    "Opal4000"    : AreaDetector,
    "OceanOptics" : AreaDetector,
    "Opal1600"    : AreaDetector,
    "Opal8000"    : AreaDetector,
    "Fli"         : AreaDetector,
    "Quartz4A150" : AreaDetector,
    "Andor"       : AreaDetector,
    "USDUSB"      : DdlDetector,
    "OrcaFl40"    : AreaDetector,
    "Imp"         : WFDetector,
    "Epix"        : AreaDetector,
    "Rayonix"     : AreaDetector,
    "EpixSampler" : AreaDetector,
    "Pimax"       : AreaDetector,
    "Fccd960"     : AreaDetector,
    "Epix10k"     : AreaDetector,
    "Epix100a"    : AreaDetector,
    "EpixS"       : AreaDetector,
    "Gotthard"    : AreaDetector 
}



# these are the names of all the BldInfo types
#    originally from pdsdata/xtc/src/BldInfo.cc
#    copied 11/30/15

bld_info = {
    "EBeam"            : DdlDetector,
    "PhaseCavity"      : DdlDetector,
    "FEEGasDetEnergy"  : DdlDetector,
    "NH2-SB1-IPM-01"   : IpimbDetector,
    "XCS-IPM-01"       : IpimbDetector,
    "XCS-DIO-01"       : DdlDetector,
    "XCS-IPM-02"       : IpimbDetector,
    "XCS-DIO-02"       : DdlDetector,
    "XCS-IPM-03"       : IpimbDetector,
    "XCS-DIO-03"       : DdlDetector,
    "XCS-IPM-03m"      : IpimbDetector,
    "XCS-DIO-03m"      : DdlDetector,
    "XCS-YAG-1"        : DdlDetector,
    "XCS-YAG-2"        : DdlDetector,
    "XCS-YAG-3m"       : DdlDetector,
    "XCS-YAG-3"        : DdlDetector,
    "XCS-YAG-mono"     : DdlDetector,
    "XCS-IPM-mono"     : IpimbDetector,
    "XCS-DIO-mono"     : DdlDetector,
    "XCS-DEC-mono"     : DdlDetector,
    "MEC-LAS-EM-01"    : DdlDetector,
    "MEC-TCTR-PIP-01"  : DdlDetector,
    "MEC-TCTR-DI-01"   : DdlDetector,
    "MEC-XT2-IPM-02"   : IpimbDetector,
    "MEC-XT2-IPM-03"   : IpimbDetector,
    "MEC-HXM-IPM-01"   : IpimbDetector,
    "GMD"              : DdlDetector,
    "CxiDg1_Imb01"     : IpimbDetector,
    "CxiDg2_Imb01"     : IpimbDetector,
    "CxiDg2_Imb02"     : IpimbDetector,
    "CxiDg3_Imb01"     : IpimbDetector,
    "CxiDg1_Pim"       : DdlDetector,
    "CxiDg2_Pim"       : DdlDetector,
    "CxiDg3_Pim"       : DdlDetector,
    "XppMon_Pim0"      : DdlDetector,
    "XppMon_Pim1"      : DdlDetector,
    "XppSb2_Ipm"       : IpimbDetector,
    "XppSb3_Ipm"       : IpimbDetector,
    "XppSb3_Pim"       : DdlDetector,
    "XppSb4_Pim"       : DdlDetector,
    "XppEnds_Ipm0"     : IpimbDetector,
    "XppEnds_Ipm1"     : IpimbDetector,
    "MEC-XT2-PIM-02"   : DdlDetector,
    "MEC-XT2-PIM-03"   : DdlDetector,
    "CxiDg3_Spec"      : DdlDetector,
    "NH2-SB1-IPM-02"   : DdlDetector,
    "FEE-SPEC0"        : DdlDetector,
    "SXR-SPEC0"        : DdlDetector,
    "XPP-SPEC0"        : DdlDetector,
    "XCS-USR-IPM-01"   : IpimbDetector,
    "XCS-USR-IPM-02"   : IpimbDetector,
    "XCS-USR-IPM-03"   : IpimbDetector,
    "XCS-USR-IPM-04"   : IpimbDetector,
    "XCS-IPM-04"       : IpimbDetector,
    "XCS-DIO-04"       : DdlDetector,
    "XCS-IPM-05"       : IpimbDetector,
    "XCS-DIO-05"       : DdlDetector,
    "XCS-IPM-gon"      : IpimbDetector,
    "XCS-IPM-ladm"     : IpimbDetector,
    "XPP-AIN-01"       : DdlDetector,
    "XCS-AIN-01"       : DdlDetector,
    "AMO-AIN-01"       : DdlDetector
}


