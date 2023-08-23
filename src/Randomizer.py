import os
import shutil
import random
from dataclasses import dataclass
import sys
sys.path.append('src')
from Manager import Manager
from Pak import Pak, MainPak
from DataTable import Row
# from Text import GameText, TalkData
from Nothing import Nothing
from Image import TitleSteam
from Spoilers import *
from Databases import *
from Shields import *
from Battles import Battles
from PathActions import PathActions
from DataTable import Row
from SpurningRibbon import SpurningRibbon
from Guilds import Guilds
from Softlocks import *
from Bosses import *
# from Testing import Testing
from Databases import *
from SkipTutorials import *
from Events import InitialEvents

@dataclass
class RNGSeed:
    seed: int

    # Start on a new seed every time to allow for toggling options on/off while
    # preserving all other settings
    def set_seed(self):
        random.seed(self.seed)
        self.seed += 1


class Rando:
    # Randomizers
    weapons = Nothing
    support = Nothing
    command = Nothing
    jp_costs = Nothing
    sp_costs = Nothing
    ability_power = Nothing
    job_stats = Nothing
    treasures = Nothing
    testing = Nothing
    process_species = Nothing
    ability_weapons = Nothing
    shields = Nothing
    battles = Battles
    guilds = Guilds
    bosses = Bosses
    enemy_groups = Nothing
    path_actions = PathActions
    spurning_ribbon = Nothing
    skip_tutorials = Nothing
    initial_events = InitialEvents

    # QOL
    jp_nerf = Nothing

    def __init__(self, pakfile):
        Manager.Pak = MainPak(pakfile)

    def add_patches(self, patch_list):
        Manager.Pak.patches = patch_list

    def initialize(self, seed):
        Manager.initialize()
        Manager.Pak.apply_patches()

        self._seed = RNGSeed(seed)
        self.out_path = f"seed_{seed}"
        if not os.path.isdir(self.out_path):
            os.makedirs(self.out_path)

        # Title
        self.title_image = self.title()

        # Load datatables -- all stored in Manager.Instances
        # TODO: remove Row class attributes, rewrite tables/rows just to use Manager.get_instance as needed
        Manager.get_table('GameTextEN', table=TextTable, row=TextRow)
        Manager.get_table('ItemDB', table=ItemTable, row=ItemRow)
        Manager.get_table('PurchaseItemTable', table=ShopTable, row=ShopRow)
        Manager.get_table('NPCPurchaseData', table=NPCShopTable)
        Manager.get_table('AbilityData', table=AbilityTable, row=AbilityRow)
        Manager.get_table('EnemyDB', table=EnemyTable, row=EnemyRow)
        Manager.get_table('EnemyGroupData', table=EnemyGroupTable, row=EnemyGroupRow)
        Manager.get_table('NPCHearData')
        Manager.get_table('NPCLeadData')
        Manager.get_table('NPCBattleData')
        Manager.get_table('PlayableCharacterDB', table=PCTable, row=PCRow)
        Manager.get_table('JobData', table=JobTable, row=JobRow)
        Manager.get_table('SupportAbilityData', row=SupportRow)
        Manager.get_table('ObjectData', table=ObjectTable, row=ObjectRow)
        Manager.get_table('NPCData', row=NPCRow)
        Manager.get_table('AbilitySetData', table=AbilitySetTable, row=AbilitySetRow) # Has some dependency on Manager!
        Manager.get_table('InvadeData', row=InvadeRow)
        Manager.get_table('GuildData', table=GuildTable, row=GuildRow)
        Manager.get_table('ReminiscenceSetting', table=ReminiscenceTable, row=ReminiscenceRow)
        Manager.get_table('LinerShipRoute')
        Manager.get_table('DiseaseData')
        Manager.get_table('ShopList', table=ShopListTable, row=ShopListRow)

        # Spoiler logs
        self.spoiler_jobs = SpoilerJobs(self.out_path)
        self.spoiler_items = SpoilerItems(self.out_path)
        self.spoiler_bosses = SpoilerBosses(self.out_path)

    def failed(self):
        print(f"Randomizer failed! Removing directory {self.out_path}.")
        shutil.rmtree(self.out_path)

    def _run(self, obj):
        obj().run()

    def _randomize(self, obj):
        self._seed.set_seed()
        self._run(obj)

    def randomize(self):
        self._run(Rando.jp_nerf) # Must be done before randomizing JP costs
        self._randomize(Rando.jp_costs)

        # Order matters for these PC & command dependent options
        self._randomize(Rando.ability_weapons)
        self._randomize(Rando.weapons)
        self._randomize(Rando.command) # after weapons & ability_weapons!
        self._randomize(Rando.guilds) # after commands!

        self._randomize(Rando.shields)
        self._randomize(Rando.sp_costs)
        self._randomize(Rando.ability_power)
        self._randomize(Rando.support)
        self._randomize(Rando.job_stats)
        self._randomize(Rando.treasures)
        self._randomize(Rando.process_species)
        self._randomize(Rando.enemy_groups)
        self._randomize(Rando.battles) # Keep enemy stat scaling after groups!
        self._randomize(Rando.bosses)

        # Default stuff
        self.title_image.updateTitle()

    def qualityOfLife(self):
        self._seed.set_seed() # SpurningRibbon QOL might still need RNG
        self._run(Rando.spurning_ribbon) # Make sure this is done AFTER support shuffling
        self._run(Rando.path_actions)
        self._run(Rando.skip_tutorials)
        self._run(Rando.initial_events)

        # Softlock stuff
        if Battles.scale_leaves == 0:
            prevent_money_softlocks()
        if Battles.scale_exp == 0:
            prevent_exp_softlocks()
        # Ensures enemies from early battles are breakable, primarily boss and event battles
        if Rando.weapons != Nothing or Rando.shields != Nothing or Rando.bosses != Nothing:
            prevent_weapon_softlocks()
        # Some bosses can be (nearly) unbeatable without some nerfing
        # Others are a joke thanks to an ally
        if Rando.bosses != Nothing:
            prevent_overpowered_early_bosses()
            prologue_shops_add_stones()
        # Ensure at least minor equippable weapons improvements exist in shops
        if Rando.weapons != Nothing:
            prologue_shops_update_weapons()

        # Testing stuff -- must be done last
        self._run(Rando.testing)

    def dump(self, filename):
        # Spoilers
        self.spoiler_jobs.stats()
        self.spoiler_jobs.support()
        self.spoiler_jobs.support_em_job()
        self.spoiler_jobs.skills()
        self.spoiler_items.chests()
        self.spoiler_items.hidden()
        self.spoiler_items.npc()
        self.spoiler_bosses.bosses()

        # Build the patch
        Manager.update_all()
        Manager.Pak.build_pak(filename)


class Steam(Rando):
    def __init__(self, pakfile):
        super(Steam, self).__init__(pakfile)
        self.title = TitleSteam
    
    def dump(self, settings=None):
        if not os.path.isdir(self.out_path):
            os.makedirs(self.out_path)
        pakname = os.path.join(self.out_path, 'rando_P.pak')
        super(Steam, self).dump(pakname)

        # Settings for future reference
        if settings:
            filename = os.path.join(self.out_path, 'settings.json')
            with open(filename, 'w') as file:
                hjson.dump(settings, file)
