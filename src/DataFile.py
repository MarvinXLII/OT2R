class DataFile:
    def __init__(self, pak, filename):
        self.filename = filename
        self.data = pak.extractFile(filename)

    def patchInt32(self, addr, value):
        self.data[addr:addr+4] = value.to_bytes(4, byteorder='little')

    def update(self, pak, force=False):
        pak.updateData(self.filename, self.data, force=force)
