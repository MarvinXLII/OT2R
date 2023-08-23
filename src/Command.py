import random
from Utility import WEAPONS, get_filename
from Shuffler import Shuffler, Slot, noWeights
from Assets import Data
import hjson

def CheckWeapon(w, s, c):
    for i, si in enumerate(s):
        if c.dependWeapon:
            w[i] *= c.restrictWeapon in si.jobWeapons


def separateAdvancedCommands(w, s, c):
    for i, si in enumerate(s):
        w[i] *= c.isAdvanced == si.isAdvanced


def separateDivine(w, s, c):
    for i, si in enumerate(s):
        w[i] *= c.isDivineAbility == si.isDivineAbility


def separateExAbilities(w, s, c):
    for i, si in enumerate(s):
        w[i] *= c.isExAbility == si.isExAbility


def skipSlot(w, s, c):
    for i, si in enumerate(s):
        w[i] *= not si.skip


# Single slot
def inventorWeights(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.isInventorValid

def inventorCheckWeapon(w, c, s):
    for i, ci in enumerate(c):
        if ci.dependWeapon:
            w[i] *= ci.restrictWeapon in s.jobWeapons

# Single slot
def swordAttacks(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.restrictWeapon == 'EWEAPON_CATEGORY::eSWORD'

def spearAttacks(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.restrictWeapon == 'EWEAPON_CATEGORY::eLANCE'

def daggerAttacks(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.restrictWeapon == 'EWEAPON_CATEGORY::eDAGGER'

def axeAttacks(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.restrictWeapon == 'EWEAPON_CATEGORY::eAXE'

def bowAttacks(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.restrictWeapon == 'EWEAPON_CATEGORY::eBOW'

def staffAttacks(w, c, s):
    for i, ci in enumerate(c):
        w[i] *= ci.restrictWeapon == 'EWEAPON_CATEGORY::eROD'



class AbilitySlot(Slot):
    weights = hjson.load(open(get_filename('json/weightsAbilitySet.json'), 'r'))


# TODO: Clean this up!!!
class Ability(AbilitySlot):
    def __init__(self, job, index, slotIndex):
        # Data needed afterwards for updating
        self.index = index
        self.job = job
        self.slotIndex = slotIndex

        # Data needed for shuffling
        self.abilitySet = job.JobCommandAbility[index]
        self.abilityName = self.abilitySet['AbilityName'].value
        abilitySetObj = Data.getInstance('AbilitySetData').table.getRow(self.abilityName)
    
        self.isAdvanced = self.job.ID >= 8
        self.isExAbility = False
        self.isArmsMaster = '_WPM_' in self.abilityName and abilitySetObj.RestrictWeaponLabel != 'None'
        self.isInventor = '_INV_' in self.abilityName
        self.isInventorValid = self.weights[self.abilityName]['isInventorValid']
        self.hasMagicLabel = self.weights[self.abilityName]['hasMagicLabel']
        self.skip = self.weights[self.abilityName]['skip']
        self.initialize()


    def initialize(self):
        assert self.abilityName != 'None'
        # Job data needed for weights
        # (Maybe separate slot and candidate objects?)
        self.jobWeapons = []
        for i, equippable in enumerate(self.job.ProperEquipment[:6]):
            if equippable:
                self.jobWeapons.append(WEAPONS[i])

        # Data needed for generating weights
        # TODO: might need to store some of this in spreadsheet and load
        # e.g. weapon, element, divine, 1-2 slot allowed
        # Probably best to ignore 1-2 slot allowed for now.
        # Should be able to separate divine and advanced job
        abilityDB = Data.getInstance('AbilityData')
        abilitySetDB = Data.getInstance('AbilitySetData')
        ablSet = abilitySetDB.table.getRow(self.abilityName)
        ability = abilityDB.table.getRow(ablSet.NoBoost)
        self.isDivineAbility = ablSet.IsDivineAbility
        self.dependWeapon = ability.DependWeapon
        self.restrictWeapon = ability.RestrictWeapon # weapon used if physical, otherwise none
        if self.restrictWeapon != 'EWEAPON_CATEGORY::eNONE':
            assert self.restrictWeapon in WEAPONS, self.restrictWeapon
        self.attribute = ability.Attribute # element type if magic, none otherwise

    def copy(self, other):
        self.abilityName = other.abilityName

    # Probably won't need all of this thanks to copy!
    def patch(self):
        if self.index < 2:
            param = 1
        elif self.index == 7:
            param = 2
        else:
            param = 0
        self.abilitySet['GetParam'].value = param
        self.abilitySet['AbilityName'].value = self.abilityName
        self.job.JobCommandAbility[self.index] = self.abilitySet


class ExAbility(Ability):
    def __init__(self, pc, job, index, slotIndex):
        # Data needed afterwards for updating 
        self.index = index
        self.job = job
        self.pc = pc
        self.slotIndex = slotIndex

        # Data needed for shuffling
        self.abilitySet = pc.AdvancedAbility[index]
        self.abilityName = self.abilitySet['AbilityID'].value
        self.isAdvanced = False
        self.isExAbility = True
        self.isInventor = False
        self.isArmsMaster = False
        self.isInventorValid = self.weights[self.abilityName]['isInventorValid']
        self.hasMagicLabel = self.weights[self.abilityName]['hasMagicLabel']
        self.skip = self.weights[self.abilityName]['skip']
        self.initialize()

    def patch(self):
        assert self.abilityName != 'None'
        self.abilitySet['AbilityID'].value = self.abilityName
        self.pc.AdvancedAbility[self.index] = self.abilitySet

# Hardly inherits anything...lol.
class Command(Shuffler):
    CheckAdvanced = noWeights
    CheckDivine = noWeights
    CheckExAbility = noWeights
    
    def __init__(self):
        self.jobDB = Data.getInstance('JobData')
        self.pcDB = Data.getInstance('PlayableCharacterDB')
        self.gameText = Data.getInstance('GameTextEN')
        self.abilitySetDB = Data.getInstance('AbilitySetData')
        self.abilityDB = Data.getInstance('AbilityData')

        self.slots = []
        self.candidates = []

        # Main 8 abilities from the jobs
        jobMap = {}
        for job in self.jobDB.table:
            if job.ID >= 12: break
            jobMap[job.key] = job
            for index, abilitySet in enumerate(job.JobCommandAbility):
                slot = Ability(job, index, len(self.slots))
                candidate = Ability(job, index, len(self.candidates))
                self.slots.append(slot)
                self.candidates.append(candidate)

        # Ex Abilities
        for pc in self.pcDB.table:
            if pc.Id > 8: break
            for index, abilitySet in enumerate(pc.AdvancedAbility):
                job = jobMap[pc.FirstJob.split('::')[1]]
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
        self.randomCandidate('ABI_SET_WPM_010', swordAttacks)
        self.randomCandidate('ABI_SET_WPM_020', spearAttacks)
        self.randomCandidate('ABI_SET_WPM_030', daggerAttacks)
        self.randomCandidate('ABI_SET_WPM_040', axeAttacks)
        self.randomCandidate('ABI_SET_WPM_050', bowAttacks)
        self.randomCandidate('ABI_SET_WPM_060', staffAttacks)

        # Fill Advanced Magic
        # Chooses a random slot for a specific candidate
        # Slots must belong to a job with at least 3 vacant slots
        self.randomJobWithMagic('ABI_SET_SCH_070') # Advanced Magic
        self.randomJobWithMagic('ABI_SET_SCH_090') # Alephan's Wisdom

        # Fill Inventor
        # All are ok if filled by Magic/Advanced Magic/Alephan's Wisdom
        self.randomCandidate('ABI_SET_INV_010', inventorWeights, inventorCheckWeapon, okIfFilled=True)
        self.randomCandidate('ABI_SET_INV_020', inventorWeights, inventorCheckWeapon, okIfFilled=True)
        self.randomCandidate('ABI_SET_INV_030', inventorWeights, inventorCheckWeapon, okIfFilled=True)
        self.randomCandidate('ABI_SET_INV_040', inventorWeights, inventorCheckWeapon, okIfFilled=True)
        self.randomCandidate('ABI_SET_INV_050', inventorWeights, inventorCheckWeapon, okIfFilled=True)
        self.randomCandidate('ABI_SET_INV_060', inventorWeights, inventorCheckWeapon, okIfFilled=True)
        self.randomCandidate('ABI_SET_INV_070', inventorWeights, inventorCheckWeapon, okIfFilled=True)

        # Finally do everything else
        self.generateWeights()
        self.sampler()

        # Confirm done
        self.checkDone()

        # Finalize Armsmaster and Inventor, then patch
        self.finish()

    def generateWeights(self, *args):
        super().generateWeights(CheckWeapon, Command.CheckAdvanced, Command.CheckDivine, Command.CheckExAbility, *args)

    def checkDone(self):
        assert sum(self.vacant) == 0
        assert sum(self.unused) == 0

    def sampler(self):
        # Sort candidates by number of allowed slots
        # Ensure most restrictive candidates get used first
        swc = list(zip(self.weights, self.candidates))
        random.shuffle(swc) # Ensure ties are randomly broken
        swc.sort(key=lambda x: sum(x[0]))

        idx = list(range(len(self.slots)))
        for slotWeights, candidate in swc:
            cIdx = candidate.slotIndex
            if not self.unused[cIdx]: continue # If candidate is used, skip
            swv = [s * v for s, v in zip(slotWeights, self.vacant)]
            assert sum(swv) > 0
            sIdx = random.choices(idx, swv, k=1)[0]
            self.slots[sIdx].copy(candidate)
            self.vacant[sIdx] = False
            self.unused[cIdx] = False

    def randomJobWithMagic(self, candAbilSetName, *args):
        idx = list(range(len(self.vacant)))
        while True:
            i = random.choices(idx, self.vacant, k=1)[0]
            slot = self.slots[i]
            job = slot.job.key
            slotIndex = []
            for s in self.slots:
                if s.job.key == job:
                    if self.vacant[s.slotIndex]:
                        slotIndex.append(s.slotIndex)
            if len(slotIndex) >= 3:
                break

        # Pick a slot and fill it with the candidate
        for cIdx, c in enumerate(self.candidates):
            if c.abilityName == candAbilSetName:
                break
        else:
            sys.exit(f'{candAbilSetName} not found in candidates!')
        assert self.unused[cIdx] == True, cIdx
        self.unused[cIdx] = False
        sIdx = random.choices(slotIndex, k=1)[0]
        slotIndex.remove(sIdx)
        slot = self.slots[sIdx]
        slot.copy(self.candidates[cIdx])
        assert self.vacant[sIdx] == True, sIdx
        self.vacant[sIdx] = False

        # Filter candidates that do appropriate magic
        candidates = []
        for cIdx, ci in enumerate(self.candidates):
            if ci.hasMagicLabel and self.unused[cIdx]:
                candidates.append(ci)

        # Pick 2 of them and fill those 2 available slots
        random.shuffle(candidates)
        cand1 = candidates[0]
        cand2 = candidates[1]
        random.shuffle(slotIndex)
        sIdx1 = slotIndex[0]
        sIdx2 = slotIndex[1]

        assert self.unused[cand1.slotIndex] == True, cand1.slotIndex
        assert self.unused[cand2.slotIndex] == True, cand2.slotIndex
        assert self.vacant[sIdx1] == True, sIdx1
        assert self.vacant[sIdx2] == True, sIdx2

        self.slots[sIdx1].copy(cand1)
        self.slots[sIdx2].copy(cand2)
        self.unused[cand1.slotIndex] == False
        self.unused[cand2.slotIndex] == False
        self.vacant[sIdx1] == False
        self.vacant[sIdx2] == False

    def randomVacantSlot(self, candAbilSetName, *args):
        for cIdx, c in enumerate(self.candidates):
            if c.abilityName == candAbilSetName:
                break
        else:
            sys.exit(f"{candAbilSetName} is not a valid candidate name")
        assert self.unused[cIdx] == True, cIdx
        self.unused[cIdx] = False, cIdx

        candidate = self.candidates[cIdx]
        weights = [v for v in self.vacant]
        for f in args:
            f(weights, self.slots, candidate)

        idx = list(range(len(self.slots)))
        sIdx = random.choices(idx, weights, k=1)[0]
        self.slots[sIdx].copy(candidate)
        self.vacant[sIdx] = False

    def randomCandidate(self, slotAbilSetName, *args, okIfFilled=False):
        # Loop over candidates here.
        # Slot abilityNames will get overwritten during shuffling.
        # This assumes candidates and slots are in the same order!
        for sIdx, c in enumerate(self.candidates):
            if c.abilityName == slotAbilSetName:
                break
        else:
            sys.exit(f"{slotAbilSetName} is not a valid slot name")
        if okIfFilled:
            if not self.vacant[sIdx]:
                return
        else:
            assert self.vacant[sIdx] == True, sIdx
        self.vacant[sIdx] = False

        slot = self.slots[sIdx]
        weights = [u for u in self.unused]
        for f in args:
            f(weights, self.candidates, slot)

        idx = list(range(len(self.candidates)))
        cIdx = random.choices(idx, weights, k=1)[0]
        slot.copy(self.candidates[cIdx])
        self.unused[cIdx] = False

    def prepare(self):
        for slot in self.slots:
            abilSet = self.abilitySetDB.table.getRow(slot.abilityName)
            if slot.isInventor:
                abilSet.makeNotInventor()
                if abilSet.SuperMagicLabel != 'None':
                    a = self.abilitySetDB.table.getRow(abilSet.SuperMagicLabel)
                    a.makeNotInventor()
                if abilSet.HyperMagicLabel != 'None':
                    a = self.abilitySetDB.table.getRow(abilSet.HyperMagicLabel)
                    a.makeNotInventor()

            elif slot.isArmsMaster:
                abilSet.makeNotArmsMaster()

        # Don't allow All-Purpose Tool to change slots
        for s, c in zip(self.slots, self.candidates):
            if s.skip:
                assert c.skip
                assert s.abilityName == c.abilityName
                self.unused[c.slotIndex] = False # Set candidate to having been used
                self.vacant[s.slotIndex] = False # Set slot to be occupied

    def finish(self):
        for slot in self.slots:
            abilSet = self.abilitySetDB.table.getRow(slot.abilityName)

            if slot.isInventor:
                abilSet.makeInventor()
                if abilSet.SuperMagicLabel != 'None':
                    a = self.abilitySetDB.table.getRow(abilSet.SuperMagicLabel)
                    a.makeInventor()
                if abilSet.HyperMagicLabel != 'None':
                    a = self.abilitySetDB.table.getRow(abilSet.HyperMagicLabel)
                    a.makeInventor()

            elif slot.isArmsMaster:
                abilSet.makeArmsMaster()

        # Finish here; the rest is easier that way
        super().finish()

        # Update text for Ex Abilities
        def getNames(pc):
            es1 = self.abilitySetDB.table.getRow(pc.exSkillOne).name
            es2 = self.abilitySetDB.table.getRow(pc.exSkillTwo).name
            return es2, es1

        # Tested and correct!
        es1, es2 = getNames(self.pcDB.hikari)
        self.gameText.replaceSubstring('ED_KEN_ADVANCEABILITY_0010', 'Ultimate Stance', es1)
        self.gameText.replaceSubstring('ED_KEN_ADVANCEABILITY_0020', 'Shinjumonjigiri', es2)

        # Tested and fixed!
        es2, es1 = getNames(self.pcDB.ochette)
        assert es2 == 'Provoke Beasts'
        self.gameText.replaceSubstring('ED_KAR_ADVANCEABILITY_0010', 'Indomitable Beast', es1)
        self.gameText.replaceSubstring('ED_KAR_ADVANCEABILITY_0020', 'Provoke Beasts', es2)

        # Tested and correct!
        es1, es2 = getNames(self.pcDB.castti)
        self.gameText.replaceSubstring('ED_KUS_ADVANCEABILITY_0010', 'Drastic Measures', es1)
        self.gameText.replaceSubstring('ED_KUS_ADVANCEABILITY_0020', 'Remedy', es2)

        # Tested and correct!
        es1, es2 = getNames(self.pcDB.partitio)
        self.gameText.replaceSubstring('ED_SHO_ADVANCEABILITY_0010', 'Negotiate Schedule', es1)
        self.gameText.replaceSubstring('ED_SHO_ADVANCEABILITY_0020', 'Share SP', es2)

        # Tested and fixed!
        es2, es1 = getNames(self.pcDB.temenos)
        self.gameText.replaceSubstring('ED_SIN_ADVANCEABILITY_0010', 'Prayer for Plenty', es1)
        self.gameText.replaceSubstring('ED_SIN_ADVANCEABILITY_0020', 'Heavenly Shine', es2)

        # Tested and fixed!
        es2, es1 = getNames(self.pcDB.osvald)
        self.gameText.replaceSubstring('ED_GAK_ADVANCEABILITY_0010', 'Teach', es1)
        # self.gameText.replaceSubstring('ED_GAK_ADVANCEABILITY_0020', '', '') ## TEXT IS BLANK????

        # Tested and fixed!
        es2, es1 = getNames(self.pcDB.throne)
        self.gameText.replaceSubstring('ED_TOU_ADVANCEABILITY_0010', 'Veil of Darkness', es1)
        self.gameText.replaceSubstring('ED_TOU_ADVANCEABILITY_0020', 'Disguise', es2)

        # Tested and fixed!
        es2, es1 = getNames(self.pcDB.agnea)
        self.gameText.replaceSubstring('ED_ODO_ADVANCEABILITY_0010', 'Windy Refrain', es1)
        # self.gameText.replaceSubstring('ED_ODO_ADVANCEABILITY_0020', '', '') ## TEXT IS BLANK??? -- Learned in battle and works without modding!

        # Does divine ability stuff need to be updated???
        # Is here a good place to do that???

