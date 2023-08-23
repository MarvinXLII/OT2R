import random
from Manager import Manager

class AbilityWeapons:
    def __init__(self):
        self.abilitySetTable = Manager.getInstance('AbilitySetData').table
        self.abilities = None
        self.bins = None

    def run(self):
        self._filterAbilities()
        self._generateBins()
        self._shuffle()
        self._updateText()

    # Generate a list of abilities using weapons
    def _filterAbilities(self):
        self.abilities = []
        for abilSet in self.abilitySetTable.jobAbilitySets:
            if abilSet.usesWeapon:
                self.abilities.append(abilSet)

    # Count how many of each weapon are used
    def _generateBins(self):
        self.bins = {}
        for ability in self.abilities:
            if ability.weapon not in self.bins:
                self.bins[ability.weapon] = 0
            self.bins[ability.weapon] += 1

    def _shuffle(self):
        num = list(self.bins.values())
        weapons = list(self.bins.keys())
        index = list(range(len(self.bins)))
        random.shuffle(num)
        random.shuffle(self.abilities)
        for a in self.abilities:
            i = random.choices(index, num, k=1)[0]
            num[i] -= 1
            a.weapon = weapons[i]

    def _updateText(self):
        for a in self.abilities:
            a.updateDetail()
            a.updateDisplay()
