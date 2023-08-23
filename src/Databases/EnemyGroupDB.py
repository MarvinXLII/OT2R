from DataTable import RowSplit, Table
import hjson
from Utility import get_filename
from Manager import Manager


class EnemyGroupRow(RowSplit):
    groupJson = hjson.load(open(get_filename('json/enemyGroups.json'), 'r', encoding='utf-8'))

    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.enemies

    @property
    def pcRegion(self):
        pc = EnemyGroupRow.groupJson[self.key]['pc']
        if pc:
            jobTable = Manager.getInstance('JobData').table
            return getattr(jobTable, pc)
        return None

    @property
    def ring(self):
        return EnemyGroupRow.groupJson[self.key]['ring']

    @property
    def enemies(self):
        enemies = Manager.getInstance('EnemyDB').table
        group = []
        for e in self.EnemyID:
            if e != 'None':
                n = enemies.getName(e)
                if n:
                    group.append(n)
        return group

    @property
    def isRandomEncounter(self):
        return '_DAY_' in self.key or '_NGT_' in self.key

    def updateWeaknessToPCs(self, weaponOnly=False):
        enemies = Manager.getInstance('EnemyDB').table
        for e in self.EnemyID:
            if e != 'None':
                enemy = enemies.getRow(e)
                if enemy:
                    enemy.updateWeaknessToPCs(weaponOnly=weaponOnly)


class EnemyGroupTable(Table):
    def __init__(self, data, rowClass):
        super().__init__(data, rowClass)
        self.updateGroupSets()

    def updateGroupSets(self):
        enemies = Manager.getInstance('EnemyDB').table
        for enemy in enemies:
            enemy.groups = set()

        for group in self:
            for e in group.EnemyID:
                if e == 'None': continue
                enemy = enemies.getRow(e)
                if enemy:
                    enemy.groups.add(group.key)
