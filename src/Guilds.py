import random
from Assets import Data
from Nothing import Nothing


def shuffleRequirements(guilds):
    for i, gi in enumerate(guilds):
        gj = random.sample(guilds[i:], 1)[0]
        for k in [1, 2]:
            gi.JobLicenseData[k], gj.JobLicenseData[k] = gj.JobLicenseData[k], gi.JobLicenseData[k]


class Guilds:
    Requirements = Nothing

    def __init__(self):
        self.guildDB = Data.getInstance('GuildData')
        self.jobDB = Data.getInstance('JobData')

    def run(self):
        guilds = list(self.guildDB.guildMap.values())
        Guilds.Requirements(guilds)

        # Update required abilities in case they got shuffled
        for job in self.jobDB.table:
            if job.ID >= 8: break
            divineAbility = job.commandAbilities[-1]
            guild = self.guildDB.guildMap[job.key]
            for data in guild.JobLicenseData:
                if data['NeedAbility'].value != 'None':
                    data['NeedAbility'].value = divineAbility
