from options.nonsequential.abstract.onEvent import OnEventBase


class Widget(OnEventBase):
    def __init__(self, *args):
        super().__init__(*args)

    def update(self):
        self.optionManger.runOptions()
