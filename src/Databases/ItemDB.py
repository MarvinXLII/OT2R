from DataTable import Table, Row
from Manager import Manager

class ItemRow(Row):
    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.name

    @property
    def name(self):
        text_db = Manager.get_instance('GameTextEN').table
        return text_db.get_text(self.ItemNameID)
    

class ItemTable(Table):
    def get_name(self, key):
        row = self.get_row(key)
        if row:
            return row.name
