from pymongo import MongoClient 
import pytesseract

import functools
import numpy as np
import smtplib,ssl  
from picamera import PiCamera  
from time import sleep  
from email.mime.multipart import MIMEMultipart  
from email.mime.base import MIMEBase  
from email.mime.text import MIMEText  
from email.utils import formatdate  
from email import encoders  
import os
import cv2
nombre=3
camera = PiCamera()
camera.start_preview()

while nombre>0:
   
 camera.capture('/home/pi/yolov5-export-to-raspberry-pi/capture.jpg')     # image path set
 sleep(5)  
 camera.stop_preview() 

 
 os.system('python inf.py -w best-fp16.tflite -i /home/pi/yolov5-export-to-raspberry-pi/capture.jpg  --img_size 640');


 image=cv2.imread('/home/pi/yolov5-export-to-raspberry-pi/matricule.jpg')
 hsv=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)


 def send_an_email():  
    toaddr = 'n.talbi@esi-sba.dz'      # To id 
    me = 'n.talbi@esi-sba.dz'          # your id
    subject = "What's News"              # Subject
  
    msg = MIMEMultipart()  
    msg['Subject'] = subject  
    msg['From'] = me  
    msg['To'] = toaddr  
    msg.preamble = "test "   
    #msg.attach(MIMEText(text))  
  
    part = MIMEBase('application', "octet-stream")  
    part.set_payload(open("/home/pi/yolov5-export-to-raspberry-pi/crop.png", "rb").read())  
    encoders.encode_base64(part)  
    part.add_header('Content-Disposition', 'attachment; filename="test.jpg"')   # File name and format name
    msg.attach(part)  
  
    try:  
       s = smtplib.SMTP('smtp.gmail.com', 587)  # Protocol
       s.ehlo()  
       s.starttls()  
       s.ehlo()  
       s.login(user = 'n.talbi@esi-sba.dz', password = 'nari@2020')  # User id & password
       #s.send_message(msg)  
       s.sendmail(me, toaddr, msg.as_string())  
       s.quit()  
    #except:  
    #   print ("Error: unable to send email")    
    except SMTPException as error:  
          print ("Error")                # Exception
 


 gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 blurred = cv2.GaussianBlur(gray, (5, 5), 0)
 thresh = cv2.adaptiveThreshold(blurred, 255,
    cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 45, 15)
 _, labels = cv2.connectedComponents(thresh)
 mask = np.zeros(thresh.shape, dtype="uint8")
 total_pixels = image.shape[0] * image.shape[1]
 lower = total_pixels // 90 # heuristic param, can be fine tuned if necessary
 upper = total_pixels // 7 # heuristic param, can be fine tuned if necessary
 for (i, label) in enumerate(np.unique(labels)):
    # If this is the background label, ignore it
    if label == 0:
        continue
 
    # Otherwise, construct the label mask to display only connected component
    # for the current label
    labelMask = np.zeros(thresh.shape, dtype="uint8")
    labelMask[labels == label] = 255
    numPixels = cv2.countNonZero(labelMask)
 
    # If the number of pixels in the component is between lower bound and upper bound, 
    # add it to our mask
    if numPixels > lower and numPixels < upper:
        mask = cv2.add(mask, labelMask)
 cv2.imwrite('matricule_pre.jpg',mask)
 send_an_email()
 # Find contours and get bounding box for each contour
 cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 boundingBoxes = [cv2.boundingRect(c) for c in cnts] 
 def compare(rect1, rect2):
    if abs(rect1[1] - rect2[1]) > 10:
        return rect1[1] - rect2[1]
    else:
        return rect1[0] - rect2[0]
 boundingBoxes = sorted(boundingBoxes, key=functools.cmp_to_key(compare) )
 TARGET_WIDTH = 128
 TARGET_HEIGHT = 128
 vehicle_plate = ""
 chars = [
    '0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G',
    'H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'
    ]
 for rect in boundingBoxes:
    # Get the coordinates from the bounding box
    x,y,w,h = rect
    # Crop the character from the mask
    # and apply bitwise_not because in our training data for pre-trained model
    # the characters are black on a white background
    crop = mask[y:y+h, x:x+w]
    crop = cv2.bitwise_not(crop)
    # Get the number of rows and columns for each cropped image
    # and calculate the padding to match the image input of pre-trained model
    rows = crop.shape[0]
    columns = crop.shape[1]
    paddingY = (TARGET_HEIGHT - rows) // 2 if rows < TARGET_HEIGHT else int(0.17 * rows)
    paddingX = (TARGET_WIDTH - columns) // 2 if columns < TARGET_WIDTH else int(0.45 * columns)
    
    # Apply padding to make the image fit for neural network model
    crop = cv2.copyMakeBorder(crop, paddingY, paddingY, paddingX, paddingX, cv2.BORDER_CONSTANT, None, 255)
    # Convert and resize image
    crop = cv2.cvtColor(crop, cv2.COLOR_GRAY2RGB)     
    crop = cv2.resize(crop, (TARGET_WIDTH, TARGET_HEIGHT))
    # Prepare data for prediction
    crop = crop.astype("float") / 255.0
    cv2.imwrite("crop.png",crop)
    img=cv2.imread("crop.png")
    text = pytesseract.image_to_string(img)
    with open("scone.txt", "w") as file:
        file.write(text)
    crop = np.expand_dims(crop, axis=0)
    # Make prediction
   
    vehicle_plate += text
    # Show bounding box and prediction on image
    cv2.rectangle(image, (x,y), (x+w,y+h), (0, 255, 0), 2)
    cv2.putText(image, text , (x,y+15), 0, 0.8, (0, 0, 255), 2)
 # Show final image
 cv2.imwrite('Final.png', image)
 print("Vehicle plate: " + vehicle_plate)
 

 send_an_email()

 data2=""
 client = MongoClient("mongodb+srv://pfe:pfe@cluster0.xyt2s.mongodb.net/pfe?retryWrites=true&w=majority")
 db = client.get_database('pfe')
 records = db.text
 new_data = {
    'text_extracted': data2,
 }
 records.insert_one(new_data)
