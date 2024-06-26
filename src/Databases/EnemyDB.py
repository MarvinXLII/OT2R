from DataTable import Table, RowSplit
import random
from Manager import Manager

class EnemyRow(RowSplit):
    def __init__(self, key, data):
        super().__init__(key, data)
        self.groups = set()

    @property
    def dont_strengthen(self):
        return self.groups.intersection([
            'ENG_NPC_GAK_10_020', # Osvald Ch. 1 battle
            'ENG_NPC_KEN_40_010', # Jin Mei in Hikari's Ch. 4 flashback
            'ENG_EVE_HUN_C01_010', # King Iguana, Ochette Ch. 1
            'ENG_NPC_HAN_C01_070', # Villager, Ochette Ch. 1
            'ENG_NPC_SIN_10_0400', # Temenos Ch. 1 (techically could grind for this, but...)
            'ENG_EVE_THI_C01_010', # Throne Ch. 1 first battle
        ])

    @property
    def name(self):
        text_db = Manager.get_instance('GameTextEN').table
        return text_db.get_text(self.DisplayNameID)

    @property
    def is_boss(self):
        return '_BOS_' in self.key

    @property
    def is_opt_boss(self):
        return self.key in [
            ### MID BOSSES
            'ENE_EVE_SUB_EXT_011', # Audnvarg
            'ENE_NML_OCN_190', # Battle-Worn Shark
            # 'ENE_NML_ENC_SUB_12', # Battle-Worn Shark
            'ENE_NML_FLD_FST_230', # Carnivorous Plant
            # 'ENE_NML_ENC_SUB_10', # Carnivorous Plant
            'ENE_EVE_SUB_EXT_016', # Delsta Devil
            'ENE_NML_FLD_MNT_200', # Devourer of Dreams
            # 'ENE_NML_ENC_SUB_04', # Devourer of Dreams
            'ENE_NML_FLD_CTY_260', # Gigantes
            # 'ENE_NML_ENC_SUB_05', # Gigantes
            'ENE_NPC_SS_TD31_0400_0200', # Gken
            'ENE_EVE_SUB_EXT_013', # Ichchadhari the Snake Charmer
            'ENE_NML_FLD_DST_280', # Lord of the Sands
            # 'ENE_NML_ENC_SUB_01', # Lord of the Sands
            'ENE_NML_FLD_ISD_250', # Manymaws
            # 'ENE_NML_ENC_SUB_07', # Manymaws
            'ENE_NML_FLD_ISD_240', # Monarch
            # 'ENE_NML_ENC_SUB_06', # Monarch
            'ENE_EVE_SUB_SNW_010', # Ruffian Leader
            'ENE_NML_OCN_200', # Scourge of the Sea
            # 'ENE_NML_ENC_SUB_13', # Scourge of the Sea
            'ENE_EVE_SUB_EXT_012', # Tyran the Seeker

            ### LATE BOSSES
            'ENE_NML_FLD_SNW_280', # Behemoth
            # 'ENE_NML_ENC_SUB_03', # Behemoth
            'ENE_NML_FLD_SEA_280', # Deep One
            # 'ENE_NML_ENC_SUB_08', # Deep One
            'ENE_NML_FLD_SNW_270', # Dreadwolf
            # 'ENE_NML_ENC_SUB_02', # Dreadwolf
            'ENE_NML_FLD_WLD_260', # Heavenwing
            # 'ENE_NML_ENC_SUB_11', # Heavenwing
            'ENE_EVE_SUB_EXT_010', # Priestess Hinoekagura
            'ENE_NML_FLD_SEA_290', # Tyrannodrake
            # 'ENE_NML_ENC_SUB_09', # Tyrannodrake
        ]

    @property
    def shields(self):
        return self.weapon_shields + self.magic_shields

    @shields.setter
    def shields(self, shields):
        assert len(shields) == 12
        self.weapon_shields = shields[:6]
        self.magic_shields = shields[6:]

    @property
    def weapon_shields(self):
        return self.WeaponResist[:6]

    @weapon_shields.setter
    def weapon_shields(self, shields):
        assert len(shields) == 6
        self.WeaponResist[:6] = shields

    @property
    def magic_shields(self):
        return self.AttributeResist[1:]

    @magic_shields.setter
    def magic_shields(self, shields):
        assert len(shields) == 6
        self.AttributeResist[1:] = shields

    def _add_weakness(self, shields, *pcs):
        can_be_removed = [s == 'EATTRIBUTE_RESIST::eWEAK' for s in shields]
        def get_can_be_added(pc):
            can_be_added = [False]*len(shields)
            for i, s in enumerate(pc.strengths()):
                if i == len(shields):
                    break
                if s and shields[i] == 'EATTRIBUTE_RESIST::eWEAK':
                    return [] # Don't add anything if enemy is already weak to a PC's weapon/magic
                if s and not can_be_removed[i]:
                    can_be_added[i] = True
            return can_be_added

        idx = range(len(shields))
        for pc in pcs:
            if sum(can_be_removed) == 0:
                break
            can_be_added = get_can_be_added(pc)
            if sum(can_be_added):
                r = random.choices(idx, can_be_removed, k=1)[0]
                a = random.choices(idx, can_be_added, k=1)[0]
                assert shields[r] == 'EATTRIBUTE_RESIST::eWEAK'
                shields[r] = 'EATTRIBUTE_RESIST::eNONE'
                shields[a] = 'EATTRIBUTE_RESIST::eWEAK'
                can_be_removed[r] = False

        return shields

    def add_weakness_to_pc(self, *pcs):
        shields = self.shields
        self.shields = self._add_weakness(shields, *pcs)

    def add_weapon_weakness_to_pc(self, *pcs):
        # Make sure enemy has a weapon weakness
        # It's possible for an enemy to be only weak to magic!
        if self.weapon_shields.count('EATTRIBUTE_RESIST::eWEAK') == 0:
            self.weapon_shields, self.magic_shields = self.magic_shields, self.weapon_shields
        if self.weapon_shields.count('EATTRIBUTE_RESIST::eWEAK') == 0:
            s = self.weapon_shields
            s[0] = 'EATTRIBUTE_RESIST::eWEAK'
            self.weapon_shields = s
        self.weapon_shields = self._add_weakness(self.weapon_shields, *pcs)

    def update_weakness_to_pcs(self, weapon_only=False):
        pcs = set()
        enemy_group_db = Manager.get_instance('EnemyGroupData').table
        for group_name in sorted(self.groups):
            group = enemy_group_db.get_row(group_name)
            if group is None: continue
            if group.pc_region is None: continue
            if group.ring > 1: continue
            pcs.add(group.pc_region)
        pc_list = sorted(pcs)
        if weapon_only:
            self.add_weapon_weakness_to_pc(*pc_list)
        else:
            self.add_weakness_to_pc(*pc_list)


class EnemyTable(Table):
    def get_name(self, key):
        row = self.get_row(key)
        if row:
            return row.name
