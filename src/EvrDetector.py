
"""
Detector interface for the EVR
"""

from DdlDetector import DdlDetector


class EvrDetector(DdlDetector):

    def __call__(self, evt):
        return self.eventCodes(evt)

    def eventCodes(self, evt):

        ddl_evrs = self._fetch_ddls(evt)

        if len(ddl_evrs) == 1:
            ddl_evr = ddl_evrs[0]
            event_code_list = [ fifo_event.eventCode() for fifo_event \
                                in ddl_evr.fifoEvents() ]

        else:
            event_code_list = None 

        return event_code_list


    # placeholder for idea: attribute that reports the EVR names, telling us
    # what the different codes actually mean -- we have to fetch this info
    # from the configstore
    #
    #@property
    #def evr_names(self):
    #    ... code ...
    #    return evr_names
    


# quick test
if __name__ == '__main__':

    # test EVR names
    import psana

    ds = psana.DataSource('exp=xpptut15:run=54')
    
    evrdet = EvrDetector('NoDetector.0:Evr.0')

    for evt in ds.events():
        print evrdet(evt)
        print evrdet.eventCodes(evt)
        break
