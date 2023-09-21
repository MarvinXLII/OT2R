from Assets import DataAsset
from copy import deepcopy

class Row:
    def __init__(self, key, data):
        self._key = key
        self._data = data
        for k, v in self._data.items():
            assert not hasattr(self, k), k
            setattr(self, k, v.value)

    def data_to_attr(self):
        for k in self.keys:
            v = self._data[k]
            setattr(self, k, v.value)

    @property
    def key(self):
        return self._key

    @property
    def keys(self):
        return list(self._data.keys())

    # Loop over elements of the row
    def __iter__(self):
        for k in self.keys:
            yield getattr(self, k)

    def update(self):
        for k, v in self._data.items():
            v.value = getattr(self, k)

    def __dict__(self):
        return {k: getattr(self, k) for k in self.keys}

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__().items():
            setattr(result, k, deepcopy(v, memo))
        setattr(result, '_key', deepcopy(self._key, memo))
        setattr(result, '_data', deepcopy(self._data, memo))
        return result


class RowSplit(Row):
    def __init__(self, key, data):
        self._key = key
        self._data = data
        for k, v in data.items():
            kj = k.split('_')[0]
            assert not hasattr(self, kj)
            setattr(self, kj, v.value)

    @property
    def keys(self):
        return [k.split('_')[0] for k in self._data.keys()]

    def update(self):
        for k, v in self._data.items():
            kj = k.split('_')[0]
            v.value = getattr(self, kj)


class Table:
    def __init__(self, data, row_class):
        self._row_class = row_class
        self._data = data
        for k, v in data.items():
            assert not hasattr(self, k)
            setattr(self, k, self._row_class(k, v))

    def get_row(self, key):
        if hasattr(self, key):
            return getattr(self, key)

    @property
    def keys(self):
        return list(self._data.keys())

    def __iter__(self):
        for k in self.keys:
            yield getattr(self, k)

    def update(self):
        for k in self._data.keys():
            row = getattr(self, k)
            row.update()

    def duplicate_data(self, key, new_key):
        if new_key not in self._data:
            self._data[new_key] = None
        self._data[new_key] = deepcopy(self._data[key])
        setattr(self, new_key, self._row_class(new_key, self._data[new_key]))
        

class DataTable(DataAsset):
    def __init__(self, pak, basename, table_class, row_class):
        super().__init__(pak, basename)
        assert self.uasset.n_exports == 1
        assert self.uasset.exports[1].structure == 'DataTable'
        self.table = table_class(self.uasset.exports[1].uexp2.data, row_class)

    def update(self, pak, force=False):
        self.table.update()
        super().update(pak, force)
