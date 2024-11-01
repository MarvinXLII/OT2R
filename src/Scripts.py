import pickle
import lzma
from Utility import get_filename
from DataJson import DataJsonFile


class Script:
    all_scripts = pickle.load(lzma.open(get_filename('lzma/scripts.xz'), 'r'))

    @classmethod
    def load(cls, basename):
        data = cls.all_scripts[f'{basename}.json']
        return DataJsonFile(data)
