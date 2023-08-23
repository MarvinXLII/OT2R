import random
from Manager import Manager
 

class JobStatsFair:
    def __init__(self):
        self.jobTable = Manager.getInstance('JobData').table
        self.pcTable = Manager.getInstance('PlayableCharacterDB').table

        jobKeys = self.jobTable.baseJobKeys + self.jobTable.advJobKeys
        self.baseJobStats = [self.jobTable.getRow(jKey) for jKey in self.jobTable.baseJobKeys]
        self.advJobStats = [self.jobTable.getRow(jKey) for jKey in self.jobTable.advJobKeys]
        self.pcStats = [self.pcTable.getRow(pKey) for pKey in self.jobTable.baseJobKeys]

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
