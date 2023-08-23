from Assets import Data
from DataTable import DataTable, Row
from Utility import JOBMAP, BASEJOBS, ADVJOBS, PCNAMESMAP

class Job(Row):
    weaponList = ['Sword', 'Lance', 'Dagger', 'Axe', 'Bow', 'Rod']

    @property
    def name(self):
        return self.textDB.getText(self.DisplayName)

    @property
    def equippableWeapons(self):
        return [Job.weaponList[i] for i, a in enumerate(self.ProperEquipment[:6]) if a]

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
        abilitySetData = DataTable.getInstance('AbilitySetData').table
        weapons = self.ProperEquipment[:6]
        assert sum(weapons) < 6
        magic = [False] * 6
        for command in self.JobCommandAbility[:7]: # Skip divine ability
            key = command['AbilityName'].value
            mIdx = abilitySetData.getRow(key).magic
            if mIdx >= 0:
                magic[mIdx] = True
        return weapons + magic


class JobDB(DataTable):
    Row = Job

    def __init__(self):
        super().__init__('JobData.uasset')
        self.baseJobKeys = list(BASEJOBS.keys())
        self.advJobKeys = list(ADVJOBS.keys())

    def clearProperEquipmentWeapons(self):
        for jKey in self.baseJobKeys:
            row = self.table.getRow(jKey)
            row.ProperEquipment[:6] = [False] * 6

    def getProperEquipment(self, jKey):
        row = self.table.getRow(jKey)
        return row.ProperEquipment

    def getParameterRevision(self, jKey):
        row = self.table.getRow(jKey)
        return row.ParameterRevision

    def getSupportAbilities(self, jKey):
        row = self.table.getRow(jKey)
        return row.JobSupportAbility

    def getCommandAbilities(self, jKey):
        row = self.table.getRow(jKey)
        return row.JobCommandAbility

    def getPCWeapons(self, pc):
        key = PCNAMESMAP[pc]
        row = self.table.getRow(key)
        return row.ProperEquipment[:6]

    @property
    def agnea(self):
        return self.table.getRow('eDANCER')

    @property
    def castti(self):
        return self.table.getRow('eALCHEMIST')

    @property
    def hikari(self):
        return self.table.getRow('eFENCER')

    @property
    def partitio(self):
        return self.table.getRow('eMERCHANT')

    @property
    def ochette(self):
        return self.table.getRow('eHUNTER')

    @property
    def osvald(self):
        return self.table.getRow('ePROFESSOR')

    @property
    def temenos(self):
        return self.table.getRow('ePRIEST')

    @property
    def throne(self):
        return self.table.getRow('eTHIEF')
