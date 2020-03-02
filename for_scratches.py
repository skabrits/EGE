from const_holder import *
import yaml

created_blank = blank_class("Выбрать", 0, scale_x_c=0, scale_y_c=0, str_point=(0,0), width_line=0, lenth_line=0, ir_zazor=0, cell_size=0)
print(yaml.dump(created_blank))