from DataFile import DataFile
from DataJson import DataJson
from Assets import DataAsset, DataAssetOnly, DataMap
from DataTable import DataTable, Table, Row


class Manager:
    Pak = None
    Instances = {}

    @classmethod
    def _getInstance(cls, basename, obj, *args, **kwargs):
        if basename not in cls.Instances:
            cls.Instances[basename] = obj(cls.Pak, basename, *args, **kwargs)
        inst = cls.Instances[basename]
        assert isinstance(inst, obj), f'Type mistmatch for {basename}: type {type(inst)} called by {type(obj)}'
        return inst

    # Use this if type checking doesn't matter
    @classmethod
    def getInstance(cls, basename):
        assert basename in cls.Instances, f'{basename} has not yet been extracted!'
        return cls.Instances[basename]

    @classmethod
    def getData(cls, basename):
        return cls._getInstance(basename, DataFile)

    @classmethod
    def getJson(cls, basename):
        return cls._getInstance(basename, DataJson)

    @classmethod
    def getAsset(cls, basename, includePatches=True):
        return cls._getInstance(basename, DataAsset, includePatches=includePatches)

    @classmethod
    def getAssetOnly(cls, basename, includePatches=True):
        return cls._getInstance(basename, DataAssetOnly, includePatches=includePatches)

    @classmethod
    def getMap(cls, basename, includePatches=True):
        return cls._getInstance(basename, DataMap, includePatches=includePatches)

    @classmethod
    def getTable(cls, basename, table=Table, row=Row):
        return cls._getInstance(basename, DataTable, table, row).table

    @classmethod
    def updateAll(cls, force=False):
        for key, obj in cls.Instances.items():
            print('Updating', key)
            obj.update(cls.Pak, force)

    @classmethod
    def clean(cls):
        cls.Instances.clear()
        cls.Pak.clean()
