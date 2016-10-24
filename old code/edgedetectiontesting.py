# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 16:51:20 2016

@author: Colin
"""

import os
from PIL import Image, ImageOps
import numpy as np
from scipy import ndimage, misc

def histeq(im,nbr_bins=256):
    """ Histogram equalization of a grayscale image. """
    # get image histogram
    imhist,bins = np.histogram(im.flatten(),nbr_bins,normed=True)
    cdf = imhist.cumsum() # cumulative distribution function
    cdf = 255 * cdf / cdf[-1] # normalize
    # use linear interpolation of cdf to find new pixel values
    im2 = np.interp(im.flatten(),bins[:-1],cdf)
    return im2.reshape(im.shape), cdf

try:
    os.remove('test1.png')
    os.remove('test2.png')
    os.remove('test3.png')
except:
    print('lol')

x = Image.open('Bimage.png', 'r')

y = np.asarray(x.getdata(), dtype=np.float64).reshape((x.size[1], x.size[0]))


imx = np.zeros(y.shape)
imy = np.zeros(y.shape)
sigma = 1
ndimage.filters.gaussian_filter(y, (sigma,sigma), (0,2), imx)


misc.imsave('test1.png', imx)

ndimage.filters.gaussian_filter(y, (sigma,sigma), (2,0), imy)

misc.imsave('test2.png', imy)

jkfd = (imx+imy)/2

jkfd,cdf = histeq(jkfd)

misc.imsave('test3.png', jkfd)