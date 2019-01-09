# USAGE
# python3 src/ocr_template_match.py --image samples/2.JPG --reference_dir references

# import the necessary packages
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import os
import sys

roi_width = 57
roi_height = 88

class Image:
    def __init__(self, filepath):
        self.image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        self.orig_image = cv2.imread(filepath)
        (self.thresh, self.im_bw) = cv2.threshold(self.image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # cv2.imshow("thresh", im_bw)
        # cv2.waitKey(0)
        self.thresh = 143
        self.im_binary = cv2.threshold(self.im_bw, self.thresh, 255, cv2.THRESH_BINARY)[1]
        self.image = self.resize(self.im_binary)
        self.orig_image = self.resize(self.orig_image)
        self.thresh = cv2.threshold(self.image, 0, 255,
        	cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # # find contours in the thresholded image, then initialize the
        # # list of digit locations
        cnts = cv2.findContours(self.thresh.copy(), cv2.RETR_EXTERNAL,
               cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        self.locs = []
        # 
        # # loop over the contours
        for (i, c) in enumerate(cnts):
        	# compute the bounding box of the contour, then use the
        	# bounding box coordinates to derive the aspect ratio
        	(x, y, w, h) = cv2.boundingRect(c)
        	self.locs.append((x, y, w, h))
        
        # sort the digit locations from left-to-right, then initialize the
        # list of classified digits
        self.locs = sorted(self.locs, key=lambda x:x[0])

    def resize(self, img, desired_width=300):
        return imutils.resize(img, width=desired_width)

    def draw_on_original(self, x, y, w, h, d):
        # draw the digit classifications around the group
        cv2.rectangle(self.orig_image, (x - 5, y - 5),
    	    (x + w + 5, y + h + 5), (0, 0, 255), 2)
        cv2.putText(self.orig_image, str(d), (x, y - 15),
    	    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)



class DigitTemplate:
    def __init__(self, filepath, digit):
        self.filepath = filepath
        self.digit = digit

        self.ref = cv2.imread(self.filepath)
        self.ref = cv2.cvtColor(self.ref, cv2.COLOR_BGR2GRAY)
        self.ref = cv2.threshold(self.ref, 150, 255, cv2.THRESH_BINARY_INV)[1]

        self.refCnts = cv2.findContours(self.ref.copy(), cv2.RETR_EXTERNAL,
        	        cv2.CHAIN_APPROX_SIMPLE)
        self.refCnts = self.refCnts[0]
        self.refCnts = contours.sort_contours(self.refCnts, method="left-to-right")[0]
        self.templates= {}
        # loop over the OCR-A reference contours
        for (i, c) in enumerate(self.refCnts):
            # compute the bounding box for the digit, extract it, and resize
            # it to a fixed size
            (x, y, w, h) = cv2.boundingRect(c)
            roi = self.ref[y:y + h, x:x + w]
            roi = cv2.resize(roi, (roi_width, roi_height))
            
            # update the references dictionary/ TODO should be prob just
            # changed to and array
            self.templates[i] = roi

    def compare_against_roi(self, roi):
        # initialize a list of template matching scores	
        self.scores = []
        # loop over the reference digit name and digit ROI
        for (which, template) in self.templates.items():
        	# apply correlation-based template matching, take the
        	# score, and update the scores list
        	result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF)
        	(_, score, _, _) = cv2.minMaxLoc(result)
        	self.scores.append(score)
        
    def get_scores(self):
        return self.scores
    def get_best_score(self):
        return np.max(self.get_scores())
    def get_avg(self):
        return np.avg(self.get_scores())

def init_digit_references(args):
    digits = {}
    
    for digit in range(0,10):
        filepath = args["reference_dir"] + "/" + str(digit) + "." + args["extension"]
        if not os.path.isfile(filepath):
            continue
        digits[digit] = DigitTemplate(filepath, digit)
    return digits

def match_digits_with_img(digits, img):
    output = []
    for (i, (x, y, w, h)) in enumerate(img.locs):
        # loop over the digit contours
        # resize it to have the same fixed size as
        # the reference OCR-A images
        roi = img.thresh[y:y + h, x:x + w]
        roi = cv2.resize(roi, (roi_width, roi_height))
        
        # initialize a list of template matching scores	
        scores_dict = {}
        
        # loop over the reference digit name and digit ROI
        for (digit, digit_obj) in digits.items():
        	# apply correlation-based template matching, take the
        	# score, and update the scores list
            digit_obj.compare_against_roi(roi)
            scores_dict[digit] = digit_obj.get_best_score()
        digit = max(scores_dict, key=scores_dict.get)
        # the classification for the digit ROI will be the reference
        # digit name with the *largest* template matching score
        if scores_dict[digit] < 36000000.0:
            continue
        output.append(str(digit))
        
        # draw the digit classifications around the group
        img.draw_on_original(x, y, w, h, digit)
    return output
     


def main():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
    	help="path to input image")
    ap.add_argument("-r", "--reference_dir", required=True,
    	help="path to reference dir with images per each digit (0-9)")
    ap.add_argument("-e", "--extension", required=False, default="PNG",
            help="Extension of the file referneces")
    args = vars(ap.parse_args())
    
    digits = init_digit_references(args)
    # load the input image
    img = Image(args["image"])
    
    output = match_digits_with_img(digits, img)

    # display the output of the volleyball score board
    print("Read Numbers: {}".format("".join(output)))
    cv2.imshow("Image", img.orig_image)
    cv2.waitKey(0)

if __name__ == "__main__":
    main()

