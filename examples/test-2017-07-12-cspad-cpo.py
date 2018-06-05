from psana import *
ds = DataSource('exp=xpptut15:run=54')
det = Detector('cspad')
evt = ds.events().next()
run = evt.run()
print det.pedestals(run)
