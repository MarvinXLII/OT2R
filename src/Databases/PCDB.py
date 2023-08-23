from DataTable import Table, Row
from Manager import Manager
from Utility import JOBMAP, BASEJOBS, ADVJOBS

class PCRow(Row):
    @property
    def name(self):
        textDB = Manager.getInstance('GameTextEN').table
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


class PCTable(Table):
    def __init__(self, data, rowClass):
        super().__init__(data, rowClass)

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
        row = self.getRow(jKey)
        return row.FirstEquipment[eKey]

    def setFirstEquipment(self, jKey, eKey, equipment):
        row = self.getRow(jKey)
        row.FirstEquipment[eKey] = equipment

    def clearFirstEquipment(self):
        for jKey in self.baseJobKeys:
            row = self.getRow(jKey)
            row.FirstEquipment['Sword'] = 'None'
            row.FirstEquipment['Lance'] = 'None'
            row.FirstEquipment['Dagger'] = 'None'
            row.FirstEquipment['Axe'] = 'None'
            row.FirstEquipment['Bow'] = 'None'
            row.FirstEquipment['Rod'] = 'None'

    def getMainWeapon(self, jKey):
        row = self.getRow(jKey)
        return row.MainWeapon

    def setMainWeapon(self, jKey, weapon):
        row = self.getRow(jKey)
        row.MainWeapon = weapon

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
