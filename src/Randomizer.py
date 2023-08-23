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
    def setSeed(self):
        random.seed(self.seed)
        self.seed += 1


class Rando:
    # Randomizers
    weapons = Nothing
    support = Nothing
    command = Nothing
    jpCosts = Nothing
    spCosts = Nothing
    abilityPower = Nothing
    jobStats = Nothing
    treasures = Nothing
    testing = Nothing
    processSpecies = Nothing
    abilityWeapons = Nothing
    shields = Nothing
    battles = Battles
    guilds = Guilds
    bosses = Bosses
    enemyGroups = Nothing
    pathActions = PathActions
    spurningRibbon = Nothing
    skipTutorials = Nothing
    initialEvents = InitialEvents

    # QOL
    jpNerf = Nothing

    def __init__(self, pakFile):
        Manager.Pak = MainPak(pakFile)

    def initialize(self, seed):
        Manager.clean()
        Manager.Pak.applyPatches()

        self._seed = RNGSeed(seed)
        self.outPath = f"seed_{seed}"
        if not os.path.isdir(self.outPath):
            os.makedirs(self.outPath)

        # Title
        self.titleImage = self.title()

        # Load datatables -- all stored in Manager.Instances
        # TODO: remove Row class attributes, rewrite tables/rows just to use Manager.getInstance as needed
        Manager.getTable('GameTextEN', table=TextTable, row=TextRow)
        Manager.getTable('ItemDB', table=ItemTable, row=ItemRow)
        Manager.getTable('PurchaseItemTable', table=ShopTable, row=ShopRow)
        Manager.getTable('NPCPurchaseData', table=NPCShopTable)
        Manager.getTable('AbilityData', table=AbilityTable, row=AbilityRow)
        Manager.getTable('EnemyDB', table=EnemyTable, row=EnemyRow)
        Manager.getTable('EnemyGroupData', table=EnemyGroupTable, row=EnemyGroupRow)
        Manager.getTable('NPCHearData')
        Manager.getTable('NPCLeadData')
        Manager.getTable('NPCBattleData')
        Manager.getTable('PlayableCharacterDB', table=PCTable, row=PCRow)
        Manager.getTable('JobData', table=JobTable, row=JobRow)
        Manager.getTable('SupportAbilityData', row=SupportRow)
        Manager.getTable('ObjectData', table=ObjectTable, row=ObjectRow)
        Manager.getTable('NPCData', row=NPCRow)
        Manager.getTable('AbilitySetData', table=AbilitySetTable, row=AbilitySetRow) # Has some dependency on Manager!
        Manager.getTable('InvadeData', row=InvadeRow)
        Manager.getTable('GuildData', table=GuildTable, row=GuildRow)
        Manager.getTable('ReminiscenceSetting', table=ReminiscenceTable, row=ReminiscenceRow)
        Manager.getTable('LinerShipRoute')
        Manager.getTable('DiseaseData')
        Manager.getTable('ShopList', table=ShopListTable, row=ShopListRow)

        # Spoiler logs
        self.spoilerJobs = SpoilerJobs(self.outPath)
        self.spoilerItems = SpoilerItems(self.outPath)
        self.spoilerBosses = SpoilerBosses(self.outPath)

    def failed(self):
        print(f"Randomizer failed! Removing directory {self.outPath}.")
        shutil.rmtree(self.outPath)

    def _run(self, obj):
        obj().run()

    def _randomize(self, obj):
        self._seed.setSeed()
        self._run(obj)

    def randomize(self):
        self._run(Rando.jpNerf) # Must be done before randomizing JP costs
        self._randomize(Rando.jpCosts)

        # Order matters for these PC & command dependent options
        self._randomize(Rando.abilityWeapons)
        self._randomize(Rando.weapons)
        self._randomize(Rando.command) # after weapons & abilityWeapons!
        self._randomize(Rando.guilds) # after commands!

        self._randomize(Rando.shields)
        self._randomize(Rando.spCosts)
        self._randomize(Rando.abilityPower)
        self._randomize(Rando.support)
        self._randomize(Rando.jobStats)
        self._randomize(Rando.treasures)
        self._randomize(Rando.processSpecies)
        self._randomize(Rando.enemyGroups)
        self._randomize(Rando.battles) # Keep enemy stat scaling after groups!
        self._randomize(Rando.bosses)

        # Default stuff
        self.titleImage.updateTitle()

    def qualityOfLife(self):
        self._run(Rando.spurningRibbon) # Make sure this is done AFTER support shuffling
        self._run(Rando.pathActions)
        self._run(Rando.skipTutorials)
        self._run(Rando.initialEvents)

        # Softlock stuff
        if Battles.scaleLeaves == 0:
            preventMoneySoftlocks()
        if Battles.scaleExp == 0:
            preventExpSoftlocks()
        # Ensures enemies from early battles are breakable, primarily boss and event battles
        if Rando.weapons != Nothing or Rando.shields != Nothing or Rando.bosses != Nothing:
            preventWeaponSoftlocks()
        # Some bosses can be (nearly) unbeatable without some nerfing
        # Others are a joke thanks to an ally
        if Rando.bosses != Nothing:
            preventOverpoweredEarlyBosses()
            prologueShopsAddStones()
        # Ensure at least minor equippable weapons improvements exist in shops
        if Rando.weapons != Nothing:
            prologueShopsUpdateWeapons()

        # Testing stuff -- must be done last
        self._run(Rando.testing)

    def dump(self, fileName):
        # Spoilers
        self.spoilerJobs.stats()
        self.spoilerJobs.support()
        self.spoilerJobs.supportEMJob()
        self.spoilerJobs.skills()
        self.spoilerItems.chests()
        self.spoilerItems.hidden()
        self.spoilerItems.npc()
        self.spoilerBosses.bosses()

        # Build the patch
        Manager.updateAll()
        Manager.Pak.buildPak(fileName)


class Steam(Rando):
    def __init__(self, pakFile):
        super(Steam, self).__init__(pakFile)
        self.title = TitleSteam
    
    def dump(self, settings=None):
        if not os.path.isdir(self.outPath):
            os.makedirs(self.outPath)
        pakName = os.path.join(self.outPath, 'rando_P.pak')
        super(Steam, self).dump(pakName)

        # Settings for future reference
        if settings:
            filename = os.path.join(self.outPath, 'settings.json')
            with open(filename, 'w') as file:
                hjson.dump(settings, file)
