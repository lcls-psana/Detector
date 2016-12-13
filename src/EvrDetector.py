
"""
Detector interface for the EVR
"""

from DdlDetector import DdlDetector
from _psana import EventId

class EvrDetector(DdlDetector):
    """
    The EVR device is used by the DAQ system to control what
    happens from shot-to-shot (e.g. which devices are triggered
    (e.g. a camera, or a shutter)).  For each event this object provides
    a list of "event codes" which can be used to understand which devices
    were activated in a particular LCLS event.
    """

    def __call__(self, evt, **kwargs):
        """
        Parameters
        ----------
        evt: a psana event object

        Returns
        -------
        A list of integer event-codes associated with the input event
        """
        return self.eventCodes(evt, **kwargs)

    def eventCodes(self, evt, this_fiducial_only=False):
        """
        Parameters
        ----------
        evt: a psana event object
        this_fiducial_only: bool.
            If true, returns only eventcodes that were sent on precisely
            the fiducial corresponding to evt.

        Returns
        -------
        A list of integer event-codes associated with the input event
        """
        ddl_evrs = self._fetch_ddls(evt)

        if len(ddl_evrs) == 1:
            ddl_evr = ddl_evrs[0]
            if this_fiducial_only:
                this_fid = evt.get(EventId).fiducials()
                event_code_list = [ fifo_event.eventCode()
                                    for fifo_event in ddl_evr.fifoEvents()
                                    if fifo_event.timestampHigh()==this_fid]
            else:
                event_code_list = [ fifo_event.eventCode()
                                    for fifo_event in ddl_evr.fifoEvents() ]

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
    


if __name__ == '__main__':

    # test EVR names
    import psana

    ds = psana.DataSource('exp=xpptut15:run=54')
    
    evrdet = EvrDetector('NoDetector.0:Evr.0')

    for evt in ds.events():
        print evrdet(evt)
        print evrdet(evt, this_fiducial_only=True)
        print evrdet.eventCodes(evt)
        print evrdet.eventCodes(evt, this_fiducial_only=True)
        break
