from Assets import Data
from DataTable import DataTable, Row
import hjson
from Utility import get_filename

class Object(Row):
    placements = hjson.load(open(get_filename('json/placedTreasures.json'), 'r'))

    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.item

    @property
    def isPlaced(self):
        return Object.placements[self.key]

    @property
    def isKnowledge(self):
        return 'ITM_INF' in self.HaveItemLabel

    @property
    def isValuable(self):
        return 'ITM_TRE' in self.HaveItemLabel

    @property
    def isEventItem(self):
        return 'EventItem' in self.key

    @property
    def item(self):
        if self.ObjectType == 8:
            return 'Random item?'

        if self.IsMoney:
            assert self.HaveItemCnt > 0
            return f"{self.HaveItemCnt} leaves"

        name = self.itemDB.getName(self.HaveItemLabel)
        if name == 'None':
            assert self.HaveItemCnt == 0
            return 'None'
        if name is None:
            return 'None'

        if self.HaveItemCnt > 1:
            name = f"{name} x{self.haveItemCnt}"

        return name

    @property
    def skipShuffling(self):
        valid = self.item != 'None' or self.IsMoney
        skip = False
        skip |= not valid
        skip |= self.isEventItem
        skip |= self.isValuable
        skip |= self.isKnowledge
        skip |= self.ObjectType in [0, 5, 8]
        skip |= not self.isPlaced
        return skip
        

class ObjectDB(DataTable):
    Row = Object

    def __init__(self):
        super().__init__('ObjectData.uasset')

    def getChests(self):
        return [row for row in self.table if row.ObjectType in [1, 2]]

    def getHidden(self): # Not sure what the difference between 4 and 5 are
        return [row for row in self.table if row.ObjectType in [4, 5]]

    def getTBD(self): # Not sure what object type 8 is; seem to be random items
        return [row for row in self.table if row.ObjectType == 8]
