# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import copy
import cv2
from PIL import Image, ImageEnhance, ImageFilter, ImageFile
import ast
import multiprocessing
import time
import math

# python2 saveme1.py --image images/color_ref1.png --width 17.9 --desiredwidth 5.8 --spsi 15 --ppmm 8.15642458101
# python2 saveme1.py --image images/image_PSI1.png --width 17.9 --desiredwidth .8 --spsi 8 --margin .05
# python2 saveme1.py --image images/peanut_test.png --width 17.9 --desiredwidth 2.1 --spsi 15 --margin .05

def make_measurements(orig, final_edged, start_x, end_x, start_y, end_y, pixelsPerMetric, num_divisions=13.0):

	measurements = []

	for i in range(1, int(num_divisions)):

		# experimental section start
		start_white_x = int(start_x)
		# middle_y = int((start_y + end_y) / 2.0)
		middle_y = int(start_y + ((end_y - start_y)/(num_divisions / float(i))) )

		# y is rows and x is columns
		while(final_edged[middle_y][start_white_x] == 0 and start_white_x < end_x):
			start_white_x += 1

		end_white_x = int(end_x)

		# print(str(contour_area[42][32])) # white pixel in # python2 mul_proc_measure_psi_cal.py --image images/color_ref1.png --width 17.9 --desiredwidth 5.8 --spsi 15

		# indices = np.where(contour_area == 255) # 255 is white and not 1 fml
		# coordinates = zip(indices[0], indices[1])
		# print(len(coordinates))

		# y is rows and x is columns
		while(final_edged[middle_y][end_white_x] == 0 and end_white_x > start_x):
			end_white_x -= 1

		if (final_edged[middle_y][start_white_x] != 255 and final_edged[middle_y][end_white_x] != 255):
			# orig = orig.copy() # this would ignore all previous measurements if the line is broken
			continue

		# cv2.circle(orig, (int(start_white_x), int(middle_y)), 5, (255, 0, 0), -1)
		# cv2.circle(orig, (int(end_white_x), int(middle_y)), 5, (255, 0, 0), -1)

		dAa = dist.euclidean((start_white_x, middle_y), (end_white_x, middle_y))
		dimAa = dAa / pixelsPerMetric

		measurements.append(dimAa)

		# cv2.line(orig, (int(start_white_x), int(middle_y)), (int(end_white_x), int(middle_y)),
		# 	(255, 0, 255), 2)

		# cv2.putText(orig, "{:.3f}mm".format(dimAa),
		# (int(end_white_x + 15), int(middle_y)), cv2.FONT_HERSHEY_SIMPLEX,
		# 0.65, (0, 0, 0), 2)

	measurements = measurements[2:len(measurements)-2]
	avg_measurements = sum(measurements)/len(measurements)

	# cv2.putText(orig, "Avg: {:.3f}mm".format(avg_measurements),
	# (int(start_x), int(end_y + 15)), cv2.FONT_HERSHEY_SIMPLEX,
	# 0.65, (0, 0, 0), 2)
		# experimental section end

	return avg_measurements

def isWithin(desired, actual, marginoferror=.05):
	lower = desired - (desired*marginoferror)
	upper = desired + (desired*marginoferror)

	if (lower <= actual <= upper):
		return True
	return False

def auto_canny(image, sigma=0.33):
	# compute the median of the single channel pixel intensities
	v = np.median(image)

	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)

	# return the edged image
	return edged


def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)


def process_image((image1, sat, sharp, bright, contra)): # default is original image
##	temp_image = copy.deepcopy(image)

	# print("testing " + str(sat) + " " + str(sharp))

	image = Image.open(image1).convert('RGB')
	width, height = image.size   # Get dimensions
	## these image dimsension are based off points -- I can get these points from edge detection used in offsets
	# temp_image = image.crop((int((2.0*width)/5.0), int(height/5.0), int((9.5*width)/10.0), height)) # (left, top, right, bottom) (0, height/4.0, width, height)

	temp_image = image.crop((2000, int(height/5.0)+650, width-650, height-610)) #HIGH RES CROP
	saturation = ImageEnhance.Color(temp_image)#victor test
	temp_image = saturation.enhance(sat)#victor test

	sharpness = ImageEnhance.Sharpness(temp_image)#victor test
	temp_image = sharpness.enhance(sharp)#victor test

	brightness = ImageEnhance.Brightness(temp_image)
	temp_image = brightness.enhance(bright)

	contrast = ImageEnhance.Contrast(temp_image)
	temp_image = contrast.enhance(contra)

	image = np.array(temp_image) # opens image in RGB
	image = image[:, :, ::-1].copy() # inverse to BGR for opencv format

	# rotate image here 180 degrees if need be
	# grab the dimensions of the image and calculate the center
	# of the image
	(h, w) = image.shape[:2]
	center = (w / 2, h / 2)

	# rotate the image by 180 degrees
	M = cv2.getRotationMatrix2D(center, 180, 1.0)
	image = cv2.warpAffine(image, M, (w, h))

	image = cv2.fastNlMeansDenoisingColored(image,None,2,10,7,21) #victor test

	img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	gray_im = cv2.fastNlMeansDenoising(img, 2, 31, 7) # denosises grey image to get smoother gradients over gray image

	kernel = None
	#HIGH RES CHANGE
	kernel = np.ones((11,11),np.uint8) # if needed or erosion or dilation

	#kernel = np.ones((3,3), np.uint8) # if needed for erosion or dilation
	# dilate = cv2.getStructuringElement(cv2.MORPH_RECT,(7,7))
	# erode = cv2.getStructuringElement(cv2.MORPH_RECT,(9,9))

	thresh1 = cv2.adaptiveThreshold(gray_im,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
				cv2.THRESH_BINARY,11,2)
	thresh2 = cv2.adaptiveThreshold(gray_im,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
				cv2.THRESH_BINARY,11,2)

	thresh = cv2.addWeighted(thresh1,.5,thresh2,.5, 0)

	edge = auto_canny(thresh)
	#HIGH RES
	edge = cv2.dilate(edge, kernel, iterations=2)
	edge = cv2.erode(edge, kernel, iterations=2)
	#edge = cv2.dilate(edge, kernel, iterations=1)
	#edge = cv2.erode(edge, kernel, iterations=1)

	# print("finished " + str(sat) + " " + str(sharp))

	return edge

def main():
	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", required=True,
		help="path to the input image")
	ap.add_argument("-w", "--width", type=float, required=True,
		help="width of the left-most object in the image (in mm)")
	ap.add_argument("-dw", "--desiredwidth", type=float, required=True,
		help="desired width of object (in mm)")
	ap.add_argument("-spsi", "--spsi", type=float, required=True,
		help="starting psi")
	ap.add_argument("-p", "--ppmm", type=float, required=False, default=0,
		help="pixelspermm")
	ap.add_argument("-m","--margin",type=float,required=True,
		help="margin of error")
	args = vars(ap.parse_args())

	#########################################################

	# Theo - I had to add this line to accept the truncated, decoded images
	ImageFile.LOAD_TRUNCATED_IMAGES = True

	image = Image.open(args["image"]).convert('RGB')
	width, height = image.size   # Get dimensions
	## these image dimsension are based off points -- I can get these points from edge detection used in offsets
	image = image.crop((0, int(height/5.0), width, height)) # (left, top, right, bottom) (0, height/4.0, width, height)


	### mul processes start
	data = ( [args["image"], 10, 6, .5, 1], [args["image"], 1, 1, 1, 1], [args["image"], 10, 1, 1, 1])

	p = multiprocessing.Pool(4) # assuming quad core
	edge1, edge2, edge3 = p.map(process_image, data)

	# print("If last print then did wait")

	### mul processes end

	# convert image to cv2 style
	image = np.array(image) # opens image in RGB
	image = image[:, :, ::-1].copy() # inverse to BGR for opencv format

	# rotate image here 180 degrees if need be
	# grab the dimensions of the image and calculate the center
	# of the image
	(h, w) = image.shape[:2]
	center = (w / 2, h / 2)

	# rotate the image by 180 degrees
	M = cv2.getRotationMatrix2D(center, 180, 1.0)
	image = cv2.warpAffine(image, M, (w, h))

	# #########################################################

	final_edged = cv2.addWeighted(edge1,.5,edge2,.5,0)

	ret,final_edged = cv2.threshold(final_edged,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

	final_edged = cv2.addWeighted(final_edged,.5,edge3,.5,0)

	ret,final_edged = cv2.threshold(final_edged,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)


	# find contours in the edge map
	cnts = cv2.findContours(final_edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]

	# sort the contours from left-to-right and initialize the
	# 'pixels per metric' calibration variable
	(cnts, _) = contours.sort_contours(cnts)
	pixelsPerMetric = None

	if (args["ppmm"] != 0):
		pixelsPerMetric = args["ppmm"]

	#victor -- attempt to get 2 largest areas

	reference_obj = None
	filpos = 0
	while reference_obj is None:
		#if cv2.contourArea(cnts[filpos]) > 1000: #counters possible small leftmost objects not the square
		if cv2.contourArea(cnts[filpos]) > 10000: #counters possible small leftmost objects not the square

			reference_obj = copy.deepcopy(cnts[filpos])
			cnts = cnts[:filpos] + cnts[filpos+1:]
			filament = False
		else :
			filpos += 1


	index = 0
	indices = list()
	contour_areas = list()
	for c in cnts:

		#if (cv2.contourArea(c) > 1000):
		if (cv2.contourArea(c) > 10000):
			indices.append(index)
			contour_areas.append(cv2.contourArea(c))

		index += 1

	sorted_cnts_by_areas = [cnts[x] for y, x in zip(contour_areas, indices)]
	sorted_cnts_by_areas.insert(0, reference_obj)

	# sorted_cnts_by_areas = sorted_cnts_by_areas[:2]

	if (pixelsPerMetric == None):
		sorted_cnts_by_areas = [sorted_cnts_by_areas[0], sorted_cnts_by_areas[len(sorted_cnts_by_areas)-1]]
	else:
		sorted_cnts_by_areas = [sorted_cnts_by_areas[len(sorted_cnts_by_areas)-1]]

	desiredwidth = args["desiredwidth"]

	measured_height = 0
	MIN_EXTRUSION_HEIGHT = 7
	# print("num objs: " + str(len(sorted_cnts_by_areas)))
	avg_measurements = 0
	# loop over the contours individually
	for c in sorted_cnts_by_areas:
		# if the contour is not sufficiently large, ignore it
	##	if cv2.contourArea(c) < 500:
	##		continue

		# print("contour area: " + str(cv2.contourArea(c)))

		# compute the rotated bounding box of the contour
		orig = image.copy() # if you want everything to stay just keep this outside the for loop
		c = cv2.convexHull(c) #victor added
		box = cv2.minAreaRect(c)

		# The output of cv2.minAreaRect() is ((x, y), (w, h), angle). Using cv2.cv.BoxPoints() is meant to convert this to points.
		# # (x, y) is center pixel position and w and h go in and outward accordingly encasing the contour
		# #  --- pixel position is relative to both original image and final edged image
		# # x increases going right and decreases going left
		# # y increases going down and decreases going up


	############# Experimental --- unsure if it actually works
		(x, y), (w, h), angle = box

		# print("(x, y), (w, h), angle: " + str(x) + " " + str(y) + " " + str(w) + " " + str(h) + " " + str(angle))

		# angle = 0 #converts angle to 0 rotation so its no longer the minimum bounding box

		if (90 - abs(angle) < abs(angle) - 0):
			angle = 90
		else :
			angle = 0

		box = ((x, y), (w, h), angle)
	#############

		# print(box)

		box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
		box = np.array(box, dtype="int")

		# order the points in the contour such that they appear
		# in top-left, top-right, bottom-right, and bottom-left
		# order, then draw the outline of the rotated bounding
		# box
		box = perspective.order_points(box)

		### using box pts above create the start_x and start_y coordinates


		# cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

		# # loop over the original points and draw them
		# for (x, y) in box:
		# 	cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

		# unpack the ordered bounding box, then compute the midpoint
		# between the top-left and top-right coordinates, followed by
		# the midpoint between bottom-left and bottom-right coordinates
		(tl, tr, br, bl) = box
		(tltrX, tltrY) = midpoint(tl, tr)
		(blbrX, blbrY) = midpoint(bl, br)

		# compute the midpoint between the top-left and top-right points,
		# followed by the midpoint between the top-righ and bottom-right
		(tlblX, tlblY) = midpoint(tl, bl)
		(trbrX, trbrY) = midpoint(tr, br)

		# # draw the midpoints on the image
		# cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
		# cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)

		# # draw lines between the midpoints
		# cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
		# 	(255, 0, 255), 2)

		# compute the Euclidean distance between the midpoints
		dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
		dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

		# print("dA " + str(dA))
		# print("dB " + str(dB))

		# if the pixels per metric has not been initialized, then
		# compute it as the ratio of pixels to supplied metric
		# (in this case, mm)
		if pixelsPerMetric is None:
			pixelsPerMetric = dB / args["width"]
			# print(pixelsPerMetric)
			continue # victor added to ignore reference object and go to last object

		# compute the size of the object
		dimA = dA / pixelsPerMetric
		dimB = dB / pixelsPerMetric # width of object

		measured_height = dimA
		# print("dimA " + str(dimA))
		# print("dimB " + str(dimB))


		# y is rows and x is columns
		# +-10 is to get black border --- this can cause error for overlapping or to close objects
		center_x, center_y = midpoint((tlblX, tlblY),(trbrX, trbrY))
		x_dist = dist.euclidean(tl, tr)
		y_dist = dist.euclidean(tl, bl)
		start_x = int(math.floor(center_x - (x_dist/2.0) - 10))
		end_x = int(math.ceil(center_x + (x_dist/2.0) + 10))
		start_y = int(math.floor(center_y - (y_dist/2.0) - 10))
		end_y = int(math.ceil(center_y + (y_dist/2.0) + 10))

		# print(str(start_x) + " " + str(end_x) + " " + str(start_y) + " " + str(end_y) + " added +- 10 to both ends to create black border")
		contour_area = final_edged[start_y:end_y, start_x:end_x]
		contour_area = np.array(contour_area)
		# cv2.imshow("contour_area", contour_area)
		# cv2.waitKey(0)

		# try:
		avg_measurements = make_measurements(orig, final_edged, start_x, end_x, start_y, end_y, pixelsPerMetric)
		# except Exception as e:
		# 	avg_measurements = 0
		# 	break;

		# print("avg_measurements: " + str(avg_measurements) + " mm")

		# draw the object sizes on the image
		# cv2.putText(orig, "height: {:.3f}mm".format(dimA),
		# 	(int(tltrX - 40), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
		# 	0.65, (0, 0, 0), 2)

		# show the output image

		# cv2.imshow("Object Measurement via Enhanced Image", orig)
		# cv2.waitKey(0)
	marginoferror = args["margin"]
	spsi = args["spsi"]
	# newpsi = (desiredwidth * spsi) / dimB
	if avg_measurements != 0:
		newpsi = (desiredwidth * spsi) / avg_measurements

	is_greater = False # newpsi is greater than spsi?
	if avg_measurements != 0:
		if (newpsi > spsi):
			is_greater = True

		if (abs(newpsi - spsi) > (.17 * spsi) and is_greater): # its not within 1/2 sd of the spsi as mean
			newpsi = spsi + (.17 * spsi) # if newpsi was raised larger than 1sd away cap it
		elif (abs(newpsi - spsi) > (.17 * spsi) and not is_greater):
			newpsi = spsi - (.17 * spsi) # if newpsi was lowered more than 1sd away cap it

	# print(desiredwidth)
	# print(dimB)
	# info = "[" + str(isWithin(desiredwidth, dimB)) + "," + str(newpsi) + "]"

	# when height of last printed extrusion is small
	if measured_height < MIN_EXTRUSION_HEIGHT or avg_measurements == 0:
		print("measured_height: " + str(measured_height) + " MIN_EXTRUSION_HEIGHT: " + str(MIN_EXTRUSION_HEIGHT))
		print("avg_measurements: " + str(avg_measurements))
		info = "[True, 0, 0, 0]"
	else:
		info = "[" + str(isWithin(desiredwidth, avg_measurements)) + "," + str(newpsi) + "," + str(pixelsPerMetric) + "," + str(avg_measurements) +"]"
		#orig: info = "[" + str(isWithin(desiredwidth, avg_measurements, (float(args["margin"])/100)) + "," + str(newpsi) + "," + str(pixelsPerMetric) + "," + str(avg_measurements) +"]"
		# info = "[" + str(isWithin(desiredwidth, avg_measurements)) + "," + str(newpsi) + "," + str(pixelsPerMetric) +"]"
	info = ast.literal_eval(info)
	# print(str(info[0]) + " " + str(info[1]))
	print(info)
	#return info

if __name__ == '__main__':
	# Need this line for multiprocessing to work on windows
	multiprocessing.freeze_support()
	main()
