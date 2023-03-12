# This script processes the generated dataset by resizing the images to a 
# standard size, converting them to grayscale, and saving them in the 

import cv2
import numpy as np

# Load image, convert to grayscale, normalize, and apply augmentation
img = cv2.imread('image.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray_norm = np.divide(gray, 255)

# Apply rotation
rows, cols = gray_norm.shape
M = cv2.getRotationMatrix2D((cols/2, rows/2), 10, 1)
rotated = cv2.warpAffine(gray_norm, M, (cols, rows))

# Apply flipping
flipped = cv2.flip(gray_norm, 1)

# Apply blurring
blurred = cv2.GaussianBlur(gray_norm, (5, 5), 0)
