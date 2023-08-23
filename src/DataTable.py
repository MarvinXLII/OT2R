from Assets import Data

class Row:
    def __init__(self, key, data):
        self._key = key
        self._data = data
        for k, v in data.items():
            assert not hasattr(self, k), k
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

    @property
    def textDB(self):
        return Data.getInstance('GameTextEN')

    @property
    def itemDB(self):
        return Data.getInstance('ItemDB')

    @property
    def enemyDB(self):
        return Data.getInstance('EnemyDB')

    @property
    def shopDB(self):
        return Data.getInstance('PurchaseItemTable')

    @property
    def npcShopDB(self):
        return Data.getInstance('NPCPurchaseData')


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
    def __init__(self, data, rowClass):
        self._data = data
        for k, v in data.items():
            assert not hasattr(self, k)
            setattr(self, k, rowClass(k, v))

    def getRow(self, key):
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
        

class DataTable(Data):
    Table = Table
    Row = Row

    def __init__(self, filename):
        super().__init__(filename)
        self.table = self.getDataTable()

    def getDataTable(self):
        assert self.uasset.n_exports == 1
        assert self.uasset.exports[1].structure == 'DataTable'
        return self.Table(self.uasset.exports[1].uexp2.data, self.Row)

    def update(self, force=False):
        self.table.update()
        super().update(force)
