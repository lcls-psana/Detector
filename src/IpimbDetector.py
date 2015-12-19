
"""
Detector interface for the Ipimb
"""

# issues with ipimb: 
# - can come in with either BLD or DAQ data
# - get the FEX type and implement sum(), channel(), xpos(), ypos()

import _psana
from DdlDetector import DdlDetector

class IpimbDetector(DdlDetector):


    def _fetch_ddls(self, evt):
        """
        Overrides DdlDetector's _fetch_ddls() method. Should find two DDL
        objects in the event's .keys() that map to our source. We are only
        interested in the Fex one right now.
        """

        types = self._find_types(evt)
        ddls = []
        for tp in types:
            if 'IpmFex' in str(tp):
                ddl = evt.get(tp, _psana.Source(self.source))
                ddls.append(ddl)

        if len(ddls) > 1:
            raise RuntimeError('Found %d IpmFex types in event, '
                               'expected only 1' % len(ddls))
        elif len(ddls) == 0:
            return None
        else:
            return ddls[0]


    def _ddldata_or_none(self, evt, fxn_name):
        ddl_det = self._fetch_ddls(evt)
        if ddl_det == None:
            return None
        else:
            return getattr(ddl_det, fxn_name)()

    def channel(self, evt):
        return self._ddldata_or_none(evt, 'channel')

    def sum(self, evt):
        return self._ddldata_or_none(evt, 'sum')

    def xpos(self, evt):
        return self._ddldata_or_none(evt, 'xpos')

    def ypos(self, evt):
        return self._ddldata_or_none(evt, 'ypos')

    def __call__(self, evt):
        return self.channel(evt)

# quick test
if __name__ == '__main__':

    # test IPIMB names
    import psana

    ds = psana.DataSource('exp=xpptut15:run=54')
    
    ipimbdet = IpimbDetector('XppSb2_Ipm')
    ipimbdet_not_in_data = IpimbDetector('XppEnds_Ipm1')

    for i,evt in enumerate(ds.events()):
        print ipimbdet(evt), ipimbdet.sum(evt), ipimbdet.xpos(evt), ipimbdet.ypos(evt)
        print ipimbdet_not_in_data(evt), ipimbdet_not_in_data.sum(evt)
        if i == 5: break



