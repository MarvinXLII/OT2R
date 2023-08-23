import random


# Default function for weight calculations
def noWeights(*args):
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
        self.generateWeights()
        self.sampler()
        self.checkDone()
        self.finish()

    def generateWeights(self, *func):
        self.weights = []
        weightDict = {} # Significantly less memory intensive
        for ci, candidate in enumerate(self.candidates):
            w = [True] * len(self.slots)
            for f in func:
                f(w, self.slots, candidate)
            bw = bytes(w)
            if bw not in weightDict:
                weightDict[bw] = bw
            self.weights.append(weightDict[bw])

    def checkDone(self):
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
        for slotWeights, candidate in swc:
            swv = [s * v for s, v in zip(slotWeights, self.vacant)]
            assert sum(swv) > 0
            sIdx = random.choices(idx, swv, k=1)[0]
            self.slots[sIdx].copy(candidate)
            self.vacant[sIdx] = False

    def finish(self):
        for slot in self.slots:
            slot.patch()



# Sample without replacement
class Randomizer(Shuffler):

    def run(self):
        self.generateWeights()
        self.sampler()
        self.finish()

    def sampler(self):
        idx = list(range(len(self.candidates)))
        for candidateWeights, slot in zip(self.weights, self.slots):
            cIdx = random.choices(idx, candidateWeights, k=1)[0]
            candidate = self.candidates[cIdx]
            slot.copy(candidate)

    def generateWeights(self, *func):
        self.weights = []
        weightDict = {} # Significantly less memory intensive
        for si, slot in enumerate(self.slots):
            w = [True] * len(self.candidates)
            for f in func:
                f(w, self.candidates, slot)
            bw = bytes(w)
            if bw not in weightDict:
                weightDict[bw] = bw
            self.weights.append(weightDict[bw])
