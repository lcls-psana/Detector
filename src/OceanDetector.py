
"""
Detector interface for the Generic1D type
=========================================
"""
from __future__ import print_function

from DdlDetector import DdlDetector
import numpy as np
from CythonUtils import oceanNonLinCorr

class OceanDetector(DdlDetector):
    """
    """

    def __init__(self, *args):

        super(OceanDetector, self).__init__(*args)

        cfgs = self._fetch_configs()
        if len(cfgs) == 1:
            self.cfg = cfgs[0]
        elif len(cfgs) > 1:
            raise RuntimeError('Multiple or no configuration objects found '
                               '(%d) for Ocean device! DAQ misconfigured.'
                               '' % len(cfgs))
        return

    def intensity(self, evt):
        """

        Parameters
        ----------
        evt: a psana event object

        Returns
        -------
        A 1D array of intensities from the spectrometer, corrected
        for non-linearities if possible
        """

        raw = self._raw(evt)

        if raw is not None:
            poly = self.cfg.nonlinCorrect()
            # we have sometimes seen all zeros for these
            if np.count_nonzero(poly):
                result = oceanNonLinCorr(raw,poly)
            else:
                result = raw
        else:
            result = None 

        return result

    def _raw(self, evt):
        ddls = self._fetch_ddls(evt)

        if len(ddls) == 1:
            return ddls[0].data()
        else:
            return None

    def wavelength(self, evt):
        """

        Parameters
        ----------
        evt: a psana event object

        Returns
        -------
        A 1D array of wavelength values in nm.
        """

        if not hasattr(self,'wavelen'):
            wlc = self.cfg.waveLenCalib()
            data = self._raw(evt)
            if data is not None:
                self.wavelen = np.empty_like(data,dtype=float)
                for ipix in range(data.shape[0]):
                    self.wavelen[ipix] = wlc[0]+wlc[1]*ipix+wlc[2]*(ipix**2)+wlc[3]*(ipix**3)
            else:
                return None

        return self.wavelen
                

if __name__ == '__main__':

    import psana

    ds = psana.DataSource('/reg/g/psdm/data_test/types/OceanOptics_DataV3.xtc')
    
    # The ".2" detector in the above file has zeros for the nonlinearity corr.
    ocean = OceanDetector('DetInfo(XppLas.0:OceanOptics.1)', ds.env())

    for evt in ds.events():
        print(ocean.intensity(evt),'\n',ocean.wavelength(evt),'\n',ocean._raw(evt))
        break
