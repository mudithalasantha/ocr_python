# -*- coding: utf-8 -*-
import pytesseract
import requests
import re
import numpy as np
# import cv2
# from cv2 import cv
# from matplotlib import pyplot as plt
from PIL import Image
from PIL import ImageFilter
from StringIO import StringIO
import datetime
import json
import urllib

def process_image(url):
    image = _get_image(url)
    # urllib.urlretrieve(url, "Sample.jpg")
    # img = cv2.imread(image)
    image.filter(ImageFilter.SHARPEN)
    string_val_eng = pytesseract.image_to_string(image, lang='eng')
    string_val_ben = pytesseract.image_to_string(image, lang='ben')

    # find_objects_result = _find_objects()
    # return find_objects_result
    return _validate_output(string_val_eng, string_val_ben)
    # px = img[100,100]
    # return img_m # json.dumps(img_m)

def _get_image(url):
    return Image.open(StringIO(requests.get(url).content))

def _validate_output(val_eng, val_ben):
    nid = re.search("[0-9]{6,17}", val_eng)
    nid_string = re.search("NATIONAL ID CARD", val_eng)
    gprb_1_string = re.search("Government", val_eng)
    gprb_2_string = re.search("People's", val_eng)
    gprb_3_string = re.search("Republic", val_eng)
    gprb_4_string = re.search("Bangladesh", val_eng)
    dob_string = re.search("Date of Birth", val_eng)
    name_string = re.search("Name", val_eng)

    name_eng, name_ben = _retrieve_name(val_eng, val_ben)
    blood_group = _retrieve_blood_group(val_eng)
    dob = _retrieve_dob(val_eng)
    father = _retrieve_father(val_ben)
    mother = _retrieve_mother(val_ben)

    accuracy = _calculate_accuracy(nid, 
    [nid_string, 
    gprb_1_string, 
    gprb_2_string, 
    gprb_3_string, 
    gprb_4_string, 
    dob_string, 
    name_string,
    name_eng,
    blood_group,
    dob
    ])
    
    if nid:
        return {
            "raw_data_eng":val_eng, 
            "raw_data_ben":val_ben, 
            "nid":nid.group(0) if hasattr(nid, 'group') else None,
            "name_eng":name_eng.group(0) if hasattr(name_eng, 'group') else None, 
            "name_ben":name_ben.group(0) if hasattr(name_ben, 'group') else None,
            "father":father.group(0) if hasattr(father, 'group') else None,
            "mother":mother.group(0) if hasattr(mother, 'group') else None,
            "blood_group": blood_group.group(0) if hasattr(blood_group, 'group') else None, 
            "dob":dob, 
            "accuracy": accuracy, 
            "code": 200, 
            "error": False
            }
    else:
        return {
            "raw_data_eng":val_eng, 
            "raw_data_ben":val_ben, 
            "nid":None, 
            "name_eng":name_eng.group(0) if hasattr(name_eng, 'group') else None, 
            "name_ben":name_ben.group(0) if hasattr(name_ben, 'group') else None,
            "blood_group": blood_group.group(0) if hasattr(blood_group, 'group') else None, 
            "dob":dob, 
            "accuracy": accuracy, 
            "code": 200, 
            "error": True
            }

def _retrieve_name(val_eng, val_ben):
    name_eng = re.search("(?<=Name:.).+?(?=\\n)", val_eng)
    name_ben = re.search("(?<=নাম:.).+?(?=\\n)", val_ben)
    if name_eng and name_ben:
        return name_eng, name_ben
    elif name_eng:
        return name_eng, None
    elif name_ben:
        return None, name_ben
    else:
        return None, None

def _retrieve_father(val):
    father = re.search("(?<=পিতা:.).+?(?=\\n)", val)
    if father:
        return father
    else:
        return None

def _retrieve_mother(val):
    father = re.search("(?<=মাতা:.).+?(?=\\n)", val)
    if father:
        return father
    else:
        return None

def _retrieve_blood_group(val):
    b_group = re.search("(?<=Group:.).+?(?=\\n)", val)
    if b_group:
        return b_group
    else:
        return None

def _retrieve_dob(val):
    dob = re.search("(?<=Birth:.).+?(?=\\n)", val)
    if dob:
        return _validate(dob.group(0))
    else:
        return None

def _calculate_accuracy(nid, param_array):
    value = 30
    single_weight = 70/len(param_array)
    if nid:
        for idx, item in enumerate(param_array):
            if item and hasattr(item, 'group') and re.match("[\w., _+-:]", str(item.group(0))):
                value+= single_weight
            elif item and not hasattr(item, 'group') and re.match("[\w., _+-:]", str(item)):
                value+= single_weight
        return value
    else:
        return 0

def _validate(date_text):
    try:
         return datetime.datetime.strptime(date_text, '%d %b %Y').strftime("%d %b %Y")
    except ValueError:
        if date_text[0] in "689":
            temp_list = list(date_text)
            temp_list[0] = '0'
            return _validate("".join(temp_list))
        if date_text[0] in "7":
            temp_list = list(date_text)
            temp_list[0] = '1'
            return _validate("".join(temp_list))
        is_month_corrected, return_value = _month_correction(date_text)
        if is_month_corrected:
            return return_value
        return None

def _month_correction(date_text):
    split_list = date_text.split()
    temp_list = list(date_text)
    if "Ja" in split_list[1] or "an" in split_list[1]:
        temp_list[3] = 'J'
        temp_list[4] = 'a'
        temp_list[5] = 'n'
        return True, _validate("".join(temp_list))
    if "Fe" in split_list[1] or "eb" in split_list[1]:
        temp_list[3] = 'F'
        temp_list[4] = 'e'
        temp_list[5] = 'b'
        return True, _validate("".join(temp_list))
    if "ar" in split_list[1]:
        temp_list[3] = 'M'
        temp_list[4] = 'a'
        temp_list[5] = 'r'
        return True, _validate("".join(temp_list))
    if "Ap" in split_list[1] or "pr" in split_list[1]:
        temp_list[3] = 'A'
        temp_list[4] = 'p'
        temp_list[5] = 'r'
        return True, _validate("".join(temp_list))
    if "ay" in split_list[1]:
        temp_list[3] = 'M'
        temp_list[4] = 'a'
        temp_list[5] = 'y'
        return True, _validate("".join(temp_list))
    if "un" in split_list[1]:
        temp_list[3] = 'J'
        temp_list[4] = 'u'
        temp_list[5] = 'n'
        return True, _validate("".join(temp_list))
    if "ul" in split_list[1]:
        temp_list[3] = 'J'
        temp_list[4] = 'u'
        temp_list[5] = 'l'
        return True, _validate("".join(temp_list))
    if "Au" in split_list[1] or "ug" in split_list[1]:
        temp_list[3] = 'A'
        temp_list[4] = 'u'
        temp_list[5] = 'g'
        return True, _validate("".join(temp_list))
    if "Se" in split_list[1] or "ep" in split_list[1]:
        temp_list[3] = 'S'
        temp_list[4] = 'e'
        temp_list[5] = 'p'
        return True, _validate("".join(temp_list))
    if "Oc" in split_list[1] or "ct" in split_list[1]:
        temp_list[3] = 'O'
        temp_list[4] = 'c'
        temp_list[5] = 't'
        return True, _validate("".join(temp_list))
    if "No" in split_list[1] or "ov" in split_list[1]:
        temp_list[3] = 'N'
        temp_list[4] = 'o'
        temp_list[5] = 'v'
        return True, _validate("".join(temp_list))
    if "De" in split_list[1] or "ec" in split_list[1]:
        temp_list[3] = 'D'
        temp_list[4] = 'e'
        temp_list[5] = 'c'
        return True, _validate("".join(temp_list))
    return False, None

def _find_objects():
    # method = cv.CV_TM_SQDIFF_NORMED

    # Read the images from the file
    small_image = cv2.imread('Bangla_logo.jpg')
    large_image = cv2.imread('Sample.jpg')

    result = cv2.matchTemplate(small_image, large_image, 1)
    
    minVal,maxVal,minLoc,maxLoc = cv2.minMaxLoc(result)
    MPx,MPy = minLoc
    trows,tcols = small_image.shape[:2]
    cv2.rectangle(large_image, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),2)
    cv2.imwrite('messigray.png',large_image)
    return minVal
    # # We want the minimum squared difference
    # mn,_,mnLoc,_ = cv2.minMaxLoc(result)

    # # Draw the rectangle:
    # # Extract the coordinates of our best match
    # MPx,MPy = mnLoc

    # # Step 2: Get the size of the template. This is the same size as the match.
    # trows,tcols = small_image.shape[:2]

    # # Step 3: Draw the rectangle on large_image
    # cv2.rectangle(large_image, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),2)

    # # Display the original image with the rectangle around the match.
    # cv2.imshow('output',large_image)

    # # The image is only displayed if we call this
    # cv2.waitKey(0)