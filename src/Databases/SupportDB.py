from Assets import Data
from DataTable import DataTable, Row


class Support(Row):
    @property
    def name(self):
        return self.textDB.getText(self.DisplayName)


class SupportDB(DataTable):
    Row = Support

    def __init__(self):
        super().__init__('SupportAbilityData.uasset')

    def getSupportAbilityName(self, sKey):
        row = self.table.getRow(sKey)
        if row:
            return row.name
