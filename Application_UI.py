# coding=utf-8

import yaml

from const_holder import *

from tkinter import *

from tkinter.ttk import *

from tkinter import messagebox

from tkinter.filedialog import askopenfilename

from Output import *
from realize_number import *

from PIL import Image, ImageTk


class View_app:
    def __init__(self, Controller):
        self.Controller = Controller

        self.marg = 7

        self.window_setup = Tk()
        self.window_setup.title("ЕГЭ проверяльщик")
        self.window_setup.geometry('900x700')


        self.create_blank_frame()
        self.blank_window.place(in_=self.window_setup, x=0, y=0, relwidth=1, relheight=1)

        self.create_shablon_frame()
        self.shablon_window.place(in_=self.window_setup, x=0, y=0, relwidth=1, relheight=1)

    def create_blank_frame(self):
        self.blank_window = Frame(self.window_setup, width=800, height=800)
        self.canvas1 = Canvas(self.blank_window)
        self.scroll_y1 = Scrollbar(self.blank_window, orient="vertical", command=self.canvas1.yview)
        self.blank_conf = Frame(self.canvas1, width=800, height=800)
        self.page_shabl = Button(self.blank_conf, text="Выбрать Шаблон", command=self.Controller.move_to_frame)
        self.page_shabl.grid(column=0, row=0)
        self.page_blank = Button(self.blank_conf, text="Создать Бланк", command=self.Controller.move_to_blank_conf)
        self.page_blank.grid(column=1, row=0)
        self.upload_cr = Button(self.blank_conf, text="Загрузите файл с образцом бланка",
                                command=self.Controller.load_calib_file)
        self.upload_cr.grid(column=1, row=1)
        self.cal_im = Label(self.blank_conf)
        self.cal_im.grid(column=0, row=3, pady=20, rowspan=40)
        self.uls = Button(self.blank_conf, text="Готово")
        self.uls.grid(column=0, row=41, pady=10)
        self.canvas1.create_window(0, 0, anchor='nw', window=self.blank_conf)
        # make sure everything is displayed before configuring the scrollregion
        self.canvas1.update_idletasks()
        self.canvas1.configure(scrollregion=self.canvas1.bbox('all'),
                               yscrollcommand=self.scroll_y1.set)
        self.canvas1.pack(fill='both', expand=True, anchor=NW, side=TOP)
        self.scroll_y1.pack(fill='y', anchor=NE, side=TOP)

    def create_shablon_frame(self):
        self.shablon_window = Frame(self.window_setup, width=800, height=800)
        self.canvas = Canvas(self.shablon_window)
        self.scroll_y = Scrollbar(self.shablon_window, orient="vertical", command=self.canvas.yview)
        self.frame = Frame(self.canvas, width=800, height=800)
        self.page_shabl = Button(self.frame, text="Выбрать Шаблон", command=self.Controller.move_to_frame)
        self.page_shabl.grid(column=0, row=0)
        self.page_blank = Button(self.frame, text="Создать Бланк", command=self.Controller.move_to_blank_conf)
        self.page_blank.grid(column=1, row=0)
        self.lbl = Label(self.frame, text="Расставьте типы заданий и ответы")
        self.lbl.grid(column=0, row=1, pady=10)
        self.types = list()
        self.answers = list()
        for i in range(2, 42):
            lbl1 = Label(self.frame, text=str(i - 1))
            lbl1.grid(column=0, row=i + self.marg)

            self.types.append(Combobox(self.frame))
            self.types[i - 2]['values'] = (
                choose_types.INDEF, choose_types.WORD, choose_types.NUM, choose_types.NUM_ORDER,
                choose_types.NUM_NOORDER)
            self.types[i - 2].current(0)
            self.types[i - 2].grid(column=1, row=i + self.marg)

            self.answers.append(Entry(self.frame, width=10))
            self.answers[i - 2].grid(column=3, row=i + self.marg)
        self.maket = Combobox(self.frame)
        self.maket['values'] = tuple(self.Controller.makets.keys())
        self.maket.current(0)
        self.maket.grid(column=0, row=4)
        self.btn = Button(self.frame, text="Выбрать", command=self.Controller.choose_maket)
        self.btn.grid(column=1, row=4)
        self.blank = Combobox(self.frame)
        self.blank['values'] = tuple(self.Controller.calib_data.keys())
        self.blank.current(0)
        self.blank.grid(column=0, row=2, pady=10)
        self.btnb = Button(self.frame, text="Выбрать", command=self.Controller.choose_blank)
        self.btnb.grid(column=1, row=2, pady=10)
        self.btnb1 = Button(self.frame, text="Создать", command=self.Controller.move_to_blank_conf)
        self.btnb1.grid(column=2, row=2, pady=10)
        self.upd_f = Button(self.frame, text="Загрузите папку/файл с работами", command=self.Controller.load_calib_file)
        self.upd_f.grid(column=0, row=3, pady=10)
        self.lbl2 = Label(self.frame, text="Создать новый шаблон")
        self.lbl2.grid(column=0, row=5, pady=10)
        self.entr = Entry(self.frame, width=20)
        self.entr.grid(column=1, row=5, pady=10)
        self.btn1 = Button(self.frame, text="Создать", command=self.Controller.set_maket)
        self.btn1.grid(column=2, row=5, pady=10)
        self.btn2 = Button(self.frame, text="Готово", command=self.Controller.clicked)
        self.btn2.grid(column=1, row=46 + self.marg, pady=20)
        self.canvas.create_window(0, 0, anchor='nw', window=self.frame)
        # make sure everything is displayed before configuring the scrollregion
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'),
                              yscrollcommand=self.scroll_y.set)
        self.canvas.pack(fill='both', expand=True, side='left')
        self.scroll_y.pack(fill='y', side='right')


class Controller:
    def __init__(self):
        with open('config.yaml', 'r') as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            self.makets = yaml.load(file, Loader=yaml.Loader)
            if self.makets is None:
                self.makets = dict()

        with open('calib_info.yaml', 'r') as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            self.calib_data = yaml.load(file, Loader=yaml.Loader)
            if self.calib_data is None:
                self.calib_data = dict()

        # image = cv.imread('scans/Sample1.JPG')
        # cv.namedWindow('ege11', cv.WINDOW_NORMAL)
        # cv.imshow('ege11', image)
        # cv.resizeWindow('ege11',600,600)
        # cv.waitKey(0)
        # cv.destroyAllWindows()

        self.calib_image = None
        self.check_file = None

        self.curr_mak = None
        self.curr_blank = None

        self.str_answers = list()
        self.str_types = list()

        self.VA = View_app(self)

        self.VA.window_setup.mainloop()

    def get_types_and_answers(self):
        return self.str_types, self.str_answers

    def check_set_types(self):
        for i in range(len(self.VA.types)):
            if str(self.VA.types[i].get()) == choose_types.INDEF and str(self.VA.answers[i].get()) != "":
                messagebox.showerror('Выбирите все типы.', ('Проблема в задании ' + str(i + 1)))
                return False
        return True

    def check_blank(self):
        return not(self.curr_blank is None)

    def is_named(self):
        return self.VA.entr.get() != ""

    def choose_blank(self):
        self.curr_blank = self.calib_data[self.VA.blank.get()]

    def create_blank(self):
        if self.is_named():
            with open('calib_info.yaml', 'w') as outfile:
                created_blank = blank_class(self.VA.answers, self.VA.types)
                self.calib_data[self.VA.blank.get()] = created_blank
                yaml.dump(self.calib_data, outfile)
        else:
            messagebox.showerror('Выбирите название бланка.', 'Укажите имя')

    def set_maket(self):
        if self.is_named():
            with open('config.yaml', 'w') as outfile:
                created_maket = maket_class(self.VA.answers, self.VA.types)
                self.makets[self.VA.entr.get()] = created_maket
                yaml.dump(self.makets, outfile)
        else:
            messagebox.showerror('Выбирите название макета.', 'Укажите имя')

    # def isalpha_rus(c):
    #     return c >= 'а' and c <= 'я' or c >= 'А' and c <= 'Я' or c == 'ё' or c == 'Ё'
    #
    # def isAlpha_rus(word):
    #     ret = True
    #     for i in word:
    #         ret = isalpha_rus(i)
    #     return ret

    def check_types(self):
        if self.check_set_types():
            for i in range(len(self.VA.answers)):
                if str(self.VA.types[i].get()) == choose_types.WORD:
                    if not ((str(self.VA.answers[i].get())).isalpha()):
                        messagebox.showerror('Тип не соответствует значению.',
                                             ('Проблема в задании ' + str(i + 1)))
                        return False
                elif str(self.VA.types[i].get()) == choose_types.NUM_NOORDER or str(
                        self.VA.types[i].get()) == choose_types.NUM_ORDER:
                    if not (str(self.VA.answers[i].get()).isdigit()):
                        messagebox.showerror('Тип не соответствует значению.',
                                             ('Проблема в задании ' + str(i + 1)))
                        return False
                # elif str(answers[i].get()) == "":

            return True
        return False

    def clicked(self):
        if self.check_blank():
            if self.check_types():
                self.str_answers = list(map(lambda i: i.get(), self.VA.answers))
                self.str_types = list(map(lambda i: i.get(), self.VA.types))
                print(self.str_answers, "----", self.str_types)
                self.VA.window_setup.destroy()
        else:
            messagebox.showerror('Выбирите тип бланка.', 'Выбирите тип бланка')

    def choose_maket(self):
        self.curr_mak = self.makets[self.VA.maket.get()]
        for i in range(len(self.VA.types)):
            self.VA.types[i].set(self.curr_mak.types_str[i])
            self.VA.answers[i].delete(0, END)
            self.VA.answers[i].insert(0, self.curr_mak.answers_str[i])

    def move_to_blank_conf(self):
        self.VA.blank_window.lift()

    def move_to_frame(self):
        self.VA.shablon_window.lift()

    def load_calib_file(self):
        self.calib_image = askopenfilename()
        render = ImageTk.PhotoImage(Image.open(self.calib_image).resize((472, 668),Image.ANTIALIAS))
        self.VA.cal_im.configure(image=render)
        self.VA.cal_im.image = render

    def load_check_file(self):
        self.check_file = askopenfilename()



class GUI_Application(Controller):
    def __init__(self):
        super().__init__()

        str_types, str_answers = self.get_types_and_answers()

        image, height, width = upload_image()

        calib_rects = rotation_fix(image, height, width, self.curr_blank.name, self.curr_blank.number_of_calib_rects)

        zerox, str_point, width_line, lenth_line, ir_zazor, cell_size, borders = finish_calibration(calib_rects, height, width, (self.curr_blank.name, self.curr_blank.number_of_calib_rects, self.curr_blank.scale_x_c, self.curr_blank.scale_y_c, self.curr_blank.str_point, self.curr_blank.width_line, self.curr_blank.lenth_line, self.curr_blank.ir_zazor, self.curr_blank.cell_size))

        answ = image_to_answers(image, str_types, str_answers, (zerox, str_point, width_line, lenth_line, ir_zazor, cell_size, borders), height, width)

        print(answ)

        # write_answers_to_exel(answ, str_types, str_answers)

        cv.waitKey(0)
        cv.destroyAllWindows()