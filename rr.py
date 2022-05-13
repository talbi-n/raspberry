# Loading the required python modules
import pytesseract # this is tesseract module
import matplotlib.pyplot as plt
import cv2 # this is opencv module
import glob
import os
# specify path to the license plate images folder as shown below
path_for_license_plates =  "matricule.jpg"
list_license_plates = []
predicted_license_plates = []

for path_to_license_plate in glob.glob(path_for_license_plates, recursive = True):
	
	license_plate_file = path_to_license_plate.split("/")[-1]
	license_plate, _ = os.path.splitext(license_plate_file)
	'''
	Here we append the actual license plate to a list
	'''
	list_license_plates.append(license_plate)
	
	'''
	Read each license plate image file using openCV
	'''
	img = cv2.imread(path_to_license_plate)
	
	'''
	We then pass each license plate image file
	to the Tesseract OCR engine using the Python library
	wrapper for it. We get back predicted_result for
	license plate. We append the predicted_result in a
	list and compare it with the original the license plate
	'''
	predicted_result = pytesseract.image_to_string(img, lang ='eng',config ="--oem 3 --psm 6 ")
	print(predicted_result)
       
	filter_predicted_result = "".join(predicted_result.split()).replace(":", "").replace("-", "")
	predicted_license_plates.append(filter_predicted_result)
with open("text.txt",'w') as file:
                   file.write(predicted_result)
