import random
from Manager import Manager

class AbilitySP:
    def __init__(self):
        self.abilitySetTable = Manager.getInstance('AbilitySetData').table

    def run(self):
        for abilSet in self.abilitySetTable.jobAbilitySets:
            if abilSet.doesCostSP:
                cost = abilSet.spCost
                change = round(0.5 + 0.3*cost*random.random())
                change *= 1 if random.random() < 0.5 else -1
                abilSet.spCost = cost + change
