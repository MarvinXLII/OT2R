from Assets import Data
import os
import sys
import hjson

from Databases import *
from Utility import STATLIST, get_filename
import hjson


class SpoilerItems:
    def __init__(self, outPath):
        self.outPath = outPath
        self.gameText = Data.getInstance('GameTextEN')
        self.itemData = Data.getInstance('ItemDB')
        self.objectData = Data.getInstance('ObjectData')
        self.npcData = Data.getInstance('NPCData')
        self.shopDB = Data.getInstance('PurchaseItemTable')
        with open(get_filename('json/treasure.json'), 'r', encoding='utf-8') as file:
            self.locations = hjson.load(file)

    def chests(self):
        outfile = os.path.join(self.outPath, 'spoiler_chests.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        chests = self.objectData.getChests()
        maxLength = 0
        for chest in chests:
            maxLength = max(maxLength, len(chest.vanilla))
            maxLength = max(maxLength, len(chest.item))
        maxLength += 5
        
        for chest in chests:
            if not chest.isPlaced:
                continue
            if chest.key not in self.locations:
                loc = "UNKNOWN LOCATION"
            else:
                loc = self.locations[chest.key]
            if chest.vanilla == '':
                assert chest.item == ''
                continue
            v = chest.vanilla.rjust(maxLength, ' ')
            i = chest.item.ljust(maxLength, ' ')
            if chest.item != chest.vanilla:
                # print(chest.key, loc, v, ' <-- ', i)
                print(loc, v, ' <-- ', i)
            else:
                # print(chest.key, loc, v)
                print(loc, v)
        
        sys.stdout = sys.__stdout__

    def hidden(self):
        outfile = os.path.join(self.outPath, 'spoiler_hidden_items.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        hidden = self.objectData.getHidden()
        maxLength = 0
        for h in hidden:
            maxLength = max(maxLength, len(h.vanilla))
            maxLength = max(maxLength, len(h.item))
        maxLength += 5
        
        for h in hidden:
            if not h.isPlaced:
                continue
            if h.key not in self.locations:
                loc = "UNKNOWN LOCATION"
            else:
                loc = self.locations[h.key]
            if h.vanilla == '':
                assert h.item == ''
                continue
            if h.vanilla == 'None':
                assert h.item == 'None'
                continue
            v = h.vanilla.rjust(maxLength, ' ')
            i = h.item.ljust(maxLength, ' ')
            if h.item != h.vanilla:
                # print(h.key, loc, v, ' <-- ', i)
                print(loc, v, ' <-- ', i)
            else:
                # print(h.key, loc, v)
                print(loc, v)
        
        sys.stdout = sys.__stdout__

    def npc(self):
        myShopData = hjson.load(open(get_filename('json/myNPCShopData.json'), 'r', encoding='utf-8'))
        shopData = hjson.load(open(get_filename('json/orgNPCShopData.json'), 'r', encoding='utf-8'))
        outfile = os.path.join(self.outPath, 'spoiler_npc_items.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')
        locations = sorted(list(myShopData.keys()) + list(shopData.keys()))
        for loc in locations:
            try:
                shops = myShopData[loc]
            except:
                shops = shopData[loc]
            shopsToPrint = []
            for npc in shops:
                if npc['shop']:
                    shopsToPrint.append(npc)
            if shopsToPrint:
                print(loc)
                print('')
                for shop in shopsToPrint:
                    if shop['placed']:
                        print('  ', shop['name'])
                    else:
                        print('  ', shop['name'], '  (might not exist in game)')
                    for inv in shop['shop']:
                        row = self.shopDB.table.getRow(inv)
                        if row is None: continue
                        if row.vanilla != row.item:
                            # print('      ', row.key, row.FCPrice, row.vanilla, ' <-- ', row.item)
                            print('      ', row.FCPrice, row.vanilla, ' <-- ', row.item)
                        else:
                            # print('      ', row.key, row.FCPrice, row.vanilla)
                            print('      ', row.FCPrice, row.vanilla)
                    print('')
                print('')

        
        for npc in self.npcData.table:
            print(npc.name)
            for i in npc.inventory:
                vItem = i.vanilla
                sItem = i.item
                if sItem == vItem:
                    # print('  ', i.key, i.FCPrice, i.vanilla)
                    print('  ', i.FCPrice, i.vanilla)
                else:
                    # print('  ', i.key, i.FCPrice, i.vanilla, ' <-- ', i.item)
                    print('  ', i.FCPrice, i.vanilla, ' <-- ', i.item)
            print('')

        sys.stdout = sys.__stdout__


class SpoilerJobs:
    def __init__(self, outPath):
        self.outPath = outPath
        self.gameText = Data.getInstance('GameTextEN')
        self.jobData = Data.getInstance('JobData')
        self.pcData = Data.getInstance('PlayableCharacterDB')
        self.abilityData = Data.getInstance('AbilityData')
        self.supportData = Data.getInstance('SupportAbilityData')

        self.jobKeys = [
            'eFENCER', 'eHUNTER', 'eALCHEMIST', 'eMERCHANT',
            'ePRIEST', 'ePROFESSOR', 'eTHIEF', 'eDANCER',
        ]

        self.advJobKeys = [
            'eWEAPON_MASTER', 'eWIZARD', 'eSHAMAN', 'eINVENTOR',
        ]


    def stats(self):
        outfile = os.path.join(self.outPath, 'spoiler_job_stats.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')

        def adjust(s):
            return s.rjust(5, ' ')

        def printStatNames():
            statList = list(STATLIST)
            statList.remove('BP')
            statList.remove('SP')
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
        for jKey in self.pcData.baseJobKeys:
            pc = self.pcData.table.getRow(jKey)
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
        jobKeys = self.jobData.baseJobKeys + self.jobData.advJobKeys
        for jKey in jobKeys:
            job = self.jobData.table.getRow(jKey)
            values = [adjust(f"{v-100}%") for v in job.ParameterRevision.values()]
            values = values[:2] + values[5:]
            name = job.name.ljust(14, ' ')
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
        jobKeys = self.jobData.baseJobKeys + self.jobData.advJobKeys
        for jKey in jobKeys:
            job = self.jobData.table.getRow(jKey)
            name = job.name.ljust(14, ' ')
            print(' '*3, name)
            for ability in job.supportAbilities:
                abilityName = self.supportData.getSupportAbilityName(ability)
                print(' '*6, abilityName)
            print('')
        sys.stdout = sys.__stdout__

    def supportEMJob(self):
        outfile = os.path.join(self.outPath, 'spoiler_job_with_EM.txt')
        sys.stdout = open(outfile, 'w', encoding='utf-8')
        for job in self.jobData.table:
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
        for pc in self.pcData.table:
            if pc.Id > 8: break
            k = pc.FirstJob.split('::')[1]
            pcMap[k] = pc
        for index, jKey in enumerate(jobKeys):
            commands = self.jobData.getCommandAbilities(jKey)
            job = self.jobData.table.getRow(jKey)
            name = job.name
            print(' '*3, name)
            print(' '*3, '-'*len(name))
            print(' '*40, 'Weapon'.rjust(10, ' '), 'SP'.rjust(5, ' '), 'Power Change'.rjust(15, ' '))
            print('')
            for abilitySet in job.commandAbilities:
                ability = abilitySet.replace('_SET', '') + '_04'
                name = self.abilityData.getAbilityName(ability)
                weapon = self.abilityData.getAbilityWeapon(ability)
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
