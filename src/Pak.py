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
        self.offsetEntry = self.indexer.tell()
        self._initialize()

    def _initialize(self):
        self._isModded = False
        self._data = None
        self._sha = None
        self._extracted = False
        self._shaDecomp = None

        self.indexer.data.seek(self.offsetEntry)
        self.flags = self.indexer.readUInt32()
        self.isOffset32BitSafe = self.flags & (1 << 31) > 0
        self.isUncompSize32BitSafe = self.flags & (1 << 30) > 0
        self.isSize32BitSafe = self.flags & (1 << 29) > 0
        self.compMethodIdx = (self.flags >> 23) & 0x3F
        self.isEncrypted = self.flags & (1 << 22) > 0
        self.compBlkCnt = (self.flags >> 6) & 0xFFFF
        self.calcMaxCompBlkSize = (self.flags & 0x3F) < 0x3F

        self.maxCompBlkSize = self.getMaxCompBlkSize()
        self.offset = self.read32Or64(self.isOffset32BitSafe)
        self.uncompSize = self.read32Or64(self.isUncompSize32BitSafe)
        self.compSize = self.getCompSize()
        self.returnSize = self.getCompReadSize()
        assert self.returnSize <= self.compSize
        self.compBlkSizes = self.getCompBlkSizes()
        self.maxCompBlkSize = min(self.maxCompBlkSize, self.uncompSize)

    def reset(self):
        self._initialize()
    
    def getCompReadSize(self):
        if self.isEncrypted and self.compMethodIdx and self.compBlkCnt == 1:
            return self.indexer.readUInt32()
        return self.compSize

    def getMaxCompBlkSize(self):
        if self.compBlkCnt == 0:
            return 0
        if self.calcMaxCompBlkSize:
            size = (self.flags & 0x3F) << 11
        else:
            size = self.indexer.readUInt32()
        return size

    def getCompSize(self):
        if self.compMethodIdx:
            return self.read32Or64(self.isSize32BitSafe)
        return self.uncompSize

    def read32Or64(self, is32BitSafe):
        if is32BitSafe:
            return self.indexer.readUInt32()
        return self.indexer.readUInt64()

    def getCompBlkSizes(self):
        if self.compBlkCnt == 0:
            return []
        elif self.compBlkCnt == 1:
            return [self.returnSize]
        sizes = []
        for _ in range(self.compBlkCnt):
            sizes.append(self.indexer.readUInt32())
        return sizes

    def extract(self, filename, pak):
        # assert not self._extracted, "Already extracted!"
        pak.data.seek(self.offset)
        assert pak.readUInt64() == 0
        assert pak.readUInt64() == self.compSize
        assert pak.readUInt64() == self.uncompSize
        assert pak.readUInt32() == self.compMethodIdx
        self._sha = pak.readBytes(20)
        offsetBlocks = []
        if self.compMethodIdx:
            assert pak.readUInt32() == self.compBlkCnt
            for size in self.compBlkSizes:
                start = pak.readUInt64()
                end = pak.readUInt64()
                if size != end - start:
                    assert self.isEncrypted
                    s = size + (16 - size%16)%16
                    assert s == end - start
                offsetBlocks.append((start, end))
        assert pak.readInt8() == self.isEncrypted

        if self.isEncrypted:
            assert pak.readUInt32() == self.maxCompBlkSize
            if self.compBlkSizes:
                self._data = bytearray()
                sizes = []
                maxDecompSize = 0
                for start, end in offsetBlocks:
                    pak.data.seek(self.offset + start)
                    sizes.append(end - start)
                    tmp = pak.readBytes(end - start)
                    # tmp = decrypt(pak, end - start)
                    if self.compMethodIdx:
                        tmp = zlib.decompress(bytearray(tmp))
                    self._data += tmp
                    maxDecompSize = max(maxDecompSize, len(tmp))
                assert len(sizes) == len(self.compBlkSizes)
                assert len(self._data) == self.uncompSize
                if len(offsetBlocks) == 1:
                    assert len(sizes) == 1
                    assert sizes[0] == self.returnSize
                    assert self.compBlkSizes[0] == self.returnSize
                    compSize = self.returnSize + (16 - self.returnSize%16)%16
                    assert compSize == self.compSize
                    assert self.compMethodIdx
                else:
                    assert self.returnSize == self.compSize
                    compSize = 0
                    for s in sizes:
                        compSize += s + (16 - s%16)%16
                    assert compSize == self.compSize
                    assert maxDecompSize == self.maxCompBlkSize
                compSize = self.returnSize + (16 - self.returnSize%16)%16
                assert compSize == self.compSize
            else:
                # self._data = decrypt(pak, self.compSize)
                self._data = pak.readBytes(self.compSize)
                assert len(self._data) == self.uncompSize
                assert self.returnSize == self.compSize
                assert self.uncompSize == self.compSize
                assert self.compMethodIdx == 0
                assert self.maxCompBlkSize == 0

        elif self.compMethodIdx:
            self._data = bytearray([])
            assert pak.readUInt32() == self.maxCompBlkSize
            compSize = 0
            for start, end in offsetBlocks:
                assert pak.tell() == self.offset + start
                tmp = pak.readBytes(end - start)
                compSize += len(tmp)
                self._data += zlib.decompress(tmp)
            assert compSize == self.compSize
            assert len(self._data) == self.uncompSize
            assert self.returnSize == self.compSize
        else:
            assert self.compSize == self.uncompSize
            assert self.returnSize == self.uncompSize
            assert pak.readInt32() == 0
            self._data = pak.readBytes(self.uncompSize)

        self._shaDecomp = hashlib.sha1(self._data).digest()
        self._isModded = False
        self._extracted = True

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, newData):
        sha = hashlib.sha1(newData).digest()
        self._isModded = sha != self._shaDecomp
        if self._isModded:
            self._data = newData
            # self._shaDecomp = sha  ## ALWAYS compare to the vanilla sha

    @data.deleter
    def data(self):
        self._data = None
        self._shaDecomp = None
        self._isModded = False

    @property
    def isModded(self):
        return self._isModded

    @property
    def extracted(self):
        return self._extracted

    def buildEntry(self):
        base = 0
        size = 0x10000
        data = bytearray([])
        self.compBlkSizes = []

        if self.isEncrypted:
            if self.compMethodIdx:
                while base < len(self._data):
                    start = len(data)
                    tmp = zlib.compress(self._data[base:base+size])
                    data += encrypt(tmp)
                    assert (len(data) - start)%16 == 0
                    # end = len(data)
                    end = start + len(tmp)
                    self.compBlkSizes.append(end - start)
                    base += size
                self.uncompSize = len(self._data)
                if len(self.compBlkSizes) == 1:
                    self.returnSize = self.compBlkSizes[0]
                    self.compSize = self.returnSize + (16 - self.returnSize%16)%16
                else:
                    self.compSize = 0
                    for s in self.compBlkSizes:
                        self.compSize += s + (16 - s%16)%16
                    self.returnSize = self.compSize
            else:
                data = encrypt(self._data)
                self.uncompSize = len(self._data)
                self.compSize = self.uncompSize
                self.returnSize = self.uncompSize
                self.maxCompBlkSize = 0
            self._sha = hashlib.sha1(data[:self.compSize]).digest()
        elif self.compMethodIdx:
            while base < len(self._data):
                start = len(data)
                tmp = zlib.compress(self._data[base:base+size])
                data += tmp
                end = len(data)
                self.compBlkSizes.append(end - start)
                base += size
            self.compBlkCnt = len(self.compBlkSizes)
            self.compSize = len(data)
            self.uncompSize = len(self._data)
            self.returnSize = self.compSize
            assert not self.isEncrypted
            self._sha = hashlib.sha1(data[:self.compSize]).digest()
        else:
            self.uncompSize = len(self._data)
            self.compSize = self.uncompSize
            self.returnSize = self.uncompSize
            assert not self.isEncrypted
            data = self._data
            self._sha = hashlib.sha1(data).digest()

        if self.compMethodIdx > 0:
            self.maxCompBlkSize = min(0x10000, self.uncompSize)
            self.calcMaxCompBlkSize = (self.maxCompBlkSize >> 11) << 11 == self.maxCompBlkSize
            assert self.compBlkCnt > 0
        else:
            self.calcMaxCompBlkSize = False
            self.compBlkCnt = 0
            assert len(self.compBlkSizes) == 0

        entry = bytearray([0]*8)
        entry += Byte.getUInt64(self.compSize)
        entry += Byte.getUInt64(self.uncompSize)
        entry += Byte.getUInt32(self.compMethodIdx)
        entry += self._sha
        if self.compBlkCnt > 0:
            entry += Byte.getUInt32(self.compBlkCnt)
            offset = len(entry) + 8*2*self.compBlkCnt + 5
            for size in self.compBlkSizes:
                entry += Byte.getUInt64(offset)
                offset += size
                entry += Byte.getUInt64(offset)
            entry += Byte.getUInt8(self.isEncrypted)
            entry += Byte.getUInt32(self.maxCompBlkSize)
        else:
            entry += Byte.getUInt8(self.isEncrypted)
            entry += Byte.getUInt32(0)
        entry += data
        return entry

    def buildEncoding(self):
        self.isOffset32BitSafe = self.offset < 0x7fffffff
        self.isUncompSize32BitSafe = self.uncompSize < 0x7fffffff
        self.isSize32BitSafe = self.compSize < 0x7fffffff

        self.flags = self.isOffset32BitSafe << 31 \
            | self.isUncompSize32BitSafe << 30 \
            | self.isSize32BitSafe << 29 \
            | self.compMethodIdx << 23 \
            | self.isEncrypted << 22 \
            | self.compBlkCnt << 6

        if self.calcMaxCompBlkSize:
            self.flags |= self.maxCompBlkSize >> 11
        elif self.compBlkCnt > 0:
            self.flags |= 0x3f

        arr = Byte.getUInt32(self.flags)
        if self.compBlkCnt:
            if not self.calcMaxCompBlkSize:
                arr += Byte.getUInt32(self.maxCompBlkSize)
                assert self.maxCompBlkSize < 0x10000

        if self.isOffset32BitSafe:
            arr += Byte.getUInt32(self.offset)
        else:
            arr += Byte.getUInt64(self.offset)

        if self.isUncompSize32BitSafe:
            arr += Byte.getUInt32(self.uncompSize)
        else:
            arr += Byte.getUInt64(self.uncompSize)

        if self.compMethodIdx > 0:
            if self.isSize32BitSafe:
                arr += Byte.getUInt32(self.compSize)
            else:
                arr += Byte.getUInt64(self.compSize)
        else:
            assert self.compSize == self.uncompSize

        if self.isEncrypted and self.compMethodIdx and self.compBlkCnt == 1:
            arr += Byte.getUInt32(self.returnSize)

        if self.compBlkCnt > 1:
            for size in self.compBlkSizes:
                arr += Byte.getUInt32(size)

        return arr


class Mod(Byte):
    def __init__(self):
        super().__init__()
        self.entryDict = {}  ## FOR MODDED ENTRY ONLY
        self.sizeEntryies = None
        self.pak = None
        self.mountpoint = None
        self.numModdedFiles = 0
        self.pakName = None
        self.crc32 = None
        self.offsetEncoding = None
        self.offsetPathHash = None
        self.startPathHash = None
        self.sizePathHash = None
        self.offsetDirIdx = None
        self.startDirIdx = None
        self.sizeDirIdx = None
        self.dirContents = {'/':[]}

    def addEntry(self, filename, entry):
        # assert entry.isModded
        self.entryDict[filename] = entry
        self.numModdedFiles = len(self.entryDict)

    def _buildEntry(self):
        assert len(self.pak) == 0
        for entry in self.entryDict.values():
            entry.offset = len(self.pak)
            self.pak += entry.buildEntry()
        self.sizeEntries = len(self.pak)

    def _buildMountpoint(self):
        if self.numModdedFiles == 0:
            return
        assert len(self.pak) == self.sizeEntries
        filenames = iter(self.entryDict.keys())
        path = next(filenames).split('/')[:-1]
        for filename in filenames:
            tmp = filename.split('/')[:-1]
            i = 0
            for p, t in zip(path, tmp):
                if p != t: break
                i += 1
            path = path[:i]
        self.mountpoint = '/'.join(path) + '/'
        self.pak += self.getString(self.mountpoint)

    def _buildNumModdedFiles(self):
        assert len(self.entryDict) == self.numModdedFiles
        self.pak += self.getUInt32(self.numModdedFiles)

    def calcCRC32(self, arr):
        barr = bytearray([0]*len(arr)*4)
        if type(arr) == str:
            for i,a in enumerate(arr.lower()):
                barr[i*4] = ord(a)
        else:
            for i,a in enumerate(arr):
                barr[i*4] = a
        f = crcmod.mkCrcFun(0x104C11DB7, initCrc=0xFFFFFFFF, xorOut=0)
        return 0xFFFFFFFF - f(barr)

    def _buildCRC32(self, pakName):
        self.pakName = os.path.basename(pakName)
        self.crc32 = self.calcCRC32(self.mountpoint + 'Paks/' + self.pakName)
        self.pak += self.getUInt64(self.crc32)

    def _addBuffers(self):
        self.offsetPathHash = len(self.pak)
        self.pak += b'\x00' * (4 + 8*2 + 20)
        self.offsetDirIdx = len(self.pak)
        self.pak += b'\x00' * (4 + 8*2 + 20)

    def _buildEncoding(self):
        self.offsetEncoding = {}
        encoding = bytearray()
        for filename, entry in self.entryDict.items():
            self.offsetEncoding[filename] = len(encoding)
            encoding += entry.buildEncoding()
        self.pak += self.getUInt32(len(encoding))
        self.pak += encoding
        self.pak += b'\x00'*4

    def _patchFile(self, offset, start, size):
        arr = self.getUInt32(1)
        arr += self.getUInt64(start)
        arr += self.getUInt64(size)
        chunk = self.pak[start:start+size]
        arr += hashlib.sha1(chunk).digest()
        self.pak[offset:offset+len(arr)] = arr
        assert len(arr) == 4 + 8*2 + 20

    def calcHashFNV(self, filename):
        filename = filename.lower().encode('utf16')[2:]
        offset = 0xcbf29ce484222325
        prime = 0x00000100000001b3
        fnv = offset + self.crc32
        for f in filename:
            fnv ^= f
            fnv *= prime
            fnv &= 0xFFFFFFFFFFFFFFFF
        return fnv

    def _buildPathHash(self, encrypt):
        self.startPathHash = len(self.pak)
        self.pak += self.getUInt32(self.numModdedFiles)
        for filename, entry in self.entryDict.items():
            f = filename.split(self.mountpoint)[1]
            fnv = self.calcHashFNV(f)
            self.pak += self.getUInt64(fnv)
            self.pak += self.getUInt32(self.offsetEncoding[filename])
        self.pak += b'\x00'*4

        if encrypt:
            self._extendPak(self.startPathHash)

        self.sizePathHash = len(self.pak) - self.startPathHash
        self._patchFile(self.offsetPathHash, self.startPathHash, self.sizePathHash)

    def _buildDirIdx(self, encrypt):
        self.startDirIdx = len(self.pak)

        # Organize the contents of each directory
        for filename, entry in self.entryDict.items():
            path = filename.split(self.mountpoint)[1].split('/')
            basename = path.pop()
            if path == []:
                self.dirContents['/'].append(basename)
            else:
                p = ''
                for pi in path:
                    p += pi + '/'
                    if p not in self.dirContents:
                        self.dirContents[p] = []
                self.dirContents[p].append(basename)

        # Build the directory data
        self.pak += self.getUInt32(len(self.dirContents))
        for directory in sorted(self.dirContents.keys()):
            fileList = self.dirContents[directory]
            self.pak += self.getString(directory)
            self.pak += self.getUInt32(len(fileList))
            directory = self.mountpoint + directory
            if directory[-2:] == '//':
                directory = directory[:-1]
            for basename in sorted(fileList):
                filename = directory + basename
                assert filename in self.offsetEncoding
                self.pak += self.getString(basename)
                self.pak += self.getUInt32(self.offsetEncoding[filename])

        if encrypt:
            self._extendPak(self.startDirIdx)

        self.sizeDirIdx = len(self.pak) - self.startDirIdx
        self._patchFile(self.offsetDirIdx, self.startDirIdx, self.sizeDirIdx)

    def _buildFooter(self, encrypt):
        self.pak += b'\x00'*16
        if encrypt:
            self.pak += b'\x01'
        else:
            self.pak += b'\x00'
        self.pak += self.getUInt64(MAGIC)
        self.pak += self.getUInt64(self.sizeEntries)
        self.pak += self.getUInt64(self.startPathHash - self.sizeEntries)
        self.pak += self._indexSHADecrypted
        compTypes = bytearray([0]*0xa0)
        compTypes[:4] = b'Zlib'
        self.pak += compTypes

    def _extendPak(self, addr):
        size = len(self.pak[addr:])
        incr = (16 - (size%16)) % 16
        self.pak += self.pak[addr:addr+incr]
        assert len(self.pak[addr:])%16 == 0

    def _buildIndexing(self, pakName, encryptIndexing):
        addr = len(self.pak)
        self._buildMountpoint()
        self._buildNumModdedFiles()
        self._buildCRC32(pakName)
        self._addBuffers()
        self._buildEncoding()
        if encryptIndexing:
            self._extendPak(addr)
        self._buildPathHash(encryptIndexing)
        self._buildDirIdx(encryptIndexing)
        self._indexSHADecrypted = hashlib.sha1(self.pak[self.sizeEntries:self.startPathHash]).digest()
        if encryptIndexing:
            assert len(self.pak[addr:])%16 == 0
            index = encrypt(self.pak[addr:])
            assert len(index)%16 == 0
            self.pak = self.pak[:addr] + index

    def buildPak(self, pakName, encrypt):
        self.pak = bytearray()
        if self.numModdedFiles:
            print(self.numModdedFiles, 'files modded. Building pak')
            self._buildEntry()
            self._buildIndexing(pakName, encrypt)
            self._buildFooter(encrypt)
        return self.pak


class Pak(File):
    def __init__(self, filename):
        self.filename = filename
        self.data = open(filename, 'rb')

        # Check sha
        self.data.seek(-0xcd, 2)
        self.encryptedIndexing = self.readInt8() > 0
        assert self.readUInt64() == MAGIC
        self.offsetIndex = self.readUInt64()
        self.sizeIndex = self.readUInt64()
        self.shaIndex = self.readBytes(20)
        # self.checkSHA(self.shaIndex, self.offsetIndex, self.sizeIndex)

        # Compression types -- assumed Zlib only
        self.compressionTypes = bytearray(self.data.read())
        assert self.compressionTypes[:4] == b'Zlib'
        assert int.from_bytes(self.compressionTypes[4:], byteorder='little') == 0

        # Index data - keep data separate to allow for decrypting if needed
        self.indexData = self.getIndexData()

        # Start indexing
        self.indexData.seek(self.offsetIndex)
        self.mountpoint = self.indexData.readString()
        self.numFiles = self.indexData.readUInt32()
        self.crc32PakName = self.indexData.readUInt64()

        assert self.indexData.readUInt32() == 1
        self.offsetPathHash = self.indexData.readUInt64()
        self.sizePathHash = self.indexData.readUInt64()
        self.shaPathHash = self.indexData.readBytes(20)
        # self.checkSHA(self.shaPathHash, self.offsetPathHash, self.sizePathHash)

        assert self.indexData.readUInt32() == 1
        self.offsetFullDir = self.indexData.readUInt64()
        self.sizeFullDir = self.indexData.readUInt64()
        self.shaFullDir = self.indexData.readBytes(20)
        # self.checkSHA(self.shaFullDir, self.offsetFullDir, self.sizeFullDir)

        # Encoded pak entries
        self.offsetPakEntries = self.indexData.data.tell()
        self.encodedPakEntries = self.parsePakEntries(self.indexData)
        assert self.indexData.readInt32() == 0

        # Filenames
        self.indexData.seek(self.offsetFullDir)
        self.entryDict, self.basenameDict = self.parseFilenames()

        # Other
        self._mod = Mod()

    def __del__(self):
        self.data.close()

    def getIndexData(self):
        if self.encryptedIndexing:
            sys.exit("Not setup for decrypting")
            # print('Decrypting indexing')
            # offsetIndexEnd = self.data.seek(-0xdd, 2)
            # indexDataSize = offsetIndexEnd - self.offsetIndex
            # indexData = decrypt(self, indexDataSize, offset=self.offsetIndex)
            # indexSHA = hashlib.sha1(indexData)
        else:
            self.data.seek(self.offsetIndex)
            indexData = self.data.read()
        return IndexData(indexData, offset=self.offsetIndex)

    def clean(self):
        self._mod = Mod()
        for entry in self.entryDict.values():
            entry.reset()

    def parseFilenames(self):
        # Map each encoded area offset to a full filename
        encodedOffsetDict = {}
        while len(encodedOffsetDict) < self.numFiles:
            numDir = self.indexData.readUInt32()
            if numDir == 0: break
            for _ in range(numDir):
                directory = self.mountpoint + self.indexData.readString()
                numFiles = self.indexData.readUInt32()
                if directory[-2:] == '//':
                    directory = directory[:-1]
                for _ in range(numFiles):
                    filename = directory + self.indexData.readString()
                    offset = self.indexData.readUInt32()
                    if offset in encodedOffsetDict:
                        assert encodedOffsetDict[offset] == filename
                    encodedOffsetDict[offset] = filename
        assert len(encodedOffsetDict) == self.numFiles

        # Map filenames to their corresponding entry
        # Sort keys by offsets to ensure the encoded pak entry
        # is mapped to the correct filename
        entryDict = {}
        keys = sorted(encodedOffsetDict.keys())
        for i, key in enumerate(keys):
            filename = encodedOffsetDict[key]
            assert filename not in entryDict
            entryDict[filename] = self.encodedPakEntries[i]
        assert len(entryDict) == len(self.encodedPakEntries)
        assert len(entryDict) == self.numFiles

        # Map basenames to full filenames
        # Done for convenience when picking files to extract
        basenameDict = {}
        for filename in entryDict:
            basename = filename.split('/')[-1]
            if basename not in basenameDict:
                basenameDict[basename] = []
            basenameDict[basename].append(filename)

        return entryDict, basenameDict

    def parsePakEntries(self, indexData):
        assert self.indexData.tell() == self.offsetPakEntries
        pakEntriesSize = self.indexData.readUInt32()
        offsetEnd = self.offsetPakEntries + pakEntriesSize + 4
        entries = []
        for _ in range(self.numFiles):
            entries.append(Entry(indexData))
        assert self.indexData.data.tell() <= offsetEnd
        entries.sort(key=lambda x: x.offset)
        return entries

    def checkSHA(self, sha, offset, size):
        origOffset = self.data.tell()
        self.data.seek(offset)
        data = self.readBytes(size)
        assert sha == hashlib.sha1(data).digest()
        self.data.seek(origOffset)

    def getFullFilePath(self, filename):
        if filename in self.entryDict:
            return filename
        basename = filename.split('/')[-1]
        if basename in self.basenameDict:
            if len(self.basenameDict[basename]) == 1:
                return self.basenameDict[basename][0]
            test = [filename in f for f in self.basenameDict[basename]]
            if sum(test) == 1:
                idx = test.index(1)
                return self.basenameDict[basename][idx]

    def getDirContents(self, directory):
        filenames = []
        for filename in self.entryDict:
            if directory in filename:
                filenames.append(filename)
        return filenames

    def extractFile(self, filename):
        filename = self.getFullFilePath(filename)
        if not self.entryDict[filename].extracted:
            self.entryDict[filename].extract(filename, self)
        return bytearray(self.entryDict[filename].data)

    def deleteFile(self, filename):
        del self.entryDict[filename].data

    def updateData(self, filename, data, force=False):
        filename = self.getFullFilePath(filename)
        if not self.entryDict[filename].extracted:
            self.entryDict[filename].extract(filename, self)
        self.entryDict[filename].data = data
        if self.entryDict[filename].isModded or force:
            self._mod.addEntry(filename, self.entryDict[filename])

    def buildPak(self, pakName):
        pak = self._mod.buildPak(pakName, self.encryptedIndexing)
        if pak:
            print('Dumping pak to', pakName)
            with open(pakName, 'wb') as file:
                file.write(pak)
        else:
            print('No files were modded. No pak to dump!')

    def listLoadedFileNames(self):
        filesLoaded = []
        for filename, entry in self.entryDict.items():
            if entry.extracted:
                filesLoaded.append(filename)
        return filesLoaded


class MainPak(Pak):
    def __init__(self, filename):
        super().__init__(filename)
        self.patches = []

    # At the very least, filenames must belong in the main pak
    def getFullFilePath(self, filename):
        fullFilePath = super().getFullFilePath(filename)
        if fullFilePath is None:
            # All files should be in the main pak. Check for errors.
            basename = filename.split('/')[-1]
            if basename not in self.basenameDict:
                sys.exit(f"Basename {basename} does not exist! Double check {filename}!")
            names = '\n  '.join(self.basenameDict[basename])
            sys.exit(f"{filename} is not unique! Be more specific!\n " + names)
        return fullFilePath

    # Patch from lowest to highest priority
    def applyPatches(self):
        for patch in self.patches[::-1]:
            for filename in patch.entryDict:
                data = patch.extractFile(filename)
                self.updateData(filename, data)

    def extractFile(self, filename, includePatches=True):
        # Returns a patched file if patches have been applied.
        # Otherwise it will extract a file from the main pak.
        if includePatches:
            return super().extractFile(filename)
        # Force extraction from the main pak.
        # This will overwrite any patches applied.
        filename = self.getFullFilePath(filename)
        self.entryDict[filename].extract(filename, self)
        return bytearray(self.entryDict[filename].data)

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

    def tellPak(self):
        return self.tell() + self.offset
