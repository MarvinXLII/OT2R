from Utility import Byte, File
import os
import hashlib
import sys
import zlib
import crcmod
# from Decrypt import *

MAGIC = 0x0b5a6f12e1


class Entry:
    def __init__(self, pak):
        self.indexer = pak
        self.offset_entry = self.indexer.tell()
        self._initialize()

    def _initialize(self):
        self._is_modded = False
        self._data = None
        self._sha = None
        self._extracted = False
        self._sha_decomp = None

        self.indexer.data.seek(self.offset_entry)
        self.flags = self.indexer.read_uint32()
        self.is_offset_32bit_safe = self.flags & (1 << 31) > 0
        self.is_uncomp_size_32bit_safe = self.flags & (1 << 30) > 0
        self.is_size_32bit_safe = self.flags & (1 << 29) > 0
        self.comp_method_idx = (self.flags >> 23) & 0x3F
        self.is_encrypted = self.flags & (1 << 22) > 0
        self.comp_blk_cnt = (self.flags >> 6) & 0xFFFF
        self.calc_max_comp_blk_size = (self.flags & 0x3F) < 0x3F

        self.max_comp_blk_size = self.get_max_comp_blk_size()
        self.offset = self.read_32_or_64(self.is_offset_32bit_safe)
        self.uncomp_size = self.read_32_or_64(self.is_uncomp_size_32bit_safe)
        self.comp_size = self.get_comp_size()
        self.return_size = self.get_comp_read_size()
        assert self.return_size <= self.comp_size
        self.comp_blk_sizes = self.get_comp_blk_sizes()
        self.max_comp_blk_size = min(self.max_comp_blk_size, self.uncomp_size)

    def reset(self):
        self._initialize()
    
    def get_comp_read_size(self):
        if self.is_encrypted and self.comp_method_idx and self.comp_blk_cnt == 1:
            return self.indexer.read_uint32()
        return self.comp_size

    def get_max_comp_blk_size(self):
        if self.comp_blk_cnt == 0:
            return 0
        if self.calc_max_comp_blk_size:
            size = (self.flags & 0x3F) << 11
        else:
            size = self.indexer.read_uint32()
        return size

    def get_comp_size(self):
        if self.comp_method_idx:
            return self.read_32_or_64(self.is_size_32bit_safe)
        return self.uncomp_size

    def read_32_or_64(self, is_32bit_safe):
        if is_32bit_safe:
            return self.indexer.read_uint32()
        return self.indexer.read_uint64()

    def get_comp_blk_sizes(self):
        if self.comp_blk_cnt == 0:
            return []
        elif self.comp_blk_cnt == 1:
            return [self.return_size]
        sizes = []
        for _ in range(self.comp_blk_cnt):
            sizes.append(self.indexer.read_uint32())
        return sizes

    def extract(self, filename, pak):
        # assert not self._extracted, "Already extracted!"
        pak.data.seek(self.offset)
        assert pak.read_uint64() == 0
        assert pak.read_uint64() == self.comp_size
        assert pak.read_uint64() == self.uncomp_size
        assert pak.read_uint32() == self.comp_method_idx
        self._sha = pak.read_bytes(20)
        offset_blocks = []
        if self.comp_method_idx:
            assert pak.read_uint32() == self.comp_blk_cnt
            for size in self.comp_blk_sizes:
                start = pak.read_uint64()
                end = pak.read_uint64()
                if size != end - start:
                    assert self.is_encrypted
                    s = size + (16 - size%16)%16
                    assert s == end - start
                offset_blocks.append((start, end))
        assert pak.read_int8() == self.is_encrypted

        if self.is_encrypted:
            assert pak.read_uint32() == self.max_comp_blk_size
            if self.comp_blk_sizes:
                self._data = bytearray()
                sizes = []
                max_decomp_size = 0
                for start, end in offset_blocks:
                    pak.data.seek(self.offset + start)
                    sizes.append(end - start)
                    tmp = pak.read_bytes(end - start)
                    # tmp = decrypt(pak, end - start)
                    if self.comp_method_idx:
                        tmp = zlib.decompress(bytearray(tmp))
                    self._data += tmp
                    max_decomp_size = max(max_decomp_size, len(tmp))
                assert len(sizes) == len(self.comp_blk_sizes)
                assert len(self._data) == self.uncomp_size
                if len(offset_blocks) == 1:
                    assert len(sizes) == 1
                    assert sizes[0] == self.return_size
                    assert self.comp_blk_sizes[0] == self.return_size
                    comp_size = self.return_size + (16 - self.return_size%16)%16
                    assert comp_size == self.comp_size
                    assert self.comp_method_idx
                else:
                    assert self.return_size == self.comp_size
                    comp_size = 0
                    for s in sizes:
                        comp_size += s + (16 - s%16)%16
                    assert comp_size == self.comp_size
                    assert max_decomp_size == self.max_comp_blk_size
                comp_size = self.return_size + (16 - self.return_size%16)%16
                assert comp_size == self.comp_size
            else:
                # self._data = decrypt(pak, self.comp_size)
                self._data = pak.read_bytes(self.comp_size)
                assert len(self._data) == self.uncomp_size
                assert self.return_size == self.comp_size
                assert self.uncomp_size == self.comp_size
                assert self.comp_method_idx == 0
                assert self.max_comp_blk_size == 0

        elif self.comp_method_idx:
            self._data = bytearray([])
            assert pak.read_uint32() == self.max_comp_blk_size
            comp_size = 0
            for start, end in offset_blocks:
                assert pak.tell() == self.offset + start
                tmp = pak.read_bytes(end - start)
                comp_size += len(tmp)
                self._data += zlib.decompress(tmp)
            assert comp_size == self.comp_size
            assert len(self._data) == self.uncomp_size
            assert self.return_size == self.comp_size
        else:
            assert self.comp_size == self.uncomp_size
            assert self.return_size == self.uncomp_size
            assert pak.read_int32() == 0
            self._data = pak.read_bytes(self.uncomp_size)

        self._sha_decomp = hashlib.sha1(self._data).digest()
        self._is_modded = False
        self._extracted = True

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, new_data):
        sha = hashlib.sha1(new_data).digest()
        self._is_modded = sha != self._sha_decomp
        if self._is_modded:
            self._data = new_data
            # self._sha_decomp = sha  ## ALWAYS compare to the vanilla sha

    @data.deleter
    def data(self):
        self._data = None
        self._sha_decomp = None
        self._is_modded = False

    @property
    def is_modded(self):
        return self._is_modded

    @property
    def extracted(self):
        return self._extracted

    def build_entry(self):
        base = 0
        size = 0x10000
        data = bytearray([])
        self.comp_blk_sizes = []

        if self.is_encrypted:
            if self.comp_method_idx:
                while base < len(self._data):
                    start = len(data)
                    tmp = zlib.compress(self._data[base:base+size])
                    data += encrypt(tmp)
                    assert (len(data) - start)%16 == 0
                    # end = len(data)
                    end = start + len(tmp)
                    self.comp_blk_sizes.append(end - start)
                    base += size
                self.uncomp_size = len(self._data)
                if len(self.comp_blk_sizes) == 1:
                    self.return_size = self.comp_blk_sizes[0]
                    self.comp_size = self.return_size + (16 - self.return_size%16)%16
                else:
                    self.comp_size = 0
                    for s in self.comp_blk_sizes:
                        self.comp_size += s + (16 - s%16)%16
                    self.return_size = self.comp_size
            else:
                data = encrypt(self._data)
                self.uncomp_size = len(self._data)
                self.comp_size = self.uncomp_size
                self.return_size = self.uncomp_size
                self.max_comp_blk_size = 0
            self._sha = hashlib.sha1(data[:self.comp_size]).digest()
        elif self.comp_method_idx:
            while base < len(self._data):
                start = len(data)
                tmp = zlib.compress(self._data[base:base+size])
                data += tmp
                end = len(data)
                self.comp_blk_sizes.append(end - start)
                base += size
            self.comp_blk_cnt = len(self.comp_blk_sizes)
            self.comp_size = len(data)
            self.uncomp_size = len(self._data)
            self.return_size = self.comp_size
            assert not self.is_encrypted
            self._sha = hashlib.sha1(data[:self.comp_size]).digest()
        else:
            self.uncomp_size = len(self._data)
            self.comp_size = self.uncomp_size
            self.return_size = self.uncomp_size
            assert not self.is_encrypted
            data = self._data
            self._sha = hashlib.sha1(data).digest()

        if self.comp_method_idx > 0:
            self.max_comp_blk_size = min(0x10000, self.uncomp_size)
            self.calc_max_comp_blk_size = (self.max_comp_blk_size >> 11) << 11 == self.max_comp_blk_size
            assert self.comp_blk_cnt > 0
        else:
            self.calc_max_comp_blk_size = False
            self.comp_blk_cnt = 0
            assert len(self.comp_blk_sizes) == 0

        entry = bytearray([0]*8)
        entry += Byte.get_uint64(self.comp_size)
        entry += Byte.get_uint64(self.uncomp_size)
        entry += Byte.get_uint32(self.comp_method_idx)
        entry += self._sha
        if self.comp_blk_cnt > 0:
            entry += Byte.get_uint32(self.comp_blk_cnt)
            offset = len(entry) + 8*2*self.comp_blk_cnt + 5
            for size in self.comp_blk_sizes:
                entry += Byte.get_uint64(offset)
                offset += size
                entry += Byte.get_uint64(offset)
            entry += Byte.get_uint8(self.is_encrypted)
            entry += Byte.get_uint32(self.max_comp_blk_size)
        else:
            entry += Byte.get_uint8(self.is_encrypted)
            entry += Byte.get_uint32(0)
        entry += data
        return entry

    def build_encoding(self):
        self.is_offset_32bit_safe = self.offset < 0x7fffffff
        self.is_uncomp_size_32bit_safe = self.uncomp_size < 0x7fffffff
        self.is_size_32bit_safe = self.comp_size < 0x7fffffff

        self.flags = self.is_offset_32bit_safe << 31 \
            | self.is_uncomp_size_32bit_safe << 30 \
            | self.is_size_32bit_safe << 29 \
            | self.comp_method_idx << 23 \
            | self.is_encrypted << 22 \
            | self.comp_blk_cnt << 6

        if self.calc_max_comp_blk_size:
            self.flags |= self.max_comp_blk_size >> 11
        elif self.comp_blk_cnt > 0:
            self.flags |= 0x3f

        arr = Byte.get_uint32(self.flags)
        if self.comp_blk_cnt:
            if not self.calc_max_comp_blk_size:
                arr += Byte.get_uint32(self.max_comp_blk_size)
                assert self.max_comp_blk_size < 0x10000

        if self.is_offset_32bit_safe:
            arr += Byte.get_uint32(self.offset)
        else:
            arr += Byte.get_uint64(self.offset)

        if self.is_uncomp_size_32bit_safe:
            arr += Byte.get_uint32(self.uncomp_size)
        else:
            arr += Byte.get_uint64(self.uncomp_size)

        if self.comp_method_idx > 0:
            if self.is_size_32bit_safe:
                arr += Byte.get_uint32(self.comp_size)
            else:
                arr += Byte.get_uint64(self.comp_size)
        else:
            assert self.comp_size == self.uncomp_size

        if self.is_encrypted and self.comp_method_idx and self.comp_blk_cnt == 1:
            arr += Byte.get_uint32(self.return_size)

        if self.comp_blk_cnt > 1:
            for size in self.comp_blk_sizes:
                arr += Byte.get_uint32(size)

        return arr


class Mod(Byte):
    def __init__(self):
        super().__init__()
        self.entry_dict = {}  ## FOR MODDED ENTRY ONLY
        self.size_entries = None
        self.pak = None
        self.mountpoint = None
        self.num_modded_files = 0
        self.pakname = None
        self.crc32 = None
        self.offset_encoding = None
        self.offset_path_hash = None
        self.start_path_hash = None
        self.size_path_hash = None
        self.offset_dir_idx = None
        self.start_dir_idx = None
        self.size_dir_idx = None
        self.dir_contents = {'/':[]}

    def add_entry(self, filename, entry):
        # assert entry.is_modded
        self.entry_dict[filename] = entry
        self.num_modded_files = len(self.entry_dict)

    def _build_entry(self):
        assert len(self.pak) == 0
        for entry in self.entry_dict.values():
            entry.offset = len(self.pak)
            self.pak += entry.build_entry()
        self.size_entries = len(self.pak)

    def _build_mountpoint(self):
        if self.num_modded_files == 0:
            return
        assert len(self.pak) == self.size_entries
        filenames = iter(self.entry_dict.keys())
        path = next(filenames).split('/')[:-1]
        for filename in filenames:
            tmp = filename.split('/')[:-1]
            i = 0
            for p, t in zip(path, tmp):
                if p != t: break
                i += 1
            path = path[:i]
        self.mountpoint = '/'.join(path) + '/'
        self.pak += self.get_string(self.mountpoint)

    def _build_num_modded_files(self):
        assert len(self.entry_dict) == self.num_modded_files
        self.pak += self.get_uint32(self.num_modded_files)

    def calc_crc32(self, arr):
        b_arr = bytearray([0]*len(arr)*4)
        if isinstance(arr, str):
            for i,a in enumerate(arr.lower()):
                b_arr[i*4] = ord(a)
        else:
            for i,a in enumerate(arr):
                b_arr[i*4] = a
        f = crcmod.mkCrcFun(0x104C11DB7, initCrc=0xFFFFFFFF, xorOut=0)
        return 0xFFFFFFFF - f(b_arr)

    def _build_crc32(self, pakname):
        self.pakname = os.path.basename(pakname)
        self.crc32 = self.calc_crc32(self.mountpoint + 'Paks/' + self.pakname)
        self.pak += self.get_uint64(self.crc32)

    def _add_buffers(self):
        self.offset_path_hash = len(self.pak)
        self.pak += b'\x00' * (4 + 8*2 + 20)
        self.offset_dir_idx = len(self.pak)
        self.pak += b'\x00' * (4 + 8*2 + 20)

    def _build_encoding(self):
        self.offset_encoding = {}
        encoding = bytearray()
        for filename, entry in self.entry_dict.items():
            self.offset_encoding[filename] = len(encoding)
            encoding += entry.build_encoding()
        self.pak += self.get_uint32(len(encoding))
        self.pak += encoding
        self.pak += b'\x00'*4

    def _patch_file(self, offset, start, size):
        arr = self.get_uint32(1)
        arr += self.get_uint64(start)
        arr += self.get_uint64(size)
        chunk = self.pak[start:start+size]
        arr += hashlib.sha1(chunk).digest()
        self.pak[offset:offset+len(arr)] = arr
        assert len(arr) == 4 + 8*2 + 20

    def calc_hash_fnv(self, filename):
        filename = filename.lower().encode('utf16')[2:]
        offset = 0xcbf29ce484222325
        prime = 0x00000100000001b3
        fnv = offset + self.crc32
        for f in filename:
            fnv ^= f
            fnv *= prime
            fnv &= 0xFFFFFFFFFFFFFFFF
        return fnv

    def _build_path_hash(self, encrypt):
        self.start_path_hash = len(self.pak)
        self.pak += self.get_uint32(self.num_modded_files)
        for filename, entry in self.entry_dict.items():
            f = filename.split(self.mountpoint)[1]
            fnv = self.calc_hash_fnv(f)
            self.pak += self.get_uint64(fnv)
            self.pak += self.get_uint32(self.offset_encoding[filename])
        self.pak += b'\x00'*4

        if encrypt:
            self._extend_pak(self.start_path_hash)

        self.size_path_hash = len(self.pak) - self.start_path_hash
        self._patch_file(self.offset_path_hash, self.start_path_hash, self.size_path_hash)

    def _build_dir_idx(self, encrypt):
        self.start_dir_idx = len(self.pak)

        # Organize the contents of each directory
        for filename, entry in self.entry_dict.items():
            path = filename.split(self.mountpoint)[1].split('/')
            basename = path.pop()
            if path == []:
                self.dir_contents['/'].append(basename)
            else:
                p = ''
                for pi in path:
                    p += pi + '/'
                    if p not in self.dir_contents:
                        self.dir_contents[p] = []
                self.dir_contents[p].append(basename)

        # Build the directory data
        self.pak += self.get_uint32(len(self.dir_contents))
        for directory in sorted(self.dir_contents.keys()):
            file_list = self.dir_contents[directory]
            self.pak += self.get_string(directory)
            self.pak += self.get_uint32(len(file_list))
            directory = self.mountpoint + directory
            if directory[-2:] == '//':
                directory = directory[:-1]
            for basename in sorted(file_list):
                filename = directory + basename
                assert filename in self.offset_encoding
                self.pak += self.get_string(basename)
                self.pak += self.get_uint32(self.offset_encoding[filename])

        if encrypt:
            self._extend_pak(self.start_dir_idx)

        self.size_dir_idx = len(self.pak) - self.start_dir_idx
        self._patch_file(self.offset_dir_idx, self.start_dir_idx, self.size_dir_idx)

    def _build_footer(self, encrypt):
        self.pak += b'\x00'*16
        if encrypt:
            self.pak += b'\x01'
        else:
            self.pak += b'\x00'
        self.pak += self.get_uint64(MAGIC)
        self.pak += self.get_uint64(self.size_entries)
        self.pak += self.get_uint64(self.start_path_hash - self.size_entries)
        self.pak += self._index_sha_decrypted
        comp_types = bytearray([0]*0xa0)
        comp_types[:4] = b'Zlib'
        self.pak += comp_types

    def _extend_pak(self, addr):
        size = len(self.pak[addr:])
        incr = (16 - (size%16)) % 16
        self.pak += self.pak[addr:addr+incr]
        assert len(self.pak[addr:])%16 == 0

    def _build_indexing(self, pakname, encrypt_indexing):
        addr = len(self.pak)
        self._build_mountpoint()
        self._build_num_modded_files()
        self._build_crc32(pakname)
        self._add_buffers()
        self._build_encoding()
        if encrypt_indexing:
            self._extend_pak(addr)
        self._build_path_hash(encrypt_indexing)
        self._build_dir_idx(encrypt_indexing)
        self._index_sha_decrypted = hashlib.sha1(self.pak[self.size_entries:self.start_path_hash]).digest()
        if encrypt_indexing:
            assert len(self.pak[addr:])%16 == 0
            index = encrypt(self.pak[addr:])
            assert len(index)%16 == 0
            self.pak = self.pak[:addr] + index

    def build_pak(self, pakname, encrypt):
        self.pak = bytearray()
        if self.num_modded_files:
            print(self.num_modded_files, 'files modded. Building pak')
            self._build_entry()
            self._build_indexing(pakname, encrypt)
            self._build_footer(encrypt)
        return self.pak


class Pak(File):
    def __init__(self, filename):
        self.filename = filename
        self.data = open(filename, 'rb')

        # Check sha
        self.data.seek(-0xcd, 2)
        self.encrypted_indexing = self.read_int8() > 0
        assert self.read_uint64() == MAGIC
        self.offset_index = self.read_uint64()
        self.size_index = self.read_uint64()
        self.sha_index = self.read_bytes(20)
        # self.check_sha(self.sha_index, self.offset_index, self.size_index)

        # Compression types -- assumed Zlib only
        self.compression_types = bytearray(self.data.read())
        assert self.compression_types[:4] == b'Zlib'
        assert int.from_bytes(self.compression_types[4:], byteorder='little') == 0

        # Index data - keep data separate to allow for decrypting if needed
        self.index_data = self.get_index_data()

        # Start indexing
        self.index_data.seek(self.offset_index)
        self.mountpoint = self.index_data.read_string()
        self.num_files = self.index_data.read_uint32()
        self.crc32_pakname = self.index_data.read_uint64()

        assert self.index_data.read_uint32() == 1
        self.offset_path_hash = self.index_data.read_uint64()
        self.size_path_hash = self.index_data.read_uint64()
        self.sha_path_hash = self.index_data.read_bytes(20)
        # self.check_sha(self.sha_path_hash, self.offset_path_hash, self.size_path_hash)

        assert self.index_data.read_uint32() == 1
        self.offset_full_dir = self.index_data.read_uint64()
        self.size_full_dir = self.index_data.read_uint64()
        self.sha_full_dir = self.index_data.read_bytes(20)
        # self.check_sha(self.sha_full_dir, self.offset_full_dir, self.size_full_dir)

        # Encoded pak entries
        self.offset_pak_entries = self.index_data.data.tell()
        self.encoded_pak_entries = self.parse_pak_entries(self.index_data)
        assert self.index_data.read_int32() == 0

        # Filenames
        self.index_data.seek(self.offset_full_dir)
        self.entry_dict, self.basename_dict = self.parse_filenames()

        # Other
        self._mod = Mod()

    def __del__(self):
        self.data.close()

    def get_index_data(self):
        if self.encrypted_indexing:
            sys.exit("Not setup for decrypting")
            # print('Decrypting indexing')
            # offset_indexEnd = self.data.seek(-0xdd, 2)
            # index_data_size = offset_indexEnd - self.offset_index
            # index_data = decrypt(self, index_data_size, offset=self.offset_index)
            # indexSHA = hashlib.sha1(index_data)
        else:
            self.data.seek(self.offset_index)
            index_data = self.data.read()
        return IndexData(index_data, offset=self.offset_index)

    def clean(self):
        self._mod = Mod()
        for entry in self.entry_dict.values():
            entry.reset()

    def parse_filenames(self):
        # Map each encoded area offset to a full filename
        encoded_offset_dict = {}
        while len(encoded_offset_dict) < self.num_files:
            numDir = self.index_data.read_uint32()
            if numDir == 0: break
            for _ in range(numDir):
                directory = self.mountpoint + self.index_data.read_string()
                num_files = self.index_data.read_uint32()
                if directory[-2:] == '//':
                    directory = directory[:-1]
                for _ in range(num_files):
                    filename = directory + self.index_data.read_string()
                    offset = self.index_data.read_uint32()
                    if offset in encoded_offset_dict:
                        assert encoded_offset_dict[offset] == filename
                    encoded_offset_dict[offset] = filename
        assert len(encoded_offset_dict) == self.num_files

        # Map filenames to their corresponding entry
        # Sort keys by offsets to ensure the encoded pak entry
        # is mapped to the correct filename
        entry_dict = {}
        keys = sorted(encoded_offset_dict.keys())
        for i, key in enumerate(keys):
            filename = encoded_offset_dict[key]
            assert filename not in entry_dict
            entry_dict[filename] = self.encoded_pak_entries[i]
        assert len(entry_dict) == len(self.encoded_pak_entries)
        assert len(entry_dict) == self.num_files

        # Map basenames to full filenames
        # Done for convenience when picking files to extract
        basename_dict = {}
        for filename in entry_dict:
            basename = filename.split('/')[-1]
            if basename not in basename_dict:
                basename_dict[basename] = []
            basename_dict[basename].append(filename)

        return entry_dict, basename_dict

    def parse_pak_entries(self, index_data):
        assert self.index_data.tell() == self.offset_pak_entries
        pak_entries_size = self.index_data.read_uint32()
        offset_end = self.offset_pak_entries + pak_entries_size + 4
        entries = []
        for _ in range(self.num_files):
            entries.append(Entry(index_data))
        assert self.index_data.data.tell() <= offset_end
        entries.sort(key=lambda x: x.offset)
        return entries

    def check_sha(self, sha, offset, size):
        orig_offset = self.data.tell()
        self.data.seek(offset)
        data = self.read_bytes(size)
        assert sha == hashlib.sha1(data).digest()
        self.data.seek(orig_offset)

    def get_full_file_path(self, filename):
        if filename in self.entry_dict:
            return filename
        basename = filename.split('/')[-1]
        if basename in self.basename_dict:
            if len(self.basename_dict[basename]) == 1:
                return self.basename_dict[basename][0]
            test = [filename in f for f in self.basename_dict[basename]]
            if sum(test) == 1:
                idx = test.index(1)
                return self.basename_dict[basename][idx]

    def get_dir_contents(self, directory):
        filenames = []
        for filename in self.entry_dict:
            if directory in filename:
                filenames.append(filename)
        return filenames

    def extract_file(self, filename):
        filename = self.get_full_file_path(filename)
        if not self.entry_dict[filename].extracted:
            self.entry_dict[filename].extract(filename, self)
        return bytearray(self.entry_dict[filename].data)

    def delete_file(self, filename):
        del self.entry_dict[filename].data

    def update_data(self, filename, data, force=False):
        filename = self.get_full_file_path(filename)
        if not self.entry_dict[filename].extracted:
            self.entry_dict[filename].extract(filename, self)
        self.entry_dict[filename].data = data
        if self.entry_dict[filename].is_modded or force:
            self._mod.add_entry(filename, self.entry_dict[filename])

    def build_pak(self, pakname):
        pak = self._mod.build_pak(pakname, self.encrypted_indexing)
        if pak:
            print('Dumping pak to', pakname)
            with open(pakname, 'wb') as file:
                file.write(pak)
        else:
            print('No files were modded. No pak to dump!')

    def list_loaded_file_names(self):
        files_loaded = []
        for filename, entry in self.entry_dict.items():
            if entry.extracted:
                files_loaded.append(filename)
        return files_loaded


class MainPak(Pak):
    def __init__(self, filename):
        super().__init__(filename)
        self.patches = []

    # At the very least, filenames must belong in the main pak
    def get_full_file_path(self, filename):
        full_file_path = super().get_full_file_path(filename)
        if full_file_path is None:
            # All files should be in the main pak. Check for errors.
            basename = filename.split('/')[-1]
            if basename not in self.basename_dict:
                sys.exit(f"Basename {basename} does not exist! Double check {filename}!")
            names = '\n  '.join(self.basename_dict[basename])
            sys.exit(f"{filename} is not unique! Be more specific!\n " + names)
        return full_file_path

    # Patch from lowest to highest priority
    def apply_patches(self):
        for patch in self.patches[::-1]:
            for filename in patch.entry_dict:
                data = patch.extract_file(filename)
                self.update_data(filename, data)

    def extract_file(self, filename, include_patches=True):
        # Returns a patched file if patches have been applied.
        # Otherwise it will extract a file from the main pak.
        if include_patches:
            return super().extract_file(filename)
        # Force extraction from the main pak.
        # This will overwrite any patches applied.
        filename = self.get_full_file_path(filename)
        self.entry_dict[filename].extract(filename, self)
        return bytearray(self.entry_dict[filename].data)

    def clean(self):
        super().clean()
        for patch in self.patches:
            patch.clean()


class IndexData(File):
    def __init__(self, data, offset=0):
        super(IndexData, self).__init__(data)
        self.offset = offset

    def seek(self, addr):
        self.data.seek(addr - self.offset)

    def tell_pak(self):
        return self.tell() + self.offset
