from const_holder import *
import yaml

created_blank = blank_class("Выбрать", 0, scale_x_c=0, scale_y_c=0, str_point=(0,0), width_line=0, lenth_line=0, ir_zazor=0, cell_size=0, cell_number=17, assymetrical_blocks=False, rows_in_blocks = [5, 5, 5, 5], row_number=5, block_number=4, column_number=2)
print(yaml.dump(created_blank))