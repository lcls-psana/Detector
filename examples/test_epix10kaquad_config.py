import psana

def print_object_dir(o) :
    print 'dir(%s):\n  %s' % (str(o), ',\n  '.join([v for v in dir(o) if v[:1]!='_']))

src = psana.Source('NoDetector.0:Epix10kaQuad.0')
ds  = psana.DataSource('/reg/g/psdm/detector/data_test/types/0032-NoDetector.0-Epix10kaQuad.0.xtc')
co = ds.env().configStore().get(psana.Epix.Config10kaQuadV1, src)

print_object_dir(co)

e0co = co.elemCfg(0)
print_object_dir(e0co)

evr = co.evr()
print_object_dir(evr)

a0co = e0co.asics(0)
print_object_dir(a0co)

print 'e0co.carrierId0():', e0co.carrierId0()
print 'e0co.carrierId1():', e0co.carrierId1()
print 'a0co.chipID()    :', a0co.chipID()
