from DataTable import Table, Row
from Manager import Manager
from Utility import get_filename
import hjson

class ShopRow(Row):
    data = hjson.load(open(get_filename('json/npcShopPlaces.json'), 'r', encoding='utf-8'))

    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.item
        self.isNPC = 'NPCBUY' in self.key

    @property
    def item(self):
        itemDB = Manager.getInstance('ItemDB').table
        name = itemDB.getName(self.ItemLabel)
        if name is None:
            return 'None'
        return name

    @property
    def isValid(self):
        return self.data[self.key]['valid']

    @property
    def isAlwaysAccessible(self):
        return self.data[self.key]['alwaysAccessible']

    @property
    def fromNPC(self):
        return self.data[self.key]['npc']

    @property
    def region(self):
        return self.data[self.key]['region']

    @property
    def location(self):
        return self.data[self.key]['location']

    @property
    def ring(self):
        return self.data[self.key]['ring']

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


class ShopTable(Table):
    def __init__(self, data, rowClass):
        super().__init__(data, rowClass)

        self.shops = {}
        for row in self:
            if row.isValid:
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
