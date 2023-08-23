from DataTable import Row
from Manager import Manager

class InvadeRow(Row):
    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.processed_item

    @property
    def processed_item(self):
        if self.EnableProcess:
            item_db = Manager.get_instance('ItemDB').table
            item = item_db.get_name(self.ProcessedItem)
            num = self.ProcessNumID
            if num > 1:
                return f"{item} x{num}"
            return item

    @property
    def name(self):
        text_db = Manager.get_instance('GameTextEN').table
        return text_db.get_text(self.DisplayName)
