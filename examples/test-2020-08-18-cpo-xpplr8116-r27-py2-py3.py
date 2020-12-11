
# event_keys -d exp=xpplr8116:run=27 -m3
#EventKey(type=psana.Epix.ElementV3, src='DetInfo(XppGon.0:Epix100a.1)', alias='epix')
#EventKey(type=psana.Epix.Config100aV2, src='DetInfo(XppGon.0:Epix100a.1)', alias='epix')

import psana
ds  = psana.DataSource('exp=xpplr8116:run=27:smd')
det = psana.Detector('epix')
evt = next(ds.events())
print(det.image(evt).shape)
