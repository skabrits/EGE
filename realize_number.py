# coding=utf-8

from const_holder import *

import pprint
from copy import copy

import numpy as np
import imutils as imu

import pytesseract
import operator
import math



try:
    from cv2 import cv2 as cv
except ImportError:
    pass


def upload_image():
    cv.namedWindow('ege', cv.WINDOW_NORMAL)
    cv.namedWindow('imr', cv.WINDOW_NORMAL)
    cv.namedWindow('imc', cv.WINDOW_NORMAL)
    image = cv.imread('scans/Sample1.JPG')
    height, width, _ = image.shape
    cv.imshow('ege', image)
    cv.resizeWindow('ege', 600, 600)
    return image, height, width


def find_calib_rects(image, height, width):
    im = cv.cvtColor(image.copy(), cv.COLOR_BGR2GRAY)
    imr = cv.bitwise_not(im.copy())
    # zr = np.zeros((height // 7, width // 6))
    # imr[0: height // 7, 0: width // 6] = zr
    ret, imr = cv.threshold(imr, 175, 255, cv.THRESH_BINARY)
    # for x in range(height):
    #     for y in range(width):
    #         imr[x,y] = 255 - imr[x,y]
    cv.imshow('imr', imr)
    cv.resizeWindow('imr', 600, 600)
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

        if (cv.boundingRect(ct1[i])[2] < cv.boundingRect(ct1[i])[3] * 9.3 / 10 or cv.boundingRect(ct1[i])[2] >
                cv.boundingRect(ct1[i])[3] * 10.8 / 10 or cv.boundingRect(ct1[i])[2] * 9.3 / 10 >
                cv.boundingRect(ct1[i])[3] or cv.boundingRect(ct1[i])[2] * 10.8 / 10 < cv.boundingRect(ct1[i])[3]):
            ct = np.delete(ct, j)
            continue
        if approx_squar != 0:
            if not(16.1 > approx_peri ** 2 / approx_squar > 15.9):
                ct = np.delete(ct, j)
                continue

        j += 1

    # areas_countours = [(cv.contourArea(c), n) for n, c in enumerate(ct)]
    # sorted(areas_countours, key=operator.itemgetter(0))

    imc = image.copy()
    for i in range(5):
        imc = cv.drawContours(imc, ct, i, (0, 255, 0), 3)
        # sleep(1000)
    cv.imshow('imc', imc)
    cv.resizeWindow('imc', 600, 600)
    cv.namedWindow("ss", cv.WINDOW_NORMAL)
    # cv.imshow("ss", cv.drawContours(imc, [cv.approxPolyDP(ct[0], 0.04 * cv.arcLength(ct[0], True), True)], -1, (0, 0, 255), 3))
    # cv.resizeWindow('ss', 600, 600)

    calib_rects = list()
    calib_ct = list()
    for i in range(5):
        calib_ct.append(cv.minAreaRect(ct[i]))
        calib_rects.append(cv.boundingRect(ct[i]))  # x,y,w,h
    calib_rects = sorted(calib_rects, key=operator.itemgetter(0, 1))
    if calib_rects[2][1] > calib_rects[3][1]:
        calib_rects[2], calib_rects[3] = calib_rects[3], calib_rects[2]

    calib_ct = sorted(calib_ct, key=operator.itemgetter(0, 1))
    if calib_ct[2][1] > calib_ct[3][1]:
        calib_ct[2], calib_ct[3] = calib_ct[3], calib_ct[2]

    pct = [np.int0(cv.boxPoints(crr)) for crr in calib_ct]
    cv.imshow("ss", cv.drawContours(imc, pct, -1, (0, 0, 255), 3))
    cv.resizeWindow('ss', 600, 600)

    # stan_dev = np.array([i[0] for i in calib_rects]).std()
    # for i in range(len(calib_rects) - 1):
    #     if abs(calib_rects[i][0] - calib_rects[i + 1][0]) < stan_dev and calib_rects[i][1] > calib_rects[i + 1][1]:
    #         calib_rects[i], calib_rects[i + 1] = calib_rects[i + 1], calib_rects[i]

    return calib_rects, calib_ct


def rotation_fix(image, height, width):
    calib_rects, calib_rot_rect = find_calib_rects(image, height, width)
    angle = math.atan((calib_rot_rect[2][0][0]-calib_rot_rect[3][0][0])/(calib_rot_rect[3][0][1]-calib_rot_rect[2][0][1]))
    print(image[1000][1000])
    image = imu.rotate(image, angle) #0.4
    print(image[1000][1000])
    cv.imshow('ege', image)
    print(angle)

    pprint.pprint(calib_rects)
    print("-----+++++-----")
    pprint.pprint(calib_rot_rect)
    print("---------------")
    calib_rects,calib_rot_rect = find_calib_rects(image, height, width)
    pprint.pprint(calib_rects)
    print("-----+++++-----")
    pprint.pprint(calib_rot_rect)

    return calib_rects


def finish_calibration(calib_rects, height, width):
    scale_x = (calib_rects[3][0] - calib_rects[0][0]) / (3951 - 59)
    scale_y = (calib_rects[0][1] - calib_rects[3][1]) / (5555 - 1285)
    zerox = 0  # round(90 * scale_x)
    str_point = (round(calib_rects[0][0] + (215 - 75) * scale_x), round(calib_rects[3][1] + (1810 - 1300) * scale_y))
    width_line = round((1966 - 1790) * scale_y)
    lenth_line = round((2240 - 220) * scale_x)
    ir_zazor = round((4600 - 4540) * scale_y)
    cell_size = round((340 - 219) * scale_x)
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