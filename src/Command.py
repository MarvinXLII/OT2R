import random
from Utility import WEAPONS, get_filename
from Shuffler import Shuffler, Slot, no_weights
from Manager import Manager
import hjson

def check_weapon(w, s, c):
    for i, si in enumerate(s):
        if c.depend_weapon:
            w[i] *= c.restrict_weapon in si.job_weapons


def separate_advanced_commands(w, s, c):
    for i, si in enumerate(s):
        w[i] *= c.is_advanced == si.is_advanced


def separate_divine(w, s, c):
    for i, si in enumerate(s):
        w[i] *= c.is_divine_ability == si.is_divine_ability


def separate_ex_abilities(w, s, c):
    for i, si in enumerate(s):
        w[i] *= c.is_ex_ability == si.is_ex_ability


def skip_slot(w, s, c):
    for i, si in enumerate(s):
        w[i] *= not si.skip


# Single slot
def inventor_weights(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.is_inventor_valid

def inventor_check_weapon(w, c, s):
    for i, ci in enumerate(c):
        if ci.depend_weapon:
            w[i] *= ci.restrict_weapon in s.job_weapons

# Single slot
def sword_attacks(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.restrict_weapon == 'EWEAPON_CATEGORY::eSWORD'

def spear_attacks(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.restrict_weapon == 'EWEAPON_CATEGORY::eLANCE'

def dagger_attacks(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.restrict_weapon == 'EWEAPON_CATEGORY::eDAGGER'

def axe_attacks(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.restrict_weapon == 'EWEAPON_CATEGORY::eAXE'

def bow_attacks(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.restrict_weapon == 'EWEAPON_CATEGORY::eBOW'

def staff_attacks(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.restrict_weapon == 'EWEAPON_CATEGORY::eROD'



class AbilitySlot(Slot):
    weights = hjson.load(open(get_filename('json/weightsAbilitySet.json'), 'r', encoding='utf-8'))


# TODO: Clean this up!!!
class Ability(AbilitySlot):
    def __init__(self, job, index, slot_index):
        # Data needed afterwards for updating
        self.index = index
        self.job = job
        self.slot_index = slot_index

        # Data needed for shuffling
        self.ability_set = job.JobCommandAbility[index]
        self.ability_name = self.ability_set['AbilityName'].value
        ability_set_obj = Manager.get_instance('AbilitySetData').table.get_row(self.ability_name)
    
        self.is_advanced = self.job.ID >= 8
        self.is_ex_ability = False
        self.is_arms_master = '_WPM_' in self.ability_name and ability_set_obj.RestrictWeaponLabel != 'None'
        self.is_inventor = '_INV_' in self.ability_name
        self.is_inventor_valid = self.weights[self.ability_name]['is_inventor_valid']
        self.has_magic_label = self.weights[self.ability_name]['has_magic_label']
        self.skip = self.weights[self.ability_name]['skip']
        self.initialize()


    def initialize(self):
        assert self.ability_name != 'None'
        # Job data needed for weights
        # (Maybe separate slot and candidate objects?)
        self.job_weapons = []
        for i, equippable in enumerate(self.job.ProperEquipment[:6]):
            if equippable:
                self.job_weapons.append(WEAPONS[i])

        # Data needed for generating weights
        # TODO: might need to store some of this in spreadsheet and load
        # e.g. weapon, element, divine, 1-2 slot allowed
        # Probably best to ignore 1-2 slot allowed for now.
        # Should be able to separate divine and advanced job
        ability_db = Manager.get_instance('AbilityData')
        ability_set_db = Manager.get_instance('AbilitySetData')
        abl_set = ability_set_db.table.get_row(self.ability_name)
        ability = ability_db.table.get_row(abl_set.BoostLv3) # Lv3 used for divine ability weapon dependency
        self.is_divine_ability = abl_set.IsDivineAbility
        self.depend_weapon = ability.DependWeapon
        self.restrict_weapon = ability.RestrictWeapon # weapon used if physical, otherwise none
        if self.restrict_weapon != 'EWEAPON_CATEGORY::eNONE':
            assert self.restrict_weapon in WEAPONS, self.restrict_weapon
        self.attribute = ability.Attribute # element type if magic, none otherwise

    def copy(self, other):
        self.ability_name = other.ability_name

    # Probably won't need all of this thanks to copy!
    def patch(self):
        if self.index < 2:
            param = 1
        elif self.index == 7:
            param = 2
        else:
            param = 0
        self.ability_set['GetParam'].value = param
        self.ability_set['AbilityName'].value = self.ability_name
        self.job.JobCommandAbility[self.index] = self.ability_set


class ExAbility(Ability):
    def __init__(self, pc, job, index, slot_index):
        # Data needed afterwards for updating 
        self.index = index
        self.job = job
        self.pc = pc
        self.slot_index = slot_index

        # Data needed for shuffling
        self.ability_set = pc.AdvancedAbility[index]
        self.ability_name = self.ability_set['AbilityID'].value
        self.is_advanced = False
        self.is_ex_ability = True
        self.is_inventor = False
        self.is_arms_master = False
        self.is_inventor_valid = self.weights[self.ability_name]['is_inventor_valid']
        self.has_magic_label = self.weights[self.ability_name]['has_magic_label']
        self.skip = self.weights[self.ability_name]['skip']
        self.initialize()

    def patch(self):
        assert self.ability_name != 'None'
        self.ability_set['AbilityID'].value = self.ability_name
        self.pc.AdvancedAbility[self.index] = self.ability_set

# Hardly inherits anything...lol.
class Command(Shuffler):
    check_advanced = no_weights
    check_divine = no_weights
    check_ex_ability = no_weights
    
    def __init__(self):
        self.job_db = Manager.get_instance('JobData').table
        self.pc_db = Manager.get_instance('PlayableCharacterDB').table
        self.gametext_db = Manager.get_instance('GameTextEN').table
        self.ability_set_db = Manager.get_instance('AbilitySetData').table

        self.slots = []
        self.candidates = []

        # Main 8 abilities from the jobs
        job_map = {}
        for job in self.job_db:
            if job.ID >= 12: break
            job_map[job.key] = job
            for index, ability_set in enumerate(job.JobCommandAbility):
                slot = Ability(job, index, len(self.slots))
                candidate = Ability(job, index, len(self.candidates))
                self.slots.append(slot)
                self.candidates.append(candidate)

        # Ex Abilities
        for pc in self.pc_db:
            if pc.Id > 8: break
            for index, ability_set in enumerate(pc.AdvancedAbility):
                job = job_map[pc.FirstJob.split('::')[1]]
                slot = ExAbility(pc, job, index, len(self.slots))
                candidate = ExAbility(pc, job, index, len(self.candidates))
                self.slots.append(slot)
                self.candidates.append(candidate)

        # Other stuff to be used for shuffling
        self.vacant = None
        self.weights = None
        self.used = None

    def run(self):
        self.vacant = [True] * len(self.slots)
        self.unused = [True] * len(self.candidates)
        self.prepare()

        # Fill Armsmaster skills
        # Fills a specific slot with a random candidate
        self.random_candidate('ABI_SET_WPM_010', sword_attacks)
        self.random_candidate('ABI_SET_WPM_020', spear_attacks)
        self.random_candidate('ABI_SET_WPM_030', dagger_attacks)
        self.random_candidate('ABI_SET_WPM_040', axe_attacks)
        self.random_candidate('ABI_SET_WPM_050', bow_attacks)
        self.random_candidate('ABI_SET_WPM_060', staff_attacks)

        # Fill Advanced Magic
        # Chooses a random slot for a specific candidate
        # Slots must belong to a job with at least 3 vacant slots
        self.random_job_with_magic('ABI_SET_SCH_070') # Advanced Magic
        self.random_job_with_magic('ABI_SET_SCH_090') # Alephan's Wisdom

        # Fill Inventor
        # All are ok if filled by Magic/Advanced Magic/Alephan's Wisdom
        self.random_candidate('ABI_SET_INV_010', inventor_weights, inventor_check_weapon, ok_if_filled=True)
        self.random_candidate('ABI_SET_INV_020', inventor_weights, inventor_check_weapon, ok_if_filled=True)
        self.random_candidate('ABI_SET_INV_030', inventor_weights, inventor_check_weapon, ok_if_filled=True)
        self.random_candidate('ABI_SET_INV_040', inventor_weights, inventor_check_weapon, ok_if_filled=True)
        self.random_candidate('ABI_SET_INV_050', inventor_weights, inventor_check_weapon, ok_if_filled=True)
        self.random_candidate('ABI_SET_INV_060', inventor_weights, inventor_check_weapon, ok_if_filled=True)
        self.random_candidate('ABI_SET_INV_070', inventor_weights, inventor_check_weapon, ok_if_filled=True)

        # Finally do everything else
        self.generate_weights()
        self.sampler()

        # Confirm done
        self.check_done()

        # Finalize Armsmaster and Inventor, then patch
        self.finish()

    def generate_weights(self, *args):
        super().generate_weights(check_weapon, Command.check_advanced, Command.check_divine, Command.check_ex_ability, *args)

    def check_done(self):
        assert sum(self.vacant) == 0
        assert sum(self.unused) == 0

    def sampler(self):
        # Sort candidates by number of allowed slots
        # Ensure most restrictive candidates get used first
        swc = list(zip(self.weights, self.candidates))
        random.shuffle(swc) # Ensure ties are randomly broken
        swc.sort(key=lambda x: sum(x[0]))

        idx = list(range(len(self.slots)))
        for slot_weights, candidate in swc:
            c_idx = candidate.slot_index
            if not self.unused[c_idx]: continue # If candidate is used, skip
            swv = [s * v for s, v in zip(slot_weights, self.vacant)]
            assert sum(swv) > 0
            s_idx = random.choices(idx, swv, k=1)[0]
            self.slots[s_idx].copy(candidate)
            self.vacant[s_idx] = False
            self.unused[c_idx] = False

    def random_job_with_magic(self, cand_abil_set_name, *args):
        idx = list(range(len(self.vacant)))
        while True:
            i = random.choices(idx, self.vacant, k=1)[0]
            slot = self.slots[i]
            job = slot.job.key
            slot_index = []
            for s in self.slots:
                if s.job.key == job:
                    if self.vacant[s.slot_index]:
                        slot_index.append(s.slot_index)
            if len(slot_index) >= 3:
                break

        # Pick a slot and fill it with the candidate
        for c_idx, c in enumerate(self.candidates):
            if c.ability_name == cand_abil_set_name:
                break
        else:
            sys.exit(f'{cand_abil_set_name} not found in candidates!')
        assert self.unused[c_idx] == True, c_idx
        self.unused[c_idx] = False
        s_idx = random.choices(slot_index, k=1)[0]
        slot_index.remove(s_idx)
        slot = self.slots[s_idx]
        slot.copy(self.candidates[c_idx])
        assert self.vacant[s_idx] == True, s_idx
        self.vacant[s_idx] = False

        # Filter candidates that do appropriate magic
        candidates = []
        for c_idx, ci in enumerate(self.candidates):
            if ci.has_magic_label and self.unused[c_idx]:
                candidates.append((c_idx, ci))

        # Pick 2 of them and fill those 2 available slots
        random.shuffle(candidates)
        c_idx1, cand1 = candidates[0]
        c_idx2, cand2 = candidates[1]
        random.shuffle(slot_index)
        s_idx1 = slot_index[0]
        s_idx2 = slot_index[1]

        assert self.unused[c_idx1] == True, c_idx1
        assert self.unused[c_idx2] == True, c_idx2
        assert self.vacant[s_idx1] == True, s_idx1
        assert self.vacant[s_idx2] == True, s_idx2

        self.slots[s_idx1].copy(cand1)
        self.slots[s_idx2].copy(cand2)
        self.unused[c_idx1] = False
        self.unused[c_idx2] = False
        self.vacant[s_idx1] = False
        self.vacant[s_idx2] = False

    def random_vacant_slot(self, cand_abil_set_name, *args):
        for c_idx, c in enumerate(self.candidates):
            if c.ability_name == cand_abil_set_name:
                break
        else:
            sys.exit(f"{cand_abil_set_name} is not a valid candidate name")
        assert self.unused[c_idx] == True, c_idx
        self.unused[c_idx] = False, c_idx

        candidate = self.candidates[c_idx]
        weights = [v for v in self.vacant]
        for f in args:
            f(weights, self.slots, candidate)

        idx = list(range(len(self.slots)))
        s_idx = random.choices(idx, weights, k=1)[0]
        self.slots[s_idx].copy(candidate)
        self.vacant[s_idx] = False

    def random_candidate(self, slot_abil_set_name, *args, ok_if_filled=False):
        # Loop over candidates here.
        # Slot ability_names will get overwritten during shuffling.
        # This assumes candidates and slots are in the same order!
        for s_idx, c in enumerate(self.candidates):
            if c.ability_name == slot_abil_set_name:
                break
        else:
            sys.exit(f"{slot_abil_set_name} is not a valid slot name")
        if ok_if_filled:
            if not self.vacant[s_idx]:
                return
        else:
            assert self.vacant[s_idx] == True, s_idx
        self.vacant[s_idx] = False

        slot = self.slots[s_idx]
        weights = [u for u in self.unused]
        for f in args:
            f(weights, self.candidates, slot)

        idx = list(range(len(self.candidates)))
        c_idx = random.choices(idx, weights, k=1)[0]
        slot.copy(self.candidates[c_idx])
        self.unused[c_idx] = False

    def prepare(self):
        for slot in self.slots:
            abil_set = self.ability_set_db.get_row(slot.ability_name)
            if slot.is_inventor:
                abil_set.make_not_inventor()
                if abil_set.SuperMagicLabel != 'None':
                    a = self.ability_set_db.get_row(abil_set.SuperMagicLabel)
                    a.make_not_inventor()
                if abil_set.HyperMagicLabel != 'None':
                    a = self.ability_set_db.get_row(abil_set.HyperMagicLabel)
                    a.make_not_inventor()

            elif slot.is_arms_master:
                abil_set.make_not_arms_master()

        # Don't allow All-Purpose Tool to change slots
        for s, c in zip(self.slots, self.candidates):
            if s.skip:
                assert c.skip
                assert s.ability_name == c.ability_name
                self.unused[c.slot_index] = False # Set candidate to having been used
                self.vacant[s.slot_index] = False # Set slot to be occupied

    def finish(self):
        for slot in self.slots:
            abil_set = self.ability_set_db.get_row(slot.ability_name)

            if slot.is_inventor:
                abil_set.make_inventor()
                if abil_set.SuperMagicLabel != 'None':
                    a = self.ability_set_db.get_row(abil_set.SuperMagicLabel)
                    a.make_inventor()
                if abil_set.HyperMagicLabel != 'None':
                    a = self.ability_set_db.get_row(abil_set.HyperMagicLabel)
                    a.make_inventor()

            elif slot.is_arms_master:
                abil_set.make_arms_master()

        # Finish here; the rest is easier that way
        super().finish()

        # Update text for Ex Abilities
        def get_names(pc):
            es1 = self.ability_set_db.get_row(pc.ex_skill_one).name
            es2 = self.ability_set_db.get_row(pc.ex_skill_two).name
            return es2, es1

        # Tested and correct!
        es1, es2 = get_names(self.pc_db.hikari)
        self.gametext_db.replace_substring('ED_KEN_ADVANCEABILITY_0010', 'Ultimate Stance', es1)
        self.gametext_db.replace_substring('ED_KEN_ADVANCEABILITY_0020', 'Shinjumonjigiri', es2)

        # Tested and fixed!
        es2, es1 = get_names(self.pc_db.ochette)
        assert es2 == 'Provoke Beasts'
        self.gametext_db.replace_substring('ED_KAR_ADVANCEABILITY_0010', 'Indomitable Beast', es1)
        self.gametext_db.replace_substring('ED_KAR_ADVANCEABILITY_0020', 'Provoke Beasts', es2)

        # Tested and correct!
        es1, es2 = get_names(self.pc_db.castti)
        self.gametext_db.replace_substring('ED_KUS_ADVANCEABILITY_0010', 'Drastic Measures', es1)
        self.gametext_db.replace_substring('ED_KUS_ADVANCEABILITY_0020', 'Remedy', es2)

        # Tested and correct!
        es1, es2 = get_names(self.pc_db.partitio)
        self.gametext_db.replace_substring('ED_SHO_ADVANCEABILITY_0010', 'Negotiate Schedule', es1)
        self.gametext_db.replace_substring('ED_SHO_ADVANCEABILITY_0020', 'Share SP', es2)

        # Tested and fixed!
        es2, es1 = get_names(self.pc_db.temenos)
        self.gametext_db.replace_substring('ED_SIN_ADVANCEABILITY_0010', 'Prayer for Plenty', es1)
        self.gametext_db.replace_substring('ED_SIN_ADVANCEABILITY_0020', 'Heavenly Shine', es2)

        # Tested and fixed!
        es2, es1 = get_names(self.pc_db.osvald)
        self.gametext_db.replace_substring('ED_GAK_ADVANCEABILITY_0010', 'Teach', es1)
        # self.gametext_db.replace_substring('ED_GAK_ADVANCEABILITY_0020', 'One True Magic', es2)

        # Tested and fixed!
        es2, es1 = get_names(self.pc_db.throne)
        self.gametext_db.replace_substring('ED_TOU_ADVANCEABILITY_0010', 'Veil of Darkness', es1)
        self.gametext_db.replace_substring('ED_TOU_ADVANCEABILITY_0020', 'Disguise', es2)

        # Tested and fixed!
        es2, es1 = get_names(self.pc_db.agnea)
        self.gametext_db.replace_substring('ED_ODO_ADVANCEABILITY_0010', 'Windy Refrain', es1)
        # self.gametext_db.replace_substring('ED_ODO_ADVANCEABILITY_0020', 'Song of Hope', es2)

        # Does divine ability stuff need to be updated???
        # Is here a good place to do that???


        # Update inventor data
        inventor_quest_db = Manager.get_table('InventorInventionQuestDB')
        inventor_abilities = self.job_db.eINVENTOR.JobCommandAbility
        inventor_quest_db.INVENTION_ITEM_01.LearnAbilitylabel = inventor_abilities[0]['AbilityName'].value
        inventor_quest_db.INVENTION_ITEM_02.LearnAbilitylabel = inventor_abilities[1]['AbilityName'].value
        inventor_quest_db.INVENTION_ITEM_03.LearnAbilitylabel = inventor_abilities[2]['AbilityName'].value
        inventor_quest_db.INVENTION_ITEM_04.LearnAbilitylabel = inventor_abilities[3]['AbilityName'].value
        inventor_quest_db.INVENTION_ITEM_05.LearnAbilitylabel = inventor_abilities[4]['AbilityName'].value
        inventor_quest_db.INVENTION_ITEM_06.LearnAbilitylabel = inventor_abilities[5]['AbilityName'].value
        inventor_quest_db.INVENTION_ITEM_07.LearnAbilitylabel = inventor_abilities[6]['AbilityName'].value
        # inventor_quest_db.INVENTION_ITEM_08.LearnAbilityLabel = .... ### Always kept last; maybe later shuffle within the inventor class
