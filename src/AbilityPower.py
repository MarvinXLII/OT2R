import random
from Manager import Manager


class AbilityPower:
    def __init__(self):
        self.abilitySetTable = Manager.getInstance('AbilitySetData').table

    def run(self):
        for abilSet in self.abilitySetTable.jobAbilitySets:
            if abilSet.boostLevels[-1].AbilityRatio:
                scale = random.uniform(0.7, 1.3)
                abilSet.scaleAbilityRatio(scale)
