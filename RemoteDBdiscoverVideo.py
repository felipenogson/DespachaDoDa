# import the necessary packages
from dotenv import load_dotenv
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
from datetime import datetime
import imutils
import time
import cv2
import os
from helpers import get_sat_data
from pprint import pprint

from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect

load_dotenv()

server = SSHTunnelForwarder(
    (tunnel_address, 21098),
    ssh_username=tunnel_user,
    ssh_password= tunnel_password,
    remote_bind_address=('127.0.0.1', 3306), 
    local_bind_address=('0.0.0.0', 3306)
)
server.start()
print( server.local_bind_port)
db_user = "nogslbqf_felipon"
db_password = "felipon123"
engine = create_engine(f'mysql://{db_user}:{db_password}@127.0.0.1:3306/nogslbqf_despacho')


Base = declarative_base(engine)
class Despacho(Base):
    __tablename__ = 'despacho'
    __table_args__ = { 'autoload' : True}
    
metadata = Base.metadata
Session = sessionmaker(bind=engine)
session = Session()

 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
	help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
#vs = VideoStream(src=rtsp).start()
time.sleep(2.0)
 
# open the output CSV file for writing and initialize the set of
# barcodes found thus far
csv = open(args["output"], "w")
found = set()
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

		# Try to get the record from de db
		query = session.query(Despacho).filter_by(url=barcodeData).first()

		# Si el codigo no estan en la base de datos
		if query is None:
			# the data from the QR is a URL so here get the last part of the address
			idData = barcodeData.split('/')[-1]
			print("[INFO] barcode: {}\a".format(idData))
			d = Despacho()

			#usando uno de los helpers para obtener la informacion del sat
			sat_data = get_sat_data(barcodeData)
			#imprime la informacion a consola
			pprint(sat_data)
			print('\n')

			# Agrega los datos al objeto de la base de datos
			d.url = barcodeData
			try: 
				p = sat_data['pedimentos'][0]
			except:

				d.status = 'error'
				d.timestamp = datetime.now()
				session.add(d)
				session.commit()
				continue
			d.placas = p['Datos de Identificación  del Vehículo:']
			d.caja = sat_data['candado']['Contenedores:']
			d.sello = sat_data['candado']['Candados:']
			d.status = 'correcto'
			d.timestamp = datetime.now()
			session.add(d)
			session.commit()

		(x, y, w, h) = barcode.rect
		query = session.query(Despacho).filter_by(url=barcodeData).first()

		if query.status == 'correcto':
			cv2.rectangle(frame, (x, y), (x + w, y + h), green, 2)
			text = "{} ({})".format(barcodeData, barcodeType)
			cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
			0.5, green, 2)


		elif query.status == 'error':
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
