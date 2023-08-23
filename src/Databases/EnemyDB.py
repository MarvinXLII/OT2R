from Assets import Data
from DataTable import DataTable, Table, RowSplit
import random

class Enemy(RowSplit):
    @property
    def name(self):
        return self.textDB.getText(self.DisplayNameID)

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
        shields = self.weaponShields
        self.weaponShields = self._addWeakness(shields, *pcs)


class EnemyDB(DataTable):
    Row = Enemy

    def __init__(self):
        super().__init__('EnemyDB.uasset')

    def getName(self, eKey):
        row = self.table.getRow(eKey)
        if row:
            return row.name
