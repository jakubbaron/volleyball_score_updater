# USAGE
# python ocr_template_match.py --image images/credit_card_01.png --reference ocr_a_reference.png

# import the necessary packages
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2

roi_width = 57
roi_height = 88
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image")
ap.add_argument("-r", "--reference", required=True,
	help="path to reference OCR-A image")
args = vars(ap.parse_args())

# load the reference OCR-A image from disk, convert it to grayscale,
# and threshold it, such that the digits appear as *white* on a
# *black* background
# and invert it, such that the digits appear as *white* on a *black*
ref = cv2.imread(args["reference"])
ref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
ref = cv2.threshold(ref, 150, 255, cv2.THRESH_BINARY_INV)[1]

# find contours in the OCR-A image (i.e,. the outlines of the digits)
# sort them from left to right, and initialize a dictionary to map
# digit name to the ROI
refCnts = cv2.findContours(ref.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
refCnts = refCnts[0] #if imutils.is_cv2() else refCnts[1]
refCnts = contours.sort_contours(refCnts, method="left-to-right")[0]
digits = {}

digit_map = {0:0, 1:1, 2:2, 3:4, 4:7, 5:9, 6:1, 7:1, 8:2, 9:4, 10:7,
        11:0, 12:9}


# loop over the OCR-A reference contours
for (i, c) in enumerate(refCnts):
    # compute the bounding box for the digit, extract it, and resize
    # it to a fixed size
    (x, y, w, h) = cv2.boundingRect(c)
    roi = ref[y:y + h, x:x + w]
    roi = cv2.resize(roi, (roi_width, roi_height))
    
    # update the digits dictionary, mapping the digit name to the ROI
    digits[i] = roi

# load the input image, resize it, and convert it to grayscale
filename = args["image"]
image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
orig_image = cv2.imread(filename)
(thresh, im_bw) = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
# cv2.imshow("thresh", im_bw)
# cv2.waitKey(0)
thresh = 143
im_binary = cv2.threshold(im_bw, thresh, 255, cv2.THRESH_BINARY)[1]
# cv2.imshow("thresh", im_binary)
# cv2.waitKey(0)
image = imutils.resize(im_binary, width=300)
orig_image = imutils.resize(orig_image, width=300)
# cv2.imshow("thresh", image)
# cv2.waitKey(0)

thresh = cv2.threshold(image, 0, 255,
	cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
# cv2.imshow("thresh", thresh)
# cv2.waitKey(0)


# # 
# # find contours in the thresholded image, then initialize the
# # list of digit locations
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
       cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
locs = []
# 
# # loop over the contours
for (i, c) in enumerate(cnts):
	# compute the bounding box of the contour, then use the
	# bounding box coordinates to derive the aspect ratio
	(x, y, w, h) = cv2.boundingRect(c)
	ar = w / float(h)
	locs.append((x, y, w, h))

# sort the digit locations from left-to-right, then initialize the
# list of classified digits
locs = sorted(locs, key=lambda x:x[0])
output = []
# 
# loop over the 4 groupings of 4 digits
for (i, (x, y, w, h)) in enumerate(locs):
    # loop over the digit contours
    # compute the bounding box of the individual digit, extract
    # the digit, and resize it to have the same fixed size as
    # the reference OCR-A images
    roi = thresh[y:y + h, x:x + w]
    roi = cv2.resize(roi, (roi_width, roi_height))
    
    # initialize a list of template matching scores	
    scores = []
    
    # loop over the reference digit name and digit ROI
    for (digit, digitROI) in digits.items():
    	# apply correlation-based template matching, take the
    	# score, and update the scores list
    	result = cv2.matchTemplate(roi, digitROI,
    		cv2.TM_CCOEFF)
    	(_, score, _, _) = cv2.minMaxLoc(result)
    	scores.append(score)
    print(scores)
    
    # the classification for the digit ROI will be the reference
    # digit name with the *largest* template matching score
    score = np.argmax(scores)
    if np.max(scores) < 36000000.0:
        continue
    d = digit_map[score]
    output.append(str(d))
    
    # draw the digit classifications around the group
    cv2.rectangle(orig_image, (x - 5, y - 5),
    	(x + w + 5, y + h + 5), (0, 0, 255), 2)
    cv2.putText(orig_image, str(d), (x, y - 15),
    	cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
 
# display the output credit card information to the screen
print(output)
print("Read Numbers: {}".format("".join(output)))
cv2.imshow("Image", orig_image)
cv2.waitKey(0)
