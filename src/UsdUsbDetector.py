
"""
Detector interface for the UsdUsb Encoder Box
=============================================
"""

# issues with usdusb: 
# - can come in with DAQ data
# - can have a FEX type which implement encoder_values()

import _psana
import numpy as np
from DdlDetector import DdlDetector

class UsdUsbDetector(DdlDetector):
    """
    Detector interface for the USDUSB encoder box, the which
    monitors the encoder counts of a device. Methods of note:

    -- descriptions - user defined descriptions of each channel
    -- values
    """


    def __init__(self, source, env):
        """
        Parameters
        ----------
        source : str
            A psana source string (not a psana.Source object), e.g.
            'DetInfo(CxiDsd.0:Cspad.0)', 'BldInfo(FEEGasDetEnergy)',
            or an alias e.g. 'cspad'.
        """
        super(UsdUsbDetector, self).__init__(source, env)
        self._cfg = env.configStore()
        return

    def _fetch_ddls(self, evt, is_fex=False):
        """
        Overrides DdlDetector's _fetch_ddls() method. Should find two DDL
        objects in the event's .keys() that map to our source.
        """

        types = self._find_types(evt)
        ddls = []
        match_str = 'UsdUsb.FexData' if is_fex else 'UsdUsb.Data'
        for tp in types:
            if match_str in str(tp):
                ddl = evt.get(tp, _psana.Source(self.source))
                ddls.append(ddl)

        if len(ddls) > 1:
            raise RuntimeError('Found %d %s types in event, '
                               'expected only 1' % (len(ddls)), match_str)
        return ddls

    def _fetch_cfg_ddls(self, is_fex):
        """
        Similar to DdlDetector's _fetch_ddls() method. Should find two DDL
        objects in the config's .keys() that map to our source. We are only
        interested in the Fex one right now.
        """

        types = self._find_types(self._cfg)
        ddls = []
        match_str = 'UsdUsb.FexConfig' if is_fex else 'UsdUsb.Config'
        for tp in types:
            if match_str in str(tp):
                ddl = self._cfg.get(tp, _psana.Source(self.source))
                ddls.append(ddl)

        if len(ddls) > 1:
            raise RuntimeError('Found %d %s types in config store, '
                               'expected only 1' % (len(ddls)), match_str)
        return ddls

    def _ddldata_or_none(self, evt, fxn_name, is_fex):
        ddl_det = self._fetch_ddls(evt, is_fex)
        if len(ddl_det) == 0:
            return None
        else:
            return getattr(ddl_det[0], fxn_name)()

    def _ddlcfglist_or_none(self, fxn_name, is_fex):
        cfg_det = self._fetch_cfg_ddls(True)
        if len(cfg_det) == 0:
            return None
        else:
            chan_vals = []
            for chan in range(cfg_det[0].NCHANNELS):
                chan_vals.append(getattr(cfg_det[0], fxn_name)(chan))
            return chan_vals

    def descriptions(self):
      """
      Return the description field for all channels of the USDUSB.

      Returns
      -------
      descriptions : list
          Description string for each of the four individual channels.
      """
      return self._ddlcfglist_or_none('name', True)

    def values(self, evt):
        """
        Return the calibrated encoder values in all channels of the USDSUB
        if available. If no calibrated values are available it returns the
        raw encoder counts.

        The calibrated value is calculated for each channel as follows:
         value = scale * (raw_count + offset)

        The scale and offset values can be retrieved from the configStore.

        Parameters
        ----------
        evt : psana.Event
            The event to retrieve data from.

        Returns
        -------
        values : np.ndarray
            The calibrated encoder value measured in each of the four
            individual channels. Units depend on chosen calibration.
        """
        values = self._ddldata_or_none(evt, 'encoder_values', True)
        if values is None:
          values = self._ddldata_or_none(evt, 'encoder_count', False)
        return values


if __name__ == '__main__':
    import psana

    ds = psana.DataSource('exp=xpp00316:run=384')
    
    usdusbdet = UsdUsbDetector('XppEndstation.0:USDUSB.0',ds.env())
    usdusbdet_not_in_data = UsdUsbDetector('usbencoder1',ds.env())

    for i,evt in enumerate(ds.events()):
        print usdusbdet.descriptions(), usdusbdet.values(evt)
        print usdusbdet_not_in_data.values(evt), usdusbdet_not_in_data.values(evt)
        if i == 5: break
