from DataTable import Table, Row
from Manager import Manager
import sys
import random

class NPCBattleRow(Row):
    ranks = {i:[] for i in range(1, 11)}

    def __init__(self, *args):
        super().__init__(*args)

        # Store group id by rank
        enemy_group = self.get_enemy_group()
        if enemy_group:
            enemies = self._get_enemies()
            # Only intended for 1-1 battles
            if len(enemies) == 1:
                rank = enemy_group.get_display_rank()
                if rank in NPCBattleRow.ranks:
                    NPCBattleRow.ranks[rank].append(self.EnemyGroupID)

    def get_enemy_group(self):
        enemy_group = Manager.get_instance('EnemyGroupData').table
        if hasattr(enemy_group, self.EnemyGroupID):
            return getattr(enemy_group, self.EnemyGroupID)
        return None

    def _get_enemies(self):
        enemies = []
        enemy_group = self.get_enemy_group()
        if enemy_group:
            enemy_db = Manager.get_instance('EnemyDB').table
            for enemy in enemy_group.EnemyID:
                if enemy == 'None': continue
                if hasattr(enemy_db, enemy):
                    enemies.append(getattr(enemy_db, enemy))
        return enemies

    def set_default_challenge(self):
        if self.BattleNeedLevel > 0:
            self.BattleNeedLevel = 1

    def set_default_soothe(self):
        if self.DoseItemNum > 0:
            self.DoseItemNum = 1
            # self.DoseItemID = 'ITM_SLP_0010'
            self.DoseItemID = 'ITM_CSM_0010'

    def set_default_ambush(self):
        if self.AssassinateNeedLevel > 0:
            self.AssassinateNeedLevel = 1

    def set_default_knockout(self):
        self.set_default_challenge()
        self.set_default_soothe()
        self.set_default_ambush()


class NPCBattleTable(Table):
    pass
