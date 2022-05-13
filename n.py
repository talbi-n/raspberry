from pymongo import MongoClient 
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
    part.set_payload(open("/home/pi/yolov5-export-to-raspberry-pi/matricule_pre.jpg", "rb").read())  
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
 thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

 # Determine average contour area
 average_area = [] 
 cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 cnts = cnts[0] if len(cnts) == 2 else cnts[1]
 for c in cnts:
    x,y,w,h = cv2.boundingRect(c)
    area = w * h
    average_area.append(area)

 average = sum(average_area) / len(average_area)

 # Remove large lines if contour area is 5x bigger then average contour area
 cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 cnts = cnts[0] if len(cnts) == 2 else cnts[1]
 for c in cnts:
    x,y,w,h = cv2.boundingRect(c)
    area = w * h
    if area > average * 5:  
        cv2.drawContours(thresh, [c], -1, (0,0,0), -1)

 # Dilate with vertical kernel to connect characters
 kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,5))
 dilate = cv2.dilate(thresh, kernel, iterations=3)

 # Remove small noise if contour area is smaller than 4x average
 cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
 cnts = cnts[0] if len(cnts) == 2 else cnts[1]
 for c in cnts:
    area = cv2.contourArea(c)
    if area < average * 4:
        cv2.drawContours(dilate, [c], -1, (0,0,0), -1)

 # Bitwise mask with input image
 result = cv2.bitwise_and(image, image, mask=dilate)
 result[dilate==0] = (255,255,255)


 
 im2 = gray.copy()
 
 cv2.imwrite('matricule_pre.jpg',result)
 os.system('tesseract  /home/pi/yolov5-export-to-raspberry-pi/matricule_pre.jpg  text  --dpi 300 --oem 3 --psm 6 nobatch ')

 send_an_email()
 text_file = open("text.txt", "r")

 #read whole file to a string
 data = text_file.read()
 data1=data.replace("^L", "")
 data2 = ''.join(char for char in data1  if char.isalnum())
 print("___________")
 print(data2)



 client = MongoClient("mongodb+srv://pfe:pfe@cluster0.xyt2s.mongodb.net/pfe?retryWrites=true&w=majority")
 db = client.get_database('pfe')
 records = db.text
 new_data = {
    'text_extracted': data2,
 }
 records.insert_one(new_data)
