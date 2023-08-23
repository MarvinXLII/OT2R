import os
import json


class JsonCommand:
    def __init__(self, command):
        for k, v in command.items():
            setattr(self, k, v)


class DataJson:
    def __init__(self, pak, filename):
        self.filename = filename
        json_dict = eval(pak.extract_file(filename))
        self.json_list = []
        self.flags = {}
        for command in json_dict.values():
            jc = JsonCommand(command)
            self.add_command(jc)

    def add_command(self, command, index=None):
        self.json_list.append(command)
        self.add_flag(command)

    def insert_command(self, command, index):
        self.json_list.insert(index, command)
        self.add_flag(command)

    def add_flag(self, command):
        if command.cmd == 70:
            if command.target not in self.flags:
                self.flags[command.target]  = []
            self.flags[command.target].append(command)

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

    def update(self, pak, force=False):
        json_dict = {str(k): v.__dict__ for k, v in enumerate(self.json_list)}
        b = bytearray(json.dumps(json_dict).encode('ascii'))
        b = b.replace(b'" "', b'--TEMP--') # commands can have " " as arguments
        b = b.replace(b' ', b'')
        b = b.replace(b'}', b'}\r\n')
        b = b.replace(b'--TEMP--', b'" "')
        assert b[0] == ord('{')
        b = b'{\r\n' + b[1:]
        pak.update_data(self.filename, b, force=force)
