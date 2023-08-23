from Assets import Data
from Utility import get_filename, File
import bsdiff4


class Image(Data):
    @property
    def data(self):
        return self.uasset.exports[1].uexp2

    @data.setter
    def data(self, data):
        self.uasset.exports[1].uexp2 = data


class TitleSteam(Image):
    def __init__(self):
        super().__init__('UiTX_Title_LogoAdd_x3.uasset', includePatches=False)

        fdata = File(self.data)
        fdata.seek(0x44)
        self.imageSize = fdata.readUInt32()

    def _loadPatch(self):
        with open(get_filename('image/UiTX_Title_LogoAdd_x3.bin'), 'rb') as file:
            pixels = file.read()
        return pixels

    def updateTitle(self):
        patch = self._loadPatch()

        start = -24 - self.imageSize
        end = -24

        vanilla = bytes(self.data[start:end])
        mod = bsdiff4.patch(vanilla, patch)

        data = bytearray(self.data)
        data[start:end] = mod
        self.data = data
