from Assets import Data
from DataTable import DataTable, Table, Row
import random
import sys

class AbilitySet(Row):
    weaponToRW = {
        'sword': 'sword',
        'dagger': 'dagger',
        'lance': 'polearm',
        'axe': 'axe',
        'bow': 'bow',
        'rod': 'staff'
    }

    # def __init__(self, abilitySet):
    def __init__(self, *args):
        super().__init__(*args)
        gameText = Data.getInstance('GameTextEN')
        self.abilityDB = Data.getInstance('AbilityData')
        self.boostLevels = []
        for b in [self.NoBoost, self.BoostLv1, self.BoostLv2, self.BoostLv3]:
            ab = self.abilityDB.table.getRow(b)
            if ab:
                self.boostLevels.append(ab)
        self.vanillaWeapon = self.weapon
        self.usesWeapon = self.vanillaWeapon != ''
        self.detail = [gameText.table.getRow(b.Detail) for b in self.boostLevels]
        self.displayName = [gameText.table.getRow(b.DisplayName) for b in self.boostLevels]

    @property
    def name(self):
        return self.displayName[-1].Text

    @property
    def spCost(self): # Only return the last value, important for Divine abilities
        if self.boostLevels:
            return self.boostLevels[-1].CostValue

    @spCost.setter
    def spCost(self, cost):
        for b in self.boostLevels:
            # if b.CostValue: # skip anything that's 0 by default, e.g. Divine abilities
            #     b.CostValue = cost
            b.CostValue = cost

    @property
    def doesCostSP(self):
        if self.boostLevels:
            return self.boostLevels[0].costSP
        return False

    @property
    def abilityRatio(self):
        if self.boostLevels:
            return self.boostLevels[-1].AbilityRatio

    def scaleAbilityRatio(self, scale):
        for b in self.boostLevels:
            if b.isAttack or b.isHeal:
                b.AbilityRatio = int(b.AbilityRatio * scale)

    @property
    def weapon(self):
        if self.boostLevels:
            if self.boostLevels[0].weapon != self.boostLevels[-1].weapon:
                print("Weapons differ:", self.boostLevels[0].weapon, self.boostLevels[-1].weapon)
            return self.boostLevels[0].weapon

    @weapon.setter
    def weapon(self, newWeapon):
        for b in self.boostLevels:
            b.weapon = newWeapon

    @property
    def magic(self):
        attribute = self.boostLevels[-1].Attribute
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

    def makeArmsMaster(self):
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

    def makeNotArmsMaster(self):
        self.RestrictWeaponLabel = 'None'

    def makeInventor(self):
        self.InventorTurn = random.choices([1, 2, 3], [60, 30, 10], k=1)[0]
        self.MenuType = 'ECOMMAND_MENU_TYPE::eINVENTOR_ITEM'
        for ability in self.boostLevels:
            ability.makeInventor()

    def makeNotInventor(self):
        self.InventorTurn = 0
        self.MenuType = 'ECOMMAND_MENU_TYPE::eCOMMAND'
        self.spCost = 5 * random.randint(3, 6)  # 15 - 30
        for ability in self.boostLevels:
            ability.makeNotInventor()

    def updateDetail(self):
        self._updateText(self.detail)

    def updateDisplay(self):
        self._updateText(self.displayName)

    def _updateText(self, lst):
        if self.vanillaWeapon == self.weapon:
            return '', ''
        v  = AbilitySet.weaponToRW[self.vanillaWeapon]
        vu = v.capitalize()
        w = AbilitySet.weaponToRW[self.weapon]
        wu = self.weapon.capitalize()
        s = ''
        n = ''
        for x in [' ', 's ', ': ', 's: ']:
            if lst[0].inString(f'{v}{x}'):
                s = f'{v}{x}'
                n = f'{w}{x}'
                break
            elif lst[0].inString(f'{vu}{x}'):
                s = f'{vu}{x}'
                n = f'{wu}{x}'
                break
            if x != ' ':
                continue
            if lst[0].inString(f'{x}{v}'):
                s = f'{x}{v}'
                n = f'{x}{w}'
                break
            elif lst[0].inString(f'{x}{vu}'):
                s = f'{x}{vu}'
                n = f'{x}{wu}'
                break

        if not s and v == 'polearm' and 'Spear' in lst[0].Text:
            s = 'Spear'
            n = f'{wu}'

        if not s:
            # print('Nothing to replace in ')
            # print('    ', lst[0].TextDB)
            # print('    ', v, ' <-- ', w)
            return

        if s == n:
            return
        for l in lst:
            l.replaceSubstring(s, n)


class AbilitySetDB(DataTable):
    Row = AbilitySet
    def __init__(self):
        super().__init__('AbilitySetData.uasset')
        jobDB = Data.getInstance('JobData')
        pcDB = Data.getInstance('PlayableCharacterDB')

        # List of all ability sets on jobs (and pc for advanced abilities)
        # Need both for power scaling.
        # Where they come from does not matter for this.
        # It does matter for shuffling command abilities.
        self.jobAbilitySets = []

        for job in jobDB.table:
            if job.ID >= 12: break
            for abilSet in job.JobCommandAbility:
                # row = self.table.getRow(abilSet['AbilityName'].value)
                row = getattr(self.table, abilSet['AbilityName'].value)
                self.jobAbilitySets.append(row)

        for pc in pcDB.table:
            if pc.Id > 8: break
            for abilSet in pc.AdvancedAbility:
                # row = self.table.getRow(abilSet['AbilityID'].value)
                row = getattr(self.table, abilSet['AbilityID'].value)
                self.jobAbilitySets.append(row)
