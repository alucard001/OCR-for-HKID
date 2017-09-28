from imutils import contours
import numpy as np
import argparse
import imutils
import cv2

# http://docs.python-requests.org/en/master/user/quickstart/
import requests, json
import base64

# try:
#     import Image
# except ImportError:
# 	from PIL import Image, ImageDraw

# import pytesseract

# Google API key for Vision cloud
with open('google_key.txt') as f:
	KEY = f.read();f.closed

GOOGLE_VISION_API = "https://vision.googleapis.com/v1/images:annotate?key=" + KEY

# Parse arguments
ap = argparse.ArgumentParser()
ap.add_argument('-i', "--image", required=True, help="Path to the image")
ap.add_argument('-d', "--debug", required=False, help="Determine if showing debug message or not, default to not show",
				action="store_true")
args = vars(ap.parse_args())

# Determine if show debug mesage or not
show_debug = True if args['debug'] else False

# https://www.pyimagesearch.com/2015/04/20/sorting-contours-using-python-and-opencv/
def sort_contours(cnts, method="left-to-right"):
	# initialize the reverse flag and sort index
	reverse = False
	i = 0

	# handle if we need to sort in reverse
	if method == "right-to-left" or method == "bottom-to-top":
		reverse = True

	# handle if we are sorting against the y-coordinate rather than
	# the x-coordinate of the bounding box
	if method == "top-to-bottom" or method == "bottom-to-top":
		i = 1

	# construct the list of bounding boxes and sort them from top to
	# bottom
	boundingBoxes = [cv2.boundingRect(c) for c in cnts]
	(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
		key=lambda b:b[1][i], reverse=reverse))

	# return the list of sorted contours and bounding boxes
	return (cnts, boundingBoxes)

print("OpenCV Version: ", cv2.__version__) if show_debug else ''

# Read the image and convert it to a numpy array
img = cv2.imread(args['image'])

# Define the width and height of a rectangle box for image scanning
rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (12, 3))

# Resize image to 600px width
img = imutils.resize(img, width=600)
full_height, full_width, channels = img.shape

print("height: ", full_height, "width: ", full_width, "channels: ", channels) if show_debug else ''

# Turn to gray scale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow("gray", gray) if show_debug else ''

# Apply threshold, value lower than 120 is not black, value bigger than/equal to 255 is black
T, threshold = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
cv2.imshow("Threshold", threshold) if show_debug else ''
print("T: ", T) if show_debug else ''

# Erode the text to bigger black area using the rectangle kernal above
threshold = cv2.erode(src=threshold, kernel=rectKernel, iterations=2)
cv2.imshow('Threshold(Erode)', threshold) if show_debug else ''

# Find contours of the image
_, cnts, _ = cv2.findContours(threshold.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Sort contours from top to bottom
(cnts, boundingBoxes) = sort_contours(cnts, method='top-to-bottom')

# Find sum of all contour areas
total_eligible_area = 0
for i, c in enumerate(cnts):
	(x, y, w, h) = cv2.boundingRect(c)
	total_eligible_area += (float(w) * h)

# Loop throught all the contoures
allRequests = []
for i, c in enumerate(cnts):

	# Draw the bounding rectangle
	(x, y, w, h) = cv2.boundingRect(c)

	# Calculate the ratio and area of the contours
	aspect_ratio = w / float(h)
	contour_area = w * float(h)

	# Use 2.5 because we need to cater for Gender box
	# 0.004 is an arbitrary

	# What is full_height/20 and full_height * 0.8?
	# I don't want to capture the heading of HKID, so the first 1/20 will not be use, that's why I only start from full_height/20

	# Same situation for (full_height * 0.8), as far as my colleague concern, Google will save the image submitted to them for OCR,
	# therefore for security reason, my colleague commented that it would be better to not capture the bottom part of HKID, which
	# means I only capture the first 80% (4/5) of the whole area to avoid the HKID number.

	if(	y > (full_height/20) and y < (full_height * 0.8)
		and (contour_area/total_eligible_area >= 0.004)
		and aspect_ratio >= 2.5 and aspect_ratio <= 10):

		# Print the scanned result
		print(	"x: ", x, "y: ", y, "w: ", w, "h: ", h,
				"w/h", aspect_ratio,
				"w*h", contour_area,
				"contour_area/total_eligible_area", contour_area/total_eligible_area) if show_debug else ''

		# Add note to contour
		# cv2.putText(img, str(i), (x, y - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)

		# Crop and output images
		cropped = img[y:y + h, x:x + w]

		# Show the cropped images
		cv2.imshow("Cropped {}".format(i), cropped) if show_debug else ''

		# Save the cropped images for submission to Google vision cloud later on
		filename = 'cropped/cropped_' + str(i) + '.jpg'
		cv2.imwrite(filename, cropped)

		# Prepare data to be sent to Google
		# https://cloud.google.com/vision/docs/detecting-text#vision-text-detection-protocol

		# Image must be sent using base64
		# https://stackoverflow.com/questions/3715493/encoding-an-image-file-with-base64
		with open(filename, "rb") as image_file:
			encoded_string = base64.urlsafe_b64encode(image_file.read())

		# Construct the array/dict/associative array, whatever you call it
		data = 	{
					'features':{
						'type': 'TEXT_DETECTION'
					},
					'image':{
						# https://stackoverflow.com/questions/36212905/python-3-is-not-json-serializable
						'content': encoded_string.decode("utf-8")
					}
				}
		allRequests.append(data)

		# Originally I use Tesseract 3, but the model from Tesseract Github is too old (2012 for T.Chi) and
		# the OCR result is not good, so I switch to Google vision API.  But I still keep it for reference.
		# print("OCR: ", pytesseract.image_to_string(Image.open(filename), lang='eng+chi_tra'))

		# Add rectangle on image to highlight the scanned area
		cv2.rectangle(img, (x,y), (x + w, y + h), (0, 255, 0), 1)

# Convert request from dict to JSON
json_data = json.dumps({"requests": allRequests}, indent=4)

# Submit it to Google cloud vision API
r = requests.post(GOOGLE_VISION_API, data=json_data)

# Read response from Google
# https://stackoverflow.com/questions/18337407/saving-utf-8-texts-in-json-dumps-as-utf8-not-as-u-escape-sequence
json_result = json.dumps(r.json(), indent=4, ensure_ascii=False).encode('utf8')
result = json.loads(json_result)

# Save returned result to text file
if show_debug:
	with open("returned_json.txt", "w") as f:
		f.write(str(json_result)); f.close()

# Loop through the result array and save the scanned text
allTexts = []
for r in result['responses']:

	if len(r) > 0 and 'fullTextAnnotation' in r:

		# https://stackoverflow.com/questions/1185524/how-to-trim-whitespace-including-tabs
		text = r['fullTextAnnotation']['text'].strip(' \t\n\r')
		allTexts.append(text)

		print("Scanned text: ", text) if show_debug else ''

# Show the whole image with green rectangle
cv2.imshow("Image", img) if show_debug else ''

# Print final result
result = json.loads(json.dumps({"result": allTexts}, ensure_ascii=False).encode('utf8'))
print(result)

# Press ESC to close all windows
if show_debug:
	if((cv2.waitKey(0) & 0xFF) == 27):
		cv2.destroyAllWindows()