import random
from Manager import Manager

class AbilityWeapons:
    def __init__(self):
        self.ability_set_db = Manager.get_instance('AbilitySetData').table
        self.abilities = None
        self.bins = None

    def run(self):
        self._filter_abilities()
        self._generate_bins()
        self._shuffle()
        self._update_text()

    # Generate a list of abilities using weapons
    def _filter_abilities(self):
        self.abilities = []
        for abil_set in self.ability_set_db.job_ability_sets:
            if abil_set.uses_weapon:
                self.abilities.append(abil_set)

    # Count how many of each weapon are used
    def _generate_bins(self):
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
        for ability in self.abilities:
            i = random.choices(index, num, k=1)[0]
            num[i] -= 1
            ability.weapon = weapons[i]

    def _update_text(self):
        for ability in self.abilities:
            ability.update_detail()
            ability.update_display()
