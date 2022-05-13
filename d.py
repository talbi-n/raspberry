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
import pytesseract

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
 


 gray = cv2.imread('/home/pi/yolov5-export-to-raspberry-pi/matricule.jpg', 0)
 gray = cv2.resize( gray, None, fx = 3, fy = 3, interpolation = cv2.INTER_CUBIC)
 blur = cv2.GaussianBlur(gray, (5,5), 0)
 gray = cv2.medianBlur(gray, 3)
 # perform otsu thresh (using binary inverse since opencv contours work better with white text)
 ret, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

 rect_kern = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))

 # apply dilation 
 dilation = cv2.dilate(thresh, rect_kern, iterations = 1)
 

 try:
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
 except:
    ret_img, contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
 sorted_contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])
 _, labels = cv2.connectedComponents(thresh)
 mask = np.zeros(thresh.shape, dtype="uint8")
 
 im2 = gray.copy()
 # Set lower bound and upper bound criteria for characters
 total_pixels = image.shape[0] * image.shape[1]
 lower = total_pixels // 70 # heuristic param, can be fine tuned if necessary
 upper = total_pixels // 20 # heuristic param, can be fine tuned if necessary
 # Loop over the unique components
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

 plate_num = ""
 # loop through contours and find letters in license plate
 for cnt in sorted_contours:
    x,y,w,h = cv2.boundingRect(cnt)
    height, width = im2.shape
    
    # if height of box is not a quarter of total height then skip
    if height / float(h) > 6: continue
    ratio = h / float(w)
    # if height to width ratio is less than 1.5 skip
    if ratio < 1.5: continue
    area = h * w
    # if width is not more than 25 pixels skip
    if width / float(w) > 15: continue
    # if area is less than 100 pixels skip
    if area < 100: continue
    # draw the rectangle
    rect = cv2.rectangle(im2, (x,y), (x+w, y+h), (0,255,0),2)
    roi = thresh[y-5:y+h+5, x-5:x+w+5]
    roi = cv2.bitwise_not(roi)
    roi = cv2.medianBlur(roi, 5)
    #cv2.imshow("ROI", roi)
    #cv2.waitKey(0)
    text = pytesseract.image_to_string(roi, config='-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 6 --dpi 300 --oem 3')
    #print(text)
    plate_num =plate_num + text
 print("the plate") 
 print(plate_num)
 im2 = gray.copy()
 cv2.imwrite('matricule_pre.jpg',mask)
 send_an_email()
 with open('readme.txt', 'w') as f:
    f.write(plate_num)
 
 im2 = gray.copy()
 

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
