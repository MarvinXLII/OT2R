import random
from Shuffler import Shuffler, Slot, noWeights
from Manager import Manager
from Nothing import Nothing


def separateAdvancedSupport(w, s, c):
    for i, si in enumerate(s):
        w[i] *= c.isAdvanced == si.isAdvanced


def evasiveManeuversFirst(jobsMap, jobDB):
    indexWithEM = -1
    slotWithEM = None
    for jobID, support in jobsMap.items():
        for i, s in enumerate(support):
            if s.isEvasiveManeuvers:
                slotWithEM = s
                indexWithEM = jobID
                break
    assert indexWithEM >= 0
    assert slotWithEM
    
    # If it's in a base job, just move it to the front
    if indexWithEM < 8:
        first = jobsMap[indexWithEM][0]
    else:
        newIndexWithEM = random.randint(0, 7)
        first = jobsMap[newIndexWithEM][0]
    slotWithEM.ability['AbilityName'], first.ability['AbilityName'] = first.ability['AbilityName'], slotWithEM.ability['AbilityName']

    # Update job data so it gets EM as early as possible
    first.job.JPCost[2] = 1
    first.ability['GetParam'].value = 3


class Ability(Slot):
    def __init__(self, index, job):
        self.job = job
        self.index = index
        self.ability = job.JobSupportAbility[index]
        self.isAdvanced = job.ID >= 8

    @property
    def isEvasiveManeuvers(self):
        return self.ability['AbilityName'].value == 'ABI_SCH_SUP_01'

    def copy(self, other):
        self.ability = other.ability

    def patch(self):
        self.job.JobSupportAbility[self.index] = self.ability
        self.ability['GetParam'].value = self.index + 4


class Support(Shuffler):
    CheckAdvanced = noWeights
    EMFirst = Nothing

    def __init__(self):
        self.jobDB = Manager.getInstance('JobData')

        self.slots = []
        self.candidates = []
        self.jobMap = {}
        for job in self.jobDB.table:
            if job.ID >= 12: continue
            for index, _ in enumerate(job.JobSupportAbility):
                slot = Ability(index, job)
                candidate = Ability(index, job)
                self.slots.append(slot)
                self.candidates.append(candidate)
                if slot.job.ID not in self.jobMap:
                    self.jobMap[slot.job.ID] = []
                self.jobMap[slot.job.ID].append(slot)

    def finish(self):
        # Patch everything first
        super().finish()
        # Update for EM if necessary
        Support.EMFirst(self.jobMap, self.jobDB)

    def generateWeights(self):
        super().generateWeights(Support.CheckAdvanced)
