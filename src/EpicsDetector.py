
import _psana



class EpicsDetector(object):

    def __init__(self, pv_string, env):
        """
        Parameters
        ----------
        pv_string : str
            The string or alias

        env : psana.Env
            The event, for example from psana.DataSource.env()
        """
        self._pv_string = pv_string
        self._epics = env.epicsStore()
        return


    def __call__(self, evt=None):
        """
        Returns the value of the EPICS PV for the current event. Note
        that the argument evt is actually not required (!), and that
        the value you get returned will be for the *most recently
        accessed* event.
        """
        pv = self._epics.getPV(self._pv_string)
        if pv.numElements() > 1:
            return pv.data() # *always* returns an np.array
        elif pv.numElements() == 1:
            return pv.value(0) # returns int/float
        

