import sys, keyboard
from time import time, sleep
from tkinter import *

from gui import *

root = Tk()
gui = GUI(root)
keys = [i[0] for i in keyboard._winkeyboard.official_virtual_keys.values()]
activated = False
currentButton = None
warning = 'Cannot activate autoclick when this GUI is in focus'
focus = False
while True:
    try:
        if root.focus_get() != None:
            if not focus:
                gui.error.config(text=warning)
            focus = True
        else:
            focus = False
            if gui.error.cget('text') == warning:
                gui.error.config(text='') 
            if gui.hotkey.get() in keys:
                if keyboard.is_pressed(gui.hotkey.get()):
                    if activated:
                        for o in gui.optionWidgets:
                            o.widget.stop()
                        gui.status.config(text='Inactive', fg='#ff0000')
                        activated = False
                        gui.uptime.config(fg='#ff0000')
                        sleep(1)
                    else:
                        sleep(1)
                        activated = True
                        gui.status.config(text='Active', fg='#00ff00')
                        for o in gui.optionWidgets:
                            o.widget.start()
                        timer = time()
                        gui.uptime.config(fg='#00ff00')
        if activated:
            for o in gui.optionWidgets:
                o.widget.update()
            gui.uptime.config(text=str(round(time()-timer, 2)))
        root.update_idletasks()
        root.update()
        sleep(0.01)#minimise CPU usage
    except Exception as e:
        try:
            gui.error.config(text=e)
            root.update_idletasks()
            root.update()
        except TclError:
            sys.exit()


