from DataTable import DataTable, Row, Table
from Manager import Manager
import random

class NPCRow(Row):
    ranks = {i:[] for i in range(1, 11)}

    def __init__(self, *args):
        super().__init__(*args)
        self.shops = self._get_shop_obj()
        self.vanilla = list(self.inventory)

        # Hear
        self.hear = self._get_hear_obj()

        # Battle
        self.battle = self._get_battle_obj()
        if self.enemy_group:
            rank = self.enemy_group.get_display_rank()
            if rank in NPCRow.ranks:
                enemies = self.enemy_group.get_enemies_objs()
                if len(enemies) == 1:
                    NPCRow.ranks[rank].append(self.enemy_group.key)

        # Join party
        self.join_party = self._get_join_obj()

    def print_info(self):
        print("HERE", self.key, self.name)

    @property
    def name(self):
        text_db = Manager.get_instance('GameTextEN').table
        return text_db.get_text(self.TextLabel)

    @property
    def inventory(self):
        return [shop.ItemLabel for shop in self.shops]

    def _get_shop_obj(self):
        npc_shop_db = Manager.get_instance('NPCPurchaseData').table
        if not hasattr(npc_shop_db, self.FCmd_Purchase_ID):
            return []
        shop_id = getattr(npc_shop_db, self.FCmd_Purchase_ID)

        shop_list = Manager.get_instance('ShopList').table
        if not hasattr(shop_list, shop_id.ShopID):
            return []
        shop_label_list = getattr(shop_list, shop_id.ShopID).LabelList

        shops = []
        purchases = Manager.get_table('PurchaseItemTable')
        for label in shop_label_list:
            if hasattr(purchases, label):
                shops.append(getattr(purchases, label))

        return shops

    def _get_hear_obj(self):
        npc_hear = Manager.get_instance('NPCHearData').table
        if hasattr(npc_hear, self.FCmd_Search_ID):
            return getattr(npc_hear, self.FCmd_Search_ID)
        return None

    def _get_battle_obj(self):
        npc_battle = Manager.get_instance('NPCBattleData').table
        if hasattr(npc_battle, self.FCmd_Battle_ID):
            return getattr(npc_battle, self.FCmd_Battle_ID)
        return None

    @property
    def enemy_group(self):
        group = Manager.get_instance('EnemyGroupData').table
        if hasattr(group, self.FCmd_EnemyGroup):
            return getattr(group, self.FCmd_EnemyGroup)
        return None

    @enemy_group.setter
    def enemy_group(self, value):
        assert self.FCmd_EnemyGroup != 'None'
        self.FCmd_EnemyGroup = value

    def set_default_enemy(self, rank=0):
        enemies = self.enemy_group.get_enemies_objs()
        if len(enemies) == 0: return
        assert len(enemies) == 1, "Only designed for 1-1 battles"
        # ONLY change enemyID when necessary
        if rank > 0:
            assert len(NPCRow.ranks[rank]) > 0, f'no battles at rank {rank}'
            self.enemy_group = random.sample(NPCRow.ranks[rank], 1)[0]
        # ALWAYS make enemy weak to Temenos
        enemies = self.enemy_group.get_enemies_objs()
        job_db = Manager.get_instance('JobData').table
        enemies[0].add_weapon_weakness_to_pc(job_db.temenos)

    def _get_join_obj(self):
        return None
