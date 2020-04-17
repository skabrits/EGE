import torch.nn as nn
import torch.nn.functional as F


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

class SimpleConvNet(nn.Module):
    def __init__(self):
        # вызов конструктора предка
        super(SimpleConvNet, self).__init__()
        # необходмо заранее знать, сколько каналов у картинки (сейчас = 1),
        # которую будем подавать в сеть, больше ничего
        # про входящие картинки знать не нужно
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=6, kernel_size=5)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5)
        self.fc1 = nn.Linear(4 * 4 * 16, 120)  # !!!
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        #print(x.shape)
        x = x.view(-1, 4 * 4 * 16)  # !!!
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x