
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
        return


    def _find_types(self, evt):

        psana_types = []
        for k in evt.keys():
            if source_is_same(self.source, k.src()):
                psana_types.append( k.type() )

        return psana_types


    def _fetch_ddls(self, evt):

        types = self._find_types(evt)
        ddls = []
        for tp in types:
            ddl = evt.get(tp, _psana.Source(self.source))
            ddls.append(ddl)

        return ddls


    def __call__(self, evt):
        """
        Default behavior for detectors who's special Detector class has not
        yet been implemented. Return DDL base class for the Detector.

        Should be overridden by subclasses. Override required when Detector
        may have multiple types in the same event.
        """
        ddls = self._fetch_ddls(evt)
        if len(ddls) == 1:
            return ddls[0]
        else:
            return None
