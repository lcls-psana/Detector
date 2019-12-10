
"""
Detector interface for the Generic1D type, but specialized for the
case where it represents waveforms with a time axis.  This interface
is intended to be identical to the WFDetector 
"""
from __future__ import print_function
from __future__ import absolute_import

from .Generic1DDetector import Generic1DDetector
import numpy as np

class GenericWFDetector(Generic1DDetector):
    """
    This class returns a list of arrays of values (one entry
    in the list for each channel) and a corresponding list of time arrays
    that are used as oscilloscope-style channels.
    """

    def __init__(self, *args):

        super(GenericWFDetector, self).__init__(*args)

        return

    # This method interface designed to be similar to WFDetector
    # but returns lists of 1D arrays instead of 2D arrays.
    def raw(self, *args):
        """

        Parameters
        ----------
        evt: a psana event object

        Returns
        -------
        a list of waveform arrays, not converted into voltage
        """

        return super(GenericWFDetector,self).__call__(*args)

    # This method interface designed to be similar to WFDetector
    # but returns lists of 1D arrays instead of 2D arrays.
    def wftime(self, evt=None):
        """

        Parameters
        ----------
        (optional) evt: a psana event object. not used in this method
        but allowed to allow the interface similar to other Detector
        interface methods

        Returns
        -------
        a list of 1D arrays of time values of each sample, in seconds
        """

        cfg = self._g1d_cfg

        times = []
        for i in range(cfg.NChannels()):
            offset = cfg.Offset()[i]
            period = cfg.Period()[i]
            length = cfg.Length()[i]
            start  = offset*period
            stop   = start+(length-1)*period # -1 since we count from zero
            times.append(np.linspace(start,stop,length))

        return times

if __name__ == '__main__':

    import psana

    ds = psana.DataSource('exp=mfxc0116:run=66')
    g1ddet = GenericWFDetector('DetInfo(MfxEndstation.0:Wave8.0)', ds.env())

    for evt in ds.events():
        for t,wf in zip(g1ddet.raw(evt),g1ddet.wftime(evt)):
            print(t.shape,wf.shape)
        break
