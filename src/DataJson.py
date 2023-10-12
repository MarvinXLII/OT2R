import os
import json
from copy import deepcopy
import sys

class JsonCommand:
    branch_opt = [3120, 4000, 5090, 5500]
    while_opt = [7420]
    goto_target = [5]
    item_count = [4200]
    
    def __init__(self, command):
        for k, v in command.items():
            setattr(self, k, v)
        self.branches = [None, None]

    def add_true_branch(self, cmd):
        self.branches[0] = cmd

    def add_false_branch(self, cmd):
        self.branches[1] = cmd

    def add_branch(self, commands):
        # CHECK IF/ELSE
        if self.cmd in self.branch_opt:
            for i, o in enumerate(self.opt):
                if o == "":
                    self.opt[i] = None
                else:
                    index = int(self.opt[i])
                    self.opt[i] = commands[index]

        # CHECK WHILE
        if self.cmd in self.while_opt:
            self.opt[1] = commands[int(self.opt[1])]
            self.opt[2] = commands[int(self.opt[2])]

        # CHECK GOTO
        if self.cmd in self.goto_target:
            self.target = commands[self.target]

        # ITEM COUNT
        if self.cmd in self.item_count:
            self.opt[2] = commands[int(self.opt[2])]
            self.opt[3] = commands[int(self.opt[3])]
            

    def update_branch(self, commands):
        if self.cmd in self.branch_opt:
            for i, o in enumerate(self.opt):
                if o is None:
                    self.opt[i] = ""
                else:
                    index = commands.index(o)
                    self.opt[i] = str(index)

        if self.cmd in self.while_opt:
            self.opt[1] = str(commands.index(self.opt[1]))
            self.opt[2] = str(commands.index(self.opt[2]))

        if self.cmd in self.goto_target:
            self.target = commands.index(self.target)

        if self.cmd in self.item_count:
            self.opt[2] = str(commands.index(self.opt[2]))
            self.opt[3] = str(commands.index(self.opt[3]))

    # __dict__ will affect deepcopy
    def make_dict(self):
        d = {k: getattr(self, k) for k in ['cmd', 'target', 'pos', 'dir', 'text', 'async', 'opt']}
        return d
        

class DataJson:
    def __init__(self, pak, filename):
        self.filename = filename
        json_dict = eval(pak.extract_file(filename))
        self.initialize(json_dict)

    def initialize(self, json_dict):
        self.reset()
        for command in json_dict.values():
            jc = JsonCommand(command)
            self.add_command(jc)
        self.set_branches()

    def reset(self):
        self.json_list = []
        self.flags = {}
        self.flag_checks = {}

    def set_branches(self):
        for command in self.json_list:
            command.add_branch(self.json_list)

    def add_command(self, command, index=None):
        self.json_list.append(command)
        self.add_flag(command)

    def insert_command(self, command, index):
        if index < 0:
            index = len(self.json_list) + index
        self.json_list.insert(index, command)
        self.add_flag(command)

    def remove_command(self, index):
        return self.json_list.pop(index)

    def replace_command(self, command, index):
        self.remove_command(index)
        self.insert_command(command, index)

    def add_flag(self, command):
        if command.cmd == 70 or command.cmd == 71:
            if command.target not in self.flags:
                self.flags[command.target]  = []
            self.flags[command.target].append(command)
        if command.cmd == 4000:
            if command.target not in self.flag_checks:
                self.flag_checks[command.target]  = []
            self.flag_checks[command.target].append(command)

    def toggle_flag_off(self, flag):
        for command in self.flags[flag]:
            assert len(command.opt) == 1
            assert command.opt[0] == '1'
            command.opt[0] = '0'

    def toggle_flag_on(self, flag):
        for command in self.flags[flag]:
            assert len(command.opt) == 1
            assert command.opt[0] == '0'
            command.opt[0] = '1'

    def change_flag(self, old, new):
        if old in self.flags:
            for command in self.flags[old]:
                command.target = new
        if old in self.flag_checks:
            for command in self.flag_checks[old]:
                command.target = new

    def filter_out_command(self, cmd):
        self.json_list = list(filter(lambda x: x.cmd != cmd, self.json_list))

    def remove_script_call(self):
        self.filter_out_command(1000)

    def remove_fadeout(self):
        self.filter_out_command(62)

    def remove_give_item(self, item_key):
        new_list = []
        for x in self.json_list:
            if x.opt[0] == item_key and x.cmd == 2000:
                continue
            new_list.append(x)
        self.json_list = new_list

    def remove_display_item(self, item_key):
        new_list = []
        for x in self.json_list:
            if x.opt[0] == item_key and x.cmd == 5005:
                continue
            new_list.append(x)
        self.json_list = new_list

    def insert_script(self, script, index):
        if index < 0:
            index = len(self.json_list) + index
        # deepcopy important when script is used multiple time
        # otherwise opt in branches will be converted back to strings
        # the first time the script is inserted
        for i, command in enumerate(deepcopy(script.json_list)):
            self.insert_command(command, index + i)
        # self.set_branches()

    def make_script(self):
        for command in self.json_list:
            command.update_branch(self.json_list)
        json_dict = {str(k): v.make_dict() for k, v in enumerate(self.json_list)}
        b = bytearray(json.dumps(json_dict).encode('ascii'))
        b = b.replace(b'" "', b'--TEMP--') # commands can have " " as arguments
        b = b.replace(b' ', b'')
        b = b.replace(b'}', b'}\r\n')
        b = b.replace(b'--TEMP--', b'" "')
        assert b[0] == ord('{')
        b = b'{\r\n' + b[1:]
        return b

    def update(self, pak, force=False):
        script = self.make_script()
        pak.update_data(self.filename, script, force=force)


class DataJsonFile(DataJson):
    def __init__(self, data):
        json_dict = eval(data)
        self.initialize(json_dict)

    def update(self, *args):
        pass

