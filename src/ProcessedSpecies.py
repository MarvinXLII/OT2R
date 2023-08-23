import random
from Manager import Manager


class Process:
    def __init__(self):
        self.invadeDB = Manager.getInstance('InvadeData')
        self.species = []
        for species in self.invadeDB.table:
            if species.ID == 5001: # Skip iguana, Ochette Ch 1
                continue
            if species.ID == 5013: # Skip Buttermeep, Ochette Ch 2, Tera's Route
                continue
            if species.EnableProcess:
                self.species.append(species)
        
    def run(self):
        self._shuffle()

    def _shuffle(self):
        for i, si in enumerate(self.species):
            sj = random.sample(self.species[i:], 1)[0]
            si.ProcessedItem, sj.ProcessedItem = sj.ProcessedItem, si.ProcessedItem
            si.ProcessNumID, sj.ProcessNumID = sj.ProcessNumID, si.ProcessNumID
