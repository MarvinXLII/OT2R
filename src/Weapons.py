import random
from Manager import Manager

# The main thing is to shuffle weapon arrays for each job.
# Afterwards, each playable character's main weapon and initial weapons can be set.
class Weapons:
    def __init__(self):
        # PC for main weapon, first weapons
        self.pcTable = Manager.getInstance('PlayableCharacterDB').table
        # JobDB for weapons array
        self.jobTable = Manager.getInstance('JobData').table
        self.baseKeys = [
            'eFENCER', 'eHUNTER', 'eALCHEMIST', 'eMERCHANT',
            'ePRIEST', 'ePROFESSOR', 'eTHIEF', 'eDANCER',
        ]
        self.advKeys = [
            # advanced jobs (except armsmaster)
            'eSHAMAN', 'eINVENTOR', 'eWIZARD',
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
        candidates = list(self.mapToIdx.values()) * 3
        random.shuffle(candidates)

        self.jobTable.clearProperEquipmentWeapons()

        jobKeys = self.baseKeys + self.advKeys
        random.shuffle(jobKeys)
        for i, jKey in enumerate(jobKeys):
            array = self.jobTable.getProperEquipment(jKey)
            idx = candidates.pop()
            array[idx] = True
            # 7 jobs get a second weapon
            # 4 jobs stuck with one weapon
            if i < 7:
                j = 0
                while array[candidates[j]]:
                    j += 1
                idx = candidates.pop(j)
                array[idx] = True
        assert not candidates

    def _setMainWeapon(self):
        for jKey in self.baseKeys:
            weapons = self.jobTable.getProperEquipment(jKey)[:6]
            i = random.choices(range(6), weapons, k=1)[0]
            self.pcTable.setMainWeapon(jKey, self.mapToWeapon[i])

    def _setInitialWeapons(self):
        self.pcTable.clearFirstEquipment()
        for jKey in self.baseKeys:
            weaponArray = self.jobTable.getProperEquipment(jKey)[:6]
            for eKey, w in zip(self.pcTable.equipKeys, weaponArray):
                if w:
                    weapon = random.sample(self.pcTable.firstEquipmentCandidates[eKey], 1)[0]
                    self.pcTable.setFirstEquipment(jKey, eKey, weapon)

    def _setPCAbilities(self):
        abilSetDB = Manager.getInstance('AbilitySetData').table

        def updateWeaponAndText(abilSet, job):
            abilSet.weapon = random.sample(job.equippableWeapons, 1)[0]
            abilSet.updateDetail()
            abilSet.updateDisplay()

        hikari = self.jobTable.hikari
        updateWeaponAndText(abilSetDB.ABI_SET_WAR_210, hikari)
        updateWeaponAndText(abilSetDB.ABI_SET_WAR_211, hikari)
        updateWeaponAndText(abilSetDB.ABI_SET_WAR_220, hikari)
        updateWeaponAndText(abilSetDB.ABI_SET_WAR_221, hikari)
        # updateWeaponAndText(abilSetDB.ABI_SET_WAR_230, hikari) # Still operate without update
        # updateWeaponAndText(abilSetDB.ABI_SET_WAR_231, hikari)

    # Not perfect, but at least it's better than nothing
    def _patchAnimations(self):
        flipbooks = Manager.getTable('CharactersFlipbookDB')
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
