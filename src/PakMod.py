import shutil
import os
import sys

FILEDIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{FILEDIR}/../src')
from Pak import Pak, MainPak, Mod, Entry

MAGIC = 0x5a6f12e1

class ModEntry(Entry):
    def initialize(self):
        self._is_modded = False
        self._data = None
        self._sha = None
        self._extracted = False
        self._sha_decomp = None

        self.indexer.data.seek(self.offset_entry)
        self.offset = self.indexer.read_uint64()
        self.comp_size = self.indexer.read_uint64()
        self.uncomp_size = self.indexer.read_uint64()
        self.comp_method_idx = self.indexer.read_uint32()
        sha = self.indexer.read_bytes(20)
        self.comp_blk_cnt = self.indexer.read_uint32()

        # Other stuff just for checks when extracting 
        # assert self.comp_method_idx == 0
        self.return_size = self.comp_size
        self.max_comp_blk_size = 0
        self.is_encrypted = False

        self.comp_blk_sizes = []
        if self.comp_method_idx:
            for _ in range(self.comp_blk_cnt):
                start = self.indexer.read_uint64()
                end = self.indexer.read_uint64()
                self.comp_blk_sizes.append(end - start)

            assert self.indexer.read_uint8() == 0
            self.max_comp_blk_size = self.indexer.read_uint32()
        else:
            assert self.indexer.read_uint8() == 0
            self.max_comp_blk_size = 0
            

    def build_entry(self):
        # Mod won't necessarily be compressed
        # Must setup this instance to compress, if needs be
        if self.comp_size >= 0x10000:
            self.comp_method_idx = 1   ## Zlib
            
        return super().build_entry()
        

class PatchPak(Pak):
    def __init__(self, filename):
        self.filename = filename
        self.data = open(filename, 'rb')

        self.data.seek(-0x2c, 2)
        self.encrypted_indexing = False
        assert self.read_uint32() == MAGIC
        assert self.read_uint32() in [3, 4, 8]
        self.offset_index = self.read_uint64()
        self.size_index = self.read_uint64()
        self.sha_index = self.read_bytes(20)

        self.index_data = self.get_index_data()

        # Start indexing
        self.index_data.seek(self.offset_index)
        self.mountpoint = self.index_data.read_string()
        self.num_files = self.index_data.read_uint32()
        self.crc32_pakname = None

        # Filenames and entries
        self.offset_start = self.index_data.tell_pak()
        self.pak_entries = None # Done simultaneously when parsing filenames
        self.entry_dict = None
        self.basename_dict = None

        self._mod = None


    def parse_filenames(self):
        self.index_data.seek(self.offset_start)

        offset_dict = {}
        entry_dict = {}
        self.pak_entries = []
        for _ in range(self.num_files):
            filename = self.mountpoint + self.index_data.read_string()
            entry = ModEntry(self.index_data)
            # assert self.index_data.read_uint8() == 0

            self.pak_entries.append(entry)
            offset_dict[entry.offset] = filename
            assert filename not in entry_dict
            entry_dict[filename] = entry
        assert len(offset_dict) == self.num_files
        self.entry_dict = entry_dict
