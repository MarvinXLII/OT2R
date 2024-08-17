from Utility import Byte, File
from functools import partial
import sys
import ast
import struct
from dataclasses import dataclass
from copy import deepcopy


class FloatProperty(Byte):
    def __init__(self, file):
        self.data_type = 'FloatProperty'
        assert file.read_int64() == 4
        file.data.seek(1, 1)
        self.value = file.read_float()

    def build(self, uasset):
        tmp = self.get_int64(4)
        tmp += bytearray([0])
        tmp += self.get_float(self.value)
        return tmp

    def __repr__(self):
        return str(self.value)

class StrProperty(Byte):
    def __init__(self, file):
        self.data_type = 'StrProperty'
        size = file.read_int64()
        file.data.seek(1, 1)
        self.value = file.read_string()

    def build(self, uasset):
        tmp = self.get_string(self.value)
        size = len(tmp)
        return self.get_int64(size) + b'\x00' + tmp

    def __repr__(self):
        return self.value

class SetProperty(Byte):
    def __init__(self, file, uasset):
        self.data_type = 'SetProperty'
        self.size = file.read_uint64()
        self.prop = uasset.get_name(file.read_uint64())
        assert self.prop == 'NameProperty'
        file.data.seek(1, 1)
        addr = file.data.tell()
        assert file.read_int32() == 0
        self.num = file.read_uint32()
        self.value = []
        for _ in range(self.num):
            self.value.append(uasset.get_name(file.read_uint64()))
        assert file.data.tell() == addr + self.size

    def build(self, uasset):
        tmp = self.get_uint64(self.size)
        tmp += self.get_uint64(uasset.get_index(self.prop))
        tmp += bytearray([0]*5)
        tmp += self.get_uint32(self.num)
        for n in self.setList:
            tmp += self.get_uint64(uasset.get_index(n))
        return tmp

    def  __repr__(self):
        return ', '.join(self.value)

class EnumProperty(Byte):
    def __init__(self, file, uasset):
        self.data_type = 'EnumProperty'
        assert file.read_int64() == 8
        self.value_0 = uasset.get_name(file.read_int64())
        assert file.read_int8() == 0
        self.value = uasset.get_name(file.read_int64())

    def build(self, uasset):
        tmp = self.get_int64(8)
        tmp += self.get_int64(uasset.get_index(self.value_0))
        tmp += bytearray([0])
        tmp += self.get_int64(uasset.get_index(self.value))
        return tmp

    def __repr__(self):
        return self.value

    def get(self):
        return self.value


class BoolProperty(Byte):
    def __init__(self, file):
        self.data_type = 'BoolProperty'
        assert file.read_int64() == 0
        self.value = file.read_int8()
        file.data.seek(1, 1)

    def build(self, uasset):
        tmp = bytearray([0]*8)
        tmp += self.get_int8(self.value)
        tmp += bytearray([0])
        return tmp

    def __repr__(self):
        return 'True' if self.value else 'False'

    def get(self):
        return 'True' if self.value else 'False'


class NameProperty(Byte):
    def __init__(self, file, uasset):
        self.data_type = 'NameProperty'
        assert file.read_int64() == 8
        file.data.seek(1, 1)
        self.value = uasset.get_name(file.read_int64())

    def build(self, uasset):
        tmp = self.get_int64(8)
        tmp += bytearray([0])
        tmp += self.get_int64(uasset.get_index(self.value))
        return tmp

    def __repr__(self):
        return self.value

    def get(self):
        return self.value

class IntProperty(Byte):
    def __init__(self, file):
        self.data_type = 'IntProperty'
        assert file.read_int64() == 4
        file.data.seek(1, 1)
        self.value = file.read_int32()

    def build(self, uasset):
        tmp = self.get_int64(4)
        tmp += bytearray([0])
        tmp += self.get_int32(self.value)
        return tmp

    def __repr__(self):
        return str(self.value)

    def get(self):
        return self.value


class UInt32Property(Byte):
    def __init__(self, file):
        self.data_type = 'UInt32Property'
        assert file.read_int64() == 4
        file.data.seek(1, 1)
        self.value = file.read_uint32()

    def build(self, uasset):
        tmp = self.get_int64(4)
        tmp += bytearray([0])
        tmp += self.get_uint32(self.value)
        return tmp

    def __repr__(self):
        return str(self.value)

    def get(self):
        return self.value


class Int64Property(Byte):
    def __init__(self, file):
        self.data_type = 'Int64Property'
        assert file.read_int64() == 8
        file.data.seek(1, 1)
        self.value = file.read_int64()

    def build(self, uasset):
        tmp = self.get_int64(8)
        tmp += bytearray([0])
        tmp += self.get_int64(self.value)
        return tmp

    def __repr__(self):
        return str(self.value)

    def get(self):
        return self.value


class ByteProperty(Byte):
    def __init__(self, file):
        self.data_type = 'ByteProperty'
        self.size = file.read_int64()
        # assert file.read_int64() == 1
        self.value_0 = file.read_int64()
        file.data.seek(1, 1)
        if self.size == 1:
            self.value = file.read_int8()
        elif self.size == 8:
            self.value = file.read_int64()
        else:
            sys.exit(f'ByteProperty not set up for byte size of {self.size}')

    def build(self, uasset):
        tmp = self.get_int64(self.size)
        tmp += self.get_int64(self.value_0)
        tmp += bytearray([0])
        if self.size == 1:
            tmp += self.get_int8(self.value)
        elif self.size == 8:
            tmp += self.get_int64(self.value)
        return tmp

    def __repr__(self):
        return str(self.value)

    def get(self):
        return self.value


class SoftObjectProperty(Byte):
    def __init__(self, file, uasset):
        self.data_type = 'SoftObjectProperty'
        assert file.read_int64() == 0xc
        file.data.seek(1, 1)
        self.value = uasset.get_name(file.read_uint64())
        assert file.read_uint32() == 0

    def build(self, uasset):
        tmp = self.get_int64(0xc)
        tmp += bytearray([0])
        tmp += self.get_uint64(uasset.get_index(self.value))
        tmp += bytearray([0]*4)
        return tmp
        
    def __repr__(self):
        return f"{self.value} (SoftObjectProperty)"

    def get(self):
        return f"{self.value} (SoftObjectProperty)"

class ObjectProperty(Byte):
    def __init__(self, file, uasset):
        self.data_type = 'ObjectProperty'
        assert file.read_uint64() == 4
        file.data.seek(1, 1)
        self.value = file.read_int32()

    def build(self, uasset):
        tmp = self.get_int64(4)
        tmp += bytearray([0])
        tmp += self.get_int32(self.value)
        return tmp
        
    def __repr__(self):
        return f"{self.value}"

    def get(self):
        return f"{self.value}"

# Essentially an array of structs?
class MapProperty(Byte):
    def __init__(self, file, uasset, callback_load, callback_build):
        # self.none = uasset.get_index('None')
        self.callback_build = callback_build
        self.data_type = 'MapProperty'
        self.size = file.read_uint64()
        self.prop = uasset.get_name(file.read_uint64())
        self.prop_2 = uasset.get_name(file.read_uint64())
        assert self.prop_2 in ['StructProperty', 'SoftObjectProperty', 'EnumProperty', 'NameProperty'], f"MapProperty not setup for {self.prop_2}: see {hex(file.tell())}"
        assert file.read_uint8() == 0
        end = file.tell() + self.size
        assert file.read_uint32() == 0
        self.num = file.read_uint32()
        self.value = {}
        for i in range(self.num):
            if self.prop == 'EnumProperty':
                key = uasset.get_name(file.read_int64())
            elif self.prop == 'IntProperty':
                key = file.read_int32()
            elif self.prop == 'NameProperty':
                key = uasset.get_name(file.read_int64())
            else:
                sys.exit(f"loadTable MapProperty not setup for {self.data_type}")
            if self.prop_2 == 'StructProperty':
                self.value[key] = callback_load()
            elif self.prop_2 == 'SoftObjectProperty':
                self.value[key] = bytearray(file.read_bytes(0xc))
            elif self.prop_2 == 'EnumProperty':
                self.value[key] = uasset.get_name(file.read_int64())
            elif self.prop_2 == 'NameProperty':
                self.value[key] = uasset.get_name(file.read_int64())
            else:
                sys.exit(f"MapProperty prop 2 not setup for {self.prop_2}")
        assert file.tell() == end

    def build(self, uasset):
        tmp_2 = bytearray([0,0,0,0])
        tmp_2 += uasset.get_uint32(self.num)
        for key, value in self.value.items():
            if self.prop == 'EnumProperty':
                tmp_2 += uasset.get_uint64(uasset.get_index(key))
            elif self.prop == 'IntProperty':
                tmp_2 += uasset.get_uint32(key)
            elif self.prop == 'NameProperty':
                tmp_2 += uasset.get_uint64(uasset.get_index(key))
            else:
                sys.exit()
            if self.prop_2 == 'StructProperty':
                tmp_2 += self.callback_build(value)
            elif self.prop_2 == 'SoftObjectProperty':
                tmp_2 += value
            elif self.prop_2 == 'EnumProperty':
                tmp_2 += uasset.get_uint64(uasset.get_index(value))
            elif self.prop_2 == 'NameProperty':
                tmp_2 += uasset.get_uint64(uasset.get_index(value))
            else:
                sys.exit()

        tmp = bytearray([])
        tmp += uasset.get_uint64(len(tmp_2))
        tmp += uasset.get_uint64(uasset.get_index(self.prop))
        tmp += uasset.get_uint64(uasset.get_index(self.prop_2))
        tmp += bytearray([0])
        return tmp + tmp_2

    def __repr__(self):
        s = ''
        for key, value in self.value.items():
            s += key
            s += ' '
            if self.prop_2 == 'StructProperty':
                s += repr(value)
            elif self.prop_2 == 'SoftObjectProperty':
                s += ' '.join([hex(i)[2:] for i in value])
            elif self.prop_2 == 'EnumProperty':
                s += value
            elif self.prop_2 == 'NameProperty':
                s += value
            s += '\n'
        return s
        # return 'MapProperty repr not yet written!'

    def get(self):
        return 'MapProperty get not yet written!'

    def __deepcopy__(self, memo):
        cls = self.__class__
        obj = cls.__new__(cls)
        memo[id(self)] = obj
        for k, v in self.__dict__.items():
            if k == 'callback_build':
                v = dict()
            setattr(obj, k, deepcopy(v, memo))
            pass
        obj.callback_build = self.__dict__['callback_build']
        return obj
    
# MonsterDataAsset: Include a bunch of floats I won't need to modify.
# Just lost struct as a bytearray
class StructProperty(Byte):
    def __init__(self, file, uasset, callback_load, callback_build):
        self.none = uasset.get_index('None')
        self.callback_build = callback_build
        self.data_type = 'StructProperty'
        self.struct_size = file.read_int32()
        self.struct_num = file.read_int32()
        self.struct_type = uasset.get_name(file.read_int64())
        self.unknown = file.read_bytes(17)
        # self.struct_data = file.data.read(self.size)
        self.structure_works = True
        self.value = {}
        self._value = {}
        if self.struct_type == 'Vector':
            assert self.struct_size == 0xc
            self.value['x'] = file.read_float()
            self.value['y'] = file.read_float()
            self.value['z'] = file.read_float()
        elif self.struct_type == 'IntVector':
            self.value['x'] = file.read_int32()
            self.value['y'] = file.read_int32()
            self.value['z'] = file.read_int32()
        elif self.struct_type == 'IntPoint':
            self.value['x'] = file.read_int32()
            self.value['y'] = file.read_int32()
        elif self.struct_type == 'Vector2D':
            assert self.struct_size == 0x8
            self.value['x'] = file.read_int32()
            self.value['y'] = file.read_int32()
        elif self.struct_type == 'LinearColor':
            self.value['r'] = file.read_float()
            self.value['g'] = file.read_float()
            self.value['b'] = file.read_float()
            self.value['a'] = file.read_float()
        elif self.struct_type == 'Guid':
            assert self.struct_size == 0x10
            self.value['guid'] = file.read_bytes(self.struct_size)
        elif self.struct_type == 'SoftClassPath':
            assert self.struct_size == 0xc
            self.value['scp'] = file.read_bytes(self.struct_size)
        elif self.struct_type == 'Rotator':
            assert self.struct_size == 0xc
            self.value['rx'] = file.read_float()
            self.value['ry'] = file.read_float()
            self.value['rz'] = file.read_float()
        elif self.struct_type == 'Timespan':
            assert self.struct_size == 0x8
            self.value['t'] = file.read_uint64()
        else:
            start = file.tell()
            try:
                self._value = callback_load()
                self.value = {k:v.value for k, v in self._value.items()}
            except:
                print('Structure failed for', self.struct_type)
                self.structure_works = False
                file.data.seek(start)
                self.value = file.read_bytes(self.struct_size)

    def build(self, uasset):
        tmp = self.get_int32(self.struct_size)
        tmp += self.get_int32(self.struct_num)
        if self.struct_type == 'Vector':
            tmp += self.get_int64(uasset.get_index(self.struct_type))
            tmp += self.unknown
            tmp += self.get_float(self.value['x'])
            tmp += self.get_float(self.value['y'])
            tmp += self.get_float(self.value['z'])
            return tmp
        elif self.struct_type == 'IntVector':
            tmp += self.get_int64(uasset.get_index(self.struct_type))
            tmp += self.unknown
            tmp += self.get_int32(self.value['x'])
            tmp += self.get_int32(self.value['y'])
            tmp += self.get_int32(self.value['z'])
            return tmp
        elif self.struct_type == 'IntPoint':
            tmp += self.get_int64(uasset.get_index(self.struct_type))
            tmp += self.unknown
            tmp += self.get_int32(self.value['x'])
            tmp += self.get_int32(self.value['y'])
            return tmp
        elif self.struct_type == 'Vector2D':
            tmp += self.get_int64(uasset.get_index(self.struct_type))
            tmp += self.unknown
            tmp += self.get_int32(self.value['x'])
            tmp += self.get_int32(self.value['y'])
            return tmp
        elif self.struct_type == 'LinearColor':
            tmp += self.get_int64(uasset.get_index(self.struct_type))
            tmp += self.unknown
            tmp += self.get_float(self.value['r'])
            tmp += self.get_float(self.value['g'])
            tmp += self.get_float(self.value['b'])
            tmp += self.get_float(self.value['a'])
            return tmp
        elif self.struct_type == 'Guid':
            tmp += self.get_int64(uasset.get_index(self.struct_type))
            tmp += self.unknown
            tmp += self.value['guid']
            return tmp
        elif self.struct_type == 'SoftClassPath':
            tmp += self.get_int64(uasset.get_index(self.struct_type))
            tmp += self.unknown
            tmp += self.value['scp']
            return tmp
        elif self.struct_type == 'Rotator':
            tmp += self.get_int64(uasset.get_index(self.struct_type))
            tmp += self.unknown
            tmp += self.get_float(self.value['rx'])
            tmp += self.get_float(self.value['ry'])
            tmp += self.get_float(self.value['rz'])
            return tmp
        elif self.struct_type == 'Timespan':
            tmp += self.get_int64(uasset.get_index(self.struct_type))
            tmp += self.unknown
            tmp += self.get_uint64(self.value['t'])
            return tmp
        elif not self.structure_works:
            tmp += self.get_int64(uasset.get_index(self.struct_type))
            tmp += self.unknown
            tmp += self.value
            return tmp

        for k, v in self.value.items():
            self._value[k].value = v

        assert self.struct_num == 0
        none = uasset.get_index('None')
        tmp_2 = self.callback_build(self._value)
        tmp = self.get_int64(len(tmp_2))
        tmp += self.get_int64(uasset.get_index(self.struct_type))
        tmp += self.unknown
        return tmp + tmp_2

    def __repr__(self):
        # if self.struct_type == 'Vector' or self.struct_type == 'IntVector':
        #     return f"{{'x': {self._value['x']}, 'y': {self._value['y']}, 'z': {self._value['z']}}}"
        # elif self.struct_type == 'Vector2D' or self.struct_type == 'IntVector':
        #     return f"{{'x': {self._value['x']}, 'y': {self._value['y']}}}"
        # elif self.struct_type == 'LinearColor':
        #     return f"{{'r': {self._value['r']}, 'g': {self._value['g']}, 'b': {self._value['b']}, 'a': {self._value['a']}}}"
        # elif self.struct_type == 'Guid':
        #     return str(self._value['guid'].hex())
        # elif self.struct_type == 'SoftClassPath':
        #     return str(self._value['scp'].hex())
        # elif self.struct_type == 'Rotator':
        #     return f"{{'rx': {self._value['rx']}, 'ry': {self._value['ry']}, 'rz': {self._value['rz']}}}"
        return str(self.value)

    def __deepcopy__(self, memo):
        cls = self.__class__
        obj = cls.__new__(cls)
        memo[id(self)] = obj
        for k, v in self.__dict__.items():
            if k == 'callback_build':
                v = dict()
            setattr(obj, k, deepcopy(v, memo))
            pass
        obj.callback_build = self.__dict__['callback_build']
        return obj
    
class TextProperty(Byte):
    def __init__(self, file):
        self.data_type = 'TextProperty'
        self.size = file.read_int64()
        assert file.read_int8() == 0
        addr = file.tell()
        self.str_type = file.read_int32()
        if file.read_int8() == -1:
            assert file.read_int32() == 0
            self.string_1 = ''
            self.string_2 = ''
            self.value = ''
        else:
            self.size_1 = file.read_int32()
            self.string_1 = file.read_string(self.size_1)
            self.size_2 = file.read_int32()
            self.string_2 = file.read_string(self.size_2)
            self.size_3 = file.read_int32()
            self.value = file.read_string(self.size_3)
        assert file.tell() == addr + self.size

    def build(self, uasset):
        tmp = self.get_int32(self.str_type)
        if not self.string_1:
            tmp += bytearray([0xff])
            tmp += bytearray([0]*4)
            return self.get_int64(9) + bytearray([0]) + tmp

        tmp += bytearray([0])
        tmp += self.get_string(self.string_1)
        tmp += self.get_string(self.string_2)
        tmp += self.get_string(self.value)

        size = len(tmp)
        return self.get_int64(size) + bytearray([0]) + tmp

    def __repr__(self):
        return ' '.join([self.string_1, self.string_2, self.value])

# No clue what this is for
class MulticastInlineDelegateProperty(Byte):
    def __init__(self, file, uasset):
        self.data_type = 'MulticastInlineDelegateProperty'
        self.size = file.read_int64()
        assert file.read_int8() == 0
        assert self.size == 0x10
        self.x1 = uasset.get_name(file.read_uint64())
        self.x2 = uasset.get_name(file.read_uint64())

    def build(self, uasset):
        tmp = self.get_uint64(uasset.get_index(self.x1))
        tmp += self.get_uint64(uasset.get_index(self.x2))
        size = len(tmp)
        assert self.size == size
        return self.get_int64(size) + bytearray([0]) + tmp

    def __repr__(self):
        return '{self.x1}, {self.x2}'


class ArrayProperty(Byte):
    def __init__(self, file, uasset, callback_load, callback_build):
        self.none = uasset.get_index('None')
        self.callback_build = callback_build
        self.data_type = 'ArrayProperty'
        self.size = file.read_int64()
        self.prop = uasset.get_name(file.read_int64())
        file.data.seek(1, 1)
        num = file.read_int32()
        self.value = []

        if self.prop == 'ByteProperty':
            assert self.size == 4 + num, f"{self.__class__.__name__}: {self.prop}"
            self.value = file.read_bytes(num)
            return

        if self.prop == 'BoolProperty':
            assert self.size == 4 + num, f"{self.__class__.__name__}: {self.prop}"
            self.value = [bool(x) for x in file.read_bytes(num)]
            return

        if self.prop == 'IntProperty' or self.prop == 'ObjectProperty':
            assert self.size == 4 + 4*num, f"{self.__class__.__name__}: {self.prop}"
            for _ in range(num):
                self.value.append(file.read_int32())
            return

        if self.prop == 'FloatProperty':
            self.value = [file.read_float() for _ in range(num)]
            return

        if self.prop == 'EnumProperty' or self.prop == 'NameProperty':
            assert self.size == 4 + 8*num, f"{self.__class__.__name__}: {self.prop}"
            for _ in range(num):
                self.value.append(uasset.get_name(file.read_uint64()))
            return

        if self.prop == 'SoftObjectProperty':
            for _ in range(num):
                self.value.append(uasset.get_name(file.read_uint64()))
                assert file.read_uint32() == 0
            return

        if self.prop == 'StrProperty':
            for _ in range(num):
                self.value.append(file.read_string())
            return

        if self.prop == 'StructProperty':
            self.name = uasset.get_name(file.read_int64())
            assert uasset.get_name(file.read_int64()) == 'StructProperty', f"{self.__class__.__name__}: {self.prop}"
            self.struct_size = file.read_int64()
            self.struct_type = uasset.get_name(file.read_int64())
            file.data.seek(17, 1)
            if self.struct_type == 'IntVector':
                for _ in range(num):
                    x = file.read_uint32()
                    y = file.read_uint32()
                    z = file.read_uint32()
                    self.value.append((x, y, z))
            elif self.struct_type == 'Vector':
                for _ in range(num):
                    x = file.read_float()
                    y = file.read_float()
                    z = file.read_float()
                    self.value.append((x, y, z))
            elif self.struct_type == 'Guid':
                for _ in range(num):
                    guid = file.read_bytes(0x10)
                    self.value.append(guid)
            else:
                for _ in range(num):
                    self.value.append(callback_load())
            return

        sys.exit(f"Load array property does not allow for {self.prop} types!")

    def build(self, uasset):
        none = uasset.get_index('None')
        tmp_1 = self.get_int64(uasset.get_index(self.prop))
        tmp_1 += bytearray([0])

        tmp_2 = self.get_int32(len(self.value))
        if self.prop == 'ByteProperty':
            tmp_2 += self.value
        elif self.prop == 'BoolProperty':
            tmp_2 += bytearray(self.value)
        elif self.prop == 'IntProperty' or self.prop == 'ObjectProperty':
            for ai in self.value:
                tmp_2 += self.get_int32(ai)
        elif self.prop == 'FloatProperty':
            for ai in self.value:
                tmp_2 += self.get_float(ai)
        elif self.prop == 'EnumProperty' or self.prop == 'NameProperty':
            for ai in self.value:
                tmp_2 += self.get_int64(uasset.get_index(ai))
        elif self.prop == 'SoftObjectProperty':
            for ai in self.value:
                tmp_2 += self.get_int64(uasset.get_index(ai))
                tmp_2 += bytearray([0]*4)
        elif self.prop == 'StrProperty':
            for ai in self.value:
                tmp_2 += self.get_string(ai)
        elif self.prop == 'StructProperty':
            tmp_2 += self.get_int64(uasset.get_index(self.name))
            tmp_2 += self.get_int64(uasset.get_index('StructProperty'))
            tmp_2 += self.get_int64(self.struct_size)
            tmp_2 += self.get_int64(uasset.get_index(self.struct_type))
            tmp_2 += bytearray([0]*17)
            if self.struct_type == 'IntVector':
                for x, y, z in self.value:
                    tmp_2 += self.get_int32(x)
                    tmp_2 += self.get_int32(y)
                    tmp_2 += self.get_int32(z)
            elif self.struct_type == 'Vector':
                for x, y, z in self.value:
                    tmp_2 += self.get_float(x)
                    tmp_2 += self.get_float(y)
                    tmp_2 += self.get_float(z)
            elif self.struct_type == 'Guid':
                for guid in self.value:
                    tmp_2 += guid
            else:
                for ai in self.value:
                    tmp_2 += self.callback_build(ai)

        tmp = self.get_int64(len(tmp_2))
        return tmp + tmp_1 + tmp_2

    def __repr__(self):
        return str(self.value)

    def __deepcopy__(self, memo):
        cls = self.__class__
        obj = cls.__new__(cls)
        memo[id(self)] = obj
        for k, v in self.__dict__.items():
            if k == 'callback_build':
                v = dict()
            setattr(obj, k, deepcopy(v, memo))
            pass
        obj.callback_build = self.__dict__['callback_build']
        return obj


class DataTableStruct(Byte):
    def __init__(self, obj):
        self.obj = obj
        self.uasset = self.obj.uasset
        self.uexp = self.obj.uexp
        self.offset = self.uexp.tell()
        assert self.uexp.read_uint32() == 0
        self.number = self.uexp.read_uint32()
        self.data = {}
        for _ in range(self.number):
            key = self.uasset.get_name(self.uexp.read_uint64())
            self.data[key] = obj.load_entry() ## DON'T use Table/Rows here to keep everything else separate

    def build(self):
        uexp = bytearray()
        uexp += self.get_uint32(0)
        uexp += self.get_uint32(len(self.data))
        none = self.get_uint64(self.uasset.get_index('None'))
        for i, (key, value) in enumerate(self.data.items()):
            uexp += self.get_uint64(self.uasset.get_index(key))
            for k, v in value.items():
                uexp += self.get_uint64(self.uasset.get_index(k))
                uexp += self.get_uint64(self.uasset.get_index(v.data_type))
                uexp += v.build(self.uasset)
            uexp += none
        return uexp


class ChunkExports(Byte):
    def __init__(self, uasset):
        self.uasset = uasset
        self.p1 = uasset.read_int32() # class (e.g. DataTableStruct, BlueprintGeneratedClass)
        self.p2 = uasset.read_int32() # CoreUObject used for Blueprint, iff BlueprintGeneratedClass
        self.p3 = uasset.read_int32() # Default class
        self.p4 = uasset.read_int32()
        try:
            self.p4 = uasset.get_name(self.p4) # Name or number????
        except:
            pass
        self.p5 = uasset.get_name(uasset.read_uint64()) # Name seems to be important here
        self.p6 = uasset.read_uint32()
        self.size = uasset.read_int64()
        self.offset = uasset.read_uint64() - uasset.size
        assert uasset.read_uint64() == 0
        assert uasset.read_uint64() == 0
        assert uasset.read_uint64() == 0
        assert uasset.read_uint64() == 0
        self.a1 = uasset.read_uint32() # ?
        self.a2 = uasset.read_uint32() # ?
        self.a3 = uasset.read_uint32() # Starting index for preload_dependency
        self.a4 = uasset.read_uint32() # sum(a4, a5, a6, a7) == number of preload_dependency used in this uexp chunk
        self.a5 = uasset.read_uint32()
        self.a6 = uasset.read_uint32()
        self.a7 = uasset.read_uint32()
        self.uexp1 = None
        self.uexp2 = None # e.g. DataTableStruct stuff

        # Structure of uexp
        if self.p2 < 0:
            self.structure = self.uasset.imports[-self.p2].p4
        elif self.p1 < 0:
            self.structure = self.uasset.imports[-self.p1].p4
        else:
            self.structure = None

    def build(self, uassetSize):
        exp = bytearray()
        exp += self.get_int32(self.p1)
        exp += self.get_int32(self.p2)
        exp += self.get_int32(self.p3)
        try:
            exp += self.get_int32(self.uasset.get_index(self.p4))
        except:
            exp += self.get_int32(self.p4)
        exp += self.get_int64(self.uasset.get_index(self.p5))
        exp += self.get_int32(self.p6)
        exp += self.get_int64(self.size)
        exp += self.get_int64(self.offset + uassetSize)
        exp += self.get_int64(0)
        exp += self.get_int64(0)
        exp += self.get_int64(0)
        exp += self.get_int64(0)
        exp += self.get_uint32(self.a1)
        exp += self.get_uint32(self.a2)
        exp += self.get_uint32(self.a3)
        exp += self.get_uint32(self.a4)
        exp += self.get_uint32(self.a5)
        exp += self.get_uint32(self.a6)
        exp += self.get_uint32(self.a7)
        return exp

    def build_uexp(self):
        uexp = bytearray()
        if self.uexp1 is not None:
            for key, value in self.uexp1.items():
                k = key.split('__')[0]
                uexp += self.get_uint64(self.uasset.get_index(k))
                uexp += self.get_uint64(self.uasset.get_index(value.data_type))
                uexp += value.build(self.uasset)
        uexp += self.get_uint64(self.uasset.get_index('None'))

        if self.uexp2 is not None:
            try:
                uexp += self.uexp2.build()
            except:
                assert type(self.uexp2) == bytearray or type(self.uexp2) == bytes
                uexp += self.uexp2

        return uexp


class ChunkImports(File):
    def __init__(self, uasset):
        self.uasset = uasset
        self.p1 = uasset.get_name(uasset.read_uint64())
        self.p2 = uasset.get_name(uasset.read_uint64())
        self.p3 = uasset.read_int32()
        self.p4 = uasset.get_name(uasset.read_uint64())

    def build(self):
        imp = bytearray()
        imp += self.get_uint64(self.uasset.get_index(self.p1))
        imp += self.get_uint64(self.uasset.get_index(self.p2))
        imp += self.get_int32(self.p3)
        imp += self.get_uint64(self.uasset.get_index(self.p4))
        return imp

    def __repr__(self):
        return f"  {self.p1}\n  {self.p2}\n  {self.p3}\n  {self.p4}\n"


# This is similar to my File reader, but designed to work with data as bytearray types
# so bytes can be modded.
class UnparsedExport(Byte):
    def __init__(self, export):
        self.addr = 0
        if export.uexp2:
            self.data = bytearray(export.uexp2)
        else:
            self.data = bytearray()
        export.uexp2 = self.data # Won't need to update this array manually
        self.export = export

    def build(self):
        return self.data

    def update(self):
        self.export.uexp2 = self.data

    def __len__(self):
        return len(self.data)

    def read_int(self, size, signed, addr):
        if addr is not None:
            self.addr = addr
        assert self.addr+size < len(self.data)
        value = int.from_bytes(self.data[self.addr:self.addr+size], byteorder='little', signed=signed)
        self.addr += size
        return value

    def read_uint8(self, addr=None):
        return self.read_int(1, False, addr)

    def read_uint16(self, addr=None):
        return self.read_int(2, False, addr)

    def read_uint32(self, addr=None):
        return self.read_int(4, False, addr)

    def read_uint64(self, addr=None):
        return self.read_int(8, False, addr)

    def assert_uint8(self, value, addr=None):
        v = self.read_uint8(addr)
        assert value == v, f"wrong value; actually {hex(v)}"

    def assert_uint16(self, value, addr=None):
        v = self.read_uint16(addr)
        assert value == v, f"wrong value; actually {hex(v)}"

    def assert_uint32(self, value, addr=None):
        v = self.read_uint32(addr)
        assert value == v, f"wrong value; actually {hex(v)}"

    def assertUInt64(self, value, addr=None):
        v = self.read_uint64(addr)
        assert value == v, f"wrong value; actually {hex(v)}"

    def patch(self, b, addr):
        if addr is not None:
            self.addr = addr
        s = len(b)
        self.data[self.addr:self.addr+s] = b
        self.addr += s

    def patch_uint8(self, value, addr=None):
        b = self.get_uint8(value)
        self.patch(b, addr)

    def patch_uint16(self, value, addr=None):
        b = self.get_uint16(value)
        self.patch(b, addr)

    def patch_uint32(self, value, addr=None):
        b = self.get_uint32(value)
        self.patch(b, addr)

    def patch_uint64(self, value, addr=None):
        b = self.get_uint64(value)
        self.patch(b, addr)

    def print_addr(self, b, print_val=None):
        if print_val is None:
            print('Value', b, f'({list(map(hex, b))})', 'at:')
        else:
            print('Print Value', print_val, b, f'({list(map(hex, b))})', 'at:')
        # b = f(v)
        i = 0
        while True:
            try:
                i += self.data[i:].index(b)
            except:
                break
            print('  ', hex(i))
            i += 1

    def print_byte_const(self, value):
        print('Print byte const', value, f'({hex(value)})')
        value <<= 8
        value += 0x24
        self.print_addr(self.get_uint16(value))

    def print_addr_uint8(self, value):
        self.print_addr(self.get_uint8(value))

    def print_addr_uint16(self, value):
        self.print_addr(self.get_uint16(value))

    def print_addr_uint32(self, value):
        self.print_addr(self.get_uint32(value))

    def print_addr_uint64(self, value):
        self.print_addr(self.get_uint64(value))

    def print_addr_bool_on(self):
        self.print_addr_uint8(0x27)

    def print_addr_bool_off(self):
        self.print_addr_uint8(0x28)

    def print_addr_int_const(self, value):
        vb = value << 8
        vb += 0x1d
        vb = vb.to_bytes(5, byteorder='little')
        self.print_addr(vb, value)

    def assert_bool_on(self, addr=None):
        self.assert_uint8(0x27, addr)

    def assert_bool_off(self, addr=None):
        self.assert_uint8(0x28, addr)

    def toggle_bool_on(self, addr):
        vanilla = self.read_uint8(addr)
        assert vanilla in [0x27, 0x28]
        self.patch_uint8(0x27, addr)

    def toggle_bool_off(self, addr):
        vanilla = self.read_uint8(addr)
        assert vanilla in [0x27, 0x28]
        self.patch_uint8(0x28, addr)

    def patch_int_const(self, addr, orig, value):
        self.assert_uint8(0x1d, addr)
        self.assert_uint32(orig, addr+1)
        self.patch_uint32(value, addr+1)

    def read_int_const(self, addr):
        self.assert_uint8(0x1d, addr)
        return self.read_uint32(addr+1)

    def patch_byte_const(self, addr, orig, value):
        self.assert_uint8(0x24, addr)
        self.assert_uint8(orig, addr+1)
        self.patch_uint8(value, addr+1)

    def read_byte_const(self, addr):
        self.assert_uint8(0x24, addr)
        return self.read_uint8(addr+1)


@dataclass
class Index(Byte):
    idx: int
    string: str
    id: bytearray

    def build(self):
        b = self.get_string(self.string)
        b += self.id
        return b

    def get(self):
        return {
            'string': self.string,
            'id': self.id.hex(),
        }

    def __repr__(self):
        i = str(self.idx).rjust(5, ' ')
        h = struct.unpack('<H', struct.pack('>H', self.idx))[0]
        h = format(h, f'04x')
        id_val = int.from_bytes(self.id, byteorder='little')
        id_val = format(id_val, f'08x')
        return f"{i} 0x{h} 0x{id_val} {self.string}"


class UAsset(File):
    index_id = {}
    
    def __init__(self, data, uexp_size):
        super().__init__(data)
        self.skip = []

        self.data.seek(0)
        self.uexp_size = uexp_size
        
        # "Header" of uasset
        assert self.read_uint32() == 0x9e2a83c1
        assert self.read_uint32() == 0xfffffff9
        assert self.read_uint64() == 0
        assert self.read_uint64() == 0

        # Size of uasset/umap file
        self.data_size = self.read_uint32()
        assert self.data_size == self.size

        assert self.read_string() == 'None'

        # Not sure what each bit means
        self.encoding = self.read_uint32()
        assert self.encoding in [0x80000000,0x80040000,0x80020000]

        # Stuff for indexing (n = number, o = offset)
        self.n_indexing = self.read_uint32()
        self.o_indexing = self.read_uint32()
        assert self.read_uint64() == 0

        # Counts and offsets
        self.n_exports = self.read_uint32()
        self.o_exports = self.read_uint32()
        self.n_imports = self.read_uint32()
        self.o_imports = self.read_uint32()
        self.o_depends = self.read_uint32()
        self.n_depends = self.n_exports
        assert self.read_uint64() == 0
        assert self.read_uint64() == 0

        # ID for the file
        self.guid = self.read_bytes(0x10)

        # TBD (GenerationCount?)
        assert self.read_uint32() == 1

        # Repeats of stuff
        assert self.read_uint32() == self.n_exports
        assert self.read_uint32() == self.n_indexing

        assert self.read_uint64() == 0
        assert self.read_uint64() == 0
        assert self.read_uint64() == 0
        assert self.read_uint64() == 0
        assert self.read_uint32() == 0

        # More TBD stuff (u = unknown)
        self.u_tbd_4 = self.read_uint32()
        assert self.read_uint32() == 0

        # More counts and offsets
        self.o_asset_reg_data = self.read_uint32()
        self.o_bulk_data_start = self.read_uint64()
        assert self.o_bulk_data_start == self.size + self.uexp_size - 4
        assert self.read_uint64() == 0
        self.n_preload_dependency = self.read_uint32()
        self.o_preload_dependency = self.read_uint32()
        assert self.o_preload_dependency - self.o_asset_reg_data == 4

        # Indexing chunk
        assert self.tell() == self.o_indexing
        self.index = {}
        self.index_name = {}
        self.index_id = {}
        for i in range(self.n_indexing):
            string = self.read_string()
            key = self.read_bytes(4)
            idx = Index(i, string, key)
            self.index[i] = idx
            self.index_name[idx.string] = i
            if idx.string in UAsset.index_id:
                assert UAsset.index_id[idx.string] == idx.id
            else:
                UAsset.index_id[idx.string] = idx.id

        assert self.tell() == self.o_imports

        self.imports = {}
        for i in range(self.n_imports):
            self.imports[i+1] = ChunkImports(self)
        assert self.tell() == self.o_exports

        self.exports = {}
        for i in range(self.n_exports):
            self.exports[i+1] = ChunkExports(self)
        assert self.tell() == self.o_depends

        self.depends = {}
        for i in range(self.n_depends):
            self.depends[i+1] = self.read_int32()
            assert self.depends[i+1] == 0
        assert self.tell() == self.o_asset_reg_data

        self.asset_reg_data = self.read_uint32()
        assert self.asset_reg_data == 0

        self.preload_dependency = {}
        for i in range(self.n_preload_dependency):
            self.preload_dependency[i] = self.read_int32()
        assert self.tell() == self.size

    def build(self, uexp_size):
        # First build indexing
        indexing = bytearray()
        for i in range(self.n_indexing):
            indexing += self.index[i].build()
        
        # Next must calculate size of uasset (assumes nothing else will change in size!)
        size = self.o_indexing + len(indexing) + 0x1c*self.n_imports \
            + 0x68*self.n_exports + 4*self.n_depends + 4 + 4*self.n_preload_dependency

        uasset = bytearray()
        def update_offset(addr):
            assert addr > 0
            uasset[addr:addr+4] = self.get_uint32(len(uasset))
        
        offsets = [0]*7
        uasset += self.get_uint32(0x9e2a83c1)
        uasset += self.get_uint32(0xfffffff9)
        uasset += self.get_uint64(0)
        uasset += self.get_uint64(0)
        uasset += self.get_uint32(size)
        uasset += self.get_string('None')
        uasset += self.get_uint32(self.encoding)
        uasset += self.get_uint32(self.n_indexing)
        offsets[0] = len(uasset)
        uasset += self.get_uint32(self.o_indexing)
        uasset += self.get_uint64(0)
        uasset += self.get_uint32(self.n_exports)
        offsets[1] = len(uasset)
        uasset += self.get_uint32(self.o_exports)
        uasset += self.get_uint32(self.n_imports)
        offsets[2] = len(uasset)
        uasset += self.get_uint32(self.o_imports)
        offsets[3] = len(uasset)
        uasset += self.get_uint32(self.o_depends)
        uasset += self.get_uint64(0)
        uasset += self.get_uint64(0)
        uasset += self.guid
        uasset += self.get_uint32(1)
        uasset += self.get_uint32(self.n_exports)
        uasset += self.get_uint32(self.n_indexing)
        uasset += self.get_uint64(0)
        uasset += self.get_uint64(0)
        uasset += self.get_uint64(0)
        uasset += self.get_uint64(0)
        uasset += self.get_uint32(0)
        uasset += self.get_uint32(self.u_tbd_4)
        uasset += self.get_uint32(0)
        offsets[5] = len(uasset)
        uasset += self.get_uint32(self.o_asset_reg_data)
        uasset += self.get_uint64(size + uexp_size - 4)
        uasset += self.get_uint64(0)
        uasset += self.get_uint32(self.n_preload_dependency)
        offsets[6] = len(uasset)
        uasset += self.get_uint32(self.o_preload_dependency)
        update_offset(offsets[0])
        uasset += indexing
        update_offset(offsets[2])
        for imp in self.imports.values():
            uasset += imp.build()
        update_offset(offsets[1])
        for exp in self.exports.values():
            uasset += exp.build(size)
        update_offset(offsets[3])
        for dep in self.depends.values():
            uasset += self.get_int32(dep)
        update_offset(offsets[5])
        uasset += self.get_uint32(0)
        update_offset(offsets[6])
        for dep in self.preload_dependency.values():
            uasset += self.get_int32(dep)

        assert len(uasset) == size
        return uasset

    # This is for the rare case that an index must be replaced.
    # It is possible for the new index to exist already, and that's ok.
    # The old index still must be deleted and the new index must replace it.
    def replace_index(self, old, new):
        i = self.get_index(old)
        if new not in UAsset.index_id:
            n = new.split('_')
            if n[-1].isnumeric():
                v = n.pop()
            new = '_'.join(n)
            assert new in UAsset.index_id
        self.index[i] = Index(i, new, UAsset.index_id[new])
        del self.index_name[old]
        # assert new not in self.index_name
        self.index_name[new] = i

    def get_name(self, value):
        name = self.index[value & 0xffffffff].string
        value >>= 32
        if value:
            return f"{name}_{value-1}"
        return name

    # A lot of files have unnecessary indices,
    # e.g. BATTLE_WEAPON_ENEMY_N_206 and BATTLE_WEAPON_ENEMY_N
    # Priority goes towards the latter
    def get_index(self, name):
        if name in self.index_name:
            idx1 = self.index_name[name]
        else:
            idx1 = -1

        if name.isdigit():
            return idx1

        n = name.split('_')
        v = n.pop()
        if v.isnumeric() and (v[0] != '0' or len(v) == 1):
            idx2 = int(v) + 1 << 32
            b = '_'.join(n)
            if b in self.index_name:
                idx2 += self.index_name[b]
            else:
                idx2 = -1
        else:
            idx2 = -1

        idx = max(idx1, idx2)
        if idx >= 0:
            return idx

        # assert name in UAsset.index_id, f'Missing {name}'
        self.add_index(name)
        return self.get_index(name)

    def add_index(self, name):
        # If already in the object's index_name, do nothing
        if name in self.index_name:
            assert name in UAsset.index_id
            return
        # Test the full name first
        if name not in UAsset.index_id:
            # Test the basename
            n = name.split('_')
            v = n.pop()
            basename = '_'.join(n)
            assert v.isnumeric()
            assert v[0] != '0', name
            if basename not in UAsset.index_id:
                sys.exit(f"{name} is not in UAsset.index_id yet!")
            # Use the basename instead of the full name
            name = basename
        # Add new index to uasset
        i = len(self.index)
        self.index[i] = Index(i, name, UAsset.index_id[name])
        self.index_name[name] = i
        self.n_indexing += 1

    def add_new_index(self, name, hash_value):
        assert name not in self.index_name
        i = len(self.index)
        hash_bytes = int.to_bytes(hash_value, length=4, byteorder='little')
        self.index[i] = Index(i, name, hash_bytes)
        self.index_name[name] = i
        self.n_indexing += 1
        UAsset.index_id[name] = hash_bytes
        

    def skip_entry(self, name):
        self.skip.append(name)

    def swap_names(self, name1, name2):
        assert name1 in self.index_name
        assert name2 in self.index_name
        idx1 = self.index_name[name1]
        idx2 = self.index_name[name2]
        self.index[idx1], self.index[idx2] = self.index[idx2], self.index[idx1]
        self.index_name[name1] = idx2
        self.index_name[name2] = idx1


class DataAsset:
    def __init__(self, pak, basename, include_patches=False):
        print(f'Loading data from {basename}')
        uexp = pak.extract_file(f'{basename}.uexp', include_patches)
        uasset = pak.extract_file(f'{basename}.uasset', include_patches)
        self.initialize(basename, uasset, uexp)

    def initialize(self, basename, uasset, uexp):
        self.basename = basename
        self.uexp = File(uexp)
        self.uasset = UAsset(uasset, self.uexp.size)
        # Store none index
        self.none = self.uasset.get_index('None')
        # Organize/"parse" uexp data
        self.set_switcher()
        self.parse_uexp()

    def set_switcher(self):
        self.switcher = {  # REPLACE WITH MATCH IN py3.10????
            'EnumProperty': partial(EnumProperty, self.uexp, self.uasset),
            'SetProperty': partial(SetProperty, self.uexp, self.uasset),
            'TextProperty': partial(TextProperty, self.uexp),
            'IntProperty': partial(IntProperty, self.uexp),
            'Int64Property': partial(Int64Property, self.uexp),
            'UInt32Property': partial(UInt32Property, self.uexp),
            'ArrayProperty': partial(ArrayProperty, self.uexp, self.uasset, self.load_entry, self.build_entry),
            'StrProperty': partial(StrProperty, self.uexp),
            'BoolProperty': partial(BoolProperty, self.uexp),
            'NameProperty': partial(NameProperty, self.uexp, self.uasset),
            'StructProperty': partial(StructProperty, self.uexp, self.uasset, self.load_entry, self.build_entry),
            'FloatProperty': partial(FloatProperty, self.uexp),
            'ByteProperty': partial(ByteProperty, self.uexp),
            'SoftObjectProperty': partial(SoftObjectProperty, self.uexp, self.uasset),
            'ObjectProperty': partial(ObjectProperty, self.uexp, self.uasset),
            'MapProperty': partial(MapProperty, self.uexp, self.uasset, self.load_entry, self.build_entry),
            'MulticastInlineDelegateProperty': partial(MulticastInlineDelegateProperty, self.uexp, self.uasset),
        }

    def parse_uexp(self):
        self.uexp.data.seek(0)
        for i, exp in enumerate(self.uasset.exports.values()):
            assert self.uexp.tell() == exp.offset
            end = exp.offset + exp.size

            dic = self.load_entry()
            assert self.uexp.tell() <= end

            # Store dict
            if dic:
                exp.uexp1 = dic

            if exp.structure == 'DataTable':
                exp.uexp2 = DataTableStruct(self)
            else:
                size = end - self.uexp.tell()
                if size > 0:
                    exp.uexp2 = self.uexp.read_bytes(size)

            assert self.uexp.tell() == end

        # Make sure uexp is at the end of the file
        assert self.uexp.read_uint32() == 0x9e2a83c1

    def get_command(self, command):
        objs = {}
        for k, exp in self.uasset.exports.items():
            if exp.structure == command:
                objs[k] = exp.uexp1
        return objs

    def get_uexp_obj_1(self, idx):
        return self.uasset.exports[idx].uexp1

    def get_uexp_obj_2(self, idx):
        return UnparsedExport(self.uasset.exports[idx])

    def get_index(self, name):
        return self.uasset.get_index(name)

    def build(self):

        # Build uexp, storing all offsets and sizes for the start of each chunk
        # Important to store these in case anything changes (e.g. strings!)
        new_uexp = bytearray()
        for exp in self.uasset.exports.values():
            exp.offset = len(new_uexp)
            new_uexp += exp.build_uexp()
            exp.size = len(new_uexp) - exp.offset
        new_uexp += self.uexp.get_uint32(0x9e2a83c1)

        new_uasset = self.uasset.build(len(new_uexp))
        return new_uasset, new_uexp

    def load_entry(self):
        dic = {}
        next_value = self.uexp.read_uint64()
        while next_value != self.none:
            key = self.uasset.get_name(next_value)
            assert '__' not in key
            prop = self.uasset.get_name(self.uexp.read_uint64())
            assert prop in self.switcher, f"{prop} not in switcher: {hex(self.uexp.tell())}"
            #### VERY CRUDE fix for repeated keys in the same entry
            #### A better solution would be to read size (int32) and num (int32) out here
            #### before switcher, rather than size (int64) in the props and only correctly
            #### reading size/num in structProperty
            if key in dic:
                i = 1
                while f'{key}__{i}' in dic:
                    i += 1
                key = f'{key}__{i}'
            dic[key] = self.switcher[prop]()
            next_value = self.uexp.read_uint64()
        return dic

    def build_entry(self, entry):
        data = bytearray()
        for key, d in entry.items():
            data += self.uexp.get_int64(self.uasset.get_index(key))
            data += self.uexp.get_int64(self.uasset.get_index(d.data_type))
            data += d.build(self.uasset)
        data += self.uexp.get_int64(self.none)
        return data

    def update(self, pak, force=False):
        # Build data
        uasset, uexp = self.build()
        self.uasset.set_data(uasset)
        self.uexp.set_data(uexp)
        # Patch pak
        pak.update_data(f'{self.basename}.uasset', uasset, force=force)
        pak.update_data(f'{self.basename}.uexp', uexp, force=force)


# The ONLY difference between this and its parent is the extension umap rather than uasset.
class DataMap(DataAsset):
    def __init__(self, pak, basename, include_patches=True):
        print(f'Loading data from {basename}')
        uexp = pak.extract_file(f'{basename}.uexp', include_patches)
        umap = pak.extract_file(f'{basename}.umap', include_patches)
        self.initialize(basename, umap, uexp)

    def update(self, pak, force=False):
        # Build data
        uasset, uexp = self.build()
        self.uasset.set_data(uasset)
        self.uexp.set_data(uexp)
        # Patch pak
        pak.update_data(f'{self.basename}.umap', uasset, force=force)
        pak.update_data(f'{self.basename}.uexp', uexp, force=force)


# AssetOnly --> parse asset only
# It still allows for editing asset and export files.
class DataAssetOnly:
    def __init__(self, pak, basename, include_patches=True):
        self.basename = basename
        self.uexp = pak.extract_file(f'{basename}.uexp', include_patches)
        uasset = pak.extract_file(f'{basename}.uasset', include_patches)
        self.uasset = UAsset(uasset, len(self.uexp))

    def patch_int8(self, addr, value):
        self.uexp[addr] = value

    def patch_int32(self, addr, value):
        self.uexp[addr:addr+4] = value.to_bytes(4, byteorder='little')

    def patch_int64(self, addr, value):
        self.uexp[addr:addr+8] = value.to_bytes(8, byteorder='little')

    def update(self, pak, force=False):
        uasset = self.uasset.build(len(self.uexp))
        self.uasset.set_data(uasset)
        pak.update_data(f'{self.basename}.uasset', uasset, force=force)
        pak.update_data(f'{self.basename}.uexp', self.uexp, force=force)
