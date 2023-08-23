import random
import sys
from copy import deepcopy
from Shuffler import Shuffler, Slot, noWeights
from Manager import Manager


def separateByRing(w, s, c):
    for i, si in enumerate(s):
        w[i] *= si.ring == c.ring


# Keep chapter 1 bosses separate
def separateRingOne(w, s, c):
    if c.ring == 1:
        for i, si in enumerate(s):
            w[i] *= si.ring == 1
    else:
        for i, si in enumerate(s):
            w[i] *= si.ring > 1


class Group(Slot):
    def __init__(self, enemyGroup):
        self.enemyGroup = enemyGroup

        # Data to be copied/patched
        for key in self.enemyGroup.keys:
            assert hasattr(self.enemyGroup, key)
            v = getattr(self.enemyGroup, key)
            setattr(self, key, v)

        self.bossType = enemyGroup.bossType
        self.ring = enemyGroup.ring

    def copy(self, other):
        for key in self.enemyGroup.keys:
            v = getattr(other, key)
            setattr(self, key, v)
        self.enemyGroup.randoBoss = other.enemyGroup.vanillaBoss

    def patch(self):
        for key in self.enemyGroup.keys:
            v = getattr(self, key)
            setattr(self.enemyGroup, key, v)


class Bosses(Shuffler):
    ShuffleByRings = separateByRing
    IncludeMidGameOptBos = False
    IncludeLateGameOptBos = False
    IncludeGaldera = False
    IncludeVide = False

    def __init__(self):
        self.enemyGroupDB = Manager.getInstance('EnemyGroupData').table
        slots = []
        candidates = []

        # Construct all bosses
        for g in self.enemyGroupDB:
            if g.vanillaBoss:
                slots.append(Group(g))
                candidates.append(Group(g))

        # Remove bosses as needed for selected options 
        if not self.IncludeMidGameOptBos:
            slots = list(filter(lambda g: not (g.bossType == 'optional' and g.ring == 2), slots))
            candidates = list(filter(lambda g: not (g.bossType == 'optional' and g.ring == 2), candidates))

        if not self.IncludeLateGameOptBos:
            slots = list(filter(lambda g: not (g.bossType == 'optional' and g.ring == 3), slots))
            candidates = list(filter(lambda g: not (g.bossType == 'optional' and g.ring == 3), candidates))

        if not self.IncludeGaldera:
            slots = list(filter(lambda g: g.bossType != 'galdera', slots))
            candidates = list(filter(lambda g: g.bossType != 'galdera', candidates))

        if not self.IncludeVide:
            slots = list(filter(lambda g: g.bossType != 'videwicked', slots))
            candidates = list(filter(lambda g: g.bossType != 'videwicked', candidates))

        # Always omit Vide due to softlock
        slots = list(filter(lambda g: g.bossType != 'vide', slots))
        candidates = list(filter(lambda g: g.bossType != 'vide', candidates))

        self.slots = slots
        self.candidates = candidates

        self.vacant = None
        self.weights = None

    def generateWeights(self):
        super().generateWeights(Bosses.ShuffleByRings)

    def finalize(self):

        ##########################
        #### HOLD_OUT modding ####
        ##########################

        aiBP = [
            Manager.getAssetOnly('BattleAI_Bos_Mer_C01_010'),
            Manager.getAssetOnly('BattleAI_Bos_Cle_C01_010'),
            Manager.getAssetOnly('BattleAI_Bos_Hun_C01_010'),
            Manager.getAssetOnly('BattleAI_Bos_War_C01_020'),
            Manager.getAssetOnly('BattleAI_Bos_Sch_C01_010'),
        ]

        # Modify "disease" keeping bosses alive through the first in battle cutscene.
        # This seems to work for most bosses.
        diseaseTable = Manager.getInstance('DiseaseData').table
        diseaseTable.HOLD_OUT.EnableTurnCount = True

        # Setup target to be found in uexp
        zero = int.to_bytes(0, 4, byteorder='little')
        negOne = int.to_bytes(-1, 4, byteorder='little', signed=True)
        com1d = bytes([0x1d])
        com21 = bytes([0x21])
        target = com1d + zero + com1d + negOne

        # Changes a -1 to 0. Not sure what goes on for 0 HOLD_OUT's.
        # Positive numbers seems to correspond to the number of times
        # the boss get's is kept alive with 1 HP rather than killed.
        for k, bp in enumerate(aiBP):
            hoVal = bp.uasset.getIndex('HOLD_OUT').to_bytes(8, byteorder='little')
            addr = bp.uexp.index(hoVal + target)
            bp.patchInt32(addr+14, 0)

        ###################################
        ### Capturing Ochette's Bosses ####
        ###################################

        enemyDB = Manager.getInstance('EnemyDB').table

        #### Turn off Tera
        tera = enemyDB.ENE_BOS_HUN_C02_010
        tera.TameEnable = False
        tera.LegendTameMonster = False

        #### Turn off Glacis
        glacis = enemyDB.ENE_BOS_HUN_C02_020
        glacis.TameEnable = False
        glacis.LegendTameMonster = False


        ### Update rando bosses
        def getEnemyWithMaxHP(slot):
            # Make sure to get the enemy with the most HP
            boss = None
            hp = 0
            for e in slot.EnemyID:
                enemy = enemyDB.getRow(e)
                if enemy:
                    if enemy.Param['HP'] > hp:
                        boss = enemy
                        hp = enemy.Param['HP']
            assert boss, 'no boss found!?'
            return boss

        def getGroup(groupName):
            for s in self.slots:
                if s.enemyGroup.key == groupName:
                    return s
            else:
                sys.exit(f'group {groupName} not found!')
        
        teraGroup = getGroup('ENG_BOS_HUN_C02_010')
        boss = getEnemyWithMaxHP(teraGroup)
        boss.TameEnable = True
        boss.LegendTameMonster = True
        boss.InvadeMonsterID = tera.InvadeMonsterID
        boss.DefaultTameRate = tera.DefaultTameRate

        glacisGroup = getGroup('ENG_BOS_HUN_C02_020')
        boss = getEnemyWithMaxHP(glacisGroup)
        boss.TameEnable = True
        boss.LegendTameMonster = True
        boss.InvadeMonsterID = glacis.InvadeMonsterID
        boss.DefaultTameRate = glacis.DefaultTameRate

        ############################################
        #### Prevent Ochette w/o Acta Softlocks ####
        ############################################

        # Seems to work for both bosses
        hunBosA = Manager.getAsset('ENG_BOS_HUN_C03_010_A')
        export = hunBosA.getUexp2Obj(16)
        export.assertBoolOn(0x2a)
        export.toggleBoolOff(0x2a)

        # Included just in case
        hunBosB = Manager.getAsset('ENG_BOS_HUN_C03_010_B')
        export = hunBosB.getUexp2Obj(14)
        export.assertBoolOn(0x2a)
        export.toggleBoolOff(0x2a)

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

        def getPCJob(boss):
            for s in self.slots:
                if s.enemyGroup.randoBoss == boss:
                    break
            else:
                sys.exit(f'Boss {boss} not found!')

            for j in abil.keys():
                if j in s.enemyGroup.key:
                    return j

            return None
            
        # Add text for their Ex Skills
        gameTextTable = Manager.getInstance('GameTextEN').table
        abilitySetTable = Manager.getInstance('AbilitySetData').table
        pcTable = Manager.getInstance('PlayableCharacterDB').table

        def getNames(pc):
            es1 = abilitySetTable.getRow(pc.exSkillOne).name
            es2 = abilitySetTable.getRow(pc.exSkillTwo).name
            return es2, es1

        # Osvald
        job = getPCJob('Professor Harvey')
        if job in abil:
            pcSch, skillSch = abil['SCH']
            pcJob, skillJob = abil[job]

            # Boss
            bosOSV = Manager.getAsset('ENG_BOS_SCH_C05_010_A')

            se1 = bosOSV.getUexp2Obj(16)
            se1.assertUInt8(pcSch, addr=0x22)
            se1.patchUInt8(pcJob, addr=0x22)
            se1.assertUInt32(skillSch, addr=0x24)
            se1.patchUInt32(skillJob, addr=0x24)

            se2 = bosOSV.getUexp2Obj(17)
            se2.assertUInt8(pcSch, addr=0x2b)
            se2.patchUInt8(pcJob, addr=0x2b)
            se2.assertUInt32(skillSch, addr=0x2d)
            se2.patchUInt32(skillJob, addr=0x2d)

        if job != 'SCH': # If boss isn't in it's vanilla storyline
            pcSch, skillSch = abil['SCH']

            # Story end event
            jsonRef = Manager.getJson('MS_KAR_30_2500') # Ochette's end event
            osvJson = Manager.getJson('MS_GAK_50_1300') # Osvald's end event

            ref = deepcopy(jsonRef.jsonList[-3:-1])
            ref[0].target = pcSch
            ref[0].opt[0] = str(skillSch)
            ref[1].text = "ED_GAK_ADVANCEABILITY_0020"
            osvJson.insertCommand(ref[0], 161)
            osvJson.insertCommand(ref[1], 162)

            # Text
            es2, _ = getNames(pcTable.osvald)
            gameTextTable.ED_GAK_ADVANCEABILITY_0020._data['Text'].string1 = 'GameTextEN'
            gameTextTable.ED_GAK_ADVANCEABILITY_0020._data['Text'].string2 = 'ED_GAK_ADVANCEABILITY_0020'
            gameTextTable.ED_GAK_ADVANCEABILITY_0020.setText(f'Osvald learned the EX skill "{es2}"')


        # Agnea
        job = getPCJob('Dolcinaea the Star')
        if job in abil:
            pcDan, skillDan = abil['DAN']
            pcJob, skillJob = abil[job]

            # Boss
            bosAGN = Manager.getAsset('ENG_BOS_DAN_C05_020')

            se1 = bosAGN.getUexp2Obj(17)
            se1.assertUInt8(pcDan, addr=0x22)
            se1.patchUInt8(pcJob, addr=0x22)
            se1.assertUInt32(skillDan, addr=0x24)
            se1.patchUInt32(skillJob, addr=0x24)

            se2 = bosAGN.getUexp2Obj(18)
            se2.assertUInt8(pcDan, addr=0x2b)
            se2.patchUInt8(pcJob, addr=0x2b)
            se2.assertUInt32(skillDan, addr=0x2d)
            se2.patchUInt32(skillJob, addr=0x2d)

        if job != 'DAN': # If boss isn't in it's vanilla storyline
            pcDan, skillDan = abil['DAN']

            # Story end event
            jsonRef = Manager.getJson('MS_KAR_30_2500') # Ochette's end event
            agnJson = Manager.getJson('MS_ODO_50_2000') # Agnea's end event

            ref = deepcopy(jsonRef.jsonList[-3:-1])
            ref[0].target = pcDan
            ref[0].opt[0] = str(skillDan)
            ref[1].text = "ED_ODO_ADVANCEABILITY_0020"
            agnJson.insertCommand(ref[0], 139)
            agnJson.insertCommand(ref[1], 139)

            # Text
            es2, _ = getNames(pcTable.agnea)
            gameTextTable.ED_ODO_ADVANCEABILITY_0020._data['Text'].string1 = 'GameTextEN'
            gameTextTable.ED_ODO_ADVANCEABILITY_0020._data['Text'].string2 = 'ED_ODO_ADVANCEABILITY_0020'
            gameTextTable.ED_ODO_ADVANCEABILITY_0020.setText(f'Agnea learned the EX skill "{es2}"')


        ###########################
        #### Keep LT Guages On ####
        ###########################

        def keepOn(filename, flag):
            f = Manager.getJson(filename)
            f.toggleFlagOn(flag)

        keepOn('MS_KEN_10_0100', 30)
        keepOn('MS_KAR_10_0200', 31)
        keepOn('MS_KUS_10_0100', 32)
        keepOn('MS_SHO_10_0100', 33)
        keepOn('MS_SIN_10_0100', 34)
        keepOn('MS_GAK_10_0100', 35)
        keepOn('MS_TOU_10_0100', 36)
        keepOn('MS_ODO_10_0100', 37)
