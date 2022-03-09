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
  

 gray = cv2.imread("/home/pi/yolov5-export-to-raspberry-pi/matricule.jpg",0)

 blur = cv2.GaussianBlur(gray, (5,5), 0)
 #gray = cv2.medianBlur(gray, 5)
 # perform otsu thresh (using binary inverse since opencv contours work better with white text)
 ret, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
 rect_kern=cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
 dilation = cv2.dilate(thresh, rect_kern, iterations = 1)
 # create copy of image
 im2 = gray.copy()
 invd=255-dilation
 cv2.imwrite('matricule_pre.jpg',invd)
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
