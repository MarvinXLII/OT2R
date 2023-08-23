import tkinter as tk
from tkinter import ttk, filedialog, Listbox
from release import RELEASE
import hjson
import random
import traceback
import os
import sys

from builder import builder_setup

sys.path.append('src')
from Utility import get_filename
from Randomizer import Steam

from Pak import Pak
from PakMod import PatchPak

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
    def __init__(self, frame, patches=None):
        self.left_frame = tk.Frame(frame)
        self.right_frame = tk.Frame(frame)
        frame.columnconfigure(1, weight=3)

        self.scrollbar = tk.Scrollbar(self.right_frame, orient='vertical')
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky='news')
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky='news')
        self.patches = []

        self.listbox = Listbox(self.right_frame, yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        self.listbox.pack(fill='both', expand=True)

        def move_up():
            idxs = self.listbox.curselection()
            if not idxs:
                return
            for pos in idxs:
                if pos == 0:
                    continue
                entry_curr = self.listbox.get(pos)
                entry_other = self.listbox.get(pos-1)
                title_curr = entry_curr.title().split(' ')
                title_other = entry_other.title().split(' ')
                title_curr[0], title_other[0] = title_other[0], title_curr[0]
                title_curr = ' '.join(title_curr)
                title_other = ' '.join(title_other)
                self.listbox.delete(pos-1)
                self.listbox.delete(pos-1)
                self.listbox.insert(pos-1, title_other)
                self.listbox.insert(pos-1, title_curr)
                self.patches[pos], self.patches[pos-1] = self.patches[pos-1], self.patches[pos]
                entry = self.listbox.get(pos-1)
                self.listbox.selection_set(pos-1)
            self.write_patch_names()

        def move_down():
            idxs = self.listbox.curselection()
            if not idxs:
                return
            for pos in idxs:
                if pos+1 == len(self.patches):
                    continue
                entry_curr = self.listbox.get(pos)
                entry_other = self.listbox.get(pos+1)
                title_curr = entry_curr.title().split(' ')
                title_other = entry_other.title().split(' ')
                title_curr[0], title_other[0] = title_other[0], title_curr[0]
                title_curr = ' '.join(title_curr)
                title_other = ' '.join(title_other)
                self.listbox.delete(pos)
                self.listbox.delete(pos)
                self.listbox.insert(pos, title_curr)
                self.listbox.insert(pos, title_other)
                self.patches[pos], self.patches[pos+1] = self.patches[pos+1], self.patches[pos]
                entry = self.listbox.get(pos+1)
                self.listbox.selection_set(pos+1)
            self.write_patch_names()

        def del_patch():
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
            self.write_patch_names()

        self.load_patch = tk.Button(self.left_frame, text='Load Mod', command=self.get_patch)
        self.del_patch = tk.Button(self.left_frame, text='Delete Mod', command=del_patch)
        self.move_up_button = tk.Button(self.left_frame, text='Up', command=move_up)
        self.move_down_button = tk.Button(self.left_frame, text='Down', command=move_down)
        empty = tk.Label(self.left_frame, height=1)

        self.load_patch.grid(row=0, column=0, sticky='news')
        self.del_patch.grid(row=1, column=0, sticky='news')
        empty.grid(row=2, column=0, sticky='news')
        self.move_up_button.grid(row=3, column=0, sticky='news')
        self.move_down_button.grid(row=4, column=0, sticky='news')

        if patches:
            for filename in patches:
                self.load_pak(filename)

    def get_patch(self):
        filename = filedialog.askopenfilename(filetypes=(("Pak files", "*.pak"), ("All files", "*.*")))
        if not filename:
            return

        self.load_pak(filename)

    def load_pak(self, filename):
        if not os.path.isfile(filename):
            return

        patch = None

        try:
            patch = PatchPak(filename)
        except:
            pass

        if patch is None:
            try:
                patch = Pak(filename)
            except:
                print("couldn't load the patch",  filename)
                return

        if patch not in self.patches:
            self.patches.append(patch)
        else:
            return

        p = os.path.split(filename)
        np = len(self.patches)
        self.listbox.insert(np, f"{np}) {p[-1]}")
        self.write_patch_names()

    def write_patch_names(self):
        with open('previous_patches.txt', 'w') as file:
            for pak in self.patches:
                file.write(pak.filename + '\n')


class GuiApplication:
    def __init__(self, settings=None, pakfile=None, patches=None):
        self.master = tk.Tk()
        self.master.geometry('750x650') # width x height
        self.master.title(MAIN_TITLE)
        self.initialize_gui(patches)
        self.initialize_settings(settings)
        self.initialize_pakfile(pakfile)
        self.master.mainloop()


    def initialize_gui(self, patches):

        self.warnings = []
        self.settings = {}
        self.settings['release'] = tk.StringVar()
        self.pakfile = tk.StringVar()
        self.mod = None

        with open(get_filename('json/gui.json'), 'r') as file:
            self.json_file = hjson.loads(file.read())

        #####################
        # PAKS FOLDER STUFF #
        #####################

        labelfonts = ('Helvetica', 14, 'bold')
        lf = tk.LabelFrame(self.master, text='Pak File', font=labelfonts)
        lf.grid(row=0, columnspan=2, sticky='nsew', padx=5, pady=5, ipadx=5, ipady=5)

        # Path to paks
        self.pakfile.set('')

        pak_filename = tk.Entry(lf, textvariable=self.pakfile, width=75, state='readonly')
        pak_filename.grid(row=0, column=0, columnspan=2, padx=(10,0), pady=3)

        pak_label = tk.Label(lf)#, text='Pak file')
        pak_label.grid(row=1, column=0, sticky='w', padx=5, pady=2)

        pak_button = tk.Button(lf, text='Browse ...', command=self.get_pakfile, width=20) # needs command..
        pak_button.grid(row=1, column=1, sticky='e', padx=5, pady=2)
        self.build_tool_tip(pak_button,
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
        self.random_seed()

        box = tk.Spinbox(lf, from_=0, to=1e8, width=9, textvariable=self.settings['seed'])
        box.grid(row=2, column=0, sticky='e', padx=60)

        seed_btn = tk.Button(lf, text='Random Seed', command=self.random_seed, width=12, height=1)
        seed_btn.grid(row=3, column=0, columnspan=1, sticky='we', padx=30, ipadx=30)

        self.randomize_btn = tk.Button(lf, text='Randomize', command=self.randomize, height=1)
        self.randomize_btn.grid(row=4, column=0, columnspan=1, sticky='we', padx=30, ipadx=30)

        ############
        # SETTINGS #
        ############

        # Tabs setup
        tab_control = ttk.Notebook(self.master)
        tabs = {name: ttk.Frame(tab_control) for name in self.json_file}
        for name, tab in tabs.items():
            tab_control.add(tab, text=name)
        tab_control.grid(row=2, column=0, columnspan=20, sticky='news')

        # options
        self.button_data = [] # (variable, button, command, children)
        for tab_name, tab in tabs.items():
            fields = self.json_file[tab_name]
            col = 0
            for i, (key, value) in enumerate(fields.items()):
                row = i // 2
                col = i % 2
                lf = tk.LabelFrame(tab, text=key, font=labelfonts)
                lf.grid(row=row, column=col, padx=10, pady=5, ipadx=12, ipady=5, sticky='news')

                row = 0
                for s_key, stuff in value.items():
                    if 'type' in stuff and stuff['type'] == 'SpinBox':
                        self.add_box(lf, row, s_key, stuff)
                        row += 1
                    elif 'type' in stuff and stuff['type'] == 'OptionMenu':
                        self.add_options(lf, row, s_key, stuff, offset=10)
                        row += 1
                    else:
                        button = self.add_button(lf, row, 0, s_key, stuff, offset=10)
                        row += 1
                        if 'indent' in stuff:
                            _, _, _, children = self.button_data[-1]
                            for m_key, more_stuff in stuff['indent'].items():
                                b = self.add_button(lf, row, 0, m_key, more_stuff, offset=30, state=tk.DISABLED)
                                children.append(b)
                                row += 1

        if 'Other Mods' in tabs:
            other_mods = tabs['Other Mods']
            self.patch_tab = Patches(other_mods, patches)
        else:
            self.patch_tab = None

        # For warnings/text at the bottom
        self.canvas = tk.Canvas()
        self.canvas.grid(row=6, column=0, columnspan=20, pady=10)

    def add_button(self, frame, row, col, key, stuff, offset=0, state=tk.NORMAL):
        text = stuff['label']
        children = []
        variable = tk.BooleanVar()
        command = self.make_toggler(variable, stuff)
        button = ttk.Checkbutton(frame, text=text, variable=variable, command=command, state=state)
        button.grid(row=row, column=col, padx=offset, sticky='w')
        self.button_data.append((variable, button, command, children))
        self.build_tool_tip(button, stuff)
        assert key not in self.settings
        self.settings[key] = variable
        return button

    def add_box(self, frame, row, key, stuff):
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
        box = tk.Spinbox(frame, from_=stuff['min'], to=stuff['max'], increment=stuff['increment'], textvariable=variable, width=4, state='readonly')
        box.grid(row=row, column=1, sticky='w')
        assert key not in self.settings
        self.settings[key] = variable

    def add_options(self, frame, row, key, stuff, offset=0):
        text = stuff['label']
        ttk.Label(frame, text=text).grid(row=row, column=0, padx=offset, sticky='w')
        options = stuff['options']
        assert options[0] == 'None'
        variable = tk.StringVar()
        variable.set('None')
        box = tk.OptionMenu(frame, variable, *stuff['options'])
        box.config(width=10)
        box.grid(row=row, column=1, sticky='e')
        assert key not in self.settings
        self.settings[key] = variable

    def get_button_data(self, variable=None, button=None, command=None):
        for v, b, c, d in self.button_data:
            if variable and variable == v:
                break
            if button and button == b:
                break
            if command and command == c:
                break
        else:
            sys.exit("Variable not stored in button_data!")
        return v, b, c, d

    def make_toggler(self, variable, stuff):
        def f():
            _, _, _, children = self.get_button_data(variable)
            if variable.get():
                for btn in children:
                    btn.config(state=tk.NORMAL)
            else:
                for btn in children:
                    var, _, com, _ = self.get_button_data(button=btn)
                    btn.config(state=tk.DISABLED)
                    var.set(False)
                    com()
        return f

    def get_pakfile(self):
        pakfile = filedialog.askopenfilename(filetypes=(("Pak files", "*.pak"), ("All files", "*.*")))
        if pakfile:
            self.load_pak_file(pakfile)

    def load_pak_file(self, pakfile):
        self.clear_bottom_labels()
        if not os.path.isfile(pakfile):
            return False

        self.bottom_label('Loading Pak....', 'blue', 0)
        with open(pakfile, 'rb') as file:
            file.seek(-0xb4, 2)
            sha = int.from_bytes(file.read(20), byteorder='big')

        if sha == 0x224cb63a1cb9b939ab3c0102b113909dcfd05bae:
            try:
                self.mod = Steam(pakfile)
            except:
                self.pakfile.set('')
                self.clear_bottom_labels()
                self.bottom_label('Error parsing the Steam release pak file.', 'red', 0)
                return False

        else:
            self.mod = None
            self.pakfile.set('')
            self.clear_bottom_labels()
            self.bottom_label('This pak file is incompatible with the randomizer.','red',0)
            return False

        self.bottom_label('Done', 'blue', 1)
        self.pakfile.set(pakfile)
        with open('previous_pak.txt', 'w') as file:
            file.write(pakfile)

        return True

    def build_tool_tip(self, button, field, wraplength=200):
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
        for _, _, command, _ in self.button_data:
            command()

    def initialize_pakfile(self, pakfile):
        if pakfile:
            loaded = self.load_pak_file(pakfile)
            if not loaded:
                self.clear_bottom_labels()

    def bottom_label(self, text, fg, row):
        L = tk.Label(self.canvas, text=text, fg=fg)
        L.grid(row=row, columnspan=20)
        self.warnings.append(L)
        self.master.update()

    def clear_bottom_labels(self):
        while self.warnings != []:
            warning = self.warnings.pop()
            warning.destroy()
        self.master.update()
        
    def random_seed(self):
        self.settings['seed'].set(random.randint(0, 99999999))

    def randomize(self):
        if self.pakfile.get() == '':
            self.clear_bottom_labels()
            self.bottom_label('Must load an appropriate pak file.', 'red', 0)
            return

        settings = { key: value.get() for key, value in self.settings.items() }
        with open('settings.json', 'w') as file:
            hjson.dump(settings, file)

        self.clear_bottom_labels()
        self.bottom_label('Randomizing....', 'blue', 0)

        # Link patches -- list from highest to lowest priority
        if self.patch_tab:
            self.mod.add_patches(self.patch_tab.patches)

        if randomize(self.mod, settings):
            self.clear_bottom_labels()
            self.bottom_label('Randomizing...done! Good luck!', 'blue', 0)
        else:
            self.clear_bottom_labels()
            self.bottom_label('Randomizing failed.', 'red', 0)


def randomize(mod, settings):
    try:
        builder_setup(settings)
        mod.initialize(settings['seed'])
        mod.randomize()
        mod.qualityOfLife() # keep this AFTER randomizing
        mod.dump(settings)
        return True
    except:
        traceback.print_exc()
        mod.failed()
        return False


if __name__ == '__main__':
    settings_file = None
    if len(sys.argv) > 2:
        print('Usage: python gui.py <settings.json>')
    elif len(sys.argv) == 2:
        settings_file = sys.argv[1]
    else:
        if os.path.isfile('settings.json'):
            settings_file = 'settings.json'

    exe_path = os.path.dirname(sys.argv[0])
    if exe_path:
        os.chdir(exe_path)

    pakfile = None
    if os.path.isfile('previous_pak.txt'):
        with open('previous_pak.txt', 'r') as file:
            pakfile = file.readline().rstrip('\n').rstrip('\r')

    patches = []
    if os.path.isfile('previous_patches.txt'):
        with open('previous_patches.txt', 'r') as file:
            for line in file.read().splitlines():
                patches.append(line)

    settings = None
    if settings_file:
        with open(settings_file, 'r') as file:
            settings = hjson.load(file)

    GuiApplication(settings, pakfile, patches)
