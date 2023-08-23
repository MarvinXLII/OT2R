import random
from Nothing import Nothing
from Assets import Data
from DataTable import DataTable
from Shuffler import Randomizer, Slot, noWeights
from copy import deepcopy


class Entry(Slot):
    def __init__(self, enemyList, index, level):
        self.enemy = enemyList[index]
        self.enemyList = enemyList
        self.index = index
        self.level = level

    def copy(self, other):
        self.enemy = other.enemy

    def patch(self):
        self.enemyList[self.index] = self.enemy


class Candidate:
    def __init__(self, enemy):
        self.enemy = enemy.key
        self.level = enemy.EnemyLevel
        self.size = enemy.Size
        self.include = True
        self.include &= enemy.key != 'ENE_EVE_SUB_OTR_010' # Skip buttermeep

    def __hash__(self):
        return hash(self.enemy)

    def __lt__(self, other):
        if self.level == other.level:
            return self.enemy < other.enemy
        return self.level < other.level

    def __eq__(self, other):
        if isinstance(other, Candidate):
            return self.enemy == other.enemy and self.level == other.level
        

class EnemyGroups(Randomizer):
    def __init__(self):
        self.enemyGroupDB = Data.getInstance('EnemyGroupData')
        self.enemyDB = Data.getInstance('EnemyDB')

        self.regions = {}
        self.groups = []
        candidates = set()
        for group in self.enemyGroupDB.table:
            # Only doing random encounters, at least for now
            if group.isRandomEncounter:
                # Make sure the group isn't empty
                if not group.enemies:
                    continue

                # Add to the candidates
                for e in group.EnemyID:
                    if e == 'None': continue
                    enemy = self.enemyDB.table.getRow(e)
                    assert enemy.DisplayRank == 0
                    c = Candidate(enemy)
                    candidates.add(c)

                # Store group in region for (possible) shield updating
                # Maybe make shield updates a separate option?
                # (of course doing ch 1 bosses and Temenos' Coerce regardless)
                x = group.key.split('_')
                region = x[2]
                if region not in self.regions:
                    self.regions[region] = []
                self.regions[region].append(group)
                
        self.candidates = sorted(candidates)
        self.slots = [deepcopy(c) for c in self.candidates]

    def run(self):
        self.generateWeights()
        self.generateMap()
        self.finish()
        self.updateShields()

    def generateMap(self):
        self.enemyMap = {}
        # unused = [True] * len(self.candidates)
        unused = [c.include for c in self.candidates]
        idx = list(range(len(self.candidates)))
        for i, (cWeights, slot) in enumerate(zip(self.weights, self.slots)):
            if not unused[i]: continue # e.g. skip buttermeep
            w = [c*u for c, u in zip(cWeights, unused)]
            i = random.choices(idx, w, k=1)[0]
            candidate = self.candidates[i]
            self.enemyMap[slot.enemy] = candidate.enemy
            unused[i] = False

        # Quick test to ensure buttermeep stays in the same place
        # Keep for now, but remove later after tons of testing
        for k, v in self.enemyMap.items():
            assert k != 'ENE_EVE_SUB_OTR_010'
            assert v != 'ENE_EVE_SUB_OTR_010'

    def finish(self):
        for group in self.enemyGroupDB.table:
            for i, enemy in enumerate(group.EnemyID):
                if enemy in self.enemyMap:
                    group.EnemyID[i] = self.enemyMap[enemy]

    def updateShields(self):
        jobDB = DataTable.getInstance('JobData')
        regionToPC = {
            'FST': jobDB.agnea,
            'SEA': jobDB.castti,
            'DST': jobDB.hikari,
            'ISD': jobDB.ochette,
            'SNW': jobDB.osvald,
            'WLD': jobDB.partitio,
            'MNT': jobDB.temenos,
            'CTY': jobDB.throne,
        }
        regionEnemies = {k:set() for k in regionToPC}

        def updateGroups(group, *pcs):
            for e in group.EnemyID:
                if e == 'None': continue
                enemy = self.enemyDB.table.getRow(e)
                enemy.addWeaknessToPC(*pcs)

        def filterEnemies(group):
            enemies = []
            for enemy in group.EnemyID:
                if enemy != 'None':
                    enemies.append(enemy)
            return enemies

        # Organize enemies from groups into regions
        # NB: this keeps Ch 1 enemies and Ring 1 OW together
        # Stick with only 1 PC when updating, at least for now.
        for region, groups in self.regions.items():
            if region == 'Dst':
                for group in groups:
                    if '_DST_1_' in group.key:
                        regionEnemies[region].update(filterEnemies(group))
                    elif '_DST_3_1_A_' in group.key:
                        regionEnemies[region].update(filterEnemies(group))
                    elif '_DST_3_1_B_' in group.key and not '_2' in group.key:
                        regionEnemies[region].update(filterEnemies(group))
            elif region in regionToPC:
                for group in groups:
                    if f'_{region}_1_' in group.key:
                        regionEnemies[region].update(filterEnemies(group))

        for region, enemies in regionEnemies.items():
            enemiesList = sorted(enemies)
            pc = regionToPC[region]
            for enemy in enemiesList:
                e = self.enemyDB.table.getRow(enemy)
                e.addWeaknessToPC(pc)
        

    def generateWeights(self):
        def groupByLevel(w, c, s):
            # Bin by level
            # 0 - 5
            # 6 - 10
            # 11 - 15
            # 16 - 20
            # 21 - 30
            # 31 - 40
            # 41+
            if s.level <= 5:
                for i, ci in enumerate(c):
                    w[i] *= ci.level <= 5
            elif s.level <= 10:
                for i, ci in enumerate(c):
                    w[i] *= ci.level > 5 and ci.level <= 10
            elif s.level <= 15:
                for i, ci in enumerate(c):
                    w[i] *= ci.level > 10 and ci.level <= 15
            elif s.level <= 20:
                for i, ci in enumerate(c):
                    w[i] *= ci.level > 15 and ci.level <= 20
            elif s.level <= 30:
                for i, ci in enumerate(c):
                    w[i] *= ci.level > 20 and ci.level <= 30
            elif s.level <= 40:
                for i, ci in enumerate(c):
                    w[i] *= ci.level > 30 and ci.level <= 40
            else:
                for i, ci in enumerate(c):
                    w[i] *= ci.level > 40

        def groupBySize(w, c, s):
            for i, ci in enumerate(c):
                w[i] *= s.size == ci.size
            
        super().generateWeights(groupByLevel, groupBySize)
