import random
from Assets import Data


class AbilityPower:
    def __init__(self):
        self.abilitySetDB = Data.getInstance('AbilitySetData')

    def run(self):
        for abilSet in self.abilitySetDB.jobAbilitySets:
            if abilSet.boostLevels[-1].AbilityRatio:
                scale = random.uniform(0.7, 1.3)
                abilSet.scaleAbilityRatio(scale)
