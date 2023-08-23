import os
import shutil
import random
from dataclasses import dataclass
import sys
sys.path.append('src')
from Pak import Pak, MainPak
from Assets import Data
from Text import GameText, TalkData
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
from Testing import Testing

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
    battles = Battles  # All settings are set directly to this classes attributes
    guilds = Guilds
    enemyGroups = Nothing
    pathActions = PathActions
    spurningRibbon = Nothing

    # QOL
    jpNerf = Nothing

    def __init__(self, pakFile):
        self.pak = MainPak(pakFile)
        Data.pak = self.pak

    def initialize(self, seed):
        Data.clean()
        self.pak.applyPatches()

        self._seed = RNGSeed(seed)
        self.outPath = f"seed_{seed}"
        if not os.path.isdir(self.outPath):
            os.makedirs(self.outPath)

        # Title
        self.titleImage = self.title()

        # Load datatables -- all stored in Data.Instances
        GameText()
        ItemDB()
        EnemyDB()
        NPCHearData()
        NPCLeadData()
        NPCBattleData()
        NPCShopDB()
        PCDB()
        JobDB()
        SupportDB()
        AbilityDB()
        ObjectDB()
        ShopDB()
        NPCDB()
        EnemyGroupDB()
        AbilitySetDB()
        InvadeDB()
        GuildDB()

        # Spoiler logs
        self.spoilerJobs = SpoilerJobs(self.outPath)
        self.spoilerItems = SpoilerItems(self.outPath)

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
        self._randomize(Rando.battles)
        self._randomize(Rando.enemyGroups)

        # Default stuff
        self.titleImage.updateTitle()

    def qualityOfLife(self):
        self._run(Rando.spurningRibbon) # Make sure this is done AFTER support shuffling
        self._run(Rando.pathActions)

        # Softlock stuff, main for exp/money scaling
        if Battles.scaleLeaves == 0:
            preventMoneySoftlocks()
        if Battles.scaleExp == 0:
            preventExpSoftlocks()
        if Rando.weapons != Nothing or Rando.shields:
            preventWeaponSoftlocks()

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

        # Build the patch
        Data.updateAll()
        Data.pak.buildPak(fileName)


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
