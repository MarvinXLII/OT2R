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
    def isChest(self):
        return self.ObjectType in [1, 2, 6, 7]

    @property
    def isHidden(self):
        return self.ObjectType in [4, 5]

    @property
    def isValid(self):
        return self.data[self.key]['valid']

    @property
    def isAlwaysAccessible(self):
        return self.data[self.key]['alwaysAccessible']

    @property
    def fromNPC(self):
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

        itemDB = Manager.getInstance('ItemDB').table
        name = itemDB.getName(self.HaveItemLabel)
        if name == 'None':
            assert self.HaveItemCnt == 0
            return 'None'
        if name is None:
            return 'None'

        if self.HaveItemCnt > 1:
            name = f"{name} x{self.haveItemCnt}"

        return name
        

class ObjectTable(Table):
    def getChests(self):
        return [row for row in self if row.isChest and row.isValid]

    def getHidden(self):
        return [row for row in self if row.isHidden and row.isValid]

    def getTBD(self): # Not sure what object type 8 is; seem to be random items
        return [row for row in self if row.ObjectType == 8]
