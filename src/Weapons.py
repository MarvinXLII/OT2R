import random
from Assets import Data
from DataTable import DataTable

# The main thing is to shuffle weapon arrays for each job.
# Afterwards, each playable character's main weapon and initial weapons can be set.
class Weapons:
    def __init__(self):
        # PC for main weapon, first weapons
        self.pcDB = Data.getInstance('PlayableCharacterDB')
        # JobDB for weapons array
        self.jobDB = Data.getInstance('JobData')
        self.jobKeys = [
            'eFENCER', 'eHUNTER', 'eALCHEMIST', 'eMERCHANT',
            'ePRIEST', 'ePROFESSOR', 'eTHIEF', 'eDANCER',
            # omitting advanced jobs....
        ]
        self.mapToIdx = {
            "EWEAPON_CATEGORY::eSWORD": 0,  # sword
            "EWEAPON_CATEGORY::eLANCE": 1,  # polearms
            "EWEAPON_CATEGORY::eDAGGER": 2, # dagger
            "EWEAPON_CATEGORY::eAXE": 3,    # axes
            "EWEAPON_CATEGORY::eBOW": 4,    # bows
            "EWEAPON_CATEGORY::eROD": 5,    # staffs
        }
        self.mapToWeapon = list(self.mapToIdx.keys())

    def run(self):
        self._shuffleWeapons()
        self._setMainWeapon()
        self._setInitialWeapons()
        self._setPCAbilities()
        self._patchAnimations()

    def _shuffleWeapons(self):
        candidates = list(self.mapToIdx.values()) * 2
        random.shuffle(candidates)

        self.jobDB.clearProperEquipmentWeapons()

        # TODO: add advanced jobs; presumably keep all 6 weapons on the Armsmaster
        random.shuffle(self.jobKeys) # Ensure a random set of 4 PCs get 2 weapons
        for i, jKey in enumerate(self.jobKeys):
            array = self.jobDB.getProperEquipment(jKey)
            idx = candidates.pop()
            array[idx] = True
            # Four PCs get a second weapon
            if i < 4:
                j = 0
                while array[candidates[j]]:
                    j += 1
                idx = candidates.pop(j)
                array[idx] = True
        assert not candidates

    def _setMainWeapon(self):
        for jKey in self.jobKeys:
            weapons = self.jobDB.getProperEquipment(jKey)[:6]
            i = random.choices(range(6), weapons, k=1)[0]
            self.pcDB.setMainWeapon(jKey, self.mapToWeapon[i])

    def _setInitialWeapons(self):
        self.pcDB.clearFirstEquipment()
        for jKey in self.jobKeys:
            weaponArray = self.jobDB.getProperEquipment(jKey)[:6]
            for eKey, w in zip(self.pcDB.equipKeys, weaponArray):
                if w:
                    weapon = random.sample(self.pcDB.firstEquipmentCandidates[eKey], 1)[0]
                    self.pcDB.setFirstEquipment(jKey, eKey, weapon)

    def _setPCAbilities(self):
        abilSetDB = Data.getInstance('AbilitySetData').table

        def updateWeaponAndText(abilSet, job):
            abilSet.weapon = random.sample(job.equippableWeapons, 1)[0]
            abilSet.updateDetail()
            abilSet.updateDisplay()

        hikari = self.jobDB.hikari
        updateWeaponAndText(abilSetDB.ABI_SET_WAR_210, hikari)
        updateWeaponAndText(abilSetDB.ABI_SET_WAR_211, hikari)
        updateWeaponAndText(abilSetDB.ABI_SET_WAR_220, hikari)
        updateWeaponAndText(abilSetDB.ABI_SET_WAR_221, hikari)
        # updateWeaponAndText(abilSetDB.ABI_SET_WAR_230, hikari) # Still operate without update
        # updateWeaponAndText(abilSetDB.ABI_SET_WAR_231, hikari)

    # Not perfect, but at least it's better than nothing
    def _patchAnimations(self):
        flipbooks = DataTable.getInstance('CharactersFlipbookDB').table
        pcs = {
            'KenJ0XX_Mle': 0, # Hikari -- Sword
            'KusJ0XX_Fml': 3, # Castti -- Axe
            'TouJ0XX_Fml': 2, # Throne -- Dagger
            'GakJ0XX_Mlb': 5, # Osvald -- Staff
            'SinJ0XX_Mle': 5, # Temenos -- Staff
            'KarJ0XX_Fml': 4, # Ochette -- Bow
            'ShoJ0XX_Mle': 1, # Partitio -- Lance
            'OdoJ0XX_Fml': 2, # Agnea -- Dagger
            'KenE0XX_Mle': 0, # Hikari -- Sword
            'KusE0XX_Fml': 3, # Castti -- Axe
            'TouE0XX_Fml': 2, # Throne -- Dagger
            'GakE0XX_Mlb': 5, # Osvald -- Staff
            'SinE0XX_Mle': 5, # Temenos -- Staff
            'KarE0XX_Fml': 4, # Ochette -- Bow
            'ShoE0XX_Mle': 1, # Partitio -- Lance
            'OdoE0XX_Fml': 2, # Agnea -- Dagger
        }
        for pc, index in pcs.items():
            for i in range(0, 13):
                j = str(i).rjust(2, '0')
                f = pc.replace('XX', j)
                row = flipbooks.getRow(f)
                if row is None: continue
                for k, x in enumerate(row.FlipbookNames):
                    if x == 'None':
                        if k >= 421 and k < 421+6:
                            row.FlipbookNames[k] = row.FlipbookNames[421+index]
                        # if k >= 428 and k < 428+6:
                        #     row.FlipbookNames[k] = row.FlipbookNames[428+index]
                        if k >= 543 and k < 543+12:
                            row.FlipbookNames[k] = row.FlipbookNames[543+2*index]
                            row.FlipbookNames[k+1] = row.FlipbookNames[543+2*index+1]
