import os
import sys
import io
import struct
import bsdiff4

PCNAMES = {
    'eDANCER': 'Agnea',
    'eALCHEMIST': 'Castti',
    'eFENCER': 'Hikari',
    'eHUNTER': 'Ochette',
    'ePROFESSOR': 'Osvald',
    'eMERCHANT': 'Partitio',
    'ePRIEST': 'Temenos',
    'eTHIEF': 'Throne',
}

PCNAMESMAP = {v:k for k, v in PCNAMES.items()}

BASEJOBS = {
    'eFENCER': 'Warrior',
    'eHUNTER': 'Hunter',
    'eALCHEMIST': 'Apothecary',
    'eMERCHANT': 'Merhant',
    'ePRIEST': 'Cleric',
    'ePROFESSOR': 'Scholar',
    'eTHIEF': 'Thief',
    'eDANCER': 'Dancer',
}

ADVJOBS = {
    'eWEAPON_MASTER': 'Armsmaster',
    'eWIZARD': 'Wizard',
    'eSHAMAN': 'Shaman',
    'eINVENTOR': 'Inventor',
}

JOBMAP = {**BASEJOBS, **ADVJOBS}

STATLIST = ['HP', 'MP', 'BP', 'SP', 'POT', 'ATK', 'DEF',
            'MATK', 'MDEF', 'ACC', 'EVA', 'CON', 'AGI']

WEAPONS = [
    'EWEAPON_CATEGORY::eSWORD',
    'EWEAPON_CATEGORY::eLANCE',
    'EWEAPON_CATEGORY::eDAGGER',
    'EWEAPON_CATEGORY::eAXE',
    'EWEAPON_CATEGORY::eBOW',
    'EWEAPON_CATEGORY::eROD',
]

# Required for pyinstaller
def get_filename(relpath):
    if os.path.exists(relpath):
        filename = relpath
    else:
        basepath = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        filename = os.path.join(basepath, relpath)
    return filename


class Byte:
    @staticmethod
    def get_int8(value):
        return struct.pack("<b", value)

    @staticmethod
    def get_uint8(value):
        return struct.pack("<B", value)

    @staticmethod
    def get_int16(value):
        return struct.pack("<h", value)

    @staticmethod
    def get_uint16(value):
        return struct.pack("<H", value)

    @staticmethod
    def get_int32(value):
        return struct.pack("<l", value)

    @staticmethod
    def get_uint32(value):
        return struct.pack("<L", value)

    @staticmethod
    def get_int64(value):
        return struct.pack("<q", value)

    @staticmethod
    def get_uint64(value):
        return struct.pack("<Q", value)

    @staticmethod
    def get_float(value):
        return struct.pack("<f", value)

    @staticmethod
    def get_double(value):
        return struct.pack("<d", value)

    @staticmethod
    def get_string_utf8(string):
        return string.encode() + b'\x00'

    @staticmethod
    def get_string(string, nbytes=4, utf=None):
        tmp = string.encode()
        if string:
            tmp += b'\x00'
        for t in tmp:
            if t & 0x80:
                st = string.encode(encoding='UTF-16')[2:] + b'\x00\x00'
                size = Byte.get_int32(-int(len(st)/2))
                return size + st
        if nbytes == 4:
            return Byte.get_int32(len(tmp)) + tmp
        elif nbytes == 8:
            return Byte.get_int64(len(tmp)) + tmp
        else:
            sys.exit(f"Not setup for {nbytes} nbytes")

    @staticmethod
    def get_sha(sha):
        return sha.encode() + b'\x00'


class File(Byte):
    def __init__(self, data):
        self.data = None
        self.set_data(data)
        self.vanilla = self.get_data()
        self.is_patched = False

    def set_data(self, data):
        self.size = len(data)
        self.data = io.BytesIO(data)

    def get_data(self):
        return bytearray(self.data.getbuffer())

    def patch_data(self, patch):
        data = bsdiff4.patch(bytes(self.vanilla), bytes(patch))
        self.set_data(data)
        self.is_patched = True

    def get_patch(self, mod):
        return bsdiff4.diff(bytes(self.vanilla), bytes(mod))

    def tell(self):
        return self.data.tell()

    def seek(self, addr):
        self.data.seek(addr)
        
    def read_bytes(self, size=None):
        if size is None:
            return self.data.read()
        return self.data.read(size)

    def read_string(self, size=None):
        if size is None:
            size = self.read_int32()
        if size < 0:
            s = self.read_bytes(-size*2)
            return s.decode('utf-16')[:-1]
        if size > 0:
            s = self.read_bytes(size)
            return s.decode('utf-8')[:-1]
        return ''

    def read_int(self, size, signed):
        return int.from_bytes(self.data.read(size), byteorder='little', signed=signed)

    def read_int8(self):
        return self.read_int(1, True)

    def read_int16(self):
        return self.read_int(2, True)

    def read_int32(self):
        return self.read_int(4, True)

    def read_int64(self):
        return self.read_int(8, True)

    def read_uint8(self):
        return self.read_int(1, False)

    def read_uint16(self):
        return self.read_int(2, False)

    def read_uint32(self):
        return self.read_int(4, False)

    def read_uint64(self):
        return self.read_int(8, False)

    def read_float(self):
        return struct.unpack("<f", self.data.read(4))[0]

    def read_double(self):
        return struct.unpack("<d", self.data.read(8))[0]

    def read_sha(self):
        sha = self.read_bytes(0x20).decode()
        assert self.read_uint8() == 0
        return sha
