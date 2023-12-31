import random
from Nothing import Nothing
from Manager import Manager
from Shuffler import Randomizer, Slot, no_weights
from copy import deepcopy
from Utility import get_filename


class Entry:
    def __init__(self, enemy):
        self.enemy = enemy.key
        self.level = enemy.EnemyLevel
        self.size = enemy.Size
        self.include = True
        self.include &= enemy.key != 'ENE_EVE_SUB_OTR_010' # Skip buttermeep

    def __hash__(self):
        return hash(self.enemy)

    def __lt__(self, other):
        if self.level == other.level:
            return self.enemy < other.enemy
        return self.level < other.level

    def __eq__(self, other):
        if isinstance(other, Entry):
            return self.enemy == other.enemy and self.level == other.level
        

class EnemyGroups(Randomizer):
    def __init__(self):
        self.enemy_group_db = Manager.get_instance('EnemyGroupData').table
        self.enemy_db = Manager.get_instance('EnemyDB').table

        entries = set()
        for group in self.enemy_group_db:
            # Only doing random encounters, at least for now
            if group.is_random_encounter:
                # Make sure the group isn't empty
                if not group.enemies:
                    continue

                # Add to the candidates
                for e in group.EnemyID:
                    if e == 'None': continue
                    enemy = self.enemy_db.get_row(e)
                    assert enemy.DisplayRank == 0
                    c = Entry(enemy)
                    entries.add(c)
                
        self.candidates = sorted(entries)
        self.slots = [deepcopy(c) for c in self.candidates]

    def run(self):
        self.generate_weights()
        self.generate_map()
        self.finish()
        self.update_shields()

    def generate_map(self):
        self.enemy_map = {}
        unused = [c.include for c in self.candidates]
        idx = list(range(len(self.candidates)))
        for c_weights, slot in zip(self.weights, self.slots):
            if slot.include:
                w = [c*u for c, u in zip(c_weights, unused)]
                i = random.choices(idx, w, k=1)[0]
                candidate = self.candidates[i]
                self.enemy_map[slot.enemy] = candidate.enemy
                unused[i] = False

        # Quick test to ensure buttermeep stays in the same place
        # Keep for now, but remove later after tons of testing
        for k, v in self.enemy_map.items():
            assert k != 'ENE_EVE_SUB_OTR_010'
            assert v != 'ENE_EVE_SUB_OTR_010'

    def finish(self):
        for group in self.enemy_group_db:
            for i, enemy in enumerate(group.EnemyID):
                if enemy in self.enemy_map:
                    group.EnemyID[i] = self.enemy_map[enemy]

    def update_shields(self):
        # Update sets of groups each enemy belongs to
        self.enemy_group_db.update_group_sets()

        # Update shields given PCs as needed (ring 1 only)
        for group in self.enemy_group_db:
            group.update_weakness_to_pcs(weapon_only=True)

    def generate_weights(self):
        def group_by_level(w, c, s):
            # Bin by level
            # 0 - 5
            # 6 - 10
            # 11 - 15
            # 16 - 20
            # 21 - 30
            # 31 - 40
            # 41+
            if s.level <= 5:
                for i, ci in enumerate(c):
                    w[i] *= ci.level <= 5
            elif s.level <= 10:
                for i, ci in enumerate(c):
                    w[i] *= ci.level > 5 and ci.level <= 10
            elif s.level <= 15:
                for i, ci in enumerate(c):
                    w[i] *= ci.level > 10 and ci.level <= 15
            elif s.level <= 20:
                for i, ci in enumerate(c):
                    w[i] *= ci.level > 15 and ci.level <= 20
            elif s.level <= 30:
                for i, ci in enumerate(c):
                    w[i] *= ci.level > 20 and ci.level <= 30
            elif s.level <= 40:
                for i, ci in enumerate(c):
                    w[i] *= ci.level > 30 and ci.level <= 40
            else:
                for i, ci in enumerate(c):
                    w[i] *= ci.level > 40

        def group_by_size(w, c, s):
            for i, ci in enumerate(c):
                w[i] *= s.size == ci.size
            
        super().generate_weights(group_by_level, group_by_size)
