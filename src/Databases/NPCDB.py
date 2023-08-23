from DataTable import DataTable, Row
from Manager import Manager

class NPCRow(Row):
    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = [i.item for i in self.inventory]

    @property
    def name(self):
        text_db = Manager.get_instance('GameTextEN').table
        return text_db.get_text(self.TextLabel)

    @property
    def inventory(self):
        npc_shop_db = Manager.get_instance('NPCPurchaseData').table
        npc_shop = npc_shop_db.get_npc_shop(self.FCmd_Purchase_ID)
        if npc_shop:
            shop_db = Manager.get_instance('PurchaseItemTable').table
            return shop_db.get_shop_inventory(npc_shop.ShopID)
        return []
