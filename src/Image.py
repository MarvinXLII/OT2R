from Manager import Manager
from Assets import DataAsset
from Utility import get_filename, File
import bsdiff4


class Image(DataAsset):
    def __init__(self, filename, include_patches=True):
        self.data = Manager.get_asset(filename, include_patches=False)
        
    @property
    def image(self):
        return self.data.uasset.exports[1].uexp2

    @image.setter
    def image(self, image):
        self.data.uasset.exports[1].uexp2 = image


class TitleSteam(Image):
    def __init__(self):
        super().__init__('UiTX_Title_LogoAdd_x3', include_patches=False)

        fdata = File(self.image)
        fdata.seek(0x44)
        self.image_size = fdata.read_uint32()

    def _loadPatch(self):
        with open(get_filename('image/UiTX_Title_LogoAdd_x3.bin'), 'rb') as file:
            pixels = file.read()
        return pixels

    def updateTitle(self):
        patch = self._loadPatch()

        start = -24 - self.image_size
        end = -24

        vanilla = bytes(self.image[start:end])
        mod = bsdiff4.patch(vanilla, patch)

        image = bytearray(self.image)
        image[start:end] = mod
        self.image = image
