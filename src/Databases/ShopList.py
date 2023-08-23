from DataTable import Table, Row
from Manager import Manager
import sys

class ShopListRow(Row):

    def __init__(self, *args):
        super().__init__(*args)
        self.isPrologue = 'Prologue' in self.key

    def removeWeapons(self):
        s = set(self.LabelList).difference([
            'NPC_KEN_PrologueSHOP_03', # Lance  --> make Sword
            'NPC_SHO_PrologueSHOP_03', # Lance
            'NPC_TOU_PrologueSHOP_03', # Dagger
            'NPC_KAR_PrologueSHOP_03', # Axe
            'NPC_SHO_PrologueSHOP_04', # Bow
            'NPC_KUS_PrologueSHOP_03', # Axe    --> make Rod
            'NPC_ODO_PrologueSHOP_04', # Dagger
        ])
        self.LabelList = sorted(s)

    def addPrologueShopWeapons(self, weapons):
        if not self.isPrologue:
            sys.exit(f'{self.key} is not a prologue shop!')

        self.removeWeapons()
        for weapon in weapons:
            if weapon == 'Sword':
                self.LabelList.append('NPC_KEN_PrologueSHOP_03')
            elif weapon == 'Lance':
                self.LabelList.append('NPC_SHO_PrologueSHOP_03')
            elif weapon == 'Dagger':
                self.LabelList.append('NPC_TOU_PrologueSHOP_03')
            elif weapon == 'Axe':
                self.LabelList.append('NPC_KAR_PrologueSHOP_03')
            elif weapon == 'Bow':
                self.LabelList.append('NPC_SHO_PrologueSHOP_04')
            elif weapon == 'Rod':
                self.LabelList.append('NPC_KUS_PrologueSHOP_03')
            else:
                sys.exit(f'weapon {weapon} not setup for adding to prologue shops!')

    def addFireSoulstone(self):
        self.LabelList.append('NPC_Fld_Cty_1_2_TALK_0900_N000_01')

    def addIceSoulstone(self):
        self.LabelList.append('NPC_Fld_Cty_1_2_TALK_0900_N000_03')

    def addThunderSoulstone(self):
        self.LabelList.append('NPC_Fld_Cty_1_2_TALK_0900_N000_05')

    def addWindSoulstone(self):
        self.LabelList.append('NPC_Fld_Cty_1_2_TALK_0900_N000_07')

    def addLightSoulstone(self):
        self.LabelList.append('NPC_Fld_Cty_1_2_TALK_0900_N000_09')

    def addDarkSoulstone(self):
        self.LabelList.append('NPC_Fld_Cty_1_2_TALK_0900_N000_11')


class ShopListTable(Table):
    @property
    def prologueAgnea(self):
        return self.NPC_ODO_PrologueSHOP

    @property
    def prologueCastti(self):
        return self.NPC_KUS_PrologueSHOP

    @property
    def prologueHikari(self):
        return self.NPC_KEN_PrologueSHOP

    @property
    def prologueOchette(self):
        return self.NPC_KAR_PrologueSHOP

    @property
    def prologueOsvald(self):
        return self.NPC_GAK_PrologueSHOP

    @property
    def prologuePartitio(self):
        return self.NPC_SHO_PrologueSHOP

    @property
    def prologueTemenos(self):
        return self.NPC_SIN_PrologueSHOP

    @property
    def prologueThrone(self):
        return self.NPC_TOU_PrologueSHOP
