#!/usr/bin/env python

"""2020-01-10 Drawing from Rebecca LCL5004-007815
   Jungfrau4M segment upper-left corner coordinates


   - ??? Numeration of segments from Philip
   - ??? Location of the 1-st pixel is unknown
   - units - INCH
"""

# in inch
ul_corners_inch = [
  [-3.003, 3.261],
  [-1.379, 3.261],
  [ 0.245, 2.864],
  [ 1.869, 2.864],
  [-3.402, 0.193],
  [-1.778, 0.193],
  [-0.154,-0.204],
  [ 1.47, -0.204]]

half_s = (3.003 - 1.470)/2
half_l = (3.261 - 0.204)/2

IN_TO_UM = 25.4*1000

print('panel long  side: %6.3f mm' % (half_l*2*25.4))
print('panel short side: %6.3f mm' % (half_s*2*25.4))

print('\nJungfrau4M panel centers in inch')
print('panel X[inch] Y[inch]')
for i,c in enumerate(ul_corners_inch) :
    print('%d    %6.3f  %6.3f' % (i, c[0]+half_s, c[1]-half_l))

print('\nJungfrau4M panel centers in um')
print('panel X[um]      Y[um]')
for i,c in enumerate(ul_corners_inch) :
    print('%d    %10.3f %10.3f' % (i, (c[0]+half_s)*IN_TO_UM, (c[1]-half_l)*IN_TO_UM))
