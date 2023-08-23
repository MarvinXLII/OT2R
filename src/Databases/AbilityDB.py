from DataTable import Table, Row
from Manager import Manager


class AbilityRow(Row):
    def __init__(self, *args):
        super().__init__(*args)
        self.vanilla_ability_ratio = self.AbilityRatio
        self.cost_sp = self.CostType == 'EABILITY_COST_TYPE::eMP'

    @property
    def name(self):
        text_db = Manager.get_instance('GameTextEN').table
        return text_db.get_text(self.DisplayName)

    @property
    def weapon(self):
        w = self.RestrictWeapon.split('::e')[1]
        if w == 'NONE':
            return ''
        return w.lower()

    @weapon.setter
    def weapon(self, w):
        b = self.RestrictWeapon.split('::e')[0]
        self.RestrictWeapon = f'{b}::e{w.upper()}'

    @property
    def is_physical(self):
        return self.AbilityType == 'EABILITY_TYPE::ePHYSICS' or self.AbilityType == 'EABILITY_TYPE::eSCATTER'

    @property
    def is_magic(self):
        return self.AbilityType == 'EABILITY_TYPE::eMAGIC'

    @property
    def is_heal(self):
        return self.AbilityType == 'EABILITY_TYPE::eHP_RECOVERY' or self.AbilityType == 'EABILITY_TYPE::eREVIVE'

    @property
    def is_attack(self):
        return self.is_physical or self.is_magic

    # Cost value set in AbilitySetDB
    def make_inventor(self):
        self.CostType = 'EABILITY_COST_TYPE::eINVENTOR'

    # Cost value set in AbilitySetDB
    def make_not_inventor(self):
        self.CostType = 'EABILITY_COST_TYPE::eMP'


class AbilityTable(Table):
    def get_ability_name(self, aKey):
        row = self.get_row(aKey)
        if row:
            return row.name

    def get_ability_weapon(self, aKey):
        row = self.get_row(aKey)
        if row:
            return row.weapon

    def get_ability_sp(self, aKey):
        row = self.get_row(aKey)
        if row:
            return row.CostValue

    def get_ability_ratio_change(self, aKey):
        row = self.get_row(aKey)
        if row and (row.is_attack or row.is_heal):
            vanilla = row.vanilla_ability_ratio
            ratio = row.AbilityRatio
            return 100.0 * (ratio - vanilla) / vanilla
