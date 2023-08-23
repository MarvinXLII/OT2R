import random
from Assets import Data

class AbilitySP:
    def __init__(self):
        self.abilitySetDB = Data.getInstance('AbilitySetData')

    def run(self):
        for abilSet in self.abilitySetDB.jobAbilitySets:
            if abilSet.doesCostSP:
                cost = abilSet.spCost
                change = round(0.5 + 0.3*cost*random.random())
                change *= 1 if random.random() < 0.5 else -1
                abilSet.spCost = cost + change
