from Assets import Data
from DataTable import DataTable

class NPCShopDB(DataTable):
    def __init__(self):
        super().__init__('NPCPurchaseData.uasset')

    def getNPCShop(self, key):
        return self.table.getRow(key)
