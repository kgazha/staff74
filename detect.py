import os
from os import listdir
from os.path import isfile, join
import cv2
import numpy as np


def detect_image(filename, template_filename):
    stream = open(filename, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    img_rgb = cv2.imdecode(numpyarray, cv2.COLOR_BGR2GRAY)

    width = 100
    height = int(img_rgb.shape[0] * 100 / img_rgb.shape[1])
    dim = (width, height)
    resized = cv2.resize(img_rgb, dim, interpolation=cv2.INTER_AREA)
    img_gray = resized

    stream = open(template_filename, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    template = cv2.imdecode(numpyarray, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.6
    loc = np.where(res >= threshold)
    if loc[0].size > 0:
        return True
    return False


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files = []
    template_filename = 'small_image.png'
    for f in listdir(current_dir):
        if isfile(join(current_dir, f)) \
                and f.lower().split('.')[-1] in ['gif', 'jpe', 'jpeg', 'jpg', 'png', 'svg', 'svgz'] \
                and f.lower() != template_filename.lower():
            files.append(f)
    for file in files:
        result = detect_image(file, template_filename)
        if result:
            break
