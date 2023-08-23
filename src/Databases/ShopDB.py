from DataTable import Table, Row
from Manager import Manager
from Utility import get_filename
import hjson

class ShopRow(Row):
    data = hjson.load(open(get_filename('json/npcShopPlaces.json'), 'r', encoding='utf-8'))

    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.item
        self.is_npc = 'NPCBUY' in self.key

    @property
    def item(self):
        item_db = Manager.get_instance('ItemDB').table
        name = item_db.get_name(self.ItemLabel)
        if name is None:
            return 'None'
        return name

    @property
    def is_valid(self):
        return self.data[self.key]['valid']

    @property
    def is_always_accessible(self):
        return self.data[self.key]['always_accessible']

    @property
    def from_npc(self):
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
    def dont_shuffle(self):
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
    def __init__(self, data, row_class):
        super().__init__(data, row_class)

        self.shops = {}
        for row in self:
            if row.is_valid:
                key = row.key
                s = '_'.join(key.split('_')[:-1]) # remove inventory slot
                if s not in self.shops:
                    self.shops[s] = []
                self.shops[s].append(row)

    def get_shop_inventory(self, key):
        if key and key != 'None':
            if key in self.shops:
                return self.shops[key]
        return []
