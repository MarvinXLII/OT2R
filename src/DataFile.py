class DataFile:
    def __init__(self, pak, filename):
        self.filename = filename
        self.data = pak.extract_file(filename)

    def patch_int32(self, addr, value):
        self.data[addr:addr+4] = value.to_bytes(4, byteorder='little')

    def update(self, pak, force=False):
        pak.update_data(self.filename, self.data, force=force)
