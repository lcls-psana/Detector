
import _psana


class ControlDataDetector(object):
    """
    An object that can be used to query the names/states of
    motors used in a DAQ scan.  See PSDM confluence building-block
    examples documentation.  Create this object with Detector('ControlData').
    """

    def __init__(self, source_string, env):
        """
        Parameters
        ----------
        source_string:
            User must pass string 'ControlData' to the Detector constructor
        env : psana.Env
            The environment, for example from psana.DataSource.env()
        """

        self._config_store = env.configStore()

        for k in self._config_store.keys():
            if 'ControlData.Config' in str(k.type()):
                self._type = k.type()
                self._source = k.src() #psana.Source('ProcInfo()')

        return


    def __call__(self, evt=None):
        """
        Parameters
        ----------
        evt: an (optional) psana Event object.  It is unused in
             this routine, but provided to make the interface
             similar to other

        Returns
        -------
        An object that can be used to query the names/states of
        motors used in a DAQ scan.  See PSDM confluence building-block
        examples documentation.
        """
        return self._config_store.get(self._type, self._source)


if __name__ == '__main__':
    import psana
    ds = psana.DataSource('exp=xppk3815:run=100:idx')
    cdd = ControlDataDetector('', ds.env())

    run = ds.runs().next()
    nsteps = run.nsteps()
    for step in range(nsteps):
        times = run.times(step)
        for t in times[:2]:
            evt = run.event(t)
            print t, cdd().pvControls()[0].value()

    print 'done'



