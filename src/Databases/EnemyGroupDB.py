from DataTable import RowSplit, Table
import hjson
from Utility import get_filename
from Manager import Manager


class EnemyGroupRow(RowSplit):
    group_json = hjson.load(open(get_filename('json/enemyGroups.json'), 'r', encoding='utf-8'))
    boss_json = hjson.load(open(get_filename('json/bosses.json'), 'r', encoding='utf-8'))

    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.enemies
        self.vanilla_boss = self.boss_from_json()
        self.rando_boss = self.boss_from_json()
        self.vide_wicked_cand = self.vtw_from_json()

    def get_display_rank(self):
        rank = 0
        enemy_db = Manager.get_instance('EnemyDB').table
        for enemy in self.EnemyID:
            if hasattr(enemy_db, enemy):
                e = getattr(enemy_db, enemy)
                if rank < e.DisplayRank:
                    rank = e.DisplayRank
        return rank

    def get_enemies_objs(self):
        enemies = []
        enemy_db = Manager.get_instance('EnemyDB').table
        for enemy in self.EnemyID:
            if enemy == 'None': continue
            if hasattr(enemy_db, enemy):
                enemies.append(getattr(enemy_db, enemy))
        return enemies

    def boss_from_json(self):
        if self.key in EnemyGroupRow.boss_json:
            return EnemyGroupRow.boss_json[self.key]['boss']
        return ''

    def vtw_from_json(self):
        if self.key in EnemyGroupRow.boss_json:
            return EnemyGroupRow.boss_json[self.key]['vtwcand']
        return False

    @property
    def pc_region(self):
        pc = EnemyGroupRow.group_json[self.key]['pc']
        if pc:
            job_db = Manager.get_instance('JobData').table
            return getattr(job_db, pc)
        return None

    @property
    def ring(self):
        if self.key in EnemyGroupRow.boss_json:
            return EnemyGroupRow.boss_json[self.key]['ring']
        return EnemyGroupRow.group_json[self.key]['ring']

    @property
    def boss_type(self):
        if self.key in EnemyGroupRow.boss_json:
            return EnemyGroupRow.boss_json[self.key]['type']
        return ''

    @property
    def enemies(self):
        enemies = Manager.get_instance('EnemyDB').table
        group = self.enemy_keys
        names = []
        for e in group:
            n = enemies.get_name(e)
            if n:
                names.append(n)
        return names

    @property
    def enemy_keys(self):
        return list(filter(lambda x: x != 'None', self.EnemyID))

    @property
    def is_random_encounter(self):
        return '_DAY_' in self.key or '_NGT_' in self.key

    # This really needs to be cleaned up!
    def update_weakness_to_pcs(self, *pcs, weapon_only=False):
        pcs = sorted(pcs)
        enemies = Manager.get_instance('EnemyDB').table
        for e in self.EnemyID:
            if e != 'None':
                enemy = enemies.get_row(e)
                if enemy:
                    if pcs:
                        if weapon_only:
                            enemy.add_weapon_weakness_to_pc(*pcs)
                        else:
                            enemy.add_weakness_to_pc(*pcs)
                    else:
                        enemy.update_weakness_to_pcs(weapon_only)


class EnemyGroupTable(Table):
    def __init__(self, data, row_class):
        super().__init__(data, row_class)
        self.update_group_sets()

    def update_group_sets(self):
        enemies = Manager.get_instance('EnemyDB').table
        for enemy in enemies:
            enemy.groups = set()

        for group in self:
            for e in group.EnemyID:
                if e == 'None': continue
                enemy = enemies.get_row(e)
                if enemy:
                    enemy.groups.add(group.key)

    # Return enemy_db object of main boss
    # purpose of these is to nerf/increase boss hp as needed
    # - e.g. Felvarg vs solo Hikari can be brutal!
    @property
    def early_agnea(self):
        return self.ENG_BOS_DAN_C01_010

    @property
    def early_castti(self):
        return self.ENG_BOS_APO_C01_010

    @property
    def early_hikari(self):
        return self.ENG_BOS_WAR_C01_010

    @property
    def early_ochette(self):
        return self.ENG_BOS_HUN_C01_010

    @property
    def early_osvald(self):
        return self.ENG_BOS_SCH_C01_010

    @property
    def early_partitio(self):
        return self.ENG_BOS_MER_C01_010

    @property
    def early_temenos(self):
        return self.ENG_BOS_CLE_C01_010

    @property
    def early_throne(self):
        return self.ENG_BOS_THI_C01_010
