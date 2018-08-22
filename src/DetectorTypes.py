
"""
This file contains static declarations of the known & interpretable detector
types.
"""

from Detector.DdlDetector       import DdlDetector
from Detector.AreaDetector      import AreaDetector
from Detector.WFDetector        import WFDetector
from Detector.EvrDetector       import EvrDetector
from Detector.IpimbDetector     import IpimbDetector
from Detector.UsdUsbDetector    import UsdUsbDetector
from Detector.GenericWFDetector import GenericWFDetector
from Detector.OceanDetector     import OceanDetector
from Detector.TDCDetector       import TDCDetector

class MissingDet(object):
    """
    This detector is returned by the Detector interface
    when the user requests that the software not crash
    when a detector is missing.  It returns a method
    that returns None for all attributes.
    """
    def __init__(self,name,*args,**kwargs):
        self.name = name
    def _none(self, *args, **kwargs):
        return None
    def __getattr__(self, name):
        return self._none

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
    "Ipimb"       : IpimbDetector,
    "Encoder"     : DdlDetector,
    "Cspad"       : AreaDetector,
    "AcqTDC"      : TDCDetector,
    "Xamps"       : AreaDetector,
    "Cspad2x2"    : AreaDetector,
    "Fexamp"      : AreaDetector,
    "Gsc16ai"     : DdlDetector,
    "Phasics"     : AreaDetector,
    "Timepix"     : AreaDetector,
    "Opal2000"    : AreaDetector,
    "Opal4000"    : AreaDetector,
    "OceanOptics" : OceanDetector,
    "Opal1600"    : AreaDetector,
    "Opal8000"    : AreaDetector,
    "Fli"         : AreaDetector,
    "Quartz4A150" : AreaDetector,
    "DualAndor"   : AreaDetector,
    "Andor"       : AreaDetector,
    "USDUSB"      : UsdUsbDetector,
    "OrcaFl40"    : AreaDetector,
    "Imp"         : WFDetector,
    "Epix"        : AreaDetector,
    "Rayonix"     : AreaDetector,
    "EpixSampler" : AreaDetector,
    "Pimax"       : AreaDetector,
    "Fccd960"     : AreaDetector,
    "Epix10k"     : AreaDetector,
    "Epix10ka"    : AreaDetector,
    "Epix100a"    : AreaDetector,
    "EpixS"       : AreaDetector,
    "Gotthard"    : AreaDetector,
    "Wave8"       : GenericWFDetector,
    "LeCroy"      : GenericWFDetector,
    "ControlsCamera" : AreaDetector,
    "Archon"      : AreaDetector,
    "Jungfrau"    : AreaDetector,
    "Zyla"        : AreaDetector,
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
    "XCS-DIO-01"       : IpimbDetector,
    "XCS-IPM-02"       : IpimbDetector,
    "XCS-DIO-02"       : IpimbDetector,
    "XCS-IPM-03"       : IpimbDetector,
    "XCS-DIO-03"       : IpimbDetector,
    "XCS-IPM-03m"      : IpimbDetector,
    "XCS-DIO-03m"      : IpimbDetector,
    "XCS-YAG-1"        : DdlDetector,
    "XCS-YAG-2"        : DdlDetector,
    "XCS-YAG-3m"       : DdlDetector,
    "XCS-YAG-3"        : DdlDetector,
    "XCS-YAG-mono"     : DdlDetector,
    "XCS-IPM-mono"     : IpimbDetector,
    "XCS-DIO-mono"     : IpimbDetector,
    "XCS-DEC-mono"     : DdlDetector,
    "MEC-LAS-EM-01"    : IpimbDetector,
    "MEC-TCTR-PIP-01"  : IpimbDetector,
    "MEC-TCTR-DI-01"   : IpimbDetector,
    "MEC-XT2-IPM-02"   : IpimbDetector,
    "MEC-XT2-IPM-03"   : IpimbDetector,
    "MEC-HXM-IPM-01"   : IpimbDetector,
    "GMD"              : DdlDetector,
    "CxiDg1_Imb01"     : IpimbDetector,
    "CxiDg2_Imb01"     : IpimbDetector,
    "CxiDg2_Imb02"     : IpimbDetector,
    "CxiDg3_Imb01"     : IpimbDetector,
    "CxiDg1_Pim"       : IpimbDetector,
    "CxiDg2_Pim"       : IpimbDetector,
    "CxiDg3_Pim"       : IpimbDetector,
    "XppMon_Pim0"      : IpimbDetector,
    "XppMon_Pim1"      : IpimbDetector,
    "XppSb2_Ipm"       : IpimbDetector,
    "XppSb3_Ipm"       : IpimbDetector,
    "XppSb3_Pim"       : IpimbDetector,
    "XppSb4_Pim"       : IpimbDetector,
    "XppEnds_Ipm0"     : IpimbDetector,
    "XppEnds_Ipm1"     : IpimbDetector,
    "MEC-XT2-PIM-02"   : IpimbDetector,
    "MEC-XT2-PIM-03"   : IpimbDetector,
    "CxiDg3_Spec"      : DdlDetector,
    "NH2-SB1-IPM-02"   : IpimbDetector,
    "FEE-SPEC0"        : DdlDetector,
    "SXR-SPEC0"        : DdlDetector,
    "XPP-SPEC0"        : DdlDetector,
    "XCS-USR-IPM-01"   : IpimbDetector,
    "XCS-USR-IPM-02"   : IpimbDetector,
    "XCS-USR-IPM-03"   : IpimbDetector,
    "XCS-USR-IPM-04"   : IpimbDetector,
    "XCS-IPM-04"       : IpimbDetector,
    "XCS-DIO-04"       : IpimbDetector,
    "XCS-IPM-05"       : IpimbDetector,
    "XCS-DIO-05"       : IpimbDetector,
    "XCS-IPM-gon"      : IpimbDetector,
    "XCS-IPM-ladm"     : IpimbDetector,
    "XPP-AIN-01"       : DdlDetector,
    "XCS-AIN-01"       : DdlDetector,
    "AMO-AIN-01"       : DdlDetector,
    "MFX-BEAMMON-01"   : DdlDetector,
    "EOrbits"          : DdlDetector,
    "MfxDg1_Pim"       : DdlDetector,
    "MfxDg2_Pim"       : DdlDetector,
    "SXR-AIN-01"       : DdlDetector,
    "HX2-SB1-BMMON"    : DdlDetector,
    "XRT-USB-ENCODER-01" : UsdUsbDetector,
    "XPP-USB-ENCODER-01" : UsdUsbDetector,
    "XPP-USB-ENCODER-02" : UsdUsbDetector,
    "XCS-USB-ENCODER-01" : UsdUsbDetector,
    "CXI-USB-ENCODER-01" : UsdUsbDetector,
    "XCS-SND-DIO"      : DdlDetector,
    "MFX-USR-DIO"      : DdlDetector,
    "XPP-SB2-BMMON"    : DdlDetector,
    "XPP-SB3-BMMON"    : DdlDetector,
    "HFX-DG2-BMMON"    : DdlDetector,
    "XCS-SB1-BMMON"    : DdlDetector,
    "XCS-SB2-BMMON"    : DdlDetector,
    "CXI-DG2-BMMON"    : DdlDetector,
    "CXI-DG3-BMMON"    : DdlDetector,
    "MFX-DG1-BMMON"    : DdlDetector,
    "MFX-DG2-BMMON"    : DdlDetector,
    "MFX-AIN-01"       : DdlDetector,
    "MEC-AIN-01"       : DdlDetector,
    "FEE-AIN-01"       : DdlDetector,
    "MEC-XT2-BMMON-02" : DdlDetector,
    "MEC-XT2-BMMON-03" : DdlDetector,
}
