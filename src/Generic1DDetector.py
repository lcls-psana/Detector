
"""
Detector interface for the Generic1D type
=========================================
"""

from DdlDetector import DdlDetector


class Generic1DDetector(DdlDetector):
    """
    """

    def __init__(self, *args):

        super(Generic1DDetector, self).__init__(*args)

        cfgs = self._fetch_configs()
        if len(cfgs) == 1:
            self._g1d_cfg = cfgs[0]
        elif len(cfgs) > 1:
            raise RuntimeError('Multiple or no configuration objects found '
                               '(%d) for Generic1D device! DAQ misconfigured.'
                               '' % len(cfgs))

        self.type_index = [ 'data_u8',
                            'data_u16',
                            'data_u32',
                            'data_f32',
                            'data_f64' ]

        return


    def __call__(self, evt):
        """

        Parameters
        ----------
        evt: a psana event object

        Returns
        -------
        A list of of 1D arrays associated with the input event
        """

        ddls = self._fetch_ddls(evt)

        if len(ddls) == 1:
            ddl_g1d = ddls[0]

            channels = []
            channel_types = self._g1d_cfg.SampleType()
            for c in range(self._g1d_cfg.NChannels()):

                # c             : channel index (int)
                # channel_types : int describing getter method
                # type_index    : string describing getter method

                method_name = self.type_index[ channel_types[c] ]
                channels.append( getattr(ddl_g1d, method_name)(c) )

        else:
            channels = None 

        return channels

    


if __name__ == '__main__':

    import psana

    ds = psana.DataSource('exp=mfxc0116:run=66')
    
    g1ddet = Generic1DDetector('DetInfo(MfxEndstation.0:Wave8.0)', ds.env())

    for evt in ds.events():
        print g1ddet(evt)
        break
