from DataTable import Table, Row
from Manager import Manager


class AbilityRow(Row):
    def __init__(self, *args):
        super().__init__(*args)
        self.vanillaAbilityRatio = self.AbilityRatio
        self.costSP = self.CostType == 'EABILITY_COST_TYPE::eMP'

    @property
    def name(self):
        textDB = Manager.getInstance('GameTextEN').table
        return textDB.getText(self.DisplayName)

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
    def isPhysical(self):
        return self.AbilityType == 'EABILITY_TYPE::ePHYSICS' or self.AbilityType == 'EABILITY_TYPE::eSCATTER'

    @property
    def isMagic(self):
        return self.AbilityType == 'EABILITY_TYPE::eMAGIC'

    @property
    def isHeal(self):
        return self.AbilityType == 'EABILITY_TYPE::eHP_RECOVERY' or self.AbilityType == 'EABILITY_TYPE::eREVIVE'

    @property
    def isAttack(self):
        return self.isPhysical or self.isMagic

    # Cost value set in AbilitySetDB
    def makeInventor(self):
        self.CostType = 'EABILITY_COST_TYPE::eINVENTOR'

    # Cost value set in AbilitySetDB
    def makeNotInventor(self):
        self.CostType = 'EABILITY_COST_TYPE::eMP'


class AbilityTable(Table):
    def getAbilityName(self, aKey):
        row = self.getRow(aKey)
        if row:
            return row.name

    def getAbilityWeapon(self, aKey):
        row = self.getRow(aKey)
        if row:
            return row.weapon

    def getAbilitySP(self, aKey):
        row = self.getRow(aKey)
        if row:
            return row.CostValue

    def getAbilityRatioChange(self, aKey):
        row = self.getRow(aKey)
        if row and (row.isAttack or row.isHeal):
            vanilla = row.vanillaAbilityRatio
            ratio = row.AbilityRatio
            return 100.0 * (ratio - vanilla) / vanilla
