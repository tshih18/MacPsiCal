import cv2
import imutils
import numpy as np
import scipy.misc

# check difference of 2 images
image1 = cv2.imread('image_PSI1.png')
image2 = cv2.imread('image_decode.png')

diff = np.subtract(image1, image2)

#image_result = open('image_diff.png', 'wb')
#image_result.write(diff)

scipy.misc.imsave('image_diff.png', diff)
