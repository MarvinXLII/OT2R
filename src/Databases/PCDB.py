from Assets import Data
from DataTable import DataTable, Row
from Utility import JOBMAP, BASEJOBS, ADVJOBS

class PC(Row):
    @property
    def name(self):
        return self.textDB.getText(self.DisplayName)

    @property
    def jobName(self):
        return JOBMAP[self.key]

    @property
    def textMainWeapon(self):
        return self.MainWeapon.split('::e')[1].lower()

    @property
    def exSkillOne(self):
        return self.AdvancedAbility[0]['AbilityID'].value

    @property
    def exSkillTwo(self):
        return self.AdvancedAbility[1]['AbilityID'].value


class PCDB(DataTable):
    Row = PC

    def __init__(self):
        super().__init__('PlayableCharacterDB.uasset')

        self.equipKeys = ['Sword', 'Lance', 'Dagger', 'Axe', 'Bow', 'Rod']
        self.baseJobKeys = list(BASEJOBS.keys())
        self.advJobKeys = list(ADVJOBS.keys())

        self.firstEquipmentCandidates = {eKey:[] for eKey in self.equipKeys}
        for jKey in self.baseJobKeys:
            for eKey in self.equipKeys:
                e = self.getFirstEquipment(jKey, eKey)
                if e != 'None':
                    self.firstEquipmentCandidates[eKey].append(e)

    def getFirstEquipment(self, jKey, eKey):
        row = self.table.getRow(jKey)
        return row.FirstEquipment[eKey]

    def setFirstEquipment(self, jKey, eKey, equipment):
        row = self.table.getRow(jKey)
        row.FirstEquipment[eKey] = equipment

    def clearFirstEquipment(self):
        for jKey in self.baseJobKeys:
            row = self.table.getRow(jKey)
            for eKey in row.FirstEquipment:
                self.setFirstEquipment(jKey, eKey, 'None')

    def getMainWeapon(self, jKey):
        row = self.table.getRow(jKey)
        return row.MainWeapon

    def setMainWeapon(self, jKey, weapon):
        row = self.table.getRow(jKey)
        row.MainWeapon = weapon

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
