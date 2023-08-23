from DataTable import Table, Row
from Manager import Manager
from Utility import JOBMAP, BASEJOBS, ADVJOBS

class PCRow(Row):
    @property
    def name(self):
        text_db = Manager.get_instance('GameTextEN').table
        return self.text_db.get_text(self.DisplayName)

    @property
    def job_name(self):
        return JOBMAP[self.key]

    @property
    def text_main_weapon(self):
        return self.MainWeapon.split('::e')[1].lower()

    @property
    def ex_skill_one(self):
        return self.AdvancedAbility[0]['AbilityID'].value

    @property
    def ex_skill_two(self):
        return self.AdvancedAbility[1]['AbilityID'].value


class PCTable(Table):
    def __init__(self, data, row_class):
        super().__init__(data, row_class)

        self.equip_keys = ['Sword', 'Lance', 'Dagger', 'Axe', 'Bow', 'Rod']
        self.base_job_keys = list(BASEJOBS.keys())
        self.adv_job_keys = list(ADVJOBS.keys())

        self.first_equipment_candidates = {e_key:[] for e_key in self.equip_keys}
        for j_key in self.base_job_keys:
            for e_key in self.equip_keys:
                e = self.get_first_equipment(j_key, e_key)
                if e != 'None':
                    self.first_equipment_candidates[e_key].append(e)

    def get_first_equipment(self, j_key, e_key):
        row = self.get_row(j_key)
        return row.FirstEquipment[e_key]

    def set_first_equipment(self, j_key, e_key, equipment):
        row = self.get_row(j_key)
        row.FirstEquipment[e_key] = equipment

    def clear_first_equipment(self):
        for j_key in self.base_job_keys:
            row = self.get_row(j_key)
            row.FirstEquipment['Sword'] = 'None'
            row.FirstEquipment['Lance'] = 'None'
            row.FirstEquipment['Dagger'] = 'None'
            row.FirstEquipment['Axe'] = 'None'
            row.FirstEquipment['Bow'] = 'None'
            row.FirstEquipment['Rod'] = 'None'

    def get_main_weapon(self, j_key):
        row = self.get_row(j_key)
        return row.MainWeapon

    def set_main_weapon(self, j_key, weapon):
        row = self.get_row(j_key)
        row.MainWeapon = weapon

    @property
    def agnea(self):
        return self.get_row('eDANCER')

    @property
    def castti(self):
        return self.get_row('eALCHEMIST')

    @property
    def hikari(self):
        return self.get_row('eFENCER')

    @property
    def partitio(self):
        return self.get_row('eMERCHANT')

    @property
    def ochette(self):
        return self.get_row('eHUNTER')

    @property
    def osvald(self):
        return self.get_row('ePROFESSOR')

    @property
    def temenos(self):
        return self.get_row('ePRIEST')

    @property
    def throne(self):
        return self.get_row('eTHIEF')
