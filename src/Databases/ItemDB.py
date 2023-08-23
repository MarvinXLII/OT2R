from DataTable import Table, Row
from Manager import Manager

class ItemRow(Row):
    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.name

    @property
    def name(self):
        textDB = Manager.getInstance('GameTextEN').table
        return textDB.getText(self.ItemNameID)
    

class ItemTable(Table):
    def getName(self, key):
        row = self.getRow(key)
        if row:
            return row.name
