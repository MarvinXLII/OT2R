from Manager import Manager
import os
import sys
import hjson

from Databases import *
from Utility import STATLIST, get_filename
import hjson


class SpoilerItems:
    def __init__(self, outpath):
        self.outpath = outpath
        self.object_db = Manager.get_instance('ObjectData').table
        self.shop_db = Manager.get_instance('PurchaseItemTable').table

    def chests(self):
        outfile = os.path.join(self.outpath, 'spoiler_chests.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        chests = self.object_db.get_chests()
        max_length = 0
        for chest in chests:
            max_length = max(max_length, len(chest.vanilla))
            max_length = max(max_length, len(chest.item))
        max_length += 5

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
                    v = chest.vanilla.rjust(max_length, ' ')
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
        outfile = os.path.join(self.outpath, 'spoiler_hidden_items.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        hidden = self.object_db.get_hidden()
        max_vanilla_length = 0
        max_npc_length = 0
        for h in hidden:
            max_vanilla_length = max(max_vanilla_length, len(h.vanilla))
            max_vanilla_length = max(max_vanilla_length, len(h.item))
            max_npc_length = max(max_npc_length, len(h.from_npc))
        max_vanilla_length += 5

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
                data[reg][loc].sort(key=lambda x: x.from_npc)
                print(' '*3, loc)
                print('')
                for hi in data[reg][loc]:
                    v = hi.vanilla.rjust(max_vanilla_length, ' ')
                    n = hi.from_npc.ljust(max_npc_length, ' ')
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
        outfile = os.path.join(self.outpath, 'spoiler_npc_items.txt')
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


        shops = self.shop_db.shops
        data = {}
        for shop in self.shop_db.shops.values():
            reg = shop[0].region
            loc = shop[0].location
            if not reg in data:
                data[reg] = {}
            if not loc in data[reg]:
                data[reg][loc] = []
            data[reg][loc].append(shop)

        max_length = 0
        for shop in self.shop_db.shops.values():
            for si in shop:
                max_length = max(max_length, len(si.vanilla))
                max_length = max(max_length, len(si.item))
        max_length += 5

        regions = sorted(data.keys())
        for reg in regions:
            print('='*(len(reg)+2))
            print('', reg)
            print('='*(len(reg)+2))
            print('')
            locations = sorted(data[reg].keys())
            for loc in locations:
                data[reg][loc].sort(key=lambda x: x[0].from_npc)
                print(' '*3, loc)
                print(' '*3, '-'*len(loc))
                print('')
                for shop in data[reg][loc]:
                    print(' '*6, shop[0].from_npc)
                    for si in shop:
                        v = si.vanilla.rjust(max_length, ' ')
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
    def __init__(self, outpath):
        self.outpath = outpath
        self.job_db = Manager.get_instance('JobData').table
        self.pc_db = Manager.get_instance('PlayableCharacterDB').table
        self.ability_db = Manager.get_instance('AbilityData').table
        self.support_db = Manager.get_instance('SupportAbilityData').table

        self.job_keys = [
            'eFENCER', 'eHUNTER', 'eALCHEMIST', 'eMERCHANT',
            'ePRIEST', 'ePROFESSOR', 'eTHIEF', 'eDANCER',
        ]

        self.adv_job_keys = [
            'eWEAPON_MASTER', 'eWIZARD', 'eSHAMAN', 'eINVENTOR',
        ]

        self.sorted_base_jobs = []
        self.sorted_adv_jobs = []
        for key in self.job_keys:
            self.sorted_base_jobs.append(self.job_db.get_row(key))
        for key in self.adv_job_keys:
            self.sorted_adv_jobs.append(self.job_db.get_row(key))
        self.sorted_base_jobs.sort(key=lambda x: x.name)
        self.sorted_adv_jobs.sort(key=lambda x: x.name)

        self.sorted_pcs = []
        for jKey in self.pc_db.base_job_keys:
            self.sorted_pcs.append(self.pc_db.get_row(jKey))
        self.sorted_pcs.sort(key=lambda x: x.job_name)

    def stats(self):
        outfile = os.path.join(self.outpath, 'spoiler_job_stats.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        def adjust(s):
            return s.rjust(5, ' ')

        def print_stat_names():
            stat_list = list(STATLIST)
            stat_list.remove('BP')
            stat_list.remove('MP')
            stat_list.remove('POT')
            strings = [adjust(s) for s in stat_list]
            print(' '*18, *strings)
            print('')

        print('============')
        print(' Base Stats ')
        print('============')
        print('')
        print('')
        print_stat_names()
        for pc in self.sorted_pcs:
            values = [adjust(f"{v}%") for v in pc.ParameterRevision.values()]
            values = values[:2] + values[5:]
            name = pc.job_name.ljust(14, ' ')
            print('   ', name, *values)

        print('')
        print('')
        print('=================')
        print(' Subclass Boosts ')
        print('=================')
        print('')
        print('')
        print_stat_names()
        for i, job in enumerate(self.sorted_base_jobs + self.sorted_adv_jobs):
            values = [adjust(f"{v-100}%") for v in job.ParameterRevision.values()]
            values = values[:2] + values[5:]
            name = job.name.ljust(14, ' ')
            if i == 8: print('')
            print('   ', name, *values)
        sys.stdout = sys.__stdout__

    def support(self):
        outfile = os.path.join(self.outpath, 'spoiler_job_support.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')
        print('================')
        print(' Support Skills ')
        print('================')
        print('')
        print('')
        for job in self.sorted_base_jobs + self.sorted_adv_jobs:
            name = job.name.ljust(14, ' ')
            print(' '*3, name)
            for ability in job.support_abilities:
                ability_name = self.support_db.get_row(ability).name
                print(' '*6, ability_name)
            print('')
        sys.stdout = sys.__stdout__

    def support_em_job(self):
        outfile = os.path.join(self.outpath, 'spoiler_job_with_EM.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')
        for job in self.job_db:
            if job.has_evasive_maneuvers:
                print(job.name, 'has Evasive Maneuvers')
        sys.stdout = sys.__stdout__

    def skills(self):
        outfile = os.path.join(self.outpath, 'spoiler_job_skills.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')
        print('================')
        print(' Command Skills ')
        print('================')
        print('')
        print('')
        job_keys = self.job_db.base_job_keys + self.job_db.adv_job_keys
        pc_map = {}
        for pc in self.pc_db:
            if pc.Id > 8: break
            k = pc.FirstJob.split('::')[1]
            pc_map[k] = pc
        for index, job in enumerate(self.sorted_base_jobs + self.sorted_adv_jobs):
            jKey = job.key
            commands = self.job_db.get_command_abilities(jKey)
            name = job.name
            print(' '*3, name)
            print(' '*3, '-'*len(name))
            print(' '*40, 'Weapon'.rjust(10, ' '), 'SP'.rjust(5, ' '), 'Power Change'.rjust(15, ' '))
            print('')
            for ability_set in job.command_abilities:
                ability = ability_set.replace('_SET', '') + '_04'
                name = self.ability_db.get_ability_name(ability)
                weapon = self.ability_db.get_ability_weapon(ability)
                if weapon == 'rod':
                    weapon = 'staff'
                if weapon == 'lance':
                    weapon = 'polearm'
                sp = self.ability_db.get_ability_sp(ability)
                ratio_change = self.ability_db.get_ability_ratio_change(ability)
                if ratio_change is None:
                    ratio_change = '---'
                else:
                    ratio_change = f"{round(ratio_change)}%"
                print(' '*6, name.ljust(33, ' '), weapon.rjust(10, ' '), str(sp).rjust(5, ' '), ratio_change.rjust(15, ' '))
            print('')
            print('')
            if index > 7:
                continue

            pc = pc_map[jKey]
            for ability_set in pc.AdvancedAbility:
                ability = ability_set['AbilityID'].value.replace('_SET', '') + '_01'
                name = self.ability_db.get_ability_name(ability)
                weapon = self.ability_db.get_ability_weapon(ability)
                if weapon == 'rod':
                    weapon = 'staff'
                if weapon == 'lance':
                    weapon = 'polearm'
                sp = self.ability_db.get_ability_sp(ability)
                ratio_change = self.ability_db.get_ability_ratio_change(ability)
                if ratio_change is None:
                    ratio_change = '---'
                else:
                    ratio_change = f"{round(ratio_change)}%"
                print(' '*6, name.ljust(33, ' '), weapon.rjust(10, ' '), str(sp).rjust(5, ' '), ratio_change.rjust(15, ' '))
            print('')
            print('')

        sys.stdout = sys.__stdout__


class SpoilerBosses:
    def __init__(self, outpath):
        self.outpath = outpath
        self.enemy_groups = Manager.get_instance('EnemyGroupData').table

    def bosses(self):
        outfile = os.path.join(self.outpath, 'spoiler_bosses.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        max_length = 0
        for group in self.enemy_groups:
            if group.vanilla_boss:
                max_length = max(max_length, len(group.vanilla_boss))
                max_length = max(max_length, len(group.rando_boss))
        max_length += 5

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
                g = getattr(self.enemy_groups, vi)
                vb = g.vanilla_boss.rjust(max_length, ' ')
                b = g.rando_boss.ljust(max_length, ' ')
                if g.vanilla_boss == g.rando_boss:
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

        for g in self.enemy_groups:
            if g.boss_type == 'optional':
                if g.ring == 2:
                    groups['Mid game'].append(g)
                elif g.ring == 3:
                    groups['Late game'].append(g)
            if g.boss_type == 'galdera':
                groups['Galdera'].append(g)

        groups['Mid game'].sort(key=lambda x: x.vanilla_boss)
        groups['Late game'].sort(key=lambda x: x.vanilla_boss)

        for k, v in groups.items():
            print('  ', k)
            for g in v:
                vb = g.vanilla_boss.rjust(max_length, ' ')
                b = g.rando_boss.ljust(max_length, ' ')
                if g.vanilla_boss == g.rando_boss:
                    print('    ', vb)
                else:
                    print('    ', vb, '<--', b)
            print('')

        sys.stdout = sys.__stdout__
