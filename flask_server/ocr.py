import pytesseract
import requests
import re
from PIL import Image
from PIL import ImageFilter
from StringIO import StringIO


def process_image(url):
    image = _get_image(url)
    image.filter(ImageFilter.SHARPEN)
    string_val = pytesseract.image_to_string(image)
    return _validate_output(string_val)
    # return "Hello"


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
    if nid:
        return {"raw_data":val,"nid":nid.group(0), "accuracy": accuracy, "code": 200, "error": False}
    else:
        return {"raw_data":val,"nid":None, "accuracy": accuracy, "code": 200, "error": True}


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