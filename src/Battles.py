import random
from Nothing import Nothing
from Manager import Manager
from math import ceil


def shuffler(enemies, *attributes):
    stuff = []
    stuffBosses = []
    mainEnemies = []
    bossEnemies = []
    for enemy in enemies:
        if 'TEST' in enemy.key:
            continue

        data = []
        for attr in attributes:
            v = getattr(enemy, attr)
            data.append(v)

        if 'ENE_BOS' in enemy.key:
            stuffBosses.append(data)
            bossEnemies.append(enemy)
        else:
            stuff.append(data)
            mainEnemies.append(enemy)

    random.shuffle(stuff)
    random.shuffle(stuffBosses)

    for data, enemy in zip(stuff, mainEnemies):
        for value, attr in zip(data, attributes):
            setattr(enemy, attr, value)

    for data, enemy in zip(stuffBosses, bossEnemies):
        for value, attr in zip(data, attributes):
            setattr(enemy, attr, value)


def dropItem(enemies):
    shuffler(enemies, 'HaveItemID', 'DropProbability')

def stealItem(enemies):
    shuffler(enemies, 'StealGuard', 'StealItemID')

def stealMoney(enemies):
    shuffler(enemies, 'StealMoneyGuard', 'StealMoney')
        
def bribeMoney(enemies):
    shuffler(enemies, 'BribeGuard', 'BribeMoney')

def dropItemRate(enemies):
    for enemy in enemies:
        enemy.DropProbability = 100


class Battles:
    scaleExp = 1
    scaleJP = 1
    scaleLeaves = 1
    scaleEnemyHP = 1
    scaleEnemyATK = 1
    scaleEnemyMATK = 1
    scaleEnemyDEF = 1
    scaleEnemyMDEF = 1
    scaleEnemyACC = 1
    scaleEnemyEVA = 1
    scaleEnemyAGI = 1
    scaleEnemySP = 1
    alwaysDropItem = Nothing
    shuffleDropItem = Nothing
    shuffleStealItem = Nothing
    shuffleStealMoney = Nothing
    shuffleBribeMoney = Nothing
    
    def __init__(self):
        self.enemyDB = Manager.getInstance('EnemyDB').table

    def run(self):
        # Non-random stuff
        self._scale()
        self._scaleSPInBP()
        Battles.alwaysDropItem(self.enemyDB)

        # Randomized stuff
        Battles.shuffleDropItem(self.enemyDB)
        Battles.shuffleStealItem(self.enemyDB)
        Battles.shuffleStealMoney(self.enemyDB)
        Battles.shuffleBribeMoney(self.enemyDB)

    def _scale(self):
        for enemy in self.enemyDB:
            enemy.Exp = int(Battles.scaleExp * enemy.Exp)
            enemy.JobPoint = int(Battles.scaleJP * enemy.JobPoint)
            enemy.Money = int(Battles.scaleLeaves * enemy.Money)
            if enemy.dontStrengthen: # Make sure mandatory battles with weak PCs are still beatable
                enemy.Param['HP'] = ceil(min(Battles.scaleEnemyHP, 1) * enemy.Param['HP'])
                enemy.Param['ATK'] = ceil(min(Battles.scaleEnemyATK, 1) * enemy.Param['ATK'])
                enemy.Param['MATK'] = ceil(min(Battles.scaleEnemyMATK, 1) * enemy.Param['MATK'])
                enemy.Param['DEF'] = ceil(min(Battles.scaleEnemyDEF, 1) * enemy.Param['DEF'])
                enemy.Param['MDEF'] = ceil(min(Battles.scaleEnemyMDEF, 1) * enemy.Param['MDEF'])
                enemy.Param['ACC'] = ceil(min(Battles.scaleEnemyACC, 1) * enemy.Param['ACC'])
                enemy.Param['EVA'] = ceil(min(Battles.scaleEnemyEVA, 1) * enemy.Param['EVA'])
                enemy.Param['AGI'] = ceil(min(Battles.scaleEnemyAGI, 1) * enemy.Param['AGI'])
                enemy.Param['SP'] = ceil(min(Battles.scaleEnemySP, 1) * enemy.Param['SP'])
            else:
                enemy.Param['HP'] = ceil(Battles.scaleEnemyHP * enemy.Param['HP'])
                enemy.Param['ATK'] = ceil(Battles.scaleEnemyATK * enemy.Param['ATK'])
                enemy.Param['MATK'] = ceil(Battles.scaleEnemyMATK * enemy.Param['MATK'])
                enemy.Param['DEF'] = ceil(Battles.scaleEnemyDEF * enemy.Param['DEF'])
                enemy.Param['MDEF'] = ceil(Battles.scaleEnemyMDEF * enemy.Param['MDEF'])
                enemy.Param['ACC'] = ceil(Battles.scaleEnemyACC * enemy.Param['ACC'])
                enemy.Param['EVA'] = ceil(Battles.scaleEnemyEVA * enemy.Param['EVA'])
                enemy.Param['AGI'] = ceil(Battles.scaleEnemyAGI * enemy.Param['AGI'])
                enemy.Param['SP'] = ceil(min(Battles.scaleEnemySP * enemy.Param['SP'], 99))

    def _scaleSPInBP(self):
        def patchBP(bpName, expIndex, addr, checkVal=None):
            boss = Manager.getAsset(bpName)
            export = boss.getUexp2Obj(expIndex)
            value = export.readIntConst(addr)
            if checkVal: assert value == checkVal
            newValue = ceil(min(Battles.scaleEnemySP * value, 99))
            export.patchIntConst(addr, value, newValue)
            print(f'{bpName}, {expIndex} @ {hex(addr)}: {value} -> {newValue}')

        def patchTable(bpName, expIndex, key='ShieldMax'):
            boss = Manager.getAsset(bpName)
            value = boss.uasset.exports[expIndex].uexp1[key].value
            newValue = ceil(min(Battles.scaleEnemySP * value, 99))
            boss.uasset.exports[expIndex].uexp1[key].value = newValue
            print(f'{bpName}, {expIndex} @ {key}: {value} -> {newValue}')

        patchBP('BattleAI_Bos_Apo_C02_010', 1, 0x19cf, 9) # Sand Lion
        patchBP('BattleAI_Bos_Apo_C02_010', 1, 0x1ace, 7)
        patchBP('BattleAI_Bos_Apo_C05_010', 3, 0x1e6d, 12) # Trousseau
        patchBP('BattleAI_Bos_Apo_C05_011', 2, 0x5cb, 12)

        patchBP('BattleAI_Bos_Cle_C03_010', 3, 0x2979, 7) # Deputy Cubaryi
        patchBP('BattleAI_Bos_Cle_C03_010', 3, 0x2a21, 9)
        patchBP('BattleAI_Bos_Cle_C03_010', 3, 0x2ac9, 11)
        patchBP('BattleAI_Bos_Cre_C05_010', 1, 0xf4b, 13) # Captain Kaldena

        patchBP('BattleAI_Bos_DAN_C04_010', 3, 0x1b5a, 7) # Veronica
        patchBP('BattleAI_Bos_DAN_C04_010', 3, 0x1caa, 8)
        patchBP('BattleAI_Bos_DAN_C04_010', 3, 0x1c02, 9)
        patchBP('BattleAI_Bos_DAN_C04_010', 3, 0x37e5, 10)
        patchBP('BattleAI_Bos_DAN_C04_010', 1, 0xcd8, 1)
        patchBP('BattleAI_Bos_DAN_C04_010', 1, 0xe74, 1)
        patchBP('BattleAI_Bos_DAN_C04_010', 1, 0x1357, 1)
        patchBP('BattleAI_Bos_DAN_C04_010', 1, 0x183a, 1)
        patchBP('BattleAI_Bos_DAN_C05_030', 3, 0x238c, 9) # Dolcinaea the Star
        patchBP('BattleAI_Bos_DAN_C05_030', 3, 0x3914, 9)

        patchBP('BattleAI_Bos_Ext_Low_010', 1, 0x1939, 16) # Omniscient Eye
        patchBP('BattleAI_Bos_Ext_Upp_010', 1, 0xdee, 20) # Galdera, the Fallen
        patchBP('BattleAI_Bos_Ext_Upp_010', 1, 0xe39, 20)
        # Incrementer
        patchBP('BattleAI_Bos_Ext_Upp_010', 4, 0xa30, 2)
        # Shields after arm/head/sword start dying
        patchBP('BattleAI_Bos_Ext_Upp_010', 6, 0x232b, 50)
        patchBP('BattleAI_Bos_Ext_Upp_010', 6, 0x2864, 20)
        # # Increase arm/head/sword shields
        #### These don't work properly. First hit will drop shield count to max.
        # patchBP('BattleAI_Bos_Ext_Upp_010', 6, 0x1aa6, 6)
        # patchBP('BattleAI_Bos_Ext_Upp_010', 6, 0x20eb, 3)
        # patchBP('BattleAI_Bos_Ext_Upp_010', 6, 0x22dc, 3)
        # patchBP('BattleAI_Bos_Ext_Upp_010', 6, 0x2433, 3)
        # patchBP('BattleAI_Bos_Ext_Upp_010', 6, 0x2624, 3)
        # patchBP('BattleAI_Bos_Ext_Upp_010', 6, 0x2815, 3)
        # patchBP('BattleAI_Bos_Ext_Upp_010', 6, 0x296c, 3)
        # patchBP('BattleAI_Bos_Ext_Upp_010', 6, 0x2b5d, 6)
        # patchBP('BattleAI_Bos_Ext_Upp_010', 6, 0x2b82, 6)

        patchTable('BattleAI_Bos_Ext_Upp_020', 12, 'ShieldMax') # Abyssal Maw
        patchBP('BattleAI_Bos_Ext_Upp_020', 1, 0x69c, 2) # No clue what they are for. Keep them anyway in case the Abyssal Maw actually uses them.
        patchBP('BattleAI_Bos_Ext_Upp_020', 1, 0x716, 2)
        patchBP('BattleAI_Bos_Ext_Upp_020', 1, 0x737, 2)
        patchTable('BattleAI_Bos_Ext_Upp_030', 13, 'ShieldMax') # Sundering Arm
        patchTable('BattleAI_Bos_Ext_Upp_040', 12, 'ShieldMax') # Blade of the Fallen

        patchBP('BattleAI_Bos_Hun_C05_010', 16, 0xf63, 10) # Lājackal of the Sorrowful Moon
        patchBP('BattleAI_Bos_Hun_C05_020', 16, 0xf63, 10) # Malamaowl of the Sorrowful Moon

        patchBP('BattleAI_Bos_Lst_C02_020', 3, 0x2a0a, 7) # Arcanette
        patchBP('BattleAI_Bos_Lst_C02_020', 3, 0x2ab2, 9)
        patchBP('BattleAI_Bos_Lst_C02_020', 1, 0x10a5, 2)
        patchBP('BattleAI_Bos_Lst_C02_020', 1, 0x13b2, 2)

        patchBP('BattleAI_Bos_Lst_C03_060', 3, 0x19bf, 7) # Vide
        patchBP('BattleAI_Bos_Lst_C03_060', 3, 0x2c4f, 9)

        patchBP('BattleAI_Bos_Lst_C03_070', 3, 0x1e5b, 15) # Vide, the Wicked
        patchBP('BattleAI_Bos_Lst_C03_070', 3, 0x1f03, 12)

        #### Don't actually have anything!?
        # patchBP('BattleAI_Bos_Mer_C03_010') ### STEAM ENGINE
        # patchBP('BattleAI_Bos_Mer_C03_020') #### Enemy in the Mist

        patchBP('BattleAI_Bos_Mer_C05_010', 1, 0x29c4, 40) # Tank Obsidian
        patchBP('BattleAI_Bos_Mer_C05_010', 7, 0x193b, 30)
        patchBP('BattleAI_Bos_Mer_C05_010', 7, 0x2c98, 30)
        patchBP('BattleAI_Bos_Mer_C05_010', 7, 0x2e08, 30)
        patchBP('BattleAI_Bos_Mer_C05_010', 7, 0x1cde, 20)
        patchBP('BattleAI_Bos_Mer_C05_010', 7, 0x1d41, 20)
        patchBP('BattleAI_Bos_Mer_C05_010', 7, 0x199e, 10)
        patchBP('BattleAI_Bos_Mer_C05_010', 7, 0x1b0e, 10)
        patchBP('BattleAI_Bos_Mer_C05_010', 7, 0x2c35, 10)
        patchBP('BattleAI_Bos_Mer_C05_020', 1, 0x2a8, 5) # Glacis Plate
        patchBP('BattleAI_Bos_Mer_C05_040', 1, 0x9b3, 4) # Cannon

        patchBP('BattleAI_Bos_Sch_C04_010', 3, 0x2ed8, 14) # Grieving Golem

        patchBP('BattleAI_Bos_Sub_Karma_010', 3, 0x139f, 7) # Karma
        patchBP('BattleAI_Bos_Sub_Karma_010', 3, 0x1446, 1)
        patchBP('BattleAI_Bos_Sub_Karma_010', 3, 0x14ed, 15)
        patchTable('BattleAI_Bos_Sub_Karma_010', 11, 'ShieldMax')

        patchBP('BattleAI_Bos_Sub_Shaman_010', 1, 0x22c1, 3)
        patchBP('BattleAI_Bos_Sub_Shaman_010', 1, 0x2402, 3)

        patchBP('BattleAI_Bos_THI_C02_010', 1, 0xfc3, 8) # Bergomi

        patchTable('BattleAI_Bos_Thi_C03_010', 12, 'CurrentShield') # Mother
        patchBP('BattleAI_Bos_Thi_C03_010', 1, 0x7ce, 3)
        # Normally goes from 6 -> 9 -> 11
        # got the first boost but can't find the second

        patchBP('BattleAI_Bos_War_C02_010', 1, 0x2683, 10) # Bandelam the Reaper
        patchBP('BattleAI_Bos_War_C02_010', 1, 0x283d, 8)
        patchBP('BattleAI_Bos_War_C04_010', 3, 0x36da, 9) # Rai Mei
        patchBP('BattleAI_Bos_War_C05_010', 1, 0xcda, 9) # General Ritsu
        patchBP('BattleAI_Bos_War_C05_010', 1, 0x113a, 11)
        patchBP('BattleAI_Bos_War_C05_020', 1, 0x10a8, 9) # King Mugen

        ### SKIPPING THIS ONE, DOESN'T SEEM TO USE m_nShieldPointMax
        # patchBP('BattleAI_NPC_War_C05_010')

        patchBP('gojutou_03', 3, 0x14e5, 2) # Tyran the Seeker
        patchBP('gojutou_04', 3, 0xa89, 2) # Auðnvarg
        patchBP('SUB_BOS_01', 3, 0x1327, 2) # Yurinas
        patchBP('subB_Dng_Isd_2_1', 3, 0x1534, 2) # Behemoth
        patchBP('subB_Dng_OCN_1_1_SEA_2', 3, 0xee3, 1) # Scourge of the Sea
        patchTable('subB_Dng_Ocn_1_3', 12, 'add_shield') # Gigantes
        patchBP('subB_Dng_Snw_3_4', 3, 0x9bc, 2) # Dreadwolf
        patchBP('subB_Dng_Wld_1_2', 3, 0xc8a, 2) # Manymaws
        patchBP('subB_Dng_Wld_3_2', 3, 0x16ae, 3) # Deep One
        
