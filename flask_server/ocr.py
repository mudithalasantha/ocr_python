import pytesseract
import requests
import re
import numpy as np
import cv2
from matplotlib import pyplot as plt
from PIL import Image
from PIL import ImageFilter
from StringIO import StringIO
import datetime

def process_image(url):
    image = _get_image(url)
    # img = cv2.imread('GettyImage.jpg')
    image.filter(ImageFilter.SHARPEN)
    string_val = pytesseract.image_to_string(image)
    return _validate_output(string_val)
    # px = img[100,100]
    # img_m = find_objects()
    # return px

def _get_image(url):
    return Image.open(StringIO(requests.get(url).content))

def _validate_output(val):
    nid = re.search("[0-9]{6,17}", val)
    nid_string = re.search("NATIONAL ID CARD", val)
    gprb_1_string = re.search("Government", val)
    gprb_2_string = re.search("People's", val)
    gprb_3_string = re.search("Republic", val)
    gprb_4_string = re.search("Bangladesh", val)
    dob_string = re.search("Date of Birth", val)
    name_string = re.search("Name", val)
    accuracy = _calculate_accuracy(nid, [nid_string, gprb_1_string, gprb_2_string, gprb_3_string, gprb_4_string, dob_string, name_string])
    name = _retrieve_name(val)
    blood_group = _retrieve_blood_group(val)
    dob = _retrieve_dob(val)
    if nid:
        return {"raw_data":val, "nid":nid.group(0), "name":name, "blood_group":blood_group, "dob":dob, "accuracy": accuracy, "code": 200, "error": False}
    else:
        return {"raw_data":val, "nid":None, "name":name, "blood_group":blood_group, "dob":dob, "accuracy": accuracy, "code": 200, "error": True}

def _retrieve_name(val):
    name = re.search("(?<=Name:.).+?(?=\\n)", val)
    if name:
        return name.group(0)
    else:
        return None

def _retrieve_blood_group(val):
    b_group = re.search("(?<=Group:.).+?(?=\\n)", val)
    if b_group:
        return b_group.group(0)
    else:
        return None

def _retrieve_dob(val):
    dob = re.search("(?<=Birth:.).+?(?=\\n)", val)
    if dob:
        return validate(dob.group(0))
    else:
        return None

def _calculate_accuracy(nid, param_array):
    value = 30
    single_weight = 70/len(param_array)
    if nid:
        for idx, item in enumerate(param_array):
            if item:
                value+= single_weight
        return value
    else:
        return 0

def validate(date_text):
    try:
         return datetime.datetime.strptime(date_text, '%d %b %Y').strftime("%d %b %Y")
    except ValueError:
        if date_text[0] in "689":
            temp_list = list(date_text)
            temp_list[0] = '0'
            return validate("".join(temp_list))
        if date_text[0] in "7":
            temp_list = list(date_text)
            temp_list[0] = '1'
            return validate("".join(temp_list))
        is_month_corrected, return_value = month_correction(date_text)
        if is_month_corrected:
            return return_value
        return "Error in format"

def month_correction(date_text):
    split_list = date_text.split()
    temp_list = list(date_text)
    if "Ja" in split_list[1] or "an" in split_list[1]:
        temp_list[3] = 'J'
        temp_list[4] = 'a'
        temp_list[5] = 'n'
        return True, validate("".join(temp_list))
    if "Fe" in split_list[1] or "eb" in split_list[1]:
        temp_list[3] = 'F'
        temp_list[4] = 'e'
        temp_list[5] = 'b'
        return True, validate("".join(temp_list))
    if "Ma" in split_list[1] or "ar" in split_list[1]:
        temp_list[3] = 'M'
        temp_list[4] = 'a'
        temp_list[5] = 'r'
        return True, validate("".join(temp_list))
    if "Ap" in split_list[1] or "pr" in split_list[1]:
        temp_list[3] = 'A'
        temp_list[4] = 'p'
        temp_list[5] = 'r'
        return True, validate("".join(temp_list))
    if "Ma" in split_list[1] or "ay" in split_list[1]:
        temp_list[3] = 'M'
        temp_list[4] = 'a'
        temp_list[5] = 'y'
        return True, validate("".join(temp_list))
    if "un" in split_list[1]:
        temp_list[3] = 'J'
        temp_list[4] = 'u'
        temp_list[5] = 'n'
        return True, validate("".join(temp_list))
    if "ul" in split_list[1]:
        temp_list[3] = 'J'
        temp_list[4] = 'u'
        temp_list[5] = 'l'
        return True, validate("".join(temp_list))
    if "Au" in split_list[1] or "ug" in split_list[1]:
        temp_list[3] = 'A'
        temp_list[4] = 'u'
        temp_list[5] = 'g'
        return True, validate("".join(temp_list))
    if "Se" in split_list[1] or "ep" in split_list[1]:
        temp_list[3] = 'S'
        temp_list[4] = 'e'
        temp_list[5] = 'p'
        return True, validate("".join(temp_list))
    if "Oc" in split_list[1] or "ct" in split_list[1]:
        temp_list[3] = 'O'
        temp_list[4] = 'c'
        temp_list[5] = 't'
        return True, validate("".join(temp_list))
    if "No" in split_list[1] or "ov" in split_list[1]:
        temp_list[3] = 'N'
        temp_list[4] = 'o'
        temp_list[5] = 'v'
        return True, validate("".join(temp_list))
    if "De" in split_list[1] or "ec" in split_list[1]:
        temp_list[3] = 'D'
        temp_list[4] = 'e'
        temp_list[5] = 'c'
        return True, validate("".join(temp_list))
    return False, None

# def find_objects():
#     MIN_MATCH_COUNT = 10

#     img1 = cv2.imread('GettyImage.jpg',0)          # queryImage
#     img2 = cv2.imread('GettyImage.jpg',0) # trainImage

#     # Initiate SIFT detector
#     sift = cv2.SIFT()

#     # find the keypoints and descriptors with SIFT
#     kp1, des1 = sift.detectAndCompute(img1,None)
#     kp2, des2 = sift.detectAndCompute(img2,None)

#     FLANN_INDEX_KDTREE = 0
#     index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
#     search_params = dict(checks = 50)

#     flann = cv2.FlannBasedMatcher(index_params, search_params)

#     matches = flann.knnMatch(des1,des2,k=2)

#     # store all the good matches as per Lowe's ratio test.
#     good = []
#     for m,n in matches:
#         if m.distance < 0.7*n.distance:
#             good.append(m)

#     if len(good)>MIN_MATCH_COUNT:
#         src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
#         dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

#         M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
#         matchesMask = mask.ravel().tolist()

#         h,w = img1.shape
#         pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
#         dst = cv2.perspectiveTransform(pts,M)

#         img2 = cv2.polylines(img2,[np.int32(dst)],True,255,3, cv2.LINE_AA)

#     else:
#         matchesMask = None
#         return "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT)

#     draw_params = dict(matchColor = (0,255,0), # draw matches in green color
#                    singlePointColor = None,
#                    matchesMask = matchesMask, # draw only inliers
#                    flags = 2)

#     img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)

#     return img3