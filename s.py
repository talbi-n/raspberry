import pytesseract
target = pytesseract.image_to_string('matricule_pre.jpg', lang='eng',config='--psm 10 --dpi 300  --oem 3 -c tessedit_char_whitelist=0123456789')
with open('text.txt', 'w') as file:
        file.write(target)
