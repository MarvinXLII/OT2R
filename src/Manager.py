from DataFile import DataFile
from DataJson import DataJson, DataJsonFile
from Assets import DataAsset, DataAssetOnly, DataMap
from DataTable import DataTable, Table, Row


class Manager:
    Pak = None
    Instances = {}

    @classmethod
    def _get_instance(cls, basename, obj, *args, **kwargs):
        if basename not in cls.Instances:
            cls.Instances[basename] = obj(cls.Pak, basename, *args, **kwargs)
        inst = cls.Instances[basename]
        assert isinstance(inst, obj), f'Type mistmatch for {basename}: type {type(inst)} called by {type(obj)}'
        return inst

    # Use this if type checking doesn't matter
    @classmethod
    def get_instance(cls, basename):
        assert basename in cls.Instances, f'{basename} has not yet been extracted!'
        return cls.Instances[basename]

    @classmethod
    def get_data(cls, basename):
        return cls._get_instance(basename, DataFile)

    @classmethod
    def get_json(cls, basename):
        return cls._get_instance(basename, DataJson)

    @classmethod
    def get_json_data(cls, basename, data):
        return cls._get_instance(basename, DataJsonFile, data)

    @classmethod
    def get_asset(cls, basename, include_patches=True):
        return cls._get_instance(basename, DataAsset, include_patches=include_patches)

    @classmethod
    def get_asset_only(cls, basename, include_patches=True):
        return cls._get_instance(basename, DataAssetOnly, include_patches=include_patches)

    @classmethod
    def get_map(cls, basename, include_patches=True):
        return cls._get_instance(basename, DataMap, include_patches=include_patches)

    @classmethod
    def get_table(cls, basename, table=Table, row=Row):
        return cls._get_instance(basename, DataTable, table, row).table

    @classmethod
    def update_all(cls, force=False):
        for key, obj in cls.Instances.items():
            print('Updating', key)
            obj.update(cls.Pak, force)

    @classmethod
    def initialize(cls):
        cls.Instances.clear()
        cls.Pak.initialize()
