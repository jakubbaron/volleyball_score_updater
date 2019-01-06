import argparse
#import imutils
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
args = vars(ap.parse_args())
filename=args['image']
im_gray = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
(thresh, im_bw) = cv2.threshold(im_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
thresh = 143
im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY_INV)[1]
cv2.imwrite(filename + '_bw_image.png', im_bw)
