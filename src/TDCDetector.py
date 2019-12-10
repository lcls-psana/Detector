
"""
Detector interface for the TDC type
"""
from __future__ import print_function
from __future__ import absolute_import

from .DdlDetector import DdlDetector
import numpy as np

class TDCDetector(DdlDetector):
    """
    Provides access to hit times from a TDC device
    with multiple channels.
    """

    def __init__(self, *args):

        super(TDCDetector, self).__init__(*args)

        # only support the standard channels for now, to try
        # to make the users' and our lives simpler, until
        # we receive requests for the extra functionality (i.e.
        # no "Common" and no "AuxIO/Marker" channels)
        self.chanlist = range(1,7)

        return


    def times(self,evt):
        """

        Parameters
        ----------
        evt: a psana event object

        Returns
        -------
        A list of arrays, or None if data not found.  Each array contains
        the times (in seconds) of TDC hits for a channel.
        """
        return self._times(evt)


    def overflows(self,evt):
        """

        Parameters
        ----------
        evt: a psana event object

        Returns
        -------
        A list of arrays, or None if data not found.  Each array contains
        the times (in seconds) of TDC hits for a channel, for cases
        where the time value has "wrapped".
        """
        # 0x8 turns on the bit looking for overflows
        return self._times(evt,0x8)


    def _times(self, evt, overflows=0):
        ddls = self._fetch_ddls(evt)
        # these 28 bits are the data (50ps per bit)
        data = lambda vals: (vals&0xfffffff)*50e-12
        # 3 lower bits define the channel number
        # the 4th bit marks overflows, so we add it here
        # to (optionally) filter out the overflow data to
        # try to make the user's life simpler
        chan_select = lambda vals,i: ((vals>>28)&0xf)==(i|overflows)

        if len(ddls) == 1:
            channels = []
            tdc = ddls[0]
            # get data into numpy, since DDL is awkward for this
            # type: we get lists instead of an array and we can't
            # do the C++-style down-casts that the TdcDataV1_Item
            # wants us to do
            values = np.array([d.value() for d in tdc.data()], dtype=np.uint32)

            for i in self.chanlist:
                arr = data(values[chan_select(values,i)])
                channels.append(arr)

        else:
            channels = None 

        return channels

if __name__ == '__main__':

    import psana

    ds = psana.DataSource('exp=sxrm2016:run=7')
    
    tdcdet = TDCDetector('DetInfo(SxrEndstation.0:AcqTDC.2)', ds.env())

    print('----- Times -----')
    for evt in ds.events():
        times = tdcdet.times(evt)
        for chan,t in enumerate(times):
            if t.size>0: print(chan,t)

    print('----- Overflows -----')
    for evt in ds.events():
        times = tdcdet.overflows(evt)
        for chan,t in enumerate(times):
            if t.size>0: print(chan,t)

