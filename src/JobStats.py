import random
from Assets import Data 

class JobStatsFair:
    def __init__(self):
        self.jobDB = Data.getInstance('JobData')
        self.pcDB = Data.getInstance('PlayableCharacterDB')

        jobKeys = self.jobDB.baseJobKeys + self.jobDB.advJobKeys
        self.baseJobStats = [self.jobDB.table.getRow(jKey) for jKey in self.jobDB.baseJobKeys]
        self.advJobStats = [self.jobDB.table.getRow(jKey) for jKey in self.jobDB.advJobKeys]
        self.pcStats = [self.pcDB.table.getRow(pKey) for pKey in self.jobDB.baseJobKeys]

    def run(self):
        self._shuffle(self.baseJobStats)
        self._shuffle(self.advJobStats)
        self._shuffle(self.pcStats)

    def _shuffle(self, stats):
        for i, si in enumerate(stats):
            sj = random.choice(stats[i:])
            si.ParameterRevision, sj.ParameterRevision = sj.ParameterRevision, si.ParameterRevision



class JobStatsRandom(JobStatsFair):
    def run(self):
        self._shuffle(self.baseJobStats + self.advJobStats)
        self._shuffle(self.pcStats)

    def _shuffleStats(self, stats):
        keys = list(stats[0].keys())
        for k in keys:
            for i, si in enumerate(stats):
                sj = random.choice(stats[i:])
                si.parameterRevision[k], sj.parameterRevision[k] = si.parameterRevision[k], sj.parameterRevision[k]
