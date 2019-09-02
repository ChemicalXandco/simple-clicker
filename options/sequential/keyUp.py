from tkinter import *
from time import sleep
import keyboard

class Widget:
    def __init__(self, parent, spacing):
        self.parent = parent

        self.key = Entry(parent, width=2)
        self.key.grid(row=0, column=spacing)
        
        self.labelOne = Label(parent, text='key released')
        self.labelOne.grid(row=0, column=spacing+1, sticky=W)

    def run(self):
        keyboard.release(self.key.get())

    def returnSettings(self):
        settings = {}
        settings['key'] = self.key.get()
        return settings

    def addSettings(self, settings):
        self.key.delete(0,END)
        self.key.insert(0, settings['key'])