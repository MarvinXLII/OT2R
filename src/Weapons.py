import random
from Manager import Manager

# The main thing is to shuffle weapon arrays for each job.
# Afterwards, each playable character's main weapon and initial weapons can be set.
class Weapons:
    def __init__(self):
        # PC for main weapon, first weapons
        self.pc_db = Manager.get_instance('PlayableCharacterDB').table
        # JobDB for weapons array
        self.job_db = Manager.get_instance('JobData').table
        self.base_keys = [
            'eFENCER', 'eHUNTER', 'eALCHEMIST', 'eMERCHANT',
            'ePRIEST', 'ePROFESSOR', 'eTHIEF', 'eDANCER',
        ]
        self.adv_keys = [
            # advanced jobs (except armsmaster)
            'eSHAMAN', 'eINVENTOR', 'eWIZARD',
        ]
        self.map_to_idx = {
            "EWEAPON_CATEGORY::eSWORD": 0,  # sword
            "EWEAPON_CATEGORY::eLANCE": 1,  # polearms
            "EWEAPON_CATEGORY::eDAGGER": 2, # dagger
            "EWEAPON_CATEGORY::eAXE": 3,    # axes
            "EWEAPON_CATEGORY::eBOW": 4,    # bows
            "EWEAPON_CATEGORY::eROD": 5,    # staffs
        }
        self.map_to_weapon = list(self.map_to_idx.keys())

    def run(self):
        self._shuffle_weapons()
        self._set_main_weapon()
        self._set_initial_weapons()
        self._set_pc_abilities()
        self._patch_animations()

    def _shuffle_weapons(self):
        candidates = list(self.map_to_idx.values()) * 3
        random.shuffle(candidates)

        self.job_db.clear_proper_equipment_weapons()

        job_keys = self.base_keys + self.adv_keys
        random.shuffle(job_keys)
        for i, key in enumerate(job_keys):
            array = self.job_db.get_proper_equipment(key)
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

    def _set_main_weapon(self):
        for key in self.base_keys:
            weapons = self.job_db.get_proper_equipment(key)[:6]
            i = random.choices(range(6), weapons, k=1)[0]
            self.pc_db.set_main_weapon(key, self.map_to_weapon[i])

    def _set_initial_weapons(self):
        self.pc_db.clear_first_equipment()
        for j_key in self.base_keys:
            weapon_array = self.job_db.get_proper_equipment(j_key)[:6]
            for e_key, w in zip(self.pc_db.equip_keys, weapon_array):
                if w:
                    weapon = random.sample(self.pc_db.first_equipment_candidates[e_key], 1)[0]
                    self.pc_db.set_first_equipment(j_key, e_key, weapon)

    def _set_pc_abilities(self):
        abil_set_db = Manager.get_instance('AbilitySetData').table

        def update_weapon_and_text(abil_set, job):
            abil_set.weapon = random.sample(job.equippable_weapons, 1)[0]
            abil_set.update_detail()
            abil_set.update_display()

        hikari = self.job_db.hikari
        update_weapon_and_text(abil_set_db.ABI_SET_WAR_210, hikari)
        update_weapon_and_text(abil_set_db.ABI_SET_WAR_211, hikari)
        update_weapon_and_text(abil_set_db.ABI_SET_WAR_220, hikari)
        update_weapon_and_text(abil_set_db.ABI_SET_WAR_221, hikari)
        # update_weapon_and_text(abil_set_db.ABI_SET_WAR_230, hikari) # Still operate without update
        # update_weapon_and_text(abil_set_db.ABI_SET_WAR_231, hikari)

    # Not perfect, but at least it's better than nothing
    def _patch_animations(self):
        flipbooks = Manager.get_table('CharactersFlipbookDB')
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
                row = flipbooks.get_row(f)
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
