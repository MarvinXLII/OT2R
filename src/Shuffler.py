import random
import sys


# Default function for weight calculations
def no_weights(*args):
    pass

    
class Slot:
    def copy(self, other):
        pass

    def patch(self):
        pass


class Shuffler:
    def __init__(self):
        self.slots = None
        self.candidates = None
        self.vacant = None
        self.weights = None

    def run(self):
        self.vacant = [True] * len(self.slots)
        self.generate_weights()
        self.sampler()
        self.check_done()
        self.finalize()
        self.finish()

    def generate_weights(self, *func):
        self.weights = []
        weight_dict = {} # Significantly less memory intensive
        for ci, candidate in enumerate(self.candidates):
            w = [True] * len(self.slots)
            for f in func:
                f(w, self.slots, candidate)
            bw = bytes(w)
            if bw not in weight_dict:
                weight_dict[bw] = bw
            self.weights.append(weight_dict[bw])

    def check_done(self):
        assert sum(self.vacant) == 0

    # Only works since len(slots) == len(candidates). It literally
    # shuffles everything that already exists under constraints (the weights).
    #
    # Looping over slots and generating weights of all candidates
    # for each slot would make more sense if there were more candidates
    # than slots or resampling were allowed.
    def sampler(self):
        
        # Sort candidates by number of allowed slots
        # Ensure most restrictive candidates get used first
        swc = list(zip(self.weights, self.candidates))
        random.shuffle(swc) # Ensure ties are randomly broken
        swc.sort(key=lambda x: sum(x[0]))

        idx = list(range(len(self.slots)))
        for slot_weights, candidate in swc:
            swv = [s * v for s, v in zip(slot_weights, self.vacant)]
            assert sum(swv) > 0
            s_idx = random.choices(idx, swv, k=1)[0]
            self.slots[s_idx].copy(candidate)
            self.vacant[s_idx] = False

    # Some shufflers might require some finishing touches
    def finalize(self):
        pass

    def finish(self):
        for slot in self.slots:
            slot.patch()



# Sample without replacement
class Randomizer(Shuffler):

    def run(self):
        self.generate_weights()
        self.sampler()
        self.finish()

    def sampler(self):
        idx = list(range(len(self.candidates)))
        for candidateWeights, slot in zip(self.weights, self.slots):
            c_idx = random.choices(idx, candidateWeights, k=1)[0]
            candidate = self.candidates[c_idx]
            slot.copy(candidate)

    def generate_weights(self, *func):
        self.weights = []
        weight_dict = {} # Significantly less memory intensive
        for si, slot in enumerate(self.slots):
            w = [True] * len(self.candidates)
            for f in func:
                f(w, self.candidates, slot)
            bw = bytes(w)
            if bw not in weight_dict:
                weight_dict[bw] = bw
            self.weights.append(weight_dict[bw])


# Should make it impossible for a candidate to remain in the same slot
class ShufflerNeverSameSlot(Shuffler):
    def sampler(self):
        assert len(self.slots) == len(self.candidates)

        # Sort candidates by number of allowed slots
        # Ensure most restrictive candidates get used first
        swc = list(zip(self.weights, self.candidates, range(len(self.candidates))))
        random.shuffle(swc) # Ensure ties are randomly broken
        swc.sort(key=lambda x: sum(x[0]))

        fails = 0
        retry = False
        filled = []
        idx = list(range(len(self.slots)))
        while swc:
            slot_weights, candidate, c_idx = swc.pop(0)

            swv = [s * v for s, v in zip(slot_weights, self.vacant)]
            swv[c_idx] = 0 # Candidate cannot stay put
            if sum(swv) >= 1:
                # Fill as normal
                s_idx = random.choices(idx, swv, k=1)[0]
                self.slots[s_idx].copy(candidate)
                self.vacant[s_idx] = False
                # Store in case it needs to be undone
                filled.append((slot_weights, candidate, c_idx, s_idx))
            elif len(filled) == 0:
                # Here just in case. Should never happen.
                retry = True
                break
            else:
                # Here just in case. Should never happen.
                fails += 1
                if fails == 10:
                    retry = True
                    break
                # Undo most recent fill
                prev_sw, prev_cand, prev_c_idx, prev_s_idx = filled.pop()
                swc.insert(0, (prev_sw, prev_cand, prev_c_idx))
                assert self.vacant[prev_s_idx] == False
                self.vacant[prev_s_idx] = True
                # Give current candidate without any slots priority next
                swc.insert(0, (slot_weights, candidate, c_idx))

        # Here just in case. Should never be needed.
        if retry:
            for i, _ in enumerate(self.vacant):
                self.vacant[i] = False
            self.sampler()
