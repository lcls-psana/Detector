from __future__ import print_function
import psana

#src, dsn = 'CxiDs2.0:Cspad.0', '/reg/g/psdm/detector/data_test/types/0003-CxiDs2.0-Cspad.0-fiber-data.xtc'
#src, dsn = ':Cspad2x2.1', '/reg/g/psdm/detector/data_test/types/0004-MecTargetChamber.0-Cspad2x2.1.xtc'
#src, dsn = ':pnCCD.0', '/reg/g/psdm/detector/data_test/types/0010-Camp.0-pnCCD.0.xtc'
#src, dsn = ':Princeton.0', '/reg/g/psdm/detector/data_test/types/0015-Princeton_FrameV2.xtc'
#src, dsn = ':Epix100a.0', '/reg/g/psdm/detector/data_test/types/0007-NoDetector.0-Epix100a.0.xtc'
src, dsn = ':Fccd.0',     '/reg/g/psdm/detector/data_test/types/0015-SxrEndstation.0-Fccd.0.xtc'
#src, dsn = ':OrcaFl40.0', '/reg/g/psdm/detector/data_test/types/0015-Orca_ConfigV1.xtc'
#src, dsn = ':Tm6740.0',   '/reg/g/psdm/detector/data_test/types/0015-Pulnix_TM6740ConfigV2.xtc'
#src, dsn = ':Timepix.0',  '/reg/g/psdm/detector/data_test/types/0015-Timepix-ConfigV3.xtc'
#src, dsn = ':Pimax.0',    '/reg/g/psdm/detector/data_test/types/0015-Pimax_FrameV1.xtc'
#src, dsn = ':Fli.0',      '/reg/g/psdm/detector/data_test/types/0015-Fli_ConfigV1.xtc'
#src, dsn = ':Opal8000.1', '/reg/g/psdm/detector/data_test/types/0015-Opal8000_FrameV1.xtc'

#src, dsn = ':Imp.1',      '/reg/g/psdm/detector/data_test/types/0015-Imp_ConfigV1.xtc'

print('src=%s, dsname=%s' % (src, dsn))

src = psana.Source(src)
ds  = psana.DataSource(dsn)
env = ds.env()

evt = ds.events().next()

#pda = PyDetectorAccess(src, env, pbits=0)
cfg = env.configStore()

#co = cfg.get(psana.CsPad2x2.ConfigV2, src)
#co = cfg.get(psana.PNCCD.ConfigV2, src)
#co = cfg.get(psana.Princeton.ConfigV5, src)    # (1300, 1340)
#co = cfg.get(psana.Epix.Config100aV1, src)     # (704, 768)
co = cfg.get(psana.FCCD.FccdConfigV2, src)     # (500, 1152)
#co = cfg.get(psana.Orca.ConfigV1, src)         # (2048, 2048)
#co = cfg.get(psana.Pulnix.TM6740ConfigV2, src) # (480, 640)
#co = cfg.get(psana.Quartz.ConfigV2, src)       # (2048, 2048)
#co = cfg.get(psana.Timepix.ConfigV3, src)      # no shape in cfg
#do = evt.get(psana.Timepix.DataV2, src)        # (512, 512)
#co = cfg.get(psana.Pimax.ConfigV1, src)        # (1024, 1024)
#co = cfg.get(psana.Fli.ConfigV1, src)          # (4096, 4096)
#co = cfg.get(psana.Opal1k.ConfigV1, src)       # (1024, 1024)

# Waveform detector
#co = cfg.get(psana.Imp.ConfigV1, src)          # no shape in cfg
#co = evt.get(psana.Imp.ElementV1, src)         # 

#co.Row_Pixels
#co.Column_Pixels
#co.width()
#co.height()

print('Config object:', co)
