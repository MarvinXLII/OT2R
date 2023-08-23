import random
import sys
from copy import deepcopy
from Shuffler import Shuffler, Slot, no_weights
from Manager import Manager


def separate_by_ring(w, s, c):
    for i, si in enumerate(s):
        w[i] *= si.ring == c.ring


# Keep chapter 1 bosses separate
def separate_ring_one(w, s, c):
    if c.ring == 1:
        for i, si in enumerate(s):
            w[i] *= si.ring == 1
    else:
        for i, si in enumerate(s):
            w[i] *= si.ring > 1


class Group(Slot):
    def __init__(self, enemy_group):
        self.enemy_group = enemy_group

        # Data to be copied/patched
        for key in self.enemy_group.keys:
            assert hasattr(self.enemy_group, key)
            v = getattr(self.enemy_group, key)
            setattr(self, key, v)

        self.boss_type = enemy_group.boss_type
        self.ring = enemy_group.ring

    def copy(self, other):
        for key in self.enemy_group.keys:
            v = getattr(other, key)
            setattr(self, key, v)
        self.enemy_group.rando_boss = other.enemy_group.vanilla_boss

    def patch(self):
        for key in self.enemy_group.keys:
            v = getattr(self, key)
            setattr(self.enemy_group, key, v)


class Bosses(Shuffler):
    shuffle_by_rings = separate_by_ring
    include_mid_game_opt_bos = False
    include_late_game_opt_bos = False
    include_galdera = False
    include_vide = False

    def __init__(self):
        self.enemy_group_db = Manager.get_instance('EnemyGroupData').table
        slots = []
        candidates = []

        # Construct all bosses
        for g in self.enemy_group_db:
            if g.vanilla_boss:
                slots.append(Group(g))
                candidates.append(Group(g))

        # Remove bosses as needed for selected options 
        if not self.include_mid_game_opt_bos:
            slots = list(filter(lambda g: not (g.boss_type == 'optional' and g.ring == 2), slots))
            candidates = list(filter(lambda g: not (g.boss_type == 'optional' and g.ring == 2), candidates))

        if not self.include_late_game_opt_bos:
            slots = list(filter(lambda g: not (g.boss_type == 'optional' and g.ring == 3), slots))
            candidates = list(filter(lambda g: not (g.boss_type == 'optional' and g.ring == 3), candidates))

        if not self.include_galdera:
            slots = list(filter(lambda g: g.boss_type != 'galdera', slots))
            candidates = list(filter(lambda g: g.boss_type != 'galdera', candidates))

        if not self.include_vide:
            slots = list(filter(lambda g: g.boss_type != 'videwicked', slots))
            candidates = list(filter(lambda g: g.boss_type != 'videwicked', candidates))

        # Always omit Vide due to softlock
        slots = list(filter(lambda g: g.boss_type != 'vide', slots))
        candidates = list(filter(lambda g: g.boss_type != 'vide', candidates))

        self.slots = slots
        self.candidates = candidates

        self.vacant = None
        self.weights = None

    def generate_weights(self):
        super().generate_weights(Bosses.shuffle_by_rings)

    def finalize(self):

        ##########################
        #### HOLD_OUT modding ####
        ##########################

        ai_bp = [
            Manager.get_asset_only('BattleAI_Bos_Mer_C01_010'),
            Manager.get_asset_only('BattleAI_Bos_Cle_C01_010'),
            Manager.get_asset_only('BattleAI_Bos_Hun_C01_010'),
            Manager.get_asset_only('BattleAI_Bos_War_C01_020'),
            Manager.get_asset_only('BattleAI_Bos_Sch_C01_010'),
        ]

        # Modify "disease" keeping bosses alive through the first in battle cutscene.
        # This seems to work for most bosses.
        disease_db = Manager.get_instance('DiseaseData').table
        disease_db.HOLD_OUT.EnableTurnCount = True

        # Setup target to be found in uexp
        zero = int.to_bytes(0, 4, byteorder='little')
        neg_one = int.to_bytes(-1, 4, byteorder='little', signed=True)
        com1d = bytes([0x1d])
        com21 = bytes([0x21])
        target = com1d + zero + com1d + neg_one

        # Changes a -1 to 0. Not sure what goes on for 0 HOLD_OUT's.
        # Positive numbers seems to correspond to the number of times
        # the boss get's is kept alive with 1 HP rather than killed.
        for k, bp in enumerate(ai_bp):
            ho_val = bp.uasset.get_index('HOLD_OUT').to_bytes(8, byteorder='little')
            addr = bp.uexp.index(ho_val + target)
            bp.patch_int32(addr+14, 0)

        ###################################
        ### Capturing Ochette's Bosses ####
        ###################################

        enemy_db = Manager.get_instance('EnemyDB').table

        #### Turn off Tera
        tera = enemy_db.ENE_BOS_HUN_C02_010
        tera.TameEnable = False
        tera.LegendTameMonster = False

        #### Turn off Glacis
        glacis = enemy_db.ENE_BOS_HUN_C02_020
        glacis.TameEnable = False
        glacis.LegendTameMonster = False


        ### Update rando bosses
        def get_enemy_with_max_hp(slot):
            # Make sure to get the enemy with the most HP
            boss = None
            hp = 0
            for e in slot.EnemyID:
                enemy = enemy_db.get_row(e)
                if enemy:
                    if enemy.Param['HP'] > hp:
                        boss = enemy
                        hp = enemy.Param['HP']
            assert boss, 'no boss found!?'
            return boss

        def get_group(group_name):
            for s in self.slots:
                if s.enemy_group.key == group_name:
                    return s
            else:
                sys.exit(f'group {group_name} not found!')
        
        tera_group = get_group('ENG_BOS_HUN_C02_010')
        boss = get_enemy_with_max_hp(tera_group)
        boss.TameEnable = True
        boss.LegendTameMonster = True
        boss.InvadeMonsterID = tera.InvadeMonsterID
        boss.DefaultTameRate = tera.DefaultTameRate

        glacis_group = get_group('ENG_BOS_HUN_C02_020')
        boss = get_enemy_with_max_hp(glacis_group)
        boss.TameEnable = True
        boss.LegendTameMonster = True
        boss.InvadeMonsterID = glacis.InvadeMonsterID
        boss.DefaultTameRate = glacis.DefaultTameRate

        ############################################
        #### Prevent Ochette w/o Acta Softlocks ####
        ############################################

        # Seems to work for both bosses
        hun_bos_A = Manager.get_asset('ENG_BOS_HUN_C03_010_A')
        export = hun_bos_A.get_uexp_obj_2(16)
        export.assert_bool_on(0x2a)
        export.toggle_bool_off(0x2a)

        # Included just in case
        hun_bos_B = Manager.get_asset('ENG_BOS_HUN_C03_010_B')
        export = hun_bos_B.get_uexp_obj_2(14)
        export.assert_bool_on(0x2a)
        export.toggle_bool_off(0x2a)

        ############################
        #### Learning Ex Skills ####
        ############################

        abil = { # (pc, skill)
            'WAR': (1, 1), # Hikari
            'HUN': (2, 1), # Ochette
            'APO': (3, 0), # Castti
            'MER': (4, 0), # Partitio
            'CLE': (5, 1), # Temenos
            'SCH': (6, 1), # Osvald
            'THI': (7, 1), # Throne
            'DAN': (8, 1), # Agnea
        }

        def get_pc_job(boss):
            for s in self.slots:
                if s.enemy_group.rando_boss == boss:
                    break
            else:
                sys.exit(f'Boss {boss} not found!')

            for j in abil.keys():
                if j in s.enemy_group.key:
                    return j

            return None
            
        # Add text for their Ex Skills
        game_text_db = Manager.get_instance('GameTextEN').table
        ability_set_db = Manager.get_instance('AbilitySetData').table
        pc_db = Manager.get_instance('PlayableCharacterDB').table

        def get_names(pc):
            es1 = ability_set_db.get_row(pc.ex_skill_one).name
            es2 = ability_set_db.get_row(pc.ex_skill_two).name
            return es2, es1

        # Osvald
        job = get_pc_job('Professor Harvey')
        if job in abil:
            pc_sch, skill_sch = abil['SCH']
            pc_job, skill_job = abil[job]

            # Boss
            bos_osv = Manager.get_asset('ENG_BOS_SCH_C05_010_A')

            se1 = bos_osv.get_uexp_obj_2(16)
            se1.assert_uint8(pc_sch, addr=0x22)
            se1.patch_uint8(pc_job, addr=0x22)
            se1.assert_uint32(skill_sch, addr=0x24)
            se1.patch_uint32(skill_job, addr=0x24)

            se2 = bos_osv.get_uexp_obj_2(17)
            se2.assert_uint8(pc_sch, addr=0x2b)
            se2.patch_uint8(pc_job, addr=0x2b)
            se2.assert_uint32(skill_sch, addr=0x2d)
            se2.patch_uint32(skill_job, addr=0x2d)

        if job != 'SCH': # If boss isn't in it's vanilla storyline
            pc_sch, skill_sch = abil['SCH']

            # Story end event
            json_ref = Manager.get_json('MS_KAR_30_2500') # Ochette's end event
            osv_json = Manager.get_json('MS_GAK_50_1300') # Osvald's end event

            ref = deepcopy(json_ref.json_list[-3:-1])
            ref[0].target = pc_sch
            ref[0].opt[0] = str(skill_sch)
            ref[1].text = "ED_GAK_ADVANCEABILITY_0020"
            osv_json.insert_command(ref[0], 161)
            osv_json.insert_command(ref[1], 162)

            # Text
            es2, _ = get_names(pc_db.osvald)
            game_text_db.ED_GAK_ADVANCEABILITY_0020._data['Text'].string_1 = 'GameTextEN'
            game_text_db.ED_GAK_ADVANCEABILITY_0020._data['Text'].string_2 = 'ED_GAK_ADVANCEABILITY_0020'
            game_text_db.ED_GAK_ADVANCEABILITY_0020.set_text(f'Osvald learned the EX skill "{es2}"')


        # Agnea
        job = get_pc_job('Dolcinaea the Star')
        if job in abil:
            pc_dan, skill_dan = abil['DAN']
            pc_job, skill_job = abil[job]

            # Boss
            bos_agn = Manager.get_asset('ENG_BOS_DAN_C05_020')

            se1 = bos_agn.get_uexp_obj_2(17)
            se1.assert_uint8(pc_dan, addr=0x22)
            se1.patch_uint8(pc_job, addr=0x22)
            se1.assert_uint32(skill_dan, addr=0x24)
            se1.patch_uint32(skill_job, addr=0x24)

            se2 = bos_agn.get_uexp_obj_2(18)
            se2.assert_uint8(pc_dan, addr=0x2b)
            se2.patch_uint8(pc_job, addr=0x2b)
            se2.assert_uint32(skill_dan, addr=0x2d)
            se2.patch_uint32(skill_job, addr=0x2d)

        if job != 'DAN': # If boss isn't in it's vanilla storyline
            pc_dan, skill_dan = abil['DAN']

            # Story end event
            json_ref = Manager.get_json('MS_KAR_30_2500') # Ochette's end event
            agn_json = Manager.get_json('MS_ODO_50_2000') # Agnea's end event

            ref = deepcopy(json_ref.json_list[-3:-1])
            ref[0].target = pc_dan
            ref[0].opt[0] = str(skill_dan)
            ref[1].text = "ED_ODO_ADVANCEABILITY_0020"
            agn_json.insert_command(ref[0], 139)
            agn_json.insert_command(ref[1], 139)

            # Text
            es2, _ = get_names(pc_db.agnea)
            game_text_db.ED_ODO_ADVANCEABILITY_0020._data['Text'].string_1 = 'GameTextEN'
            game_text_db.ED_ODO_ADVANCEABILITY_0020._data['Text'].string_2 = 'ED_ODO_ADVANCEABILITY_0020'
            game_text_db.ED_ODO_ADVANCEABILITY_0020.set_text(f'Agnea learned the EX skill "{es2}"')


        ###########################
        #### Keep LT Guages On ####
        ###########################

        def keep_on(filename, flag):
            f = Manager.get_json(filename)
            f.toggle_flag_on(flag)

        keep_on('MS_KEN_10_0100', 30)
        keep_on('MS_KAR_10_0200', 31)
        keep_on('MS_KUS_10_0100', 32)
        keep_on('MS_SHO_10_0100', 33)
        keep_on('MS_SIN_10_0100', 34)
        keep_on('MS_GAK_10_0100', 35)
        keep_on('MS_TOU_10_0100', 36)
        keep_on('MS_ODO_10_0100', 37)
