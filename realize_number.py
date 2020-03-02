# coding=utf-8

import yaml
from const_holder import *

import pprint
from copy import copy

import numpy as np
import imutils as imu

import pytesseract
import operator
import math
from functools import partial



try:
    from cv2 import cv2 as cv
except ImportError:
    pass


def upload_image():
    cv.namedWindow('ege', cv.WINDOW_NORMAL)
    # cv.namedWindow('imr', cv.WINDOW_NORMAL)
    cv.namedWindow('imc', cv.WINDOW_NORMAL)
    image = cv.imread('scans/Sample2.jpeg')
    height, width, _ = image.shape
    cv.imshow('ege', image)
    cv.resizeWindow('ege', 600, 600)

    with open('calib_info.yaml', 'r') as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        calib_data = yaml.load(file, Loader=yaml.Loader)
        if calib_data is None:
            calib_data = dict()

    return image, height, width


def find_calib_rects(image, height, width, name, number_of_calib_rects):
    im = cv.cvtColor(image.copy(), cv.COLOR_BGR2GRAY)
    imr = cv.bitwise_not(im.copy())
    # zr = np.zeros((height // 7, width // 6))
    # imr[0: height // 7, 0: width // 6] = zr
    ret, imr = cv.threshold(imr, 150, 255, cv.THRESH_BINARY)
    # for x in range(height):
    #     for y in range(width):
    #         imr[x,y] = 255 - imr[x,y]
    # cv.imshow('imr', imr)
    # cv.resizeWindow('imr', 600, 600)
    a, ct, hr = cv.findContours(imr, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    # print(ct)
    # ind = 0
    # l0 = 0
    # for i in range(len(ct)):
    #     if l0<len(ct[i]):
    #         l0 = len(ct[i])
    #         ind = i
    # print len(ct[1])
    ct = sorted(ct, key=len, reverse=True)
    # for i in ct:
    #     print len(i)
    # ct = ct[::-1]
    ct1 = copy(ct)
    j = 0
    for i in range(len(ct1)):
        peri = cv.arcLength(ct1[i], True)
        squar = cv.contourArea(ct1[i])
        approx = cv.approxPolyDP(ct1[i], 0.04 * peri, True)
        approx_peri = cv.arcLength(approx, True)
        approx_squar = cv.contourArea(approx)
        if len(approx) != 4:
            ct = np.delete(ct, j)
            continue

        if (abs(cv.boundingRect(ct1[i])[2] - cv.boundingRect(ct1[i])[3]) > cv.boundingRect(ct1[i])[3] * 0.1):
            ct = np.delete(ct, j)
            continue

        if approx_squar != 0:
            if not(16.1 > approx_peri ** 2 / approx_squar > 15.9):
                ct = np.delete(ct, j)
                continue

        j += 1

    ct = sorted(ct, key=partial(cv.arcLength, closed=True), reverse=True)
    # cv.namedWindow("sas", cv.WINDOW_NORMAL)
    # cv.imshow("sas", cv.drawContours(image.copy(), ct1[0:200], -1, (255,100,10),3)) #531
    # cv.resizeWindow("sas",600,600)
    # areas_countours = [(cv.contourArea(c), n) for n, c in enumerate(ct)]
    # sorted(areas_countours, key=operator.itemgetter(0))

    imc = image.copy()
    for i in range(number_of_calib_rects):
        imc = cv.drawContours(imc, ct, i, (0, 255, 0), 3)
        # sleep(1000)
    cv.imshow('imc', imc)
    cv.resizeWindow('imc', 600, 600)
    # cv.namedWindow("ss", cv.WINDOW_NORMAL)
    # cv.imshow("ss", cv.drawContours(imc, [cv.approxPolyDP(ct[0], 0.04 * cv.arcLength(ct[0], True), True)], -1, (0, 0, 255), 3))
    # cv.resizeWindow('ss', 600, 600)

    calib_rects = list()
    calib_ct = list()
    for i in range(number_of_calib_rects):
        calib_ct.append(cv.minAreaRect(ct[i]))
        calib_rects.append(cv.boundingRect(ct[i]))  # x,y,w,h

    calib_ct, calib_rects = sort_calib_rects(calib_ct, calib_rects, name)

    # pct = [np.int0(cv.boxPoints(crr)) for crr in calib_ct]
    # cv.imshow("ss", cv.drawContours(imc, pct, -1, (0, 0, 255), 3))
    # cv.resizeWindow('ss', 600, 600)

    # stan_dev = np.array([i[0] for i in calib_rects]).std()
    # for i in range(len(calib_rects) - 1):
    #     if abs(calib_rects[i][0] - calib_rects[i + 1][0]) < stan_dev and calib_rects[i][1] > calib_rects[i + 1][1]:
    #         calib_rects[i], calib_rects[i + 1] = calib_rects[i + 1], calib_rects[i]

    return calib_rects, calib_ct


def sort_calib_rects(calib_ct, calib_rects, name):
    calib_rects = sorted(calib_rects, key=operator.itemgetter(0, 1))
    calib_ct = sorted(calib_ct, key=operator.itemgetter(0, 1))
    if name == "Русский 2020 к/р":
        if calib_rects[2][1] > calib_rects[3][1]:
            calib_rects[2], calib_rects[3] = calib_rects[3], calib_rects[2]

        if calib_ct[2][0][1] > calib_ct[3][0][1]:
            calib_ct[2], calib_ct[3] = calib_ct[3], calib_ct[2]
    elif name == "Русский 2020 п/р":
        if calib_rects[0][1] > calib_rects[1][1]:
            calib_rects[0], calib_rects[1] = calib_rects[1], calib_rects[0]
        if calib_rects[2][1] > calib_rects[3][1]:
            calib_rects[2], calib_rects[3] = calib_rects[3], calib_rects[2]

        if calib_ct[0][0][1] > calib_ct[1][0][1]:
            calib_ct[0], calib_ct[1] = calib_ct[1], calib_ct[0]
        if calib_ct[2][0][1] > calib_ct[3][0][1]:
            calib_ct[2], calib_ct[3] = calib_ct[3], calib_ct[2]
    return calib_ct, calib_rects


def rect_minus(calib_rot_rect, name):
    res = False
    if name == "Русский 2020 к/р":
        res = abs(calib_rot_rect[0][0][1]-calib_rot_rect[4][0][1]) > 0.001
    elif name == "Русский 2020 п/р":
        res = abs(calib_rot_rect[0][0][1] - calib_rot_rect[2][0][1]) > 0.001
    return res


def find_angle(calib_rot_rect, name):
    angle = 0
    if name == "Русский 2020 к/р":
        angle = math.atan(-(calib_rot_rect[0][0][1]-calib_rot_rect[4][0][1])/(calib_rot_rect[4][0][0]-calib_rot_rect[0][0][0]))
    elif name == "Русский 2020 п/р":
        angle = math.atan(-(calib_rot_rect[0][0][1]-calib_rot_rect[2][0][1])/(calib_rot_rect[2][0][0]-calib_rot_rect[0][0][0]))
    return angle


def find_scales_and_strt(calib_rects, name, scale_x_c, scale_y_c, strt_point):
    str_point, scale_x, scale_y = (0, 0), 0, 0
    if name == "Русский 2020 к/р":
        scale_x = (calib_rects[3][0] - calib_rects[0][0]) / scale_x_c
        scale_y = (calib_rects[0][1] - calib_rects[3][1]) / scale_y_c
        str_point = (round(calib_rects[0][0] + strt_point[0] * scale_x), round(calib_rects[3][1] + strt_point[1] * scale_y))
    elif name == "Русский 2020 п/р":
        scale_x = (calib_rects[2][0] - calib_rects[1][0]) / scale_x_c
        scale_y = (calib_rects[1][1] - calib_rects[2][1]) / scale_y_c
        str_point = (round(calib_rects[1][0] + strt_point[0] * scale_x), round(calib_rects[2][1] + strt_point[1] * scale_y))
    return str_point, scale_x, scale_y


def rotation_fix(image, height, width, name, number_of_calib_rects):
    calib_rects, calib_rot_rect = find_calib_rects(image, height, width, name, number_of_calib_rects)
    sa = 0
    angle = 0
    i = 0
    while rect_minus(calib_rot_rect, name):
        angle = find_angle(calib_rot_rect, name)
        if abs(angle) < 0.00004:
            angle *= 10000
        elif abs(angle) < 0.004:
            angle *= 100

        angle *= 1/(1 + round(i/30))
        print(calib_rot_rect[0][0][1] - calib_rot_rect[min(4,number_of_calib_rects-1)][0][1], "   ", angle, "   ", calib_rot_rect[min(4,number_of_calib_rects-1)][0][0] - calib_rot_rect[0][0][0])
        # print("-----+++++-----")
        # pprint.pprint(calib_rot_rect)
        image = imu.rotate(image, angle) #0.4
        sa +=angle
        calib_rects, calib_rot_rect = find_calib_rects(image, height, width, name, number_of_calib_rects)
        i += 1

    print(angle, "   sa:  ", sa)

    cv.imshow('ege', image)

    pprint.pprint(calib_rects)
    print("-----+++++-----")
    pprint.pprint(calib_rot_rect)
    # print("---------------")
    # calib_rects,calib_rot_rect = find_calib_rects(image, height, width)
    # pprint.pprint(calib_rects)
    # print("-----+++++-----")
    # pprint.pprint(calib_rot_rect)

    return calib_rects


def finish_calibration(calib_rects, height, width, bp):
    name, number_of_calib_rects, scale_x_c, scale_y_c, strt_point, width_linet, lenth_linet, ir_zazort, cell_sizet = bp
    str_point, scale_x, scale_y = find_scales_and_strt(calib_rects, name, scale_x_c, scale_y_c, strt_point)
    zerox = 0  # round(90 * scale_x)
    width_line = round(width_linet * scale_y)
    lenth_line = round(lenth_linet * scale_x)
    ir_zazor = round(ir_zazort * scale_y)
    cell_size = round(cell_sizet * scale_x)
    borders = (0.125, 0.11)
    return zerox, str_point, width_line, lenth_line, ir_zazor, cell_size, borders


def image_to_answers(image, str_types, str_answers, baze_params, height, width):
    zerox, str_point, width_line, lenth_line, ir_zazor, cell_size, borders = baze_params
    answ = dict()
    for j in range(2):
        for k in range(4):
            for i in range(1, 6):
                text = ""
                for l in range(17):
                    x, y = str_point
                    cv.namedWindow(str(l * 100 + i + k * 5 + j * 20))
                    cv.moveWindow(str(l * 100 + i + k * 5 + j * 20), (j * 400 + l * 22), (i + k * 5) * 35)

                    # print(x + (j * lenth_line + j * (x)), " vs ", width)
                    roi = image[y + (i - 1 + k * 5) * width_line + k * ir_zazor: y + (i + k * 5) * width_line + k * ir_zazor,
                          x + zerox + (j * lenth_line + j * x) + l * cell_size: x + zerox + (j * lenth_line + j * x) + (
                                      l + 1) * cell_size]
                    roi = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
                    ret, roi = cv.threshold(roi, 235, 255, cv.THRESH_BINARY)
                    cv.imshow(str(l * 100 + i + k * 5 + j * 20), roi)
                    letter = ""
                    if str_types[i - 1 + k * 5 + j * 20] == choose_types.NUM_NOORDER or str_types[
                        i - 1 + k * 5 + j * 20] == choose_types.NUM_ORDER or str_types[
                        i - 1 + k * 5 + j * 20] == choose_types.NUM:
                        letter = pytesseract.image_to_string(roi, lang='eng',
                                                             config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
                    elif str_types[i - 1 + k * 5 + j * 20] == choose_types.WORD:
                        letter = pytesseract.image_to_string(roi, lang='rus',
                                                             config='--psm 10 --oem 3 -c tessedit_char_whitelist=абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
                    text += letter
                answ[(i + k * 5 + j * 20)] = text
    # print(answers)
    print(answ.values())

    return answ