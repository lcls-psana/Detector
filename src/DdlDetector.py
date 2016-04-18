
import _psana


def source_is_same(source1, source2):
   """
   Compares strings
   """
   if str(source1) in str(source2):
       return True
   elif str(source2) in str(source1):
       return True
   elif source1 == source2:
       return True
   else:
       return False
   


class DdlDetector(object):
    """
    This class is a generic wrapper for the DAQ system data
    types.  It looks through the event keys for the object that
    have the user-specified psana source string.  If there is more
    than one, an exception is thrown.

    DDL stands for "Data Definition Language" which is a language
    that was written for LCLS to express the DAQ data objects in
    a language-independent way (i.e. for both python/C++).
    """
    def __init__(self, source, env=None):
        """
        Parameters
        ----------
        source : str
            A psana source string (not a psana.Source object), e.g.
            'DetInfo(CxiDsd.0:Cspad.0)', 'BldInfo(FEEGasDetEnergy)',
            or an alias e.g. 'cspad'.
        """
        self.source = source
        self.env = env
        return


    def _find_types(self, evt):

        psana_types = []
        for k in evt.keys():
            if source_is_same(self.source, k.src()):
                if k.type() is not None:
                    psana_types.append( k.type() )

        return psana_types


    def _fetch_ddls(self, evt):

        types = self._find_types(evt)
        ddls = []
        for tp in types:
            ddl = evt.get(tp, _psana.Source(self.source))
            ddls.append(ddl)

        return ddls


    def _fetch_configs(self):
        """
        Get the config store object pertaining to this Source.
        """

        cs = self.env.configStore()
        types = self._find_types(cs)

        configs = []
        for tp in types:
            config = cs.get(tp, _psana.Source(self.source))
            configs.append(config)

        return configs


    def get(self, evt):
        """
        Default behavior for detectors who's special Detector class has not
        been implemented. 

        Parameters
        ----------
        evt: a psana event object

        Returns
        -------
        DAQ object associated with this event
        """
        ddls = self._fetch_ddls(evt)
        if len(ddls) == 1:
            return ddls[0]
        elif len(ddls) == 0:
            return None
        else:
            raise RuntimeError('Multiple types (%d) found in event for this'
                               ' Detector: %s' % (len(ddls), str(ddls)))


