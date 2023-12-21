from Manager import Manager
from Assets import DataAsset
from Utility import get_filename, File
import bsdiff4
import pickle
import lzma

PATCHES = pickle.load(lzma.open(get_filename('lzma/image.xz'), 'rb'))

class TitleSteam:
    def __init__(self):
        self.x1 = TitleSteamX1()
        self.x2 = TitleSteamX2()
        self.x3 = TitleSteamX3()

    def patch(self):
        self.x1.update_title()
        self.x2.update_title()
        self.x3.update_title()


class Image(DataAsset):
    def __init__(self, filename, include_patches=True):
        self.data = Manager.get_asset(filename, include_patches=False)
        
    @property
    def image(self):
        return self.data.uasset.exports[1].uexp2

    @image.setter
    def image(self, image):
        self.data.uasset.exports[1].uexp2 = image


class TitleSteamX3(Image):
    offset = 0x44
    filename = 'UiTX_Title_LogoAdd_x3'
    patchname = 'image/UiTX_Title_LogoAdd_x3.bin'

    def __init__(self):
        super().__init__(self.filename, include_patches=False)
        fdata = File(self.image)
        fdata.seek(self.offset)
        self.image_size = fdata.read_uint32()

    @classmethod
    def _load_patch(cls):
        assert cls.patchname in PATCHES
        return PATCHES[cls.patchname]

    def update_title(self):
        patch = self._load_patch()

        end = -24
        start = end - self.image_size

        vanilla = bytes(self.image[start:end])
        mod = bsdiff4.patch(vanilla, patch)

        image = bytearray(self.image)
        image[start:end] = mod
        self.image = image


class TitleSteamX2(TitleSteamX3):
    offset = 0x44
    filename = 'UiTX_Title_LogoAdd_x2'
    patchname = 'image/UiTX_Title_LogoAdd_x2.bin'


class TitleSteamX1(TitleSteamX3):
    offset = 0x14
    filename = 'UiTX_Title_LogoAdd'
    patchname = 'image/UiTX_Title_LogoAdd.bin'

    def __init__(self):
        super(TitleSteamX3, self).__init__(self.filename, include_patches=False)
        self.image_size = 0xc4e00
