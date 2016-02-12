
import _psana


class ControlDataDetector(object):

    def __init__(self, source_string, env):
        """
        Parameters
        ----------
        env : psana.Env
            The event, for example from psana.DataSource.env()
        """

        self._config_store = env.configStore()

        for k in self._config_store.keys():
            if 'ControlData.Config' in str(k.type()):
                self._type = k.type()
                self._source = k.src() #psana.Source('ProcInfo()')

        return


    def __call__(self, evt=None):
        """
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



