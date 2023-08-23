import random
from Manager import Manager

class AbilitySP:
    def __init__(self):
        self.ability_set_db = Manager.get_instance('AbilitySetData').table

    def run(self):
        for abil_set in self.ability_set_db.job_ability_sets:
            if abil_set.does_cost_sp:
                cost = abil_set.sp_cost
                change = round(0.5 + 0.3*cost*random.random())
                change *= 1 if random.random() < 0.5 else -1
                abil_set.sp_cost = cost + change
