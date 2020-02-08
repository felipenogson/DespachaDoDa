# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
from json import loads
import requests
import argparse
import datetime
import imutils
import time
import cv2
import os
from pprint import pprint
import winsound

frequency = 2500
duration = 500 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
	help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=1).start()
#vs = VideoStream(src=rtsp).start()
time.sleep(2.0)
 
# open the output CSV file for writing and initialize the set of
# barcodes found thus far
csv = open(args["output"], "w")
found = set()

# Esta tabla captura los codigos detectados en esta session para generar un solo beep
detectados = []

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it to
	# have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=600)
 
	# find the barcodes in the frame and decode each of the barcodes
	barcodes = pyzbar.decode(frame)


	# Set de los colores para correcto y error
	red = (0, 0, 255)
	green = (0,255,0)
    # bucle sobre los barcodes encontrados 

	for barcode in barcodes:
		barcodeData = barcode.data.decode("utf-8")
		barcodeType = barcode.type

		if barcodeData not in detectados:
			winsound.Beep(frequency, duration)
			detectados.append(barcodeData)
			print(detectados)
			
		data = { "url" : barcodeData }
		r = requests.post("http://kbrown.xyz:5000/api", json=data)
		jreq = loads(r.text)
		status = jreq['doda']['status']

		(x, y, w, h) = barcode.rect
		if status == 'correcto':
			cv2.rectangle(frame, (x, y), (x + w, y + h), green, 2)
			text = "{} ({})".format(barcodeData, barcodeType)
			cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
			0.5, green, 2)


		elif status == 'error':
			cv2.rectangle(frame, (x, y), (x + w, y + h), red, 2)
			text = "{} ({})".format(barcodeData, barcodeType)
			cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
			0.5, red, 2)

	

	cv2.imshow("Barcode Scanner", frame)
	key = cv2.waitKey(1) & 0xFF
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
 
# close the output CSV file do a bit of cleanup
print("[INFO] cleaning up...")
csv.close()
cv2.destroyAllWindows()
vs.stop()
