import random
from Manager import Manager
from Nothing import Nothing


def shuffle_requirements(guilds):
    for i, gi in enumerate(guilds):
        gj = random.sample(guilds[i:], 1)[0]
        for k in [1, 2]:
            gi.JobLicenseData[k], gj.JobLicenseData[k] = gj.JobLicenseData[k], gi.JobLicenseData[k]


class Guilds:
    Requirements = Nothing

    def __init__(self):
        self.guild_db = Manager.get_instance('GuildData').table
        self.job_db = Manager.get_instance('JobData').table

    def run(self):
        guilds = list(self.guild_db.guild_map.values())
        Guilds.Requirements(guilds)

        # Update required abilities in case they got shuffled
        for job in self.job_db:
            if job.ID >= 8: break
            divine_ability = job.command_abilities[-1]
            guild = self.guild_db.guild_map[job.key]
            for data in guild.JobLicenseData:
                if data['NeedAbility'].value != 'None':
                    data['NeedAbility'].value = divine_ability
