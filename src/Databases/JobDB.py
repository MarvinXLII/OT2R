from DataTable import Table, Row
from Utility import JOBMAP, BASEJOBS, ADVJOBS, PCNAMESMAP
from Manager import Manager

class JobRow(Row):
    weapon_list = ['Sword', 'Lance', 'Dagger', 'Axe', 'Bow', 'Rod']

    @property
    def name(self):
        text_db = Manager.get_instance('GameTextEN').table
        return text_db.get_text(self.DisplayName)

    @property
    def equippable_weapons(self):
        return [self.weapon_list[i] for i, a in enumerate(self.ProperEquipment[:6]) if a]

    @property # List of ability sets
    def command_abilities(self):
        return [s['AbilityName'].value for s in self.JobCommandAbility]

    @property
    def support_abilities(self):
        return [s['AbilityName'].value for s in self.JobSupportAbility]

    @property
    def has_evasive_maneuvers(self):
        return 'ABI_SCH_SUP_01' in self.support_abilities

    def strengths(self):
        ability_set_db = Manager.get_instance('AbilitySetData').table
        weapons = self.ProperEquipment[:6]
        assert sum(weapons) < 6
        magic = [False] * 6
        for command in self.JobCommandAbility[:7]: # Skip divine ability
            key = command['AbilityName'].value
            ability = ability_set_db.get_row(key)
            if ability is None: continue
            m_idx = ability.magic
            if m_idx >= 0:
                magic[m_idx] = True
        return weapons + magic

    def __lt__(self, other):
        return self.key < other.key


class JobTable(Table):
    def __init__(self, data, row_class):
        super().__init__(data, row_class)
        self.base_job_keys = list(BASEJOBS.keys())
        self.adv_job_keys = list(ADVJOBS.keys())

    def clear_proper_equipment_weapons(self):
        for key in self.base_job_keys:
            row = self.get_row(key)
            row.ProperEquipment[:6] = [False] * 6
        for key in self.adv_job_keys:
            if key == 'eWEAPON_MASTER': continue
            row = self.get_row(key)
            row.ProperEquipment[:6] = [False] * 6

    def get_proper_equipment(self, key):
        row = self.get_row(key)
        return row.ProperEquipment

    def getParameterRevision(self, key):
        row = self.get_row(key)
        return row.ParameterRevision

    def get_support_abilities(self, key):
        row = self.get_row(key)
        return row.JobSupportAbility

    def get_command_abilities(self, key):
        row = self.get_row(key)
        return row.JobCommandAbility

    def get_pc_weapons(self, pc):
        key = PCNAMESMAP[pc]
        row = self.get_row(key)
        return row.ProperEquipment[:6]

    @property
    def agnea(self):
        return self.eDANCER

    @property
    def castti(self):
        return self.eALCHEMIST

    @property
    def hikari(self):
        return self.eFENCER

    @property
    def partitio(self):
        return self.eMERCHANT

    @property
    def ochette(self):
        return self.eHUNTER

    @property
    def osvald(self):
        return self.ePROFESSOR

    @property
    def temenos(self):
        return self.ePRIEST

    @property
    def throne(self):
        return self.eTHIEF

    @property
    def hikari_flashback(self):
        return self.eGUEST_JOB_008

    @property
    def crick(self):
        return self.eGUEST_JOB_003

    @property
    def gus(self):
        return self.eGUEST_JOB_004

    @property
    def emerald(self):
        return self.eGUEST_JOB_005

    @property
    def ritsu(self):
        return self.eGUEST_JOB_000

    @property
    def rai_mei(self):
        return self.eGUEST_JOB_001

    @property
    def pirro(self):
        return self.eGUEST_JOB_006

    @property
    def scaracci(self):
        return self.eGUEST_JOB_007
