import os
import json


class JsonCommand:
    def __init__(self, command):
        for k, v in command.items():
            setattr(self, k, v)


class DataJson:
    def __init__(self, pak, filename):
        self.filename = filename
        jsonDict = eval(pak.extractFile(filename))
        self.jsonList = []
        self.flags = {}
        for command in jsonDict.values():
            jc = JsonCommand(command)
            self.addCommand(jc)

    def addCommand(self, jCommand, index=None):
        self.jsonList.append(jCommand)
        self.addFlag(jCommand)

    def insertCommand(self, jCommand, index):
        self.jsonList.insert(index, jCommand)
        self.addFlag(jCommand)

    def addFlag(self, jCommand):
        if jCommand.cmd == 70:
            if jCommand.target not in self.flags:
                self.flags[jCommand.target]  = []
            self.flags[jCommand.target].append(jCommand)

    def toggleFlagOff(self, flag):
        for command in self.flags[flag]:
            assert len(command.opt) == 1
            assert command.opt[0] == '1'
            command.opt[0] = '0'

    def toggleFlagOn(self, flag):
        for command in self.flags[flag]:
            assert len(command.opt) == 1
            assert command.opt[0] == '0'
            command.opt[0] = '1'

    def changeFlag(self, old, new):
        if old in self.flags:
            for command in self.flags[old]:
                command.target = new

    def update(self, pak, force=False):
        jsonDict = {str(k): v.__dict__ for k, v in enumerate(self.jsonList)}
        b = bytearray(json.dumps(jsonDict).encode('ascii'))
        b = b.replace(b'" "', b'--TEMP--') # commands can have " " as arguments
        b = b.replace(b' ', b'')
        b = b.replace(b'}', b'}\r\n')
        b = b.replace(b'--TEMP--', b'" "')
        assert b[0] == ord('{')
        b = b'{\r\n' + b[1:]
        pak.updateData(self.filename, b, force=force)
