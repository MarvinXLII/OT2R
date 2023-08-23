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
def get_filename(relative_path):
    if os.path.exists(relative_path):
        filename = relative_path
    else:
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        filename = os.path.join(base_path, relative_path)
    return filename


class Byte:
    @staticmethod
    def getInt8(value):
        return struct.pack("<b", value)

    @staticmethod
    def getUInt8(value):
        return struct.pack("<B", value)

    @staticmethod
    def getInt16(value):
        return struct.pack("<h", value)

    @staticmethod
    def getUInt16(value):
        return struct.pack("<H", value)

    @staticmethod
    def getInt32(value):
        return struct.pack("<l", value)

    @staticmethod
    def getUInt32(value):
        return struct.pack("<L", value)

    @staticmethod
    def getInt64(value):
        return struct.pack("<q", value)

    @staticmethod
    def getUInt64(value):
        return struct.pack("<Q", value)

    @staticmethod
    def getFloat(value):
        return struct.pack("<f", value)

    @staticmethod
    def getDouble(value):
        return struct.pack("<d", value)

    @staticmethod
    def getStringUTF8(string):
        return string.encode() + b'\x00'

    @staticmethod
    def getString(string, nbytes=4, utf=None):
        tmp = string.encode()
        if string:
            tmp += b'\x00'
        for t in tmp:
            if t & 0x80:
                st = string.encode(encoding='UTF-16')[2:] + b'\x00\x00'
                size = Byte.getInt32(-int(len(st)/2))
                return size + st
        if nbytes == 4:
            return Byte.getInt32(len(tmp)) + tmp
        elif nbytes == 8:
            return Byte.getInt64(len(tmp)) + tmp
        else:
            sys.exit(f"Not setup for {nbytes} nbytes")

    @staticmethod
    def getSHA(sha):
        return sha.encode() + b'\x00'


class File(Byte):
    def __init__(self, data):
        self.data = None
        self.setData(data)
        self.vanilla = self.getData()
        self.isPatched = False

    def setData(self, data):
        self.size = len(data)
        self.data = io.BytesIO(data)

    def getData(self):
        return bytearray(self.data.getbuffer())

    def patchData(self, patch):
        data = bsdiff4.patch(bytes(self.vanilla), bytes(patch))
        self.setData(data)
        self.isPatched = True

    def getPatch(self, mod):
        return bsdiff4.diff(bytes(self.vanilla), bytes(mod))

    def tell(self):
        return self.data.tell()

    def seek(self, addr):
        self.data.seek(addr)
        
    def readBytes(self, size=None):
        if size is None:
            return self.data.read()
        return self.data.read(size)

    def readString(self, size=None):
        if size is None:
            size = self.readInt32()
        if size < 0:
            s = self.readBytes(-size*2)
            return s.decode('utf-16')[:-1]
        if size > 0:
            s = self.readBytes(size)
            return s.decode('utf-8')[:-1]
        return ''

    def readInt(self, size, signed):
        return int.from_bytes(self.data.read(size), byteorder='little', signed=signed)

    def readInt8(self):
        return self.readInt(1, True)

    def readInt16(self):
        return self.readInt(2, True)

    def readInt32(self):
        return self.readInt(4, True)

    def readInt64(self):
        return self.readInt(8, True)

    def readUInt8(self):
        return self.readInt(1, False)

    def readUInt16(self):
        return self.readInt(2, False)

    def readUInt32(self):
        return self.readInt(4, False)

    def readUInt64(self):
        return self.readInt(8, False)

    def readFloat(self):
        return struct.unpack("<f", self.data.read(4))[0]

    def readDouble(self):
        return struct.unpack("<d", self.data.read(8))[0]

    def readSHA(self):
        sha = self.readBytes(0x20).decode()
        assert self.readUInt8() == 0
        return sha
