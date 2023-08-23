from Manager import Manager
import os
import sys
import hjson

from Databases import *
from Utility import STATLIST, get_filename
import hjson


class SpoilerItems:
    def __init__(self, outPath):
        self.outPath = outPath
        self.objectData = Manager.getInstance('ObjectData').table
        self.shopDB = Manager.getInstance('PurchaseItemTable').table

    def chests(self):
        outfile = os.path.join(self.outPath, 'spoiler_chests.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        chests = self.objectData.getChests()
        maxLength = 0
        for chest in chests:
            maxLength = max(maxLength, len(chest.vanilla))
            maxLength = max(maxLength, len(chest.item))
        maxLength += 5

        data = {}
        for chest in chests:
            reg = chest.region
            loc = chest.location
            if not reg in data:
                data[reg] = {}
            if not loc in data[reg]:
                data[reg][loc] = []
            data[reg][loc].append(chest)

        regions = sorted(data.keys())
        for reg in regions:
            print('='*(len(reg)+2))
            print('', reg)
            print('='*(len(reg)+2))
            print('')
            locations = sorted(data[reg].keys())
            for loc in locations:
                data[reg][loc].sort(key=lambda x: x.vanilla)
                print(' '*3, loc)
                print('')
                for chest in data[reg][loc]:
                    v = chest.vanilla.rjust(maxLength, ' ')
                    if chest.vanilla == chest.item:
                        # print(' '*6, v, chest.key)
                        print(' '*6, v)
                    else:
                        # print(' '*6, v, ' <-- ', chest.item, chest.key)
                        print(' '*6, v, ' <-- ', chest.item)
                print('')
                print('')
            print('')
            print('')

        sys.stdout = sys.__stdout__

    def hidden(self):
        outfile = os.path.join(self.outPath, 'spoiler_hidden_items.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        hidden = self.objectData.getHidden()
        maxVanillaLength = 0
        maxNPCLength = 0
        for h in hidden:
            maxVanillaLength = max(maxVanillaLength, len(h.vanilla))
            maxVanillaLength = max(maxVanillaLength, len(h.item))
            maxNPCLength = max(maxNPCLength, len(h.fromNPC))
        maxVanillaLength += 5

        data = {}
        for hi in hidden:
            reg = hi.region
            loc = hi.location
            if not reg in data:
                data[reg] = {}
            if not loc in data[reg]:
                data[reg][loc] = []
            data[reg][loc].append(hi)

        regions = sorted(data.keys())
        for reg in regions:
            print('='*(len(reg)+2))
            print('', reg)
            print('='*(len(reg)+2))
            print('')
            locations = sorted(data[reg].keys())
            for loc in locations:
                data[reg][loc].sort(key=lambda x: x.fromNPC)
                print(' '*3, loc)
                print('')
                for hi in data[reg][loc]:
                    v = hi.vanilla.rjust(maxVanillaLength, ' ')
                    n = hi.fromNPC.ljust(maxNPCLength, ' ')
                    if hi.vanilla == hi.item:
                        # print(' '*6, n, v, hi.key)
                        print(' '*6, n, v)
                    else:
                        # print(' '*6, n, v, ' <-- ', hi.item, hi.key)
                        print(' '*6, n, v, ' <-- ', hi.item)
                print('')
                print('')
            print('')
            print('')
        
        sys.stdout = sys.__stdout__

    def npc(self):
        outfile = os.path.join(self.outPath, 'spoiler_npc_items.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        print("Inaccuracies are likely due to NPCs relocating for events.")
        print("")
        print("Key items like Licenses should never be missable, but they might end up")
        print("on NPCs only accessible late in the game.")
        print("")
        print("For example, they won't be held by NPCs Osvald can only Mug in his Chapter 1,")
        print("but they can be held by NPCs only accessible at Frigid Isle after Osvald's")
        print("story is completed.") 
        print("")
        print("")
        print("")


        shops = self.shopDB.shops
        data = {}
        for shop in self.shopDB.shops.values():
            reg = shop[0].region
            loc = shop[0].location
            if not reg in data:
                data[reg] = {}
            if not loc in data[reg]:
                data[reg][loc] = []
            data[reg][loc].append(shop)

        maxLength = 0
        for shop in self.shopDB.shops.values():
            for si in shop:
                maxLength = max(maxLength, len(si.vanilla))
                maxLength = max(maxLength, len(si.item))
        maxLength += 5

        regions = sorted(data.keys())
        for reg in regions:
            print('='*(len(reg)+2))
            print('', reg)
            print('='*(len(reg)+2))
            print('')
            locations = sorted(data[reg].keys())
            for loc in locations:
                data[reg][loc].sort(key=lambda x: x[0].fromNPC)
                print(' '*3, loc)
                print(' '*3, '-'*len(loc))
                print('')
                for shop in data[reg][loc]:
                    print(' '*6, shop[0].fromNPC)
                    for si in shop:
                        v = si.vanilla.rjust(maxLength, ' ')
                        if si.vanilla == si.item:
                            # print(' '*6, v, si.key)
                            print(' '*6, v)
                        else:
                            # print(' '*6, v, ' <-- ', si.item, si.key)
                            print(' '*6, v, ' <-- ', si.item)
                    print('')
                print('')
                print('')
            print('')
            print('')

        sys.stdout = sys.__stdout__


class SpoilerJobs:
    def __init__(self, outPath):
        self.outPath = outPath
        self.jobData = Manager.getInstance('JobData').table
        self.pcData = Manager.getInstance('PlayableCharacterDB').table
        self.abilityData = Manager.getInstance('AbilityData').table
        self.supportData = Manager.getInstance('SupportAbilityData').table

        self.jobKeys = [
            'eFENCER', 'eHUNTER', 'eALCHEMIST', 'eMERCHANT',
            'ePRIEST', 'ePROFESSOR', 'eTHIEF', 'eDANCER',
        ]

        self.advJobKeys = [
            'eWEAPON_MASTER', 'eWIZARD', 'eSHAMAN', 'eINVENTOR',
        ]

        self.sortedBaseJobs = []
        self.sortedAdvJobs = []
        for key in self.jobKeys:
            self.sortedBaseJobs.append(self.jobData.getRow(key))
        for key in self.advJobKeys:
            self.sortedAdvJobs.append(self.jobData.getRow(key))
        self.sortedBaseJobs.sort(key=lambda x: x.name)
        self.sortedAdvJobs.sort(key=lambda x: x.name)

        self.sortedPCs = []
        for jKey in self.pcData.baseJobKeys:
            self.sortedPCs.append(self.pcData.getRow(jKey))
        self.sortedPCs.sort(key=lambda x: x.jobName)

    def stats(self):
        outfile = os.path.join(self.outPath, 'spoiler_job_stats.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        def adjust(s):
            return s.rjust(5, ' ')

        def printStatNames():
            statList = list(STATLIST)
            statList.remove('BP')
            statList.remove('MP')
            statList.remove('POT')
            strings = [adjust(s) for s in statList]
            print(' '*18, *strings)
            print('')

        print('============')
        print(' Base Stats ')
        print('============')
        print('')
        print('')
        printStatNames()
        for pc in self.sortedPCs:
            values = [adjust(f"{v}%") for v in pc.ParameterRevision.values()]
            values = values[:2] + values[5:]
            name = pc.jobName.ljust(14, ' ')
            print('   ', name, *values)

        print('')
        print('')
        print('=================')
        print(' Subclass Boosts ')
        print('=================')
        print('')
        print('')
        printStatNames()
        for i, job in enumerate(self.sortedBaseJobs + self.sortedAdvJobs):
            values = [adjust(f"{v-100}%") for v in job.ParameterRevision.values()]
            values = values[:2] + values[5:]
            name = job.name.ljust(14, ' ')
            if i == 8: print('')
            print('   ', name, *values)
        sys.stdout = sys.__stdout__

    def support(self):
        outfile = os.path.join(self.outPath, 'spoiler_job_support.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')
        print('================')
        print(' Support Skills ')
        print('================')
        print('')
        print('')
        for job in self.sortedBaseJobs + self.sortedAdvJobs:
            name = job.name.ljust(14, ' ')
            print(' '*3, name)
            for ability in job.supportAbilities:
                abilityName = self.supportData.getRow(ability).name
                print(' '*6, abilityName)
            print('')
        sys.stdout = sys.__stdout__

    def supportEMJob(self):
        outfile = os.path.join(self.outPath, 'spoiler_job_with_EM.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')
        for job in self.jobData:
            if job.hasEvasiveManeuvers:
                print(job.name, 'has Evasive Maneuvers')
        sys.stdout = sys.__stdout__

    def skills(self):
        outfile = os.path.join(self.outPath, 'spoiler_job_skills.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')
        print('================')
        print(' Command Skills ')
        print('================')
        print('')
        print('')
        jobKeys = self.jobData.baseJobKeys + self.jobData.advJobKeys
        pcMap = {}
        for pc in self.pcData:
            if pc.Id > 8: break
            k = pc.FirstJob.split('::')[1]
            pcMap[k] = pc
        for index, job in enumerate(self.sortedBaseJobs + self.sortedAdvJobs):
            jKey = job.key
            commands = self.jobData.getCommandAbilities(jKey)
            name = job.name
            print(' '*3, name)
            print(' '*3, '-'*len(name))
            print(' '*40, 'Weapon'.rjust(10, ' '), 'SP'.rjust(5, ' '), 'Power Change'.rjust(15, ' '))
            print('')
            for abilitySet in job.commandAbilities:
                ability = abilitySet.replace('_SET', '') + '_04'
                name = self.abilityData.getAbilityName(ability)
                weapon = self.abilityData.getAbilityWeapon(ability)
                if weapon == 'rod':
                    weapon = 'staff'
                if weapon == 'lance':
                    weapon = 'polearm'
                sp = self.abilityData.getAbilitySP(ability)
                ratioChange = self.abilityData.getAbilityRatioChange(ability)
                if ratioChange is None:
                    ratioChange = '---'
                else:
                    ratioChange = f"{round(ratioChange)}%"
                print(' '*6, name.ljust(33, ' '), weapon.rjust(10, ' '), str(sp).rjust(5, ' '), ratioChange.rjust(15, ' '))
            print('')
            print('')
            if index > 7:
                continue

            pc = pcMap[jKey]
            for abilitySet in pc.AdvancedAbility:
                ability = abilitySet['AbilityID'].value.replace('_SET', '') + '_01'
                name = self.abilityData.getAbilityName(ability)
                weapon = self.abilityData.getAbilityWeapon(ability)
                if weapon == 'rod':
                    weapon = 'staff'
                if weapon == 'lance':
                    weapon = 'polearm'
                sp = self.abilityData.getAbilitySP(ability)
                ratioChange = self.abilityData.getAbilityRatioChange(ability)
                if ratioChange is None:
                    ratioChange = '---'
                else:
                    ratioChange = f"{round(ratioChange)}%"
                print(' '*6, name.ljust(33, ' '), weapon.rjust(10, ' '), str(sp).rjust(5, ' '), ratioChange.rjust(15, ' '))
            print('')
            print('')

        sys.stdout = sys.__stdout__


class SpoilerBosses:
    def __init__(self, outPath):
        self.outPath = outPath
        self.enemyGroups = Manager.getInstance('EnemyGroupData').table

    def bosses(self):
        outfile = os.path.join(self.outPath, 'spoiler_bosses.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        maxLength = 0
        for group in self.enemyGroups:
            if group.vanillaBoss:
                maxLength = max(maxLength, len(group.vanillaBoss))
                maxLength = max(maxLength, len(group.randoBoss))
        maxLength += 5

        print('===================')
        print(' Main Story Bosses ')
        print('===================')
        print('')
        print('')

        groups = {
            'Agnea': [
                'ENG_BOS_DAN_C01_010',
                'ENG_BOS_DAN_C02_010',
                'ENG_BOS_DAN_C04_010',
                'ENG_BOS_DAN_C05_010',
                'ENG_BOS_DAN_C05_020',
            ],
            'Castti': [
                'ENG_BOS_APO_C01_010',
                'ENG_BOS_APO_C02_010',
                'ENG_BOS_APO_C02_020',
                'ENG_BOS_APO_C05_010',
            ],
            'Hikari': [
                'ENG_BOS_WAR_C01_010',
                'ENG_BOS_WAR_C02_010',
                'ENG_BOS_WAR_C04_010',
                'ENG_BOS_WAR_C05_010',
                'ENG_BOS_WAR_C05_020',
                'ENG_BOS_WAR_C05_030',
            ],
            'Partitio': [
                'ENG_BOS_MER_C01_010',
                'ENG_BOS_MER_C02_010',
                'ENG_BOS_MER_C03_010',
                'ENG_BOS_MER_C05_010',
            ],
            'Temenos': [
                'ENG_BOS_CLE_C01_010',
                'ENG_BOS_CLE_C02_010',
                'ENG_BOS_CLE_C03_010',
                'ENG_BOS_CLE_C05_010',
            ],
            'Osvald': [
                'ENG_BOS_SCH_C01_010',
                'ENG_BOS_SCH_C03_010',
                'ENG_BOS_SCH_C04_010',
                'ENG_BOS_SCH_C05_010',
            ],
            'Ochette': [
                'ENG_BOS_HUN_C01_010',
                'ENG_BOS_HUN_C02_010',
                'ENG_BOS_HUN_C02_020',
                'ENG_BOS_HUN_C05_010',
                'ENG_BOS_HUN_C05_020',
            ],
            'Throne': [
                'ENG_BOS_THI_C01_010',
                'ENG_BOS_THI_C02_010',
                'ENG_BOS_THI_C03_010',
                'ENG_BOS_THI_C03_020',
                'ENG_BOS_THI_C05_010',
            ],
            'Crossovers': [
                'ENG_EVE_APO_THI_010',
                'ENG_EVE_APO_THI_020',
            ],
            'Extra': [
                'ENG_BOS_LST_C02_020',
                'ENG_EVE_LST_EXT_010',
                'ENG_BOS_LST_C03_060',
                'ENG_BOS_LST_C03_070',
            ],
        }

        for k, v in groups.items():
            print('  ', k)
            for vi in v:
                g = getattr(self.enemyGroups, vi)
                vb = g.vanillaBoss.rjust(maxLength, ' ')
                b = g.randoBoss.ljust(maxLength, ' ')
                if g.vanillaBoss == g.randoBoss:
                    print('    ', vb)
                else:
                    print('    ', vb, '<--', b)
            print('')

        print('')
        print('=================')
        print(' Optional Bosses ')
        print('=================')
        print('')
        print('')

        groups = {
            'Mid game': [],
            'Late game': [],
            'Galdera': [],
        }

        for g in self.enemyGroups:
            if g.bossType == 'optional':
                if g.ring == 2:
                    groups['Mid game'].append(g)
                elif g.ring == 3:
                    groups['Late game'].append(g)
            if g.bossType == 'galdera':
                groups['Galdera'].append(g)

        groups['Mid game'].sort(key=lambda x: x.vanillaBoss)
        groups['Late game'].sort(key=lambda x: x.vanillaBoss)

        for k, v in groups.items():
            print('  ', k)
            for g in v:
                vb = g.vanillaBoss.rjust(maxLength, ' ')
                b = g.randoBoss.ljust(maxLength, ' ')
                if g.vanillaBoss == g.randoBoss:
                    print('    ', vb)
                else:
                    print('    ', vb, '<--', b)
            print('')

        sys.stdout = sys.__stdout__
