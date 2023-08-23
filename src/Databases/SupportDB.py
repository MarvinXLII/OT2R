from DataTable import Row
from Manager import Manager


class SupportRow(Row):
    @property
    def name(self):
        textDB = Manager.getInstance('GameTextEN').table
        return textDB.getText(self.DisplayName)
