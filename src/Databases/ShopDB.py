from Assets import Data
from DataTable import DataTable, Row
from Utility import get_filename
import hjson

class Shop(Row):
    placed = hjson.load(open(get_filename('json/placedShop.json'), 'r'))

    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.item
        self.isNPC = 'NPCBUY' in self.key
        self.isPlaced = Shop.placed[self.key]

    @property
    def item(self):
        return self.itemDB.getName(self.ItemLabel)

    @property
    def dontShuffle(self):
        return self.key in [
            # Partitio Ch 1; expensive items could cause softlocks
            # during this scene or even later in the chapter if
            # players overlook costs
            'NPC_SHO_10_2300_NPCBUY_01',
            'NPC_SHO_10_2300_NPCBUY_02',
            'NPC_SHO_10_2400_NPCBUY_01',
            'NPC_SHO_10_2500_NPCBUY_01',
            'NPC_SHO_10_2500_NPCBUY_02',
            'NPC_SHO_10_2500_NPCBUY_03',
            'NPC_SHO_10_2600_NPCBUY_01',
            'NPC_SHO_10_2700_NPCBUY_01',
            'NPC_SHO_10_2700_NPCBUY_02',
            'NPC_SHO_10_2800_NPCBUY_01',
            'NPC_SHO_10_2800_NPCBUY_02',
	    'Twn_Wld_1_1_A_NPCBUY_01_01',
	    'Twn_Wld_1_1_A_NPCBUY_01_03',
        ]


class ShopDB(DataTable):
    Row = Shop

    def __init__(self):
        super().__init__('PurchaseItemTable.uasset')

        self.shops = {}
        for row in self.table:
            if row.isPlaced:
                key = row.key
                s = '_'.join(key.split('_')[:-1]) # remove inventory slot
                if s not in self.shops:
                    self.shops[s] = []
                self.shops[s].append(row)

    def getShopInventory(self, key):
        if key and key != 'None':
            if key in self.shops:
                return self.shops[key]
        return []
