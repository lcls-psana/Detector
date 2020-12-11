
import numpy as np
import matplotlib.pyplot as plt

if False:
    a = ((1,2,3),(4,5,6))

    nda = np.array(a)

    print 'array:\n',a
    print 'np.array:\n',nda

    plt.imshow(nda)
    plt.colorbar()
    plt.show()

    img = np.load('img-ev100.npy')

    plt.imshow(img,vmin=-5,vmax=5)
    plt.colorbar()
    plt.show()


if False:
    gfname = '/reg/neh/home/dubrovin/epix10ka2m.1-2020-02-25-metrology/2020-02-25-geometry-epix10ka2m.1-v1-z0-center0.txt'
    from PSCalib.GeometryAccess import GeometryAccess
    o = GeometryAccess(gfname, 0o377)
    X, Y, Z = o.get_pixel_coords(cframe=1)
    sh = (16, 352, 384)
    X.shape = sh
    Y.shape = sh


import psana

from Detector.GlobalUtils import print_ndarr #, info_ndarr, divide_protected

ds  = psana.DataSource('exp=mfxp17318:run=16')
#env = ds.env()
evt = ds.events().next()

det = psana.Detector('MfxEndstation.0:Epix10ka2M.0')
#runnum = 16
X, Y, Z = det.coords_xyz(evt, cframe=1)

print_ndarr(X,'X')
print_ndarr(Y,'Y')
print_ndarr(Z,'Z')

w=100
w2=w*2
amarker = np.arange(w*w)*10
print_ndarr(amarker,'amarker')

amarker.shape = (w,w)
X[0,w:w2,w:w2] = amarker
Y[0,w:w2,w:w2] = amarker
Z[0,w:w2,w:w2] = amarker

if False:

    for i, evt in enumerate(ds.events()):

        print '%s\nEvent %4d' % (50*'_', i)

        if i<0: continue
        if i>=1: break

        raw = det.raw(evt)
        print_ndarr(raw,'raw')

if True:
        imgX = det.image(evt,X)
        imgY = det.image(evt,Y)
        print_ndarr(imgX,'img X')
        print_ndarr(imgY,'img Y')

        fig = plt.figure(figsize=(10,5))#, title='img x and y', dpi=80, facecolor='w', edgecolor='w', frameon=True, move=(800,0))
        fig.canvas.set_window_title('img x and y')
        #plt.imshow(imgX)
        #plt.colorbar()

        ax1 = fig.add_subplot(1, 2, 1)
        ax1.set_title('pixel X (LAB) coordinate on psana-frame image')
        #ax1.set_title('pixel X (matrix) coordinate')
        imsh1 = ax1.imshow(imgX)
        #axcb1 = fig.add_subplot(1, 40, 40)
        #cb1 = fig.colorbar(imsh1, cax=axcb1)

        ax2 = fig.add_subplot(1, 2, 2)
        ax2.set_title('pixel Y (LAB) coordinate on psana-frame image')
        imsh2 = ax2.imshow(imgY)
        axcb2 = fig.add_axes((0.905, 0.145, 0.02, 0.70))
        cb2 = fig.colorbar(imsh2, cax=axcb2, orientation='vertical')
        #plt.colorbar()
         
        plt.show()
 
