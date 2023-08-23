import random
from Manager import Manager


class AbilityPower:
    def __init__(self):
        self.ability_set_db = Manager.get_instance('AbilitySetData').table

    def run(self):
        for abil_set in self.ability_set_db.job_ability_sets:
            if abil_set.boost_levels[-1].AbilityRatio:
                scale = random.uniform(0.7, 1.3)
                abil_set.scale_ability_ratio(scale)
