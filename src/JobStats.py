import random
from Manager import Manager
 

class JobStatsFair:
    def __init__(self):
        self.job_db = Manager.get_instance('JobData').table
        self.pc_db = Manager.get_instance('PlayableCharacterDB').table

        self.base_job_stats = [self.job_db.get_row(key) for key in self.job_db.base_job_keys]
        self.adv_job_stats = [self.job_db.get_row(key) for key in self.job_db.adv_job_keys]
        self.pc_stats = [self.pc_db.get_row(key) for key in self.job_db.base_job_keys]

    def run(self):
        self._shuffle(self.base_job_stats)
        self._shuffle(self.adv_job_stats)
        self._shuffle(self.pc_stats)

    def _shuffle(self, stats):
        for i, si in enumerate(stats):
            sj = random.choice(stats[i:])
            si.ParameterRevision, sj.ParameterRevision = sj.ParameterRevision, si.ParameterRevision



class JobStatsRandom(JobStatsFair):
    def run(self):
        self._shuffle(self.base_job_stats + self.adv_job_stats)
        self._shuffle(self.pc_stats)

    # def _shuffle(self, stats):
    #     keys = list(stats[0].ParameterRevision.keys())
    #     for k in keys:
    #         for i, si in enumerate(stats):
    #             sj = random.choice(stats[i:])
    #             si.ParameterRevision[k], sj.ParameterRevision[k] = si.ParameterRevision[k], sj.ParameterRevision[k]
