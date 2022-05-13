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
import RPi.GPIO as GPIO
import cv2
nombre=3
camera = PiCamera()
camera.start_preview()
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)

while nombre>0:
 GPIO.output(18,False)
 camera.capture('/home/pi/yolov5-export-to-raspberry-pi/capture.jpg')    
 sleep(5)
 camera.stop_preview()


 os.system('python inf.py -w best-fp16.tflite -i /home/pi/yolov5-export-to-rasp>


 image=cv2.imread('/home/pi/yolov5-export-to-raspberry-pi/matricule.jpg')
 hsv=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)


 def send_an_email():
    toaddr = 'n.talbi@esi-sba.dz'      # To id
    me = 'n.talbi@esi-sba.dz'          # your id
    subject = "What's News"              # Subject

    msg = MIMEMultipart()
 msg['From'] = me
    msg['To'] = toaddr
    msg.preamble = "test "
    #msg.attach(MIMEText(text))

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("/home/pi/yolov5-export-to-raspberry-pi/matricule_pre>
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="test.jpg"')  >
    msg.attach(part)

    try:
       s = smtplib.SMTP('smtp.gmail.com', 587)  # Protocol
       s.ehlo()
       s.starttls()
       s.ehlo()
       s.login(user = 'n.talbi@esi-sba.dz', password = 'nari@2020')  # User id >
       #s.send_message(msg)
  s.sendmail(me, toaddr, msg.as_string())
       s.quit()
    #except:
    #   print ("Error: unable to send email")
    except SMTPException as error:
          print ("Error")                # Exception


 gray = cv2.imread("/home/pi/yolov5-export-to-raspberry-pi/mask",0)

 blur = cv2.GaussianBlur(gray, (5,5), 0)
 thresh = cv2.adaptiveThreshold(blur, 255,
    cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 45, 15)
 
 rect_kern=cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
 dilation = cv2.dilate(thresh, rect_kern, iterations = 1)
 _, labels = cv2.connectedComponents(thresh)
 mask = np.zeros(thresh.shape, dtype="uint8")
 total_pixels = image.shape[0] * image.shape[1]
 lower = total_pixels 
 upper = total_pixels 
 # Loop over the unique components
 for (i, label) in enumerate(np.unique(labels)):
    
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




 # create copy of image
 im2 = gray.copy()
 invd=255-dilation
 cv2.imwrite('matricule_pre.jpg',invd)
 os.system('tesseract  /home/pi/yolov5-export-to-raspberry-pi/matricule_pre.jpg>

 send_an_email()
 text_file = open("text.txt", "r")

 #read whole file to a string
 data = text_file.read()
 data1=data.replace("^L", "")
 data2 = ''.join(char for char in data1  if char.isalnum())
 print("___________")
 print(data2)



 client = MongoClient("mongodb+srv://pfe:pfe@cluster0.xyt2s.mongodb.net/pfe?ret>
 db = client.get_database('pfe')
 records = db.text
 new_data = {
    'text_extracted': data2,
 }
 records.insert_one(new_data)
 col2=db.license_authorized
 l = list(records.find({}, {'text_extracted': 1, '_id': 0}))
 l2=list(col2.find({}, {'auth': 1, '_id': 0}))
 tab:bool=[records.count_documents({})]
 for item in l:
      i=item.get("text_extracted")
      for item2 in l2:
          if item2.get("auth")==i:
            tab.append(item2.get("auth"))
 if  data2 in tab :
    GPIO.output(18,True)
    sleep(5)
 else:
   print("noo")


