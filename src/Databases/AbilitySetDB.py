from Manager import Manager
from DataTable import Table, Row
import random
import sys

class AbilitySetRow(Row):
    weapon_to_rw = {
        'sword': 'sword',
        'dagger': 'dagger',
        'lance': 'polearm',
        'axe': 'axe',
        'bow': 'bow',
        'rod': 'staff'
    }

    def __init__(self, *args):
        super().__init__(*args)

        ability_db = Manager.get_instance('AbilityData').table
        text_db = Manager.get_instance('GameTextEN').table
        
        self.boost_levels = []
        for b in [self.NoBoost, self.BoostLv1, self.BoostLv2, self.BoostLv3]:
            ab = ability_db.get_row(b)
            if ab:
                self.boost_levels.append(ab)
        self.vanilla_weapon = self.weapon
        self.uses_weapon = self.vanilla_weapon != ''
        self.detail = [text_db.get_row(b.Detail) for b in self.boost_levels]
        self.display_name = [text_db.get_row(b.DisplayName) for b in self.boost_levels]

    @property
    def name(self):
        return self.display_name[-1].Text

    @property
    def sp_cost(self): # Only return the last value, important for Divine abilities
        if self.boost_levels:
            return self.boost_levels[-1].CostValue

    @sp_cost.setter
    def sp_cost(self, cost):
        for b in self.boost_levels:
            # if b.CostValue: # skip anything that's 0 by default, e.g. Divine abilities
            #     b.CostValue = cost
            b.CostValue = cost

    @property
    def does_cost_sp(self):
        if self.boost_levels:
            return self.boost_levels[0].cost_sp
        return False

    @property
    def ability_ratio(self):
        if self.boost_levels:
            return self.boost_levels[-1].AbilityRatio

    def scale_ability_ratio(self, scale):
        for b in self.boost_levels:
            if b.is_attack or b.is_heal:
                b.AbilityRatio = int(b.AbilityRatio * scale)

    @property
    def weapon(self):
        if self.boost_levels:
            return self.boost_levels[-1].weapon

    @weapon.setter
    def weapon(self, new_weapon):
        for b in self.boost_levels:
            b.weapon = new_weapon

    @property
    def magic(self):
        attribute = self.boost_levels[-1].Attribute
        if attribute == 'EATTRIBUTE_TYPE::eFIRE':
            return 0
        if attribute == 'EATTRIBUTE_TYPE::eICE':
            return 1
        if attribute == 'EATTRIBUTE_TYPE::eTHUNDER':
            return 2
        if attribute == 'EATTRIBUTE_TYPE::eWIND':
            return 3
        if attribute == 'EATTRIBUTE_TYPE::eLIGHT':
            return 4
        if attribute == 'EATTRIBUTE_TYPE::eDARK':
            return 5
        assert attribute == 'EATTRIBUTE_TYPE::eNONE'
        return -1

    def make_arms_master(self):
        if self.weapon == 'sword':
            self.RestrictWeaponLabel = 'ITM_EQP_SWD_990'
        elif self.weapon == 'lance':
            self.RestrictWeaponLabel = 'ITM_EQP_LNS_990'
        elif self.weapon == 'dagger':
            self.RestrictWeaponLabel = 'ITM_EQP_DGR_990'
        elif self.weapon == 'axe':
            self.RestrictWeaponLabel = 'ITM_EQP_AXE_990'
        elif self.weapon == 'bow':
            self.RestrictWeaponLabel = 'ITM_EQP_BOW_990'
        elif self.weapon == 'rod':
            self.RestrictWeaponLabel = 'ITM_EQP_ROD_990'
        else:
            sys.exit(f'Cannot make the ability set an Armsmaster; weapon is {self.weapon}')

    def make_not_arms_master(self):
        self.RestrictWeaponLabel = 'None'

    def make_inventor(self):
        # TODO: make formula/json file for inventorTurns; random choices 1-3 can be too small
        self.InventorTurn = random.choices([1, 2, 3], [60, 30, 10], k=1)[0]
        self.MenuType = 'ECOMMAND_MENU_TYPE::eINVENTOR_ITEM'
        self.sp_cost = 0
        for ability in self.boost_levels:
            ability.make_inventor()

    def make_not_inventor(self):
        self.InventorTurn = 0
        self.MenuType = 'ECOMMAND_MENU_TYPE::eCOMMAND'
        self.sp_cost = 5 * random.randint(3, 6)  # 15 - 30
        assert self.sp_cost > 0
        for ability in self.boost_levels:
            ability.make_not_inventor()

    def update_detail(self):
        self._update_text(self.detail)

    def update_display(self):
        self._update_text(self.display_name)

    def _update_text(self, lst):
        if self.vanilla_weapon == self.weapon:
            return '', ''
        v  = self.weapon_to_rw[self.vanilla_weapon]
        vu = v.capitalize()
        w = self.weapon_to_rw[self.weapon]
        wu = w.capitalize()
        s = ''
        n = ''
        for x in [' ', 's ', ': ', 's: ']:
            if lst[-1].in_string(f'{v}{x}'):
                s = f'{v}{x}'
                n = f'{w}{x}'
                break
            elif lst[-1].in_string(f'{vu}{x}'):
                s = f'{vu}{x}'
                n = f'{wu}{x}'
                break
            if x != ' ':
                continue
            if lst[-1].in_string(f'{x}{v}'):
                s = f'{x}{v}'
                n = f'{x}{w}'
                break
            elif lst[-1].in_string(f'{x}{vu}'):
                s = f'{x}{vu}'
                n = f'{x}{wu}'
                break

        if not s and v == 'polearm' and 'Spear' in lst[0].Text:
            s = 'Spear'
            n = f'{wu}'

        if not s:
            return

        if s == n:
            return

        for l in lst:
            l.replace_substring(s, n)

        if 'axe' in n:
            for l in lst:
                l.replace_substring('a axe', 'an axe')


class AbilitySetTable(Table):

    def __init__(self, data, row_class):
        super().__init__(data, row_class)

        job_db = Manager.get_instance('JobData')
        pc_db = Manager.get_instance('PlayableCharacterDB')

        # List of all ability sets on jobs (and pc for advanced abilities)
        # Need both for power scaling.
        # Where they come from does not matter for this.
        # It does matter for shuffling command abilities.
        self.job_ability_sets = []

        for job in job_db.table:
            if job.ID >= 12: break
            for abil_set in job.JobCommandAbility:
                row = getattr(self, abil_set['AbilityName'].value)
                self.job_ability_sets.append(row)

        for pc in pc_db.table:
            if pc.Id > 8: break
            for abil_set in pc.AdvancedAbility:
                row = getattr(self, abil_set['AbilityID'].value)
                self.job_ability_sets.append(row)
