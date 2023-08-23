from DataTable import RowSplit, Table
import hjson
from Utility import get_filename
from Manager import Manager


class EnemyGroupRow(RowSplit):
    groupJson = hjson.load(open(get_filename('json/enemyGroups.json'), 'r', encoding='utf-8'))
    bossJson = hjson.load(open(get_filename('json/bosses.json'), 'r', encoding='utf-8'))

    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.enemies
        self.vanillaBoss = self.bossFromJson()
        self.randoBoss = self.bossFromJson()

    def bossFromJson(self):
        if self.key in EnemyGroupRow.bossJson:
            return EnemyGroupRow.bossJson[self.key]['boss']
        return ''

    @property
    def pcRegion(self):
        pc = EnemyGroupRow.groupJson[self.key]['pc']
        if pc:
            jobTable = Manager.getInstance('JobData').table
            return getattr(jobTable, pc)
        return None

    @property
    def ring(self):
        if self.key in EnemyGroupRow.bossJson:
            return EnemyGroupRow.bossJson[self.key]['ring']
        return EnemyGroupRow.groupJson[self.key]['ring']

    @property
    def bossType(self):
        if self.key in EnemyGroupRow.bossJson:
            return EnemyGroupRow.bossJson[self.key]['type']
        return ''

    @property
    def enemies(self):
        enemies = Manager.getInstance('EnemyDB').table
        group = self.enemyKeys
        names = []
        for e in group:
            n = enemies.getName(e)
            if n:
                names.append(n)
        return names

    @property
    def enemyKeys(self):
        return list(filter(lambda x: x != 'None', self.EnemyID))

    @property
    def isRandomEncounter(self):
        return '_DAY_' in self.key or '_NGT_' in self.key

    # This really needs to be cleaned up!
    def updateWeaknessToPCs(self, *pcs, weaponOnly=False):
        pcs = sorted(pcs)
        enemies = Manager.getInstance('EnemyDB').table
        for e in self.EnemyID:
            if e != 'None':
                enemy = enemies.getRow(e)
                if enemy:
                    if pcs:
                        if weaponOnly:
                            enemy.addWeaponWeaknessToPC(*pcs)
                        else:
                            enemy.addWeaknessToPC(*pcs)
                    else:
                        enemy.updateWeaknessToPCs(weaponOnly)


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

    # Return enemyDB object of main boss
    # purpose of these is to nerf/increase boss hp as needed
    # - e.g. Felvarg vs solo Hikari can be brutal!
    @property
    def earlyAgnea(self):
        return self.ENG_BOS_DAN_C01_010

    @property
    def earlyCastti(self):
        return self.ENG_BOS_APO_C01_010

    @property
    def earlyHikari(self):
        return self.ENG_BOS_WAR_C01_010

    @property
    def earlyOchette(self):
        return self.ENG_BOS_HUN_C01_010

    @property
    def earlyOsvald(self):
        return self.ENG_BOS_SCH_C01_010

    @property
    def earlyPartitio(self):
        return self.ENG_BOS_MER_C01_010

    @property
    def earlyTemenos(self):
        return self.ENG_BOS_CLE_C01_010

    @property
    def earlyThrone(self):
        return self.ENG_BOS_THI_C01_010
