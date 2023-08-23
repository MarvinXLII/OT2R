import random
from Shuffler import Shuffler, Slot, no_weights
from Manager import Manager
from Nothing import Nothing


def separate_advanced_support(w, s, c):
    for i, si in enumerate(s):
        w[i] *= c.is_advanced == si.is_advanced


def evasive_maneuvers_first(jobs_map, job_db):
    index_with_em = -1
    slot_with_em = None
    for job_id, support in jobs_map.items():
        for i, s in enumerate(support):
            if s.is_evasive_maneuvers:
                slot_with_em = s
                index_with_em = job_id
                break
    assert index_with_em >= 0
    assert slot_with_em
    
    # If it's in a base job, just move it to the front
    if index_with_em < 8:
        first = jobs_map[index_with_em][0]
    else:
        new_index_with_em = random.randint(0, 7)
        first = jobs_map[new_index_with_em][0]
    slot_with_em.ability['AbilityName'], first.ability['AbilityName'] = first.ability['AbilityName'], slot_with_em.ability['AbilityName']

    # Update job data so it gets EM as early as possible
    first.job.JPCost[2] = 1
    first.ability['GetParam'].value = 3


class Ability(Slot):
    def __init__(self, index, job):
        self.job = job
        self.index = index
        self.ability = job.JobSupportAbility[index]
        self.is_advanced = job.ID >= 8

    @property
    def is_evasive_maneuvers(self):
        return self.ability['AbilityName'].value == 'ABI_SCH_SUP_01'

    def copy(self, other):
        self.ability = other.ability

    def patch(self):
        self.job.JobSupportAbility[self.index] = self.ability
        self.ability['GetParam'].value = self.index + 4


class Support(Shuffler):
    check_advanced = no_weights
    em_first = Nothing

    def __init__(self):
        self.job_db = Manager.get_instance('JobData')

        self.slots = []
        self.candidates = []
        self.job_map = {}
        for job in self.job_db.table:
            if job.ID >= 12: continue
            for index, _ in enumerate(job.JobSupportAbility):
                slot = Ability(index, job)
                candidate = Ability(index, job)
                self.slots.append(slot)
                self.candidates.append(candidate)
                if slot.job.ID not in self.job_map:
                    self.job_map[slot.job.ID] = []
                self.job_map[slot.job.ID].append(slot)

    def finish(self):
        # Patch everything first
        super().finish()
        # Update for EM if necessary
        Support.em_first(self.job_map, self.job_db)

    def generate_weights(self):
        super().generate_weights(Support.check_advanced)
