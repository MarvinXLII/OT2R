from DataTable import Table, Row
from Utility import JOBMAP, BASEJOBS, ADVJOBS, PCNAMESMAP
from Manager import Manager

class JobRow(Row):
    weaponList = ['Sword', 'Lance', 'Dagger', 'Axe', 'Bow', 'Rod']

    @property
    def name(self):
        textDB = Manager.getInstance('GameTextEN').table
        return textDB.getText(self.DisplayName)

    @property
    def equippableWeapons(self):
        return [self.weaponList[i] for i, a in enumerate(self.ProperEquipment[:6]) if a]

    @property # List of ability sets
    def commandAbilities(self):
        return [s['AbilityName'].value for s in self.JobCommandAbility]

    @property
    def supportAbilities(self):
        return [s['AbilityName'].value for s in self.JobSupportAbility]

    @property
    def hasEvasiveManeuvers(self):
        return 'ABI_SCH_SUP_01' in self.supportAbilities

    def strengths(self):
        abilitySetTable = Manager.getInstance('AbilitySetData').table
        weapons = self.ProperEquipment[:6]
        assert sum(weapons) < 6
        magic = [False] * 6
        for command in self.JobCommandAbility[:7]: # Skip divine ability
            key = command['AbilityName'].value
            ability = abilitySetTable.getRow(key)
            if ability is None: continue
            mIdx = ability.magic
            if mIdx >= 0:
                magic[mIdx] = True
        return weapons + magic

    def __lt__(self, other):
        return self.key < other.key


class JobTable(Table):
    def __init__(self, data, rowClass):
        super().__init__(data, rowClass)
        self.baseJobKeys = list(BASEJOBS.keys())
        self.advJobKeys = list(ADVJOBS.keys())

    def clearProperEquipmentWeapons(self):
        for jKey in self.baseJobKeys:
            row = self.getRow(jKey)
            row.ProperEquipment[:6] = [False] * 6
        for jKey in self.advJobKeys:
            if jKey == 'eWEAPON_MASTER': continue
            row = self.getRow(jKey)
            row.ProperEquipment[:6] = [False] * 6

    def getProperEquipment(self, jKey):
        row = self.getRow(jKey)
        return row.ProperEquipment

    def getParameterRevision(self, jKey):
        row = self.getRow(jKey)
        return row.ParameterRevision

    def getSupportAbilities(self, jKey):
        row = self.getRow(jKey)
        return row.JobSupportAbility

    def getCommandAbilities(self, jKey):
        row = self.getRow(jKey)
        return row.JobCommandAbility

    def getPCWeapons(self, pc):
        key = PCNAMESMAP[pc]
        row = self.getRow(key)
        return row.ProperEquipment[:6]

    @property
    def agnea(self):
        return self.getRow('eDANCER')

    @property
    def castti(self):
        return self.getRow('eALCHEMIST')

    @property
    def hikari(self):
        return self.getRow('eFENCER')

    @property
    def partitio(self):
        return self.getRow('eMERCHANT')

    @property
    def ochette(self):
        return self.getRow('eHUNTER')

    @property
    def osvald(self):
        return self.getRow('ePROFESSOR')

    @property
    def temenos(self):
        return self.getRow('ePRIEST')

    @property
    def throne(self):
        return self.getRow('eTHIEF')
