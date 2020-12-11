from psana import *
from pyimgalgos.RadialBkgd import RadialBkgd, polarization_factor
import h5py
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from Detector.GlobalUtils import print_ndarr

def rebin(arr, new_shape):
    shape = (new_shape[0], arr.shape[0] // new_shape[0], new_shape[1], arr.shape[1] // new_shape[1])
    return arr.reshape(shape).mean(-1).mean(1)

ds = DataSource('exp=mfxlv1218:run=405:smd')
det = Detector('epix10k2M')
#det.set_print_bits(0o377)
evt = ds.events().next()

userMask = np.load('/reg/d/psdm/mfx/mfxlv1218/scratch/yoon82/psocake/r0314/mask.npy')
print_ndarr(userMask,'userMask')

for nevent, evt in enumerate(ds.events()):
    if nevent > 2: break
    psanaMask = det.mask(evt, calib=True, status=True, edges=True, central=True, unbond=True, unbondnbrs=True)
    mask = userMask * psanaMask
    mask = mask.astype(np.bool)

    raw = det.raw(evt)
    if raw is None:
        print('Event %d WARNING det.raw is None' % nevent)
        continue

    print_ndarr(raw,'Event %d raw' % nevent)
    print_ndarr(psanaMask,'psanaMask')
    
    calib = det.calib(evt)
    if calib is None:
        print('Event %d WARNING det.calib is None' % nevent)
        continue

    calib_masked = calib * mask
    print("calib_masked.shape =", calib_masked.shape) # unassembled image shape = (16, 352, 384)
    print("np.sum(calib_masked) =", np.sum(calib_masked))
    img = det.image(evt,calib_masked)
    print("img.shape =", img.shape) # assembled image shape = (1662, 1663)
    print("np.sum(img) =", np.sum(img))
    #plt.imshow(img)
    xarr, yarr, zarr = det.coords_xyz(evt)  # get the pixel position
    detDist = np.mean(zarr) # detector distance in um
    rb = RadialBkgd(xarr, yarr, mask, nradbins=500, nphibins=1)
    pf = polarization_factor(rb.pixel_rad(), rb.pixel_phi()+90, detDist) # updatePolarizationFactor in psocake (polarization factor for vertically polarized beam (from run18 onwards))

    print_ndarr(calib,'calib')
    print_ndarr(pf,   'pf')
    print_ndarr(mask, 'mask')

    nda = rb.subtract_bkgd(calib.ravel() * pf) * mask.ravel() #flatten()
    print("nda.shape =", nda.shape)
    
    ##### downsample and resample unassembled images to original shapes then assemble #####
    binr = 3
    binc = 3
    calib_masked_binned = np.zeros((calib_masked.shape[0],calib_masked.shape[1]/binr,calib_masked.shape[2]/binc))
    img_binned = None
    img_upsampled = np.zeros_like(calib_masked)
    #for i in range(calib_masked.shape[0]):
    #    calib_masked_binned[i] = rebin(calib_masked[i], np.array([calib_masked.shape[1]/binr,calib_masked.shape[2]/binc]))
    #    img_upsampled[i] = calib_masked_binned[i].repeat(binr, axis=0).repeat(binc, axis=1)

    print("img_upsampled.shape =", img_upsampled.shape)
    print("np.sum(img_upsampled) =", np.sum(img_upsampled))
    img_binned = det.image(evt,img_upsampled)
    print("img_binned.shape =", img_binned.shape)
    plt.imshow(img_binned)
    plt.colorbar()
    plt.show()
