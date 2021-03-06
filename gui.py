from tkinter import *
from tkinter import scrolledtext, font
from tkinter.filedialog import askopenfile, asksaveasfile
import logging
import time
import json

import options.nonsequential
from options.utils import KeySelector, OverlayWindow, TextHandler, CheckList
from options.numbers import Numbers
from options.recordings import Recordings
from options.optionSelectors import OptionList
import profileManager

systemLogLevel = 25
logging.addLevelName(systemLogLevel, 'SYSTEM')
def system(self, message, *args, **kws):
    if self.isEnabledFor(systemLogLevel):
        self._log(systemLogLevel, message, args, **kws)
logging.Logger.system = system

profileFileTypes = [('Klicker Profile', '.kpro')]


class GUI:
    def __init__(self, master):
        self.master = master
        master.title('Klicker')
        self.setWindowIcon(master)

        self.status = Label(master, text='Inactive', fg='#ff0000')
        self.status.grid(row=0, column=0)

        self.uptime = Label(master, text='0', fg='#ff0000', width=20)
        self.uptime.grid(row=0, column=1)

        self.config = LabelFrame(master, text='Configuration')
        self.config.grid(row=1, column=0, columnspan=2, sticky=W, padx=5, pady=5)

        self.settingsFrame = Frame(self.config)
        self.settingsFrame.grid(row=0, column=0, columnspan=2, sticky=W)

        self.hotkeyLabel = Label(self.settingsFrame, text='Hotkey')
        self.hotkey = KeySelector(self.settingsFrame, master)
        self.hotkeyLabel.grid(row=0, column=0, sticky=E)
        self.hotkey.grid(row=0, column=1, sticky=W)

        self.timeSinceOverlayOpened = time.time()

        self.profileHotkeyLabel = Label(self.settingsFrame, text='Profile switch hotkey')
        self.profileHotkey = KeySelector(self.settingsFrame, master)
        self.profileHotkeyLabel.grid(row=2, column=0, sticky=E)
        self.profileHotkey.grid(row=2, column=1, sticky=W)

        self.profilesScrollFrame = ScrollFrame(self.settingsFrame, (400, 100))
        self.profilesScrollFrame.grid(row=3, column=0, columnspan=2)

        self.profilesSelectFrame = LabelFrame(self.profilesScrollFrame.viewPort, text='Profiles to switch between')
        self.profilesSelectFrame.grid(row=0, column=0, sticky=W, padx=5, pady=5)

        self.profilesSelect = CheckList(self.profilesSelectFrame, default=0)
        self.profilesSelect.grid(row=0, column=0)

        self.overlayFrame = LabelFrame(self.settingsFrame, text='Overlay')
        self.overlayFrame.grid(row=4, column=0, columnspan=2, sticky=W, padx=5, pady=5)
        self.overlayGeneral = IntVar()
        self.overlayGeneralButton = Checkbutton(self.overlayFrame, text="Enable overlay when switching profiles (configuration)", variable=self.overlayGeneral)
        self.overlayGeneralButton.grid(row=0, column=0, sticky=W)
        self.overlay = IntVar()
        self.overlayButton = Checkbutton(self.overlayFrame, text="Enabled (profile)", variable=self.overlay).grid(row=1, column=0, sticky=W)

        self.profiles = LabelFrame(self.config, text='Profile')
        self.profiles.grid(row=2, column=0, columnspan=2, sticky=W, padx=5, pady=5)

        self.profileLabel = Label(self.profiles, text='Set Profile')
        self.profileLabel.grid(row=1, column=0)

        self.profile = StringVar(master)
        self.setProfile = OptionMenu(self.profiles, self.profile, *self.profileList(), command=self.handleSetProfile)
        self.setProfile.grid(row=1, column=1)

        self.saveProfile = Button(self.profiles, text='Save', command=self.handleSaveProfile)
        self.saveProfile.grid(row=1, column=2)

        self.addProfile = Button(self.profiles, text='➕', command=self.handleAddProfile)
        self.addProfile.grid(row=1, column=3)

        self.delProfile = Button(self.profiles, text='❌', command=self.handleConfirmDelProfile)
        self.delProfile.grid(row=1, column=4)

        self.delProfile = Button(self.profiles, text='Import', command=self.handleImportProfile)
        self.delProfile.grid(row=1, column=5)

        self.delProfile = Button(self.profiles, text='Export', command=self.handleExportProfile)
        self.delProfile.grid(row=1, column=6)

        self.appendProfile = Button(self.profiles, text='Append', command=self.handleAppendProfile)
        self.appendProfile.grid(row=1, column=7)

        self.refreshButton = Button(self.config, text='Refresh Configuration', command=self.readSetting)
        self.refreshButton.grid(row=3, column=0)

        self.saveButton = Button(self.config, text='Save Configuration', command=self.writeSetting)
        self.saveButton.grid(row=3, column=1)

        self.numbers = Numbers(master, text='Numbers')
        self.numbers.grid(row=4, column=0, columnspan=2, sticky=W, padx=5, pady=5)

        self.logFrame = LabelFrame(master, text='Log')
        self.logFrame.grid(row=6, column=0, columnspan=2, sticky=W, padx=5, pady=5)

        self.logOptionsFrame = Frame(self.logFrame)
        self.logOptionsFrame.pack()

        self.level = StringVar(master)
        self.setLevel = OptionMenu(self.logOptionsFrame, self.level, *list(logging._levelToName.values()), command=self.changeLevel)
        self.setLevel.grid(row=0, column=0)

        self.clearLogButton = Button(self.logOptionsFrame, text='Clear Log', command=self.clearLog)
        self.clearLogButton.grid(row=0, column=1)

        self.log = scrolledtext.ScrolledText(self.logFrame, width=50, height=10, state='disabled')
        self.log.pack(fill=BOTH, expand=YES)

        self.textHandler = TextHandler(self.log)
        self.textHandler.setLevel(logging.DEBUG)
        self.fileHandler = logging.FileHandler('log.txt')
        self.fileHandler.setLevel(logging.DEBUG)
        self.consoleHandler = logging.StreamHandler()
        self.consoleHandler.setLevel(logging.ERROR)
        self.formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
        self.textHandler.setFormatter(self.formatter)
        self.fileHandler.setFormatter(self.formatter)
        self.consoleHandler.setFormatter(self.formatter)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.textHandler)
        self.logger.addHandler(self.fileHandler)
        self.logger.addHandler(self.consoleHandler)

        self.recordings = Recordings(master, text='Recordings', logger=self.logger, root=self.master)
        self.recordings.grid(row=5, column=0, columnspan=2, sticky=W, padx=5, pady=5)

        self.options = LabelFrame(master, text='Options')
        self.options.grid(row=0, column=3, rowspan=7, sticky='NSEW', padx=5)

        self.optionsScrollFrame = ScrollFrame(self.options, (880, 880))
        self.optionsScrollFrame.pack(fill=BOTH, expand=YES)

        self.optionManager = OptionList(self.optionsScrollFrame.viewPort,
                                        options.nonsequential,
                                        master,
                                        self.handleSaveProfile,
                                        self.logger,
                                        self.numbers,
                                        self.recordings)

        master.grid_columnconfigure(3,weight=1)
        master.grid_rowconfigure(0,weight=1)
        master.grid_rowconfigure(1,weight=1)
        master.grid_rowconfigure(2,weight=1)
        master.grid_rowconfigure(3,weight=1)
        master.grid_rowconfigure(4,weight=1)
        master.grid_rowconfigure(5,weight=1)
        master.grid_rowconfigure(6,weight=1)

        self.level.set("INFO")
        self.readSetting()
        self.changeLevel(self.level.get())

    @staticmethod
    def setWindowIcon(window):
        try:
            window.iconbitmap('icon.ico')
        except TclError:
            # Linux compatibility
            window.iconphoto(False, PhotoImage(file='icon.png'))

    def profileList(self):
        profiles = list(profileManager.read().keys())
        if profiles == []:
            profiles = [None]
        self.profilesSelect.update(profiles)
        return profiles

    def handleSaveProfile(self):
        self.handleCreateProfile(profileName=self.profile.get())

    def handleAddProfile(self):
        self.childWindow = Toplevel(self.master)
        self.childWindow.title('Name Profile')
        self.setWindowIcon(self.childWindow)
        self.childWindow.geometry('250x50')
        self.newProfileName = Entry(self.childWindow)
        self.newProfileName.pack(fill=X, expand=YES)
        createButton = Button(self.childWindow, text="Create", command=self.handleCreateProfile)
        createButton.pack(fill=X, expand=YES)

    def getProfile(self):
        profile = {}
        profile['options'] = self.optionManager.settings
        if not 'settings' in profile:
            profile['settings'] = {}
        profile['settings']['overlay'] = self.overlay.get()
        profile['settings']['numbers'] = self.numbers.get(registerSettings=True)
        profile['settings']['level'] = self.level.get()
        return profile

    def handleCreateProfile(self, profileName=None, profile=None):
        if not profileName:
            profileName = self.newProfileName.get()
        if not profile:
            profile = self.getProfile()
        profileManager.write(profileName, profile)
        self.refreshProfiles()
        self.profile.set(profileName)
        try:
            self.childWindow.destroy()
        except AttributeError:
            pass
        self.handleSetProfile()

    def handleSetProfile(self, *args, profile=None):
        self.optionManager.destroyOptions()
        if not profile:
            profile = profileManager.read()[self.profile.get()]

        settings = profile.pop('settings')

        self.overlay.set(settings['overlay'])
        self.numbers.set(settings['numbers'])
        self.level.set(settings['level'])
        self.optionManager.settings = profile['options']

    def menuCommand(self, value):
        self.profile.set(value)
        self.handleSetProfile()

    def refreshProfiles(self):
        profiles = self.profileList()
        menu = self.setProfile['menu']
        menu.delete(0, END)
        for string in profiles:
            menu.add_command(label=string,
                             command=lambda value=string: self.menuCommand(value))

    def handleConfirmDelProfile(self):
        self.childWindow = Toplevel(self.master)
        self.childWindow.title('Confirm Delete Profile')
        self.setWindowIcon(self.childWindow)
        self.childWindow.geometry('300x50')
        label = Label(self.childWindow, text='Delete Profile "{}"?'.format(self.profile.get()))
        label.pack(fill=X, expand=YES)
        createButton = Button(self.childWindow, text="Delete", command=self.handleDelProfile)
        createButton.pack(fill=X, expand=YES)

    def handleDelProfile(self):
        self.childWindow.destroy()
        profileManager.remove(self.profile.get())
        self.refreshProfiles()
        self.profile.set('')

    def handleImportProfile(self):
        f = askopenfile(
            title='Import Profile',
            filetypes=profileFileTypes,
        )
        self.handleSetProfile(profile=json.load(f))
        f.close()

    def handleExportProfile(self):
        f = asksaveasfile(
            title='Export Profile',
            defaultextension=profileFileTypes[0][1],
            filetypes=profileFileTypes,
        )
        json.dump(self.getProfile(), f)
        f.close()

    def appendSelectedProfile(self):
        profile = self.getProfile()
        otherProfile = profileManager.read()[self.profileToAppend.get()]
        checked = self.appendCheckList.get()
        if 'options' in checked:
            profile['options'] += otherProfile['options']
        if 'numbers' in checked:
            for i, n in otherProfile['settings']['numbers'].items():
                if i in profile['settings']['numbers'].keys():
                    self.logger.warning('Number {} being overriden with {}'.format(i, n))
                profile['settings']['numbers'][i] = n
        self.handleSetProfile(profile=profile)

    def handleAppendProfile(self):
        self.childWindow = Toplevel(self.master)
        self.childWindow.title('Append Profile')
        self.setWindowIcon(self.childWindow)
        self.childWindow.geometry('300x300')
        self.profileToAppend = StringVar(self.master)
        setProfile = OptionMenu(self.childWindow, self.profileToAppend, *self.profileList())
        setProfile.pack(fill=X, expand=YES)
        self.appendCheckList = CheckList(self.childWindow, ['options', 'numbers'])
        self.appendCheckList.pack(fill=X, expand=YES)
        createButton = Button(self.childWindow, text='Append', command=self.appendSelectedProfile)
        createButton.pack(fill=X, expand=YES)

    def nextProfile(self):
        profiles = self.profilesSelect.get()
        if len(profiles) == 0:
            self.logger.warning('Could not change profile because no profiles are marked as switchable.')
            return
        try:
            current = profiles.index(self.profile.get())
        except ValueError:
            current = -1
        try:
            new = profiles[current+1]
        except IndexError:
            new = profiles[0]
        if new == None:
            self.logger.warning('Could not change profile because there are no profiles to change to.')
            return
        self.profile.set(new)
        self.handleSetProfile()

        self.timeSinceOverlayOpened = time.time()
        if self.overlayGeneral.get() == 1:
            self.enableOverlay()

        self.logger.system('Change current profile to ' + new)

    def checkToDisableOverlay(self):
        try:
            if self.overlayWindow.winfo_exists() == 1:
                if time.time() - self.timeSinceOverlayOpened > 1:
                    self.disableOverlay()
        except AttributeError:
            pass

    def readSetting(self):
        f = open('config.ini', 'r')
        self.hotkey.set(f.readline().strip())
        self.profileHotkey.set(f.readline().strip())
        self.overlayGeneral.set(int(f.readline().strip()))
        self.profile.set(f.readline().strip())
        if self.profile.get() in self.profileList():
            self.handleSetProfile()
        self.profilesSelect.update(json.loads(f.readline()), updateTo=1)
        f.close
        self.refreshProfiles()

    def writeSetting(self):
        f = open('config.ini', 'w')
        f.write(self.hotkey.get()+'\n')
        f.write(self.profileHotkey.get()+'\n')
        f.write(str(self.overlayGeneral.get())+'\n')
        f.write(self.profile.get()+'\n')
        f.write(json.dumps(self.profilesSelect.get()))
        f.close()

    def changeLevel(self, level):
        self.logger.setLevel({v: k for k, v in logging._levelToName.items()}[level])

    def clearLog(self):
        f = open('log.txt', 'w').close()
        self.log.configure(state='normal')
        self.log.delete('1.0', END)
        self.log.configure(state='disabled')

    def enableOverlay(self):
        try:
            if self.overlayWindow.winfo_exists() == 1:
                return
        except AttributeError:
            pass

        self.overlayWindow = OverlayWindow(self.master)

        self.overlayWindow.log = scrolledtext.ScrolledText(self.overlayWindow, width=100, height=10, state='disabled')
        self.overlayWindow.log.grid(row=0, column=0)

        self.overlayWindow.textHandler = TextHandler(self.overlayWindow.log)
        self.overlayWindow.textHandler.setLevel(logging.DEBUG)
        self.overlayWindow.textHandler.setFormatter(self.formatter)
        self.logger.addHandler(self.overlayWindow.textHandler)

    def disableOverlay(self):
        try:
            self.overlayWindow.destroy()
            self.logger.handlers = [ h for h in self.logger.handlers if not isinstance(h, TextHandler) ]
            self.logger.addHandler(self.textHandler)
        except AttributeError:
            pass

    def updateTextHandlers(self):
        for textHandler in [ h for h in self.logger.handlers if isinstance(h, TextHandler) ]:
            textHandler.clearBacklog()


class ScrollFrame(Frame):
    # from https://gist.github.com/mp035/9f2027c3ef9172264532fcd6262f3b01
    def __init__(self, parent, dimensions):
        super().__init__(parent)

        self.width, self.height = dimensions

        self.canvas = Canvas(self, borderwidth=0, background='#F0F0F0', width=dimensions[0], height=dimensions[1])
        self.viewPort = Frame(self.canvas, background='#F0F0F0')
        self.hsb = Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.hsb.set)
        self.vsb = Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.hsb.pack(side="bottom", fill="x")
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)
        self.canvas.bind("<Configure>", self.onCanvasConfigure)
        self.onFrameConfigure(None)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        self.canvas.scale("all",0,0,wscale,hscale)

        self.canvas.itemconfig(self.canvas_window)
