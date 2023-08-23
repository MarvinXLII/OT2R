from Assets import Data
from DataTable import DataTable, RowSplit
import json
from Utility import get_filename


class Group(RowSplit):
    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla = self.enemies

    @property
    def enemies(self):
        group = []
        for e in self.EnemyID:
            if e != 'None':
                n = self.enemyDB.getName(e)
                if n:
                    group.append(n)
        return group

    @property
    def isRandomEncounter(self):
        return '_DAY_' in self.key or '_NGT_' in self.key


class EnemyGroupDB(DataTable):
    Row = Group

    def __init__(self):
        super().__init__('EnemyGroupData.uasset')

        # Organize groups by location
        # 
