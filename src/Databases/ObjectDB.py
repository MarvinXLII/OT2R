from DataTable import Table, Row
import hjson
from Utility import get_filename
from Manager import Manager

class ObjectRow(Row):
    data = hjson.load(open(get_filename('json/objectPlaces.json'), 'r', encoding='utf-8'))

    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.item

    @property
    def is_chest(self):
        return self.ObjectType in [1, 2, 6, 7]

    @property
    def is_hidden(self):
        return self.ObjectType in [4, 5]

    @property
    def is_valid(self):
        return self.data[self.key]['valid']

    @property
    def is_always_accessible(self):
        return self.data[self.key]['always_accessible']

    @property
    def from_npc(self):
        return self.data[self.key]['npc']

    @property
    def region(self):
        return self.data[self.key]['region']

    @property
    def location(self):
        return self.data[self.key]['location']

    @property
    def ring(self):
        return self.data[self.key]['ring']

    @property
    def item(self):
        if self.ObjectType == 8:
            return 'Random item?'

        if self.IsMoney:
            assert self.HaveItemCnt > 0
            return f"{self.HaveItemCnt} leaves"

        item_db = Manager.get_instance('ItemDB').table
        name = item_db.get_name(self.HaveItemLabel)
        if name == 'None':
            assert self.HaveItemCnt == 0
            return 'None'
        if name is None:
            return 'None'

        if self.HaveItemCnt > 1:
            name = f"{name} x{self.HaveItemCnt}"

        return name
        

class ObjectTable(Table):
    def get_chests(self):
        return [row for row in self if row.is_chest and row.is_valid]

    def get_hidden(self):
        return [row for row in self if row.is_hidden and row.is_valid]

    def get_tbd(self): # Not sure what object type 8 is; seem to be random items
        return [row for row in self if row.ObjectType == 8]
