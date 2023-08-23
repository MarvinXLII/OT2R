from DataTable import Table, RowSplit
import random
from Manager import Manager

class EnemyRow(RowSplit):
    def __init__(self, key, data):
        super().__init__(key, data)
        self.groups = set()

    @property
    def dontStrengthen(self):
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
        textDB = Manager.getInstance('GameTextEN').table
        return textDB.getText(self.DisplayNameID)

    @property
    def isBoss(self):
        return '_BOS_' in self.key

    @property
    def shields(self):
        return self.weaponShields + self.magicShields

    @shields.setter
    def shields(self, shields):
        assert len(shields) == 12
        self.weaponShields = shields[:6]
        self.magicShields = shields[6:]

    @property
    def weaponShields(self):
        return self.WeaponResist[:6]

    @weaponShields.setter
    def weaponShields(self, shields):
        assert len(shields) == 6
        self.WeaponResist[:6] = shields

    @property
    def magicShields(self):
        return self.AttributeResist[1:]

    @magicShields.setter
    def magicShields(self, shields):
        assert len(shields) == 6
        self.AttributeResist[1:] = shields

    def _addWeakness(self, shields, *pcs):
        canBeRemoved = [s == 'EATTRIBUTE_RESIST::eWEAK' for s in shields]
        def getCanBeAdded(pc):
            canBeAdded = [False]*len(shields)
            for i, s in enumerate(pc.strengths()):
                if i == len(shields):
                    break
                if s and shields[i] == 'EATTRIBUTE_RESIST::eWEAK':
                    return [] # Don't add anything if enemy is already weak to a PC's weapon/magic
                if s and not canBeRemoved[i]:
                    canBeAdded[i] = True
            return canBeAdded

        idx = range(len(shields))
        for pc in pcs:
            if sum(canBeRemoved) == 0:
                break
            canBeAdded = getCanBeAdded(pc)
            if sum(canBeAdded):
                r = random.choices(idx, canBeRemoved, k=1)[0]
                a = random.choices(idx, canBeAdded, k=1)[0]
                assert shields[r] == 'EATTRIBUTE_RESIST::eWEAK'
                shields[r] = 'EATTRIBUTE_RESIST::eNONE'
                shields[a] = 'EATTRIBUTE_RESIST::eWEAK'
                canBeRemoved[r] = False

        return shields

    def addWeaknessToPC(self, *pcs):
        shields = self.shields
        self.shields = self._addWeakness(shields, *pcs)

    def addWeaponWeaknessToPC(self, *pcs):
        # Make sure enemy has a weapon weakness
        # It's possible for an enemy to be only weak to magic!
        if self.weaponShields.count('EATTRIBUTE_RESIST::eWEAK') == 0:
            self.weaponShields, self.magicShields = self.magicShields, self.weaponShields
        self.weaponShields = self._addWeakness(self.weaponShields, *pcs)

    def updateWeaknessToPCs(self, weaponOnly=False):
        pcs = set()
        enemyGroupTable = Manager.getInstance('EnemyGroupData').table
        for groupName in sorted(self.groups):
            group = enemyGroupTable.getRow(groupName)
            if group is None: continue
            if group.pcRegion is None: continue
            if group.ring > 1: continue
            pcs.add(group.pcRegion)
        pcList = sorted(pcs)
        if weaponOnly:
            self.addWeaponWeaknessToPC(*pcList)
        else:
            self.addWeaknessToPC(*pcList)


class EnemyTable(Table):
    def getName(self, eKey):
        row = self.getRow(eKey)
        if row:
            return row.name
