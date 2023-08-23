from DataTable import Table, Row
from Manager import Manager
import sys

class ShopListRow(Row):

    def __init__(self, *args):
        super().__init__(*args)
        self.is_prologue = 'Prologue' in self.key

    def remove_weapons(self):
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

    def add_prologue_shop_weapons(self, weapons):
        if not self.is_prologue:
            sys.exit(f'{self.key} is not a prologue shop!')

        self.remove_weapons()
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

    def add_fire_soulstone(self):
        self.LabelList.append('NPC_Fld_Cty_1_2_TALK_0900_N000_01')

    def add_ice_soulstone(self):
        self.LabelList.append('NPC_Fld_Cty_1_2_TALK_0900_N000_03')

    def add_thunder_soulstone(self):
        self.LabelList.append('NPC_Fld_Cty_1_2_TALK_0900_N000_05')

    def add_wind_soulstone(self):
        self.LabelList.append('NPC_Fld_Cty_1_2_TALK_0900_N000_07')

    def add_light_soulstone(self):
        self.LabelList.append('NPC_Fld_Cty_1_2_TALK_0900_N000_09')

    def add_dark_soulstone(self):
        self.LabelList.append('NPC_Fld_Cty_1_2_TALK_0900_N000_11')


class ShopListTable(Table):
    @property
    def prologue_agnea(self):
        return self.NPC_ODO_PrologueSHOP

    @property
    def prologue_castti(self):
        return self.NPC_KUS_PrologueSHOP

    @property
    def prologue_hikari(self):
        return self.NPC_KEN_PrologueSHOP

    @property
    def prologue_ochette(self):
        return self.NPC_KAR_PrologueSHOP

    @property
    def prologue_osvald(self):
        return self.NPC_GAK_PrologueSHOP

    @property
    def prologue_partitio(self):
        return self.NPC_SHO_PrologueSHOP

    @property
    def prologue_temenos(self):
        return self.NPC_SIN_PrologueSHOP

    @property
    def prologue_throne(self):
        return self.NPC_TOU_PrologueSHOP
