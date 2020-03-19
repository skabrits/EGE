class maket_class:
    def __init__(self, answ, types):
        self.answers_str = [i.get() for i in answ]
        self.types_str = [i.get() for i in types]


class choose_types:
    INDEF = "выберите тип"
    NUM_NOORDER = "цифры (важен порядок)"
    NUM_ORDER = "цифры (неважен порядок)"
    WORD = "слова"
    NUM = "число"

class blank_class:
    def __init__(self, name, number_of_calib_rects, **kwargs):
        other = kwargs
        self.name = name
        self.number_of_calib_rects = number_of_calib_rects
        self.scale_x_c = other["scale_x_c"]
        self.scale_y_c = other["scale_y_c"]
        self.str_point = other["str_point"]
        self.width_line = other["width_line"]
        self.lenth_line = other["lenth_line"]
        self.block_zazor = other["block_zazor"]
        self.cell_size = other["cell_size"]
        self.cell_number = other["cell_number"]
        self.assymetrical_blocks =  other["assymetrical_blocks"]
        self.rows_in_blocks = other["rows_in_blocks"]
        self.row_number = other["row_number"]
        self.block_number = other["block_number"]
        self.column_number = other["column_number"]
        self.vert_poprav_ochcka = other["vert_poprav_ochcka"]