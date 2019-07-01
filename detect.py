import os
from os import listdir
from os.path import isfile, join
import cv2
import numpy as np
from matplotlib import pyplot as plt


def detect_image(filename, template_filename):
    f = open(filename, "rb")
    chunk = f.read()
    chunk_arr = np.frombuffer(chunk, dtype=np.uint8)
    img_rgb = cv2.imdecode(chunk_arr, cv2.IMREAD_COLOR)

    width = 100
    height = int(img_rgb.shape[0] * 100 / img_rgb.shape[1])
    dim = (width, height)
    resized = cv2.resize(img_rgb, dim, interpolation = cv2.INTER_AREA)

    img_gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(template_filename, 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where( res >= threshold)
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
            print(file)
            break

# for pt in zip(*loc[::-1]):
    # cv2.rectangle(resized, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

# cv2.imwrite('res.png',resized)