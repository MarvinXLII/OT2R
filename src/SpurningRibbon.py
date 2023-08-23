import random
from Utility import WEAPONS, PCNAMESMAP
from Shuffler import Shuffler, Slot, no_weights
from Manager import Manager
import sys

class SpurningRibbon:
    PC = 'None'

    @classmethod
    def run(cls):
        pc_db = Manager.get_instance('PlayableCharacterDB').table
        def add_accessory(pc_key):
            pc = pc_db.get_row(pc_key)
            pc.FirstEquipment['Accessory_00'] = 'ITM_EQP_ACS_031'

        if cls.PC == 'All':
            for pc_key in PCNAMESMAP.values():
                add_accessory(pc_key)
            # Set sell price to 1 so people won't abuse it
            item_db = Manager.get_instance('ItemDB').table
            item_db.ITM_EQP_ACS_031.SellPrice = 1
        elif cls.PC == 'PC with EM':
            job_db = Manager.get_instance('JobData').table
            for job in job_db:
                if job.has_evasive_maneuvers:
                    break
            else:
                sys.exit(f"Could not find job with Evasive Maneuvers")
            # Make sure the job with EM is a base job, otherwise make it so!
            if job.ID >= 8:
                base_jobs = [job for job in job_db if job.ID < 8]
                b_job = random.sample(base_jobs, 1)[0]
                b_job.JobSupportAbility, job.JobSupportAbility = job.JobSupportAbility, b_job.JobSupportAbility
                job = b_job
            add_accessory(job.key)
        elif cls.PC in PCNAMESMAP:
            add_accessory(PCNAMESMAP[cls.PC])
        else:
            sys.exit(f"spurning_ribbon not setup for {PlayableCharacters.SpurningRibbon}")
