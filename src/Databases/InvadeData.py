from Assets import Data
from DataTable import DataTable, Row

class Species(Row):
    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.processedItem

    @property
    def processedItem(self):
        if self.EnableProcess:
            num = self.ProcessNumID
            item = self.itemDB.getName(self.ProcessedItem)
            if num > 1:
                return f"{item} x{num}"
            return item

    @property
    def name(self):
        return self.textDB.getText(self.DisplayName)
    

class InvadeDB(DataTable):
    Row = Species

    def __init__(self):
        super().__init__('InvadeData.uasset')

    def getName(self, key):
        row = self.table.getRow(key)
        if row:
            return row.name
