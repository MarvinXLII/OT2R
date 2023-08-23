from DataTable import Row
from Manager import Manager

class InvadeRow(Row):
    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.processedItem

    @property
    def processedItem(self):
        if self.EnableProcess:
            itemDB = Manager.getInstance('ItemDB').table
            item = itemDB.getName(self.ProcessedItem)
            num = self.ProcessNumID
            if num > 1:
                return f"{item} x{num}"
            return item

    @property
    def name(self):
        textDB = Manager.getInstance('GameTextEN').table
        return textDB.getText(self.DisplayName)
