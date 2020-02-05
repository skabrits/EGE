# coding=utf-8

import yaml

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


class Application(Frame):
    def __init__(self, parrent, **kw):
        super().__init__(**kw)
