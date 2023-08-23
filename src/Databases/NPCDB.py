from DataTable import DataTable, Row
from Manager import Manager

class NPCRow(Row):
    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = [i.item for i in self.inventory]

    @property
    def name(self):
        textDB = Manager.getInstance('GameTextEN').table
        return textDB.getText(self.TextLabel)

    @property
    def inventory(self):
        npcShopDB = Manager.getInstance('NPCPurchaseData').table
        npcShop = npcShopDB.getNPCShop(self.FCmd_Purchase_ID)
        if npcShop:
            shopDB = Manager.getInstance('PurchaseItemTable').table
            return shopDB.getShopInventory(npcShop.ShopID)
        return []
