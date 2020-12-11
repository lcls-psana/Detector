import numpy as np

arr = (\
 0,   0,   0,\
10,   0,   8,\
20,   0,  17,\
30,   0,  12,\
39,   0,   2,\
0,    9,  20,\
10,   9,  30,\
20,   9,  39,\
30,   9,  27,\
39,   9,  15,\
0,   18,  18,\
10,  18,  32,\
20,  18,  54,\
30,  18,  42,\
39,  18,  28,\
0,   27,  19,\
10,  27,  45,\
20,  27,  59,\
30,  27,  52,\
39,  27,  45,\
0,   36,  34,\
10,  36,  48,\
20,  36,  62,\
30,  36,  59,\
39,  36,  56)

xyz = np.array(arr)
xyz.shape = (25,3)
print 'xyz\n', xyz

sh=(5,5)
x=xyz[:,0]; x.shape = sh
y=xyz[:,1]; y.shape = sh
z=xyz[:,2]; z.shape = sh



# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm

#plt.plot(x,z)
#plt.show()

#plt.plot(y,z)
#plt.show()

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_xlabel('X, mm')
ax.set_ylabel('Y, mm')
ax.set_zlabel(u'Z, \u03BCm')
#cmap=cm.coolwarm
surf = ax.plot_surface(x, y, z, cmap=cm.inferno,
                       linewidth=0, antialiased=False)
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()
