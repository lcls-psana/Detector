
"""
Detector interface for the Ipimb
"""

# issues with ipimb: 
# - can come in with either BLD or DAQ data
# - get the FEX type and implement sum(), channel(), xpos(), ypos()

from DdlDetector import DdlDetector

class IpimbDetector(DdlDetector):

    def sum(self,evt):
        ddl_ipimbs = self._fetch_ddls(evt)

    def __call__(self, evt):
        return None

# quick test
if __name__ == '__main__':

    # test IPIMB names
    import psana

    ds = psana.DataSource('exp=xpptut15:run=54')
    
    ipimbdet = IpimbDetector('XppSb2_Ipm')

    for evt in ds.events():
        print ipimbdet(evt)
        break
