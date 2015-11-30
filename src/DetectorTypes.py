
"""
This file contains static declartions of the known & interpretable detector
types.
"""

from Detector.DdlDetector   import DdlDetector
from Detector.EpicsDetector import EpicsDetector
from Detector.AreaDetector  import AreaDetector
from Detector.WFDetector    import WFDetector
from Detector.EvrDetector   import EvrDetector


def no_device_exception(*args):
    raise TypeError('Detector device is `NoDevice`, which means the'
                    'data are not interpretable.')


# list of all known detectors and their types
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

bld_names = [
    "EBeam",
    "PhaseCavity",
    "FEEGasDetEnergy",
    "NH2-SB1-IPM-01",
    "XCS-IPM-01",
    "XCS-DIO-01",
    "XCS-IPM-02",
    "XCS-DIO-02",
    "XCS-IPM-03",
    "XCS-DIO-03",
    "XCS-IPM-03m",
    "XCS-DIO-03m",
    "XCS-YAG-1",
    "XCS-YAG-2",
    "XCS-YAG-3m",
    "XCS-YAG-3",
    "XCS-YAG-mono",
    "XCS-IPM-mono",
    "XCS-DIO-mono",
    "XCS-DEC-mono",
    "MEC-LAS-EM-01",
    "MEC-TCTR-PIP-01",
    "MEC-TCTR-DI-01",
    "MEC-XT2-IPM-02",
    "MEC-XT2-IPM-03",
    "MEC-HXM-IPM-01",
    "GMD",
    "CxiDg1_Imb01",
    "CxiDg2_Imb01",
    "CxiDg2_Imb02",
    "CxiDg3_Imb01",
    "CxiDg1_Pim",
    "CxiDg2_Pim",
    "CxiDg3_Pim",
    "XppMon_Pim0",
    "XppMon_Pim1",
    "XppSb2_Ipm",
    "XppSb3_Ipm",
    "XppSb3_Pim",
    "XppSb4_Pim",
    "XppEnds_Ipm0",
    "XppEnds_Ipm1",
    "MEC-XT2-PIM-02",
    "MEC-XT2-PIM-03",
    "CxiDg3_Spec",
    "NH2-SB1-IPM-02",
    "FEE-SPEC0",
    "SXR-SPEC0",
    "XPP-SPEC0",
    "XCS-USR-IPM-01",
    "XCS-USR-IPM-02",
    "XCS-USR-IPM-03",
    "XCS-USR-IPM-04",
    "XCS-IPM-04",
    "XCS-DIO-04",
    "XCS-IPM-05",
    "XCS-DIO-05",
    "XCS-IPM-gon",
    "XCS-IPM-ladm",
    "XPP-AIN-01",
    "XCS-AIN-01",
    "AMO-AIN-01"
]


