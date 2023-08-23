import tkinter as tk
from tkinter import ttk, filedialog, Listbox
from release import RELEASE
import hjson
import random
import traceback
import os
import sys
sys.path.append('src')
from Utility import get_filename
from Randomizer import Steam, Rando

from Pak import Pak

# builders
from Shuffler import Shuffler, noWeights
from JP import JPCosts, AdvJPNerf
from Weapons import Weapons
from Support import Support
from Command import Command
from AbilityWeapons import AbilityWeapons
from AbilitySP import AbilitySP
from AbilityPower import AbilityPower
from JobStats import JobStatsFair, JobStatsRandom
from Treasures import Treasures
from ProcessedSpecies import Process
from Shields import Shields
from Battles import *
from EnemyGroups import *
from PathActions import *
from Nothing import Nothing
from Shuffler import noWeights
from SpurningRibbon import SpurningRibbon
from Guilds import Guilds, shuffleRequirements
from Command import separateAdvancedCommands, separateDivine, separateExAbilities
from Support import separateAdvancedSupport, evasiveManeuversFirst
from Treasures import separateChapter
from Events import InitialEvents, formationMenuOn
from SkipTutorials import SkipTutorials

MAIN_TITLE = f"Octopath Traveler II Randomizer v{RELEASE}"

# Source: https://www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter
class CreateToolTip(object):
    '''
    create a tooltip for a given widget
    '''
    def __init__(self, widget, text='widget info', wraplength=200, dx=25, dy=25):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)
        self.wraplength = wraplength
        self.dx = dx
        self.dy = dy

    def enter(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + self.dx
        y += self.widget.winfo_rooty() + self.dy
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                      background='white', relief='solid', borderwidth=1,
                      wraplength=self.wraplength,
                      font=("times", "12", "normal"),
                      padx=4, pady=6,
        )
        label.pack(ipadx=1)

    def close(self, event=None):
        self.tw.destroy()
        # if self.tw:
        #     self.tw.destroy()


class Patches:
    def __init__(self, frame):
        self.leftFrame = tk.Frame(frame)
        self.rightFrame = tk.Frame(frame) 
        frame.columnconfigure(1, weight=3)

        self.scrollbar = tk.Scrollbar(self.rightFrame, orient='vertical')
        self.leftFrame.grid(row=0, column=0, padx=10, pady=10, sticky='news')
        self.rightFrame.grid(row=0, column=1, padx=10, pady=10, sticky='news')
        self.patches = []

        self.listbox = Listbox(self.rightFrame, yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        self.listbox.pack(fill='both', expand=True)

        def moveUp():
            idxs = self.listbox.curselection()
            if not idxs:
                return
            for pos in idxs:
                if pos == 0:
                    continue
                entrycurr = self.listbox.get(pos)
                entryother = self.listbox.get(pos-1)
                titlecurr = entrycurr.title().split(' ')
                titleother = entryother.title().split(' ')
                titlecurr[0], titleother[0] = titleother[0], titlecurr[0]
                titlecurr = ' '.join(titlecurr)
                titleother = ' '.join(titleother)
                self.listbox.delete(pos-1)
                self.listbox.delete(pos-1)
                self.listbox.insert(pos-1, titleother)
                self.listbox.insert(pos-1, titlecurr)
                self.patches[pos], self.patches[pos-1] = self.patches[pos-1], self.patches[pos]
                entry = self.listbox.get(pos-1)
                self.listbox.selection_set(pos-1)

        def moveDown():
            idxs = self.listbox.curselection()
            if not idxs:
                return
            for pos in idxs:
                if pos+1 == len(self.patches):
                    continue
                entrycurr = self.listbox.get(pos)
                entryother = self.listbox.get(pos+1)
                titlecurr = entrycurr.title().split(' ')
                titleother = entryother.title().split(' ')
                titlecurr[0], titleother[0] = titleother[0], titlecurr[0]
                titlecurr = ' '.join(titlecurr)
                titleother = ' '.join(titleother)
                self.listbox.delete(pos)
                self.listbox.delete(pos)
                self.listbox.insert(pos, titlecurr)
                self.listbox.insert(pos, titleother)
                self.patches[pos], self.patches[pos+1] = self.patches[pos+1], self.patches[pos]
                entry = self.listbox.get(pos+1)
                self.listbox.selection_set(pos+1)

        def delPatch():
            idxs = self.listbox.curselection()
            if not idxs:
                return
            for pos in idxs[::-1]:
                self.listbox.delete(pos)
                self.patches.pop(pos)
            # Update all priority numbers
            for pos, _ in enumerate(self.patches):
                num = pos + 1
                entry = self.listbox.get(pos)
                self.listbox.delete(pos)
                title = entry.title().split(' ')
                title[0] = f"{num})"
                title = ' '.join(title)
                self.listbox.insert(pos, title)

        self.moveUpButton = tk.Button(self.leftFrame, text='Up', command=moveUp)
        self.moveDownButton = tk.Button(self.leftFrame, text='Down', command=moveDown)
        self.loadPatch = tk.Button(self.leftFrame, text='Load Mod', command=self.getPatch)
        self.delPatch = tk.Button(self.leftFrame, text='Delete Mod', command=delPatch)

        self.moveUpButton.grid(row=0, column=0, sticky='news')
        self.moveDownButton.grid(row=1, column=0, sticky='news')
        self.loadPatch.grid(row=2, column=0, sticky='news')
        self.delPatch.grid(row=3, column=0, sticky='news')

    def getPatch(self):
        patch = filedialog.askopenfilename()
        if not patch:
            return

        if not os.path.isfile(patch):
            return

        try:
            p = Pak(patch)
        except:
            print("couldn't load the patch",  patch)
            return

        self.patches.append(Pak(patch))
        p = os.path.split(patch)
        np = len(self.patches)
        self.listbox.insert(np, f"{np}) {p[-1]}")
        
            


class GuiApplication:
    def __init__(self, settings=None, pakFile=None):
        self.master = tk.Tk()
        self.master.geometry('730x630') # width x height
        self.master.title(MAIN_TITLE)
        self.initialize_gui()
        self.initialize_settings(settings)
        self.initialize_pakFile(pakFile)
        self.master.mainloop()


    def initialize_gui(self):

        self.warnings = []
        self.settings = {}
        self.settings['release'] = tk.StringVar()
        self.pakFile = tk.StringVar()
        self.mod = None

        with open(get_filename('json/gui.json'), 'r') as file:
            self.jsonFile = hjson.loads(file.read())

        #####################
        # PAKS FOLDER STUFF #
        #####################

        labelfonts = ('Helvetica', 14, 'bold')
        lf = tk.LabelFrame(self.master, text='Pak File', font=labelfonts)
        lf.grid(row=0, columnspan=2, sticky='nsew', padx=5, pady=5, ipadx=5, ipady=5)

        # Path to paks
        self.pakFile.set('')

        pakFilename = tk.Entry(lf, textvariable=self.pakFile, width=75, state='readonly')
        pakFilename.grid(row=0, column=0, columnspan=2, padx=(10,0), pady=3)

        pakLabel = tk.Label(lf)#, text='Pak file')
        pakLabel.grid(row=1, column=0, sticky='w', padx=5, pady=2)

        pakButton = tk.Button(lf, text='Browse ...', command=self.getPakFile, width=20) # needs command..
        pakButton.grid(row=1, column=1, sticky='e', padx=5, pady=2)
        self.buildToolTip(pakButton,
                          """
Input the game's pak file:\n
Octopath_Traveler2-WindowsNoEditor.pak
                          """
                          , wraplength=500)

        #####################
        # SEED & RANDOMIZER #
        #####################

        lf = tk.LabelFrame(self.master, text="Seed", font=labelfonts)
        lf.grid(row=0, column=2, columnspan=2, sticky='nsew', padx=5, pady=5, ipadx=5, ipady=5)
        self.settings['seed'] = tk.IntVar()
        self.randomSeed()

        box = tk.Spinbox(lf, from_=0, to=1e8, width=9, textvariable=self.settings['seed'])
        box.grid(row=2, column=0, sticky='e', padx=60)

        seedBtn = tk.Button(lf, text='Random Seed', command=self.randomSeed, width=12, height=1)
        seedBtn.grid(row=3, column=0, columnspan=1, sticky='we', padx=30, ipadx=30)

        self.randomizeBtn = tk.Button(lf, text='Randomize', command=self.randomize, height=1)
        self.randomizeBtn.grid(row=4, column=0, columnspan=1, sticky='we', padx=30, ipadx=30)

        ############
        # SETTINGS #
        ############

        # Tabs setup
        tabControl = ttk.Notebook(self.master)
        tabs = {name: ttk.Frame(tabControl) for name in self.jsonFile}
        for name, tab in tabs.items():
            tabControl.add(tab, text=name)
        tabControl.grid(row=2, column=0, columnspan=20, sticky='news')

        # options
        self.buttonData = [] # (variable, button, command, children)
        self.spinboxData = []
        self.optionData = []
        for tabName, tab in tabs.items():
            fields = self.jsonFile[tabName]
            col = 0
            for i, (key, value) in enumerate(fields.items()):
                row = i // 2
                col = i % 2
                lf = tk.LabelFrame(tab, text=key, font=labelfonts)
                lf.grid(row=row, column=col, padx=10, pady=5, ipadx=30, ipady=5, sticky='news')

                row = 0
                for sKey, stuff in value.items():
                    if 'type' in stuff and stuff['type'] == 'SpinBox':
                        self.addBox(lf, row, sKey, stuff)
                        row += 1
                    elif 'type' in stuff and stuff['type'] == 'OptionMenu':
                        self.addOptions(lf, row, sKey, stuff, offset=10)
                        row += 1
                    else:
                        button = self.addButton(lf, row, 0, sKey, stuff, offset=10)
                        row += 1
                        if 'indent' in stuff:
                            _, _, _, children = self.buttonData[-1]
                            for mKey, moreStuff in stuff['indent'].items():
                                b = self.addButton(lf, row, 0, mKey, moreStuff, offset=30, state=tk.DISABLED)
                                children.append(b)
                                row += 1

        if 'Other Mods' in tabs:
            otherMods = tabs['Other Mods']
            self.patchTab = Patches(otherMods)

        # For warnings/text at the bottom
        self.canvas = tk.Canvas()
        self.canvas.grid(row=6, column=0, columnspan=20, pady=10)

    def addButton(self, frame, row, col, key, stuff, offset=0, state=tk.NORMAL):
        text = stuff['label']
        children = []
        variable = tk.BooleanVar()
        command = self.makeTogglerBuilder(variable, stuff)
        button = ttk.Checkbutton(frame, text=text, variable=variable, command=command, state=state)
        button.grid(row=row, column=col, padx=offset, sticky='w')
        self.buttonData.append((variable, button, command, children))
        self.buildToolTip(button, stuff)
        assert key not in self.settings
        self.settings[key] = variable
        return button

    def addBox(self, frame, row, key, stuff):
        text = stuff['label']
        ttk.Label(frame, text=text).grid(row=row, column=0, padx=10, sticky='w')
        if 'varType' in stuff:
            if stuff['varType'] == 'double':
                variable = tk.DoubleVar()
            else:
                variable = tk.IntVar()
        else:
            variable = tk.IntVar()
        variable.set(stuff['default'])
        command = self.makeBoxBuilder(variable, stuff)
        box = tk.Spinbox(frame, from_=stuff['min'], to=stuff['max'], increment=stuff['increment'], textvariable=variable, width=4, state='readonly', command=command)
        box.grid(row=row, column=1, sticky='w')
        self.spinboxData.append((variable, command))
        assert key not in self.settings
        self.settings[key] = variable

    def addOptions(self, frame, row, key, stuff, offset=0):
        text = stuff['label']
        ttk.Label(frame, text=text).grid(row=row, column=0, padx=offset, sticky='w')
        options = stuff['options']
        assert options[0] == 'None'
        variable = tk.StringVar()
        variable.set('None')
        command = self.makeOptionBuilder(variable, stuff)
        box = tk.OptionMenu(frame, variable, *stuff['options'], command=command)
        box.config(width=10)
        box.grid(row=row, column=1, sticky='e')
        self.optionData.append((variable, command))
        assert key not in self.settings
        self.settings[key] = variable

    def getButtonData(self, variable=None, button=None, command=None):
        for v, b, c, d in self.buttonData:
            if variable and variable == v:
                break
            if button and button == b:
                break
            if command and command == c:
                break
        else:
            sys.exit("Variable not stored in buttonData!")
        return v, b, c, d

    def makeTogglerBuilder(self, variable, stuff):
        def f():
            _, _, _, children = self.getButtonData(variable)
            c = eval(stuff['class'])
            a = stuff['attribute']
            assert hasattr(c, a), f"{c}, {a}"
            if variable.get():
                b = eval(stuff['builder'])
                assert b is not None
                setattr(c, a, b)
                for btn in children:
                    btn.config(state=tk.NORMAL)
            else:
                b = eval(stuff['default'])
                assert b is not None
                setattr(c, a, b)
                for btn in children:
                    var, _, com, _ = self.getButtonData(button=btn)
                    btn.config(state=tk.DISABLED)
                    var.set(False)
                    com()
        return f

    def makeBoxBuilder(self, variable, stuff):
        def f():
            c = eval(stuff['class'])
            a = stuff['attribute']
            setattr(c, a, variable.get())
        return f

    def makeOptionBuilder(self, variable, stuff):
        def f(*args):
            assert len(args) <= 1
            c = eval(stuff['class'])
            b = eval(stuff['builder'])
            d = eval(stuff['default'])
            a = stuff['attribute']
            oa = stuff['optionsAttr']
            v = variable.get()
            if v == 'None':
                setattr(c, a, d)
            else:
                setattr(c, a, b)
            setattr(b, oa, v)
        return f

    def getPakFile(self):
        pakFile = filedialog.askopenfilename()
        if pakFile:
            self.loadPakFile(pakFile)

    def loadPakFile(self, pakFile):
        self.clearBottomLabels()
        if not os.path.isfile(pakFile):
            return False

        self.bottomLabel('Loading Pak....', 'blue', 0)
        with open(pakFile, 'rb') as file:
            file.seek(-0xb4, 2)
            sha = int.from_bytes(file.read(20), byteorder='big')

        if sha == 0x224cb63a1cb9b939ab3c0102b113909dcfd05bae:
            try:
                self.mod = Steam(pakFile)
            except:
                self.pakFile.set('')
                self.clearBottomLabels()
                self.bottomLabel('Error parsing the Steam release pak file.', 'red', 0)
                return False

        else:
            self.mod = None
            self.pakFile.set('')
            self.clearBottomLabels()
            self.bottomLabel('This pak file is incompatible with the randomizer.','red',0)
            return False

        self.bottomLabel('Done', 'blue', 1)
        self.pakFile.set(pakFile)
        with open('previousPak.txt', 'w') as file:
            file.write(pakFile)

        return True

    def buildToolTip(self, button, field, wraplength=200):
        if isinstance(field, str):
            CreateToolTip(button, field, wraplength, dx=25, dy=35)
        if isinstance(field, dict):
            if 'help' in field:
                CreateToolTip(button, field['help'])

    def initialize_settings(self, settings):
        self.settings['release'].set(RELEASE)
        if settings is None:
            return
        for key, value in settings.items():
            if key == 'release':
                continue
            if key not in self.settings:
                continue
            self.settings[key].set(value)
        for _, _, command, _ in self.buttonData:
            command()
        for _, command in self.spinboxData:
            command()
        for _, command in self.optionData:
            command()

    def initialize_pakFile(self, pakFile):
        if pakFile:
            loaded = self.loadPakFile(pakFile)
            if not loaded:
                self.clearBottomLabels()

    def bottomLabel(self, text, fg, row):
        L = tk.Label(self.canvas, text=text, fg=fg)
        L.grid(row=row, columnspan=20)
        self.warnings.append(L)
        self.master.update()

    def clearBottomLabels(self):
        while self.warnings != []:
            warning = self.warnings.pop()
            warning.destroy()
        self.master.update()
        
    def randomSeed(self):
        self.settings['seed'].set(random.randint(0, 99999999))

    def randomize(self):
        if self.pakFile.get() == '':
            self.clearBottomLabels()
            self.bottomLabel('Must load an appropriate pak file.', 'red', 0)
            return

        settings = { key: value.get() for key, value in self.settings.items() }
        with open('settings.json', 'w') as file:
            hjson.dump(settings, file)

        self.clearBottomLabels()
        self.bottomLabel('Randomizing....', 'blue', 0)

        # Link patches -- list from highest to lowest priority
        try:
            self.mod.pak.patches = self.patchTab.patches
        except:
            pass

        if randomize(self.mod, settings['seed'], settings):
            self.clearBottomLabels()
            self.bottomLabel('Randomizing...done! Good luck!', 'blue', 0)
        else:
            self.clearBottomLabels()
            self.bottomLabel('Randomizing failed.', 'red', 0)


def randomize(mod, seed, settings):
    try:
        mod.initialize(seed)
        mod.randomize()
        mod.qualityOfLife() # keep this AFTER randomizing
        mod.dump(settings)
        return True
    except:
        traceback.print_exc()
        mod.failed()
        return False


if __name__ == '__main__':
    settingsFile = None
    if len(sys.argv) > 2:
        print('Usage: python gui.py <settings.json>')
    elif len(sys.argv) == 2:
        settingsFile = sys.argv[1]
    else:
        if os.path.isfile('settings.json'):
            settingsFile = 'settings.json'

    exePath = os.path.dirname(sys.argv[0])
    if exePath:
        os.chdir(exePath)

    pakFile = None
    if os.path.isfile('previousPak.txt'):
        with open('previousPak.txt', 'r') as file:
            pakFile = file.readline().rstrip('\n').rstrip('\r')

    settings = None
    if settingsFile:
        with open(settingsFile, 'r') as file:
            settings = hjson.load(file)

    GuiApplication(settings, pakFile)
