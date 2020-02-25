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