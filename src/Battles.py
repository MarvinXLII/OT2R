import random
from Nothing import Nothing
from Manager import Manager
from math import ceil


def shuffler(enemies, *attributes):
    stuff = []
    stuff_bosses = []
    main_enemies = []
    boss_enemies = []
    for enemy in enemies:
        if 'TEST' in enemy.key:
            continue

        data = []
        for attr in attributes:
            v = getattr(enemy, attr)
            data.append(v)

        if 'ENE_BOS' in enemy.key:
            stuff_bosses.append(data)
            boss_enemies.append(enemy)
        else:
            stuff.append(data)
            main_enemies.append(enemy)

    random.shuffle(stuff)
    random.shuffle(stuff_bosses)

    for data, enemy in zip(stuff, main_enemies):
        for value, attr in zip(data, attributes):
            setattr(enemy, attr, value)

    for data, enemy in zip(stuff_bosses, boss_enemies):
        for value, attr in zip(data, attributes):
            setattr(enemy, attr, value)


def drop_item(enemies):
    ene_wo_key_items = []
    for e in enemies:
        if not e.HaveItemID.startswith('ITM_TRE'):
            ene_wo_key_items.append(e)
    shuffler(ene_wo_key_items, 'HaveItemID', 'DropProbability')

def steal_item(enemies):
    # Fix steal guards
    e = []
    for enemy in enemies:
        enemy.StealGuard = enemy.StealItemID == 'None'
        if not enemy.StealGuard:
            e.append(enemy)
    shuffler(e, 'StealGuard', 'StealItemID')

def steal_money(enemies):
    # Fix money guards
    e = []
    for enemy in enemies:
        enemy.StealMoneyGuard = enemy.StealMoney == 0
        if not enemy.StealMoneyGuard:
            e.append(enemy)
    shuffler(e, 'StealMoneyGuard', 'StealMoney')
        
def bribe_money(enemies):
    e = [en for en in enemies if en.BribeMoney > 0]
    shuffler(e, 'BribeGuard', 'BribeMoney')

def drop_item_rate(enemies):
    for enemy in enemies:
        if enemy.DropProbability > 0:
            enemy.DropProbability = 100
        else:
            assert enemy.HaveItemID == 'None' or enemy.HaveItemID == '0'


class Battles:
    scale_exp = 1
    scale_jp = 1
    scale_leaves = 1
    scale_enemy_hp = 1
    scale_enemy_atk = 1
    scale_enemy_matk = 1
    scale_enemy_def = 1
    scale_enemy_mdef = 1
    scale_enemy_acc = 1
    scale_enemy_eva = 1
    scale_enemy_agi = 1
    scale_enemy_sp = 1
    always_drop_item = Nothing
    shuffle_drop_item = Nothing
    shuffle_steal_item = Nothing
    shuffle_steal_money = Nothing
    shuffle_bribe_money = Nothing
    
    def __init__(self):
        self.enemy_db = Manager.get_instance('EnemyDB').table
        # Only use enemies with names
        # i.e. skip enemies like second boss phases, NPC battles
        self.enemies = []
        gametext = Manager.get_table('GameTextEN')
        for enemy in self.enemy_db:
            name = gametext.get_text(enemy.DisplayNameID)
            if name:
                self.enemies.append(enemy)

    def scale_stats(self):
        # Non-random stuff
        self._scale()
        self._scale_sp_in_bp()
        Battles.always_drop_item(self.enemy_db)

    def run(self):
        # Randomized stuff
        Battles.shuffle_drop_item(self.enemies)
        Battles.shuffle_steal_item(self.enemies)
        Battles.shuffle_steal_money(self.enemies)
        Battles.shuffle_bribe_money(self.enemies)

    # Only for testing purposes
    def print_steals(self, filename):
        gametext = Manager.get_table('GameTextEN')
        item_db = Manager.get_table('ItemDB')
        with open(filename, 'w') as file:
            for enemy in self.enemy_db:
                line = '' #enemy.DisplayNameID
                name = gametext.get_text(enemy.DisplayNameID)
                if name:
                    line += ' ' + name
                steal = item_db.get_name(enemy.StealItemID)
                if steal:
                    line += '\n     Steal: ' + steal + ' ' + str(enemy.StealGuard)
                if not enemy.StealMoneyGuard:
                    line += '\n     Collect Money: ' + str(enemy.StealMoney)
                file.write(line)
                file.write('\n')

    def _scale(self):
        for enemy in self.enemy_db:
            enemy.Exp = int(Battles.scale_exp * enemy.Exp)
            enemy.JobPoint = int(Battles.scale_jp * enemy.JobPoint)
            enemy.Money = int(Battles.scale_leaves * enemy.Money)
            if enemy.dont_strengthen: # Make sure mandatory battles with weak PCs are still beatable
                enemy.Param['HP'] = ceil(min(Battles.scale_enemy_hp, 1) * enemy.Param['HP'])
                enemy.Param['ATK'] = ceil(min(Battles.scale_enemy_atk, 1) * enemy.Param['ATK'])
                enemy.Param['MATK'] = ceil(min(Battles.scale_enemy_matk, 1) * enemy.Param['MATK'])
                enemy.Param['DEF'] = ceil(min(Battles.scale_enemy_def, 1) * enemy.Param['DEF'])
                enemy.Param['MDEF'] = ceil(min(Battles.scale_enemy_mdef, 1) * enemy.Param['MDEF'])
                enemy.Param['ACC'] = ceil(min(Battles.scale_enemy_acc, 1) * enemy.Param['ACC'])
                enemy.Param['EVA'] = ceil(min(Battles.scale_enemy_eva, 1) * enemy.Param['EVA'])
                enemy.Param['AGI'] = ceil(min(Battles.scale_enemy_agi, 1) * enemy.Param['AGI'])
                enemy.Param['SP'] = ceil(min(Battles.scale_enemy_sp, 1) * enemy.Param['SP'])
            else:
                enemy.Param['HP'] = ceil(Battles.scale_enemy_hp * enemy.Param['HP'])
                enemy.Param['ATK'] = ceil(Battles.scale_enemy_atk * enemy.Param['ATK'])
                enemy.Param['MATK'] = ceil(Battles.scale_enemy_matk * enemy.Param['MATK'])
                enemy.Param['DEF'] = ceil(Battles.scale_enemy_def * enemy.Param['DEF'])
                enemy.Param['MDEF'] = ceil(Battles.scale_enemy_mdef * enemy.Param['MDEF'])
                enemy.Param['ACC'] = ceil(Battles.scale_enemy_acc * enemy.Param['ACC'])
                enemy.Param['EVA'] = ceil(Battles.scale_enemy_eva * enemy.Param['EVA'])
                enemy.Param['AGI'] = ceil(Battles.scale_enemy_agi * enemy.Param['AGI'])
                enemy.Param['SP'] = ceil(min(Battles.scale_enemy_sp * enemy.Param['SP'], 99))

    def _scale_sp_in_bp(self):
        def patch_bp(bp_name, exp_index, addr, check_val=None):
            boss = Manager.get_asset(bp_name)
            export = boss.get_uexp_obj_2(exp_index)
            value = export.read_int_const(addr)
            if check_val: assert value == check_val
            new_value = ceil(min(Battles.scale_enemy_sp * value, 99))
            export.patch_int_const(addr, value, new_value)
            print(f'{bp_name}, {exp_index} @ {hex(addr)}: {value} -> {new_value}')

        def patch_table(bp_name, exp_index, key='ShieldMax'):
            boss = Manager.get_asset(bp_name)
            value = boss.uasset.exports[exp_index].uexp1[key].value
            new_value = ceil(min(Battles.scale_enemy_sp * value, 99))
            boss.uasset.exports[exp_index].uexp1[key].value = new_value
            print(f'{bp_name}, {exp_index} @ {key}: {value} -> {new_value}')

        patch_bp('BattleAI_Bos_Apo_C02_010', 1, 0x19cf, 9) # Sand Lion
        patch_bp('BattleAI_Bos_Apo_C02_010', 1, 0x1ace, 7)
        patch_bp('BattleAI_Bos_Apo_C05_010', 3, 0x1e6d, 12) # Trousseau
        patch_bp('BattleAI_Bos_Apo_C05_011', 2, 0x5cb, 12)

        patch_bp('BattleAI_Bos_Cle_C03_010', 3, 0x2979, 7) # Deputy Cubaryi
        patch_bp('BattleAI_Bos_Cle_C03_010', 3, 0x2a21, 9)
        patch_bp('BattleAI_Bos_Cle_C03_010', 3, 0x2ac9, 11)
        patch_bp('BattleAI_Bos_Cre_C05_010', 1, 0xf4b, 13) # Captain Kaldena

        patch_bp('BattleAI_Bos_DAN_C04_010', 3, 0x1b5a, 7) # Veronica
        patch_bp('BattleAI_Bos_DAN_C04_010', 3, 0x1caa, 8)
        patch_bp('BattleAI_Bos_DAN_C04_010', 3, 0x1c02, 9)
        patch_bp('BattleAI_Bos_DAN_C04_010', 3, 0x37e5, 10)
        patch_bp('BattleAI_Bos_DAN_C04_010', 1, 0xcd8, 1)
        patch_bp('BattleAI_Bos_DAN_C04_010', 1, 0xe74, 1)
        patch_bp('BattleAI_Bos_DAN_C04_010', 1, 0x1357, 1)
        patch_bp('BattleAI_Bos_DAN_C04_010', 1, 0x183a, 1)
        patch_bp('BattleAI_Bos_DAN_C05_030', 3, 0x238c, 9) # Dolcinaea the Star
        patch_bp('BattleAI_Bos_DAN_C05_030', 3, 0x3914, 9)

        patch_bp('BattleAI_Bos_Ext_Low_010', 1, 0x1939, 16) # Omniscient Eye
        patch_bp('BattleAI_Bos_Ext_Upp_010', 1, 0xdee, 20) # Galdera, the Fallen
        patch_bp('BattleAI_Bos_Ext_Upp_010', 1, 0xe39, 20)
        # Incrementer
        patch_bp('BattleAI_Bos_Ext_Upp_010', 4, 0xa30, 2)
        # Shields after arm/head/sword start dying
        patch_bp('BattleAI_Bos_Ext_Upp_010', 6, 0x232b, 50)
        patch_bp('BattleAI_Bos_Ext_Upp_010', 6, 0x2864, 20)
        # # Increase arm/head/sword shields
        #### These don't work properly. First hit will drop shield count to max.
        # patch_bp('BattleAI_Bos_Ext_Upp_010', 6, 0x1aa6, 6)
        # patch_bp('BattleAI_Bos_Ext_Upp_010', 6, 0x20eb, 3)
        # patch_bp('BattleAI_Bos_Ext_Upp_010', 6, 0x22dc, 3)
        # patch_bp('BattleAI_Bos_Ext_Upp_010', 6, 0x2433, 3)
        # patch_bp('BattleAI_Bos_Ext_Upp_010', 6, 0x2624, 3)
        # patch_bp('BattleAI_Bos_Ext_Upp_010', 6, 0x2815, 3)
        # patch_bp('BattleAI_Bos_Ext_Upp_010', 6, 0x296c, 3)
        # patch_bp('BattleAI_Bos_Ext_Upp_010', 6, 0x2b5d, 6)
        # patch_bp('BattleAI_Bos_Ext_Upp_010', 6, 0x2b82, 6)

        patch_table('BattleAI_Bos_Ext_Upp_020', 12, 'ShieldMax') # Abyssal Maw
        patch_bp('BattleAI_Bos_Ext_Upp_020', 1, 0x69c, 2) # No clue what they are for. Keep them anyway in case the Abyssal Maw actually uses them.
        patch_bp('BattleAI_Bos_Ext_Upp_020', 1, 0x716, 2)
        patch_bp('BattleAI_Bos_Ext_Upp_020', 1, 0x737, 2)
        patch_table('BattleAI_Bos_Ext_Upp_030', 13, 'ShieldMax') # Sundering Arm
        patch_table('BattleAI_Bos_Ext_Upp_040', 12, 'ShieldMax') # Blade of the Fallen

        patch_bp('BattleAI_Bos_Hun_C05_010', 16, 0xf63, 10) # Lājackal of the Sorrowful Moon
        patch_bp('BattleAI_Bos_Hun_C05_020', 16, 0xf63, 10) # Malamaowl of the Sorrowful Moon

        patch_bp('BattleAI_Bos_Lst_C02_020', 3, 0x2a0a, 7) # Arcanette
        patch_bp('BattleAI_Bos_Lst_C02_020', 3, 0x2ab2, 9)
        patch_bp('BattleAI_Bos_Lst_C02_020', 1, 0x10a5, 2)
        patch_bp('BattleAI_Bos_Lst_C02_020', 1, 0x13b2, 2)

        patch_bp('BattleAI_Bos_Lst_C03_060', 3, 0x19bf, 7) # Vide
        patch_bp('BattleAI_Bos_Lst_C03_060', 3, 0x2c4f, 9)

        patch_bp('BattleAI_Bos_Lst_C03_070', 3, 0x1e5b, 15) # Vide, the Wicked
        patch_bp('BattleAI_Bos_Lst_C03_070', 3, 0x1f03, 12)

        #### Don't actually have anything!?
        # patch_bp('BattleAI_Bos_Mer_C03_010') ### STEAM ENGINE
        # patch_bp('BattleAI_Bos_Mer_C03_020') #### Enemy in the Mist

        patch_bp('BattleAI_Bos_Mer_C05_010', 1, 0x29c4, 40) # Tank Obsidian
        patch_bp('BattleAI_Bos_Mer_C05_010', 7, 0x193b, 30)
        patch_bp('BattleAI_Bos_Mer_C05_010', 7, 0x2c98, 30)
        patch_bp('BattleAI_Bos_Mer_C05_010', 7, 0x2e08, 30)
        patch_bp('BattleAI_Bos_Mer_C05_010', 7, 0x1cde, 20)
        patch_bp('BattleAI_Bos_Mer_C05_010', 7, 0x1d41, 20)
        patch_bp('BattleAI_Bos_Mer_C05_010', 7, 0x199e, 10)
        patch_bp('BattleAI_Bos_Mer_C05_010', 7, 0x1b0e, 10)
        patch_bp('BattleAI_Bos_Mer_C05_010', 7, 0x2c35, 10)
        patch_bp('BattleAI_Bos_Mer_C05_020', 1, 0x2a8, 5) # Glacis Plate
        patch_bp('BattleAI_Bos_Mer_C05_040', 1, 0x9b3, 4) # Cannon

        patch_bp('BattleAI_Bos_Sch_C04_010', 3, 0x2ed8, 14) # Grieving Golem

        patch_bp('BattleAI_Bos_Sub_Karma_010', 3, 0x139f, 7) # Karma
        patch_bp('BattleAI_Bos_Sub_Karma_010', 3, 0x1446, 1)
        patch_bp('BattleAI_Bos_Sub_Karma_010', 3, 0x14ed, 15)
        patch_table('BattleAI_Bos_Sub_Karma_010', 11, 'ShieldMax')

        patch_bp('BattleAI_Bos_Sub_Shaman_010', 1, 0x22c1, 3)
        patch_bp('BattleAI_Bos_Sub_Shaman_010', 1, 0x2402, 3)

        patch_bp('BattleAI_Bos_THI_C02_010', 1, 0xfc3, 8) # Bergomi

        patch_table('BattleAI_Bos_Thi_C03_010', 12, 'CurrentShield') # Mother
        patch_bp('BattleAI_Bos_Thi_C03_010', 1, 0x7ce, 3)
        # Normally goes from 6 -> 9 -> 11
        # got the first boost but can't find the second

        patch_bp('BattleAI_Bos_War_C02_010', 1, 0x2683, 10) # Bandelam the Reaper
        patch_bp('BattleAI_Bos_War_C02_010', 1, 0x283d, 8)
        patch_bp('BattleAI_Bos_War_C04_010', 3, 0x36da, 9) # Rai Mei
        patch_bp('BattleAI_Bos_War_C05_010', 1, 0xcda, 9) # General Ritsu
        patch_bp('BattleAI_Bos_War_C05_010', 1, 0x113a, 11)
        patch_bp('BattleAI_Bos_War_C05_020', 1, 0x10a8, 9) # King Mugen

        ### SKIPPING THIS ONE, DOESN'T SEEM TO USE m_nShieldPointMax
        # patch_bp('BattleAI_NPC_War_C05_010')

        patch_bp('gojutou_03', 3, 0x14e5, 2) # Tyran the Seeker
        patch_bp('gojutou_04', 3, 0xa89, 2) # Auðnvarg
        patch_bp('SUB_BOS_01', 3, 0x1327, 2) # Yurinas
        patch_bp('subB_Dng_Isd_2_1', 3, 0x1534, 2) # Behemoth
        patch_bp('subB_Dng_OCN_1_1_SEA_2', 3, 0xee3, 1) # Scourge of the Sea
        patch_table('subB_Dng_Ocn_1_3', 12, 'add_shield') # Gigantes
        patch_bp('subB_Dng_Snw_3_4', 3, 0x9bc, 2) # Dreadwolf
        patch_bp('subB_Dng_Wld_1_2', 3, 0xc8a, 2) # Manymaws
        patch_bp('subB_Dng_Wld_3_2', 3, 0x16ae, 3) # Deep One
