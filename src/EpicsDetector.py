



class EpicsDetector(object):
    """
    This class is used to access data that is typically acquired
    at a rate slower than the LCLS shot rate (e.g. temperatures,
    voltages) using the EPICS slow-control system.
    """

    def __init__(self, pv_string, env):
        """
        Parameters
        ----------
        pv_string : str
            The full-name or alias of an EPICS variable

        env : psana.Env
            The psana environment, for example from psana.DataSource.env()
        """
        self._pv_string = pv_string
        self._epics = env.epicsStore()
        return


    def __call__(self, evt=None):
        """
        Parameters
        ----------
        evt: a psana event object

        Returns
        -------
        The value of the EPICS variable for the current event. Note
        that the argument evt is actually not required, and that
        the value you get returned will be for the *most recently
        accessed* event.
        """
        pv = self._epics.getPV(self._pv_string)
        if pv.numElements() > 1:
            return pv.data() # *always* returns an np.array
        elif pv.numElements() == 1:
            return pv.value(0) # returns int/float
        


if __name__ == '__main__':
    import psana
    ds = psana.DataSource('exp=xpptut15:run=59')
    det = psana.Detector('XPP:LAS:MMN:01.RBV')
    print det(ds.events().next())
 

