# coding=utf-8

import pprint
from copy import copy
from time import sleep
from tkinter import *

from tkinter.ttk import *

from tkinter import messagebox

import cv2 as cv
import numpy as np
import io
import json

import pytesseract
import requests
import itertools
import operator
import xlsxwriter as xlsxwriter

def check_set_types():
    for i in range(len(types)):
        if str(types[i].get().encode('utf-8')) == "выберите тип" and str(answers[i].get().encode('utf-8')) != "":
            messagebox.showerror('Выбирите все типы.', ('Проблема в задании ' + str(i+1)))
            return False
    return True

def isalpha_rus(c):
    return c >= ("а".encode('utf-8')) and c <= ('я'.encode('utf-8')) or c >= ('А'.encode('utf-8')) and c <= ('Я'.encode('utf-8')) or c == ('ё'.encode('utf-8')) or c == ('Ё'.encode('utf-8'))

def isAlpha_rus(word):
    ret = True
    for i in word:
        ret = isalpha_rus(i)
    return ret


def check_types():
    if check_set_types():
        for i in range(len(answers)):
            if str(types[i].get().encode('utf-8')) == "слова":
                if not(isAlpha_rus(str(answers[i].get().encode('utf-8')))):
                    messagebox.showerror('Тип не соответствует значению.',
                                         ('Проблема в задании ' + str(i+1)))
                    return False
            elif str(types[i].get().encode('utf-8')) == "число (неважен порядок)" or str(types[i].get().encode('utf-8')) == "число (важен порядок)":
                if not(str(answers[i].get().encode('utf-8')).isdigit()):
                    messagebox.showerror('Тип не соответствует значению.',
                                         ('Проблема в задании ' + str(i+1)))
                    return False
            # elif str(answers[i].get()) == "":

        return True
    return False

def clicked():
    if check_types():
        str_answers = map(lambda i: str(i.get()),answers)
        str_types = map(lambda i: str(i.get()), types)
        print (str_answers, "----", str_types)
        window_setup.destroy()

def choose_maket():
    pass


str_answers = list()
str_types = list()

window_setup = Tk()
window_setup.title("ЕГЭ проверяльщик")
window_setup.geometry('800x600')

canvas = Canvas(window_setup)
scroll_y = Scrollbar(window_setup, orient="vertical", command=canvas.yview)

frame = Frame(canvas, width=800, height=800)
# group of widgets



lbl = Label(frame, text="Расставьте типы заданий и ответы")
lbl.grid(column=0, row=0)

types = list()
answers = list()

for i in range(2,42):
    lbl1 = Label(frame, text=str(i-1))
    lbl1.grid(column=0, row=i+1)

    types.append(Combobox(frame))
    types[i-2]['values'] = ("выберите тип", "число (важен порядок)", "число (неважен порядок)", "слова")
    types[i - 2].current(0)
    types[i - 2].grid(column=1, row=i+1)

    answers.append(Entry(frame, width=10))
    answers[i-2].grid(column=3, row=i+1)

maket = Combobox(frame)
maket['values'] = ("выберите шаблон", "русский язык 2019 год", "физика 2019 год")
maket.current(0)
maket.grid(column=1, row=1)

btn = Button(frame, text="Выбрать", command=choose_maket)
btn.grid(column=2, row=1)

btn = Button(frame, text="Готово", command=clicked)
btn.grid(column=1, row=45)

canvas.create_window(0, 0, anchor='nw', window=frame)
# make sure everything is displayed before configuring the scrollregion
canvas.update_idletasks()

canvas.configure(scrollregion=canvas.bbox('all'),
                 yscrollcommand=scroll_y.set)

canvas.pack(fill='both', expand=True, side='left')
scroll_y.pack(fill='y', side='right')
window_setup.mainloop()


answ = dict()

cv.namedWindow('ege', cv.WINDOW_NORMAL)
cv.namedWindow('imr', cv.WINDOW_NORMAL)
cv.namedWindow('imc', cv.WINDOW_NORMAL)
image = cv.imread('/Users/sevakabrits/Pictures/scans/student1.jpeg')
height, width, _ = image.shape
cv.imshow('ege', image)
cv.resizeWindow('ege', 600, 600)
im = cv.cvtColor(image.copy(), cv.COLOR_BGR2GRAY)
imr = cv.bitwise_not(im.copy())
zr = np.zeros((height // 7, width // 5))
imr[0: height // 7, 0: width // 5] = zr
ret, imr = cv.threshold(imr, 175, 255, cv.THRESH_BINARY)
# for x in range(height):
#     for y in range(width):
#         imr[x,y] = 255 - imr[x,y]
cv.imshow('imr', imr)
cv.resizeWindow('imr', 600, 600)

ct, hr = cv.findContours(imr, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
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
    approx = cv.approxPolyDP(ct1[i], 0.04 * peri, True)
    if len(approx) != 4:
        ct = np.delete(ct, j)
        j -= 1
    j += 1
imc = image.copy()
for i in range(5):
    imc = cv.drawContours(imc, ct, i, (0, 255, 0), 3)
    # sleep(1000)

cv.imshow('imc', imc)
cv.resizeWindow('imc', 600, 600)
calib_rects = list()
for i in range(5):
    calib_rects.append(cv.boundingRect(ct[i]))  # x,y,w,h

calib_rects = sorted(calib_rects, key=operator.itemgetter(0, 1))
# pprint.pprint(calib_rects)
scale_x = (calib_rects[3][0] - calib_rects[0][0]) / (2062 - 135)
scale_y = (calib_rects[0][1] - calib_rects[3][1]) / (2765 - 624)

zerox = 90 * scale_x
str_point = ((calib_rects[0][0] + 72 - 90) * scale_x, (calib_rects[3][1] + 260) * scale_y)
width_line = (87 * scale_y) // 1
lenth_line = (1003 * scale_x) // 1
ir_zazor = (37 * scale_y) // 1

for j in range(2):
    for k in range(4):
        for i in range(1, 6):
            x, y = str_point
            cv.namedWindow(str(i + k * 5 + j * 20))
            cv.moveWindow(str(i + k * 5 + j * 20), j*400, (i+k*5)*35)

            # print(x + (j * lenth_line + j * (x)), " vs ", width)
            roi = image[y + (i - 1 + k * 5) * width_line + k * ir_zazor: y + (i + k * 5) * width_line + k * ir_zazor,
                  x + zerox + (j * lenth_line + j * (x)): x + zerox + ((j + 1) * lenth_line)]
            roi = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
            ret, roi = cv.threshold(roi, 240, 255, cv.THRESH_BINARY)
            cv.imshow(str(i + k * 5 + j * 20), roi)
            text = pytesseract.image_to_string(roi, lang='eng',
                                               config='--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789')
            if text == None or text == "":
                text = pytesseract.image_to_string(roi, lang='rus')
            answ[(i + k * 5 + j * 20)] = text

workbook = xlsxwriter.Workbook('student1_checked.xlsx')
worksheet = workbook.add_worksheet()

row = 0
col = 0


# Iterate over the data and write it out row by row.
for key, val in answ.items():
    worksheet.write(row, col, key)
    worksheet.write(row, col + 1, val)
    row += 1

workbook.close()

cv.waitKey(0)
cv.destroyAllWindows()
