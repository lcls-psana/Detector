"""
Philip Hart <philiph@slac.stanford.edu>
2018-09-16, 5:18 PM
Hi, I'm trying to run on detdaq17 run 99.  I was able to run calibman on
run 98, but my code seg faults when I ask for raw(evt).  It also dies on
old data I used to be able to analyze, e.g. run 84.  Could you check,
please?

Thanks,
Philip
"""
from psana import DataSource, Detector
from Detector.GlobalUtils import print_ndarr

ds = DataSource('exp=detdaq17:run=99')
det = Detector('DetLab.0:Epix10ka.0') # 'epix10ka'

for i,evt in enumerate(ds.events()) :
   raw = det.raw(evt) 
   print_ndarr(raw, '%03d raw' % i)
