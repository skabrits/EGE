# coding=utf-8
import torch
from torchvision import transforms
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
import matplotlib.pyplot as plt



try:
    from cv2 import cv2 as cv
except ImportError:
    pass


class Blanck_processer:
    def __init__(self, proc_blank, types_numbers):
        self.ct_t = list()
        self.ct_f = list()
        self.proc_blank = proc_blank
        self.str_types, self.str_answers = types_numbers
        self.height = 0
        self.width = 0
        self.image = None
        self.calib_rects = None
        self.calib_rot_rect = None
        self.angle = 0
        self.zerox = 0
        self.width_line = 0
        self.lenth_line = 0
        self.block_zazor = 0
        self.cell_size = 0
        self.borders = (0, 0)
        self.answ = None

    def upload_image(self):
        cv.namedWindow('ege', cv.WINDOW_NORMAL)
        cv.namedWindow('imr', cv.WINDOW_NORMAL)
        cv.namedWindow('imc', cv.WINDOW_NORMAL)
        self.image = cv.imread('scans/Образец 15118480 5.jpeg')
        self.height, self.width, _ = self.image.shape
        cv.imshow('ege', self.image)
        cv.resizeWindow('ege', 600, 600)

    def find_calib_rects(self):
        im = cv.cvtColor(self.image.copy(), cv.COLOR_BGR2GRAY)
        imr = cv.bitwise_not(im.copy())
        ret, imr = cv.threshold(imr, 150, 255, cv.THRESH_BINARY)
        cv.imshow('imr', imr)
        cv.resizeWindow('imr', 600, 600)
        a, ct, hr = cv.findContours(imr, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        ct = sorted(ct, key=len, reverse=True)
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

            if (abs(cv.minAreaRect(ct1[i])[1][0] - cv.minAreaRect(ct1[i])[1][1]) > cv.minAreaRect(ct1[i])[1][1] * 0.1):
                ct = np.delete(ct, j)
                continue

            if approx_squar != 0:
                if not(16.1 > approx_peri ** 2 / approx_squar > 15.9):
                    ct = np.delete(ct, j)
                    continue

            j += 1

        ct = sorted(ct, key=partial(cv.arcLength, closed=True), reverse=True)

        imc = self.image.copy()
        for i in range(self.proc_blank.number_of_calib_rects):
            imc = cv.drawContours(imc, ct, i, (0, 255, 0), 3)
        cv.imshow('imc', imc)
        cv.resizeWindow('imc', 600, 600)
        # cv.namedWindow("ss", cv.WINDOW_NORMAL)
        # cv.imshow("ss", cv.drawContours(imc, [cv.approxPolyDP(ct[0], 0.04 * cv.arcLength(ct[0], True), True)], -1, (0, 0, 255), 3))
        # cv.resizeWindow('ss', 600, 600)

        calib_rects = list()
        calib_ct = list()
        for i in range(self.proc_blank.number_of_calib_rects):
            calib_ct.append(cv.minAreaRect(ct[i]))
            calib_rects.append(cv.boundingRect(ct[i]))  # x,y,w,h

        def calib_ct_normalizer(cont):
            box = cv.boxPoints(cont)
            def sorter(x):
                return x[1]
            box = sorted(box, key=sorter)
            if box[0][0] > box[1][0]:
                box[0], box[1] = box[1], box[0]
            return box

        calib_ct = list(map(calib_ct_normalizer, calib_ct))

        calib_ct, calib_rects = self.sort_calib_rects(calib_rects, calib_ct)

        # pct = [np.int0(cv.boxPoints(crr)) for crr in calib_ct]
        # cv.imshow("ss", cv.drawContours(imc, pct, -1, (0, 0, 255), 3))
        # cv.resizeWindow('ss', 600, 600)

        # stan_dev = np.array([i[0] for i in calib_rects]).std()
        # for i in range(len(calib_rects) - 1):
        #     if abs(calib_rects[i][0] - calib_rects[i + 1][0]) < stan_dev and calib_rects[i][1] > calib_rects[i + 1][1]:
        #         calib_rects[i], calib_rects[i + 1] = calib_rects[i + 1], calib_rects[i]

        self.calib_rects, self.calib_rot_rect = calib_rects, calib_ct

    def sort_calib_rects(self, calib_rects, calib_ct):
        calib_rects = sorted(calib_rects, key=operator.itemgetter(0, 1))
        def sorter(x):
            return x[0][0]
        calib_ct = sorted(calib_ct, key=sorter)
        if self.proc_blank.name == "Русский 2020 к/р":
            if calib_rects[2][1] > calib_rects[3][1]:
                calib_rects[2], calib_rects[3] = calib_rects[3], calib_rects[2]

            if calib_ct[2][0][1] > calib_ct[3][0][1]:
                calib_ct[2], calib_ct[3] = calib_ct[3], calib_ct[2]
        elif self.proc_blank.name == "Русский 2020 п/р":
            if calib_rects[0][1] > calib_rects[1][1]:
                calib_rects[0], calib_rects[1] = calib_rects[1], calib_rects[0]
            if calib_rects[2][1] > calib_rects[3][1]:
                calib_rects[2], calib_rects[3] = calib_rects[3], calib_rects[2]

            if calib_ct[0][0][1] > calib_ct[1][0][1]:
                calib_ct[0], calib_ct[1] = calib_ct[1], calib_ct[0]
            if calib_ct[2][0][1] > calib_ct[3][0][1]:
                calib_ct[2], calib_ct[3] = calib_ct[3], calib_ct[2]
        return calib_ct, calib_rects

    def find_angle(self):
        angle = 0
        if self.proc_blank.name == "Русский 2020 к/р":
            angle = math.atan(-(self.calib_rot_rect[0][0][1]-self.calib_rot_rect[4][0][1])/(self.calib_rot_rect[4][0][0]-self.calib_rot_rect[0][0][0]))
        elif self.proc_blank.name == "Русский 2020 п/р":
            angle = (math.atan(-(self.calib_rot_rect[0][0][1]-self.calib_rot_rect[2][0][1])/(self.calib_rot_rect[2][0][0]-self.calib_rot_rect[0][0][0])) +
                     math.atan(-(self.calib_rot_rect[1][0][1]-self.calib_rot_rect[3][0][1])/(self.calib_rot_rect[3][0][0]-self.calib_rot_rect[1][0][0])))/2
        return angle

    def find_scales_and_strt(self):
        self.str_point, self.scale_x, self.scale_y = (0, 0), 0, 0
        if self.proc_blank.name == "Русский 2020 к/р":
            self.scale_x = (self.calib_rects[3][0] - self.calib_rects[0][0]) / self.proc_blank.scale_x_c
            self.scale_y = (self.calib_rects[0][1] - self.calib_rects[3][1]) / self.proc_blank.scale_y_c
            self.str_point = (self.calib_rects[0][0] + self.proc_blank.str_point[0] * self.scale_x, self.calib_rects[3][1] + self.proc_blank.str_point[1] * self.scale_y)
        elif self.proc_blank.name == "Русский 2020 п/р":
            self.scale_x = (self.calib_rects[2][0] - self.calib_rects[1][0]) / self.proc_blank.scale_x_c
            self.scale_y = (self.calib_rects[1][1] - self.calib_rects[2][1]) / self.proc_blank.scale_y_c
            self.str_point = (self.calib_rects[1][0] + self.proc_blank.str_point[0] * self.scale_x, self.calib_rects[2][1] + self.proc_blank.str_point[1] * self.scale_y)

    def rotation_fix(self):
        self.find_calib_rects()
        pprint.pprint(self.calib_rects)
        print("-----+++++-----")
        pprint.pprint(self.calib_rot_rect)
        print("---------------")
        sa = 0
        angle = self.find_angle()

        self.image = imu.rotate(self.image, math.degrees(angle), center=(self.calib_rects[0][0], self.calib_rects[0][1])) #0.4
        self.find_calib_rects()

        cv.imshow('ege', self.image)

        pprint.pprint(self.calib_rects)
        print("-----+++++-----")
        pprint.pprint(self.calib_rot_rect)

    def finish_calibration(self):
        self.find_scales_and_strt()
        self.vert_poprav_ochcka = self.proc_blank.vert_poprav_ochcka * self.scale_x
        self.zerox = 0  # round(90 * scale_x)
        self.width_line = self.proc_blank.width_line * self.scale_y
        self.lenth_line = self.proc_blank.lenth_line * self.scale_x
        self.block_zazor = self.proc_blank.block_zazor * self.scale_y
        self.cell_size = self.proc_blank.cell_size * self.scale_x
        self.borders = (0.125, 0.11)

    def check_str(self, column, block, row):
        text = ""
        for l in range(self.proc_blank.cell_number):
            letter = self.check_cell(row, column, block, l)
            text += letter
        return text

    def image_to_answers(self):
        self.answ = dict()
        plt.yticks(np.arange(0, 700, 1))
        from matplotlib.pyplot import figure
        for j in range(self.proc_blank.column_number):
            self.check_column(j)
        # print(answers)
        print(self.answ.values())
        plt.show()

        return self.answ

    def check_column(self, column):
        res_blocks = 0
        if self.proc_blank.assymetrical_blocks:
            res_blocks = len(self.proc_blank.rows_in_blocks)
        else:
            res_blocks = self.proc_blank.block_number

        for k in range(res_blocks):
            self.check_block(column, k)

    def check_block(self, column, block):
        res_rows = 0
        if self.proc_blank.assymetrical_blocks:
            res_rows = self.proc_blank.rows_in_blocks[block]
            row_sum = sum(self.proc_blank.rows_in_blocks)
        else:
            res_rows = self.proc_blank.row_number
            row_sum = self.proc_blank.row_number * self.proc_blank.block_number

        for i in range(res_rows):
            text = self.check_str(column, block, i)
            self.answ[(i + 1 + block * 5 + column * row_sum)] = text

    def check_cell(self, row, column, block, cell_number):
        x, y = self.str_point
        # print(x + (j * lenth_line + j * (x)), " vs ", width)
        roi = self.image[round(y + (row + block * 5) * self.width_line + block * self.block_zazor): round(y + (
                row + 1 + block * 5) * self.width_line + block * self.block_zazor),
              round(x + self.zerox + column * self.lenth_line + column * x + cell_number * self.cell_size - (row + block * 5) * self.vert_poprav_ochcka): round(x + self.zerox +
                                                                                                                                                                column * self.lenth_line + column * x + (cell_number + 1) * self.cell_size - (row + block * 5) * self.vert_poprav_ochcka)]

        letter = self.process_cell(block, cell_number, column, roi, row)
        return letter

    def process_cell(self, block, cell_number, column, roi, row):
        cell_image = cv.cvtColor(roi.copy(), cv.COLOR_BGR2GRAY)
        ret, cell_image = cv.threshold(cell_image, 230, 255, cv.THRESH_BINARY)
        cv.namedWindow(str(cell_number * 100 + row + 1 + block * 5 + column * 20))
        cv.moveWindow(str(cell_number * 100 + row + 1 + block * 5 + column * 20), (column * 400 + cell_number * 22),
                      (row + 1 + block * 5) * 35)
        # cv.imshow(str(cell_number * 100 + row + 1 + block * 5 + column * 20), cell_image[9:-9, 9:-9])

        imr = cv.bitwise_not(cell_image.copy())
        # imr = cv.GaussianBlur(imr, (3,3),7)
        # ret, imr = cv.threshold(imr, 5, 255, cv.THRESH_BINARY)

        a, ct, hr = cv.findContours(imr.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        c_a = np.array([cv.contourArea(cv.approxPolyDP(k, 0.0000001 * cv.arcLength(k, True), True)) for k in ct])
        c_m = c_a.mean()
        c_s = c_a.std()
        mask = np.zeros(imr.shape, dtype="uint8")
        need_to_realize = False
        if c_m  / c_s < 0.65:
            self.ct_f.append(c_m / c_s)
            need_to_realize = True
            for i in ct:
                if cv.contourArea(i) > c_m:
                    cv.drawContours(mask, [i], -1, 255, -1)
        else:
            self.ct_t.append(c_m/c_s)

        imr = cv.bitwise_and(imr, imr, mask=mask)
        plt.scatter(c_a, [cell_number + 1 + row * 17 + block * 5 * 17 + column * 20 * 17 for _ in range(len(c_a))])

        numpy_hi = np.hstack((cv.drawContours(roi.copy(), ct, -1, (0,255,100), 1), cv.cvtColor(imr.copy(), cv.COLOR_GRAY2BGR)))
        cv.imshow(str(cell_number * 100 + row + 1 + block * 5 + column * 20), numpy_hi)

        letter = self.read_text(block, imr, column, row, need_to_realize)
        return letter

    def read_text(self, block, cell_image, column, row, need_to_realize=False):
        letter1 = ""
        if need_to_realize:
            net = SimpleConvNet()
            net.load_state_dict(torch.load('numbers_cnn'))
            net.eval()

            transform = transforms.Compose(
                [transforms.ToTensor()])

            y_pred = net(transform(cv.resize(cell_image, (28, 28))).float().unsqueeze(0))
            _, predicted = torch.max(y_pred, 1)
            letter1 = str(predicted[0].tolist())
            # if self.str_types[row + block * 5 + column * 20] == choose_types.NUM_NOORDER or self.str_types[
            #     row + block * 5 + column * 20] == choose_types.NUM_ORDER or self.str_types[
            #     row + block * 5 + column * 20] == choose_types.NUM:
            #     letter = pytesseract.image_to_string(cell_image, lang='eng',
            #                                          config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
            # elif self.str_types[row + block * 5 + column * 20] == choose_types.WORD:
            #     letter = pytesseract.image_to_string(cell_image, lang='rus',
            #                                          config='--psm 10 --oem 3 -c tessedit_char_whitelist=абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
        return letter1
