from Assets import Data
from DataTable import DataTable, Row

class Item(Row):
    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.name

    @property
    def name(self):
        return self.textDB.getText(self.ItemNameID)
    

class ItemDB(DataTable):
    Row = Item

    def __init__(self):
        super().__init__('ItemDB.uasset')

    def getName(self, key):
        row = self.table.getRow(key)
        if row:
            return row.name
