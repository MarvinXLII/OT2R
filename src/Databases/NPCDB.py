from Assets import Data
from DataTable import DataTable, Row

class NPC(Row):
    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = [i.item for i in self.inventory]

    @property
    def name(self):
        return self.textDB.getText(self.TextLabel)

    @property
    def inventory(self):
        npcShop = self.npcShopDB.getNPCShop(self.FCmd_Purchase_ID)
        if npcShop:
            return self.shopDB.getShopInventory(npcShop.ShopID)
        return []


class NPCDB(DataTable):
    Row = NPC

    def __init__(self):
        super().__init__('NPCData.uasset')
