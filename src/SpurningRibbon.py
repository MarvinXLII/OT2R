import random
from Utility import WEAPONS, PCNAMESMAP
from Shuffler import Shuffler, Slot, noWeights
from Assets import Data
import sys

class SpurningRibbon:
    PC = 'None'

    @classmethod
    def run(cls):
        pcDB = Data.getInstance('PlayableCharacterDB')
        def addAccessory(pcKey):
            pc = pcDB.table.getRow(pcKey)
            pc.FirstEquipment['Accessory_00'] = 'ITM_EQP_ACS_031'

        if cls.PC == 'All':
            for pcKey in PCNAMESMAP.values():
                addAccessory(pcKey)
            # Set sell price to 1 so people won't abuse it
            itemDB = Data.getInstance('ItemDB')
            itemDB.table.ITM_EQP_ACS_031.SellPrice = 1
        elif cls.PC == 'PC with EM':
            jobDB = Data.getInstance('JobData')
            for row in jobDB.table:
                if row.hasEvasiveManeuvers:
                    addAccessory(row.key)
                    break
            else:
                sys.exit(f"Could not find job with Evasive Maneuvers")
        elif cls.PC in PCNAMESMAP:
            addAccessory(PCNAMESMAP[cls.PC])
        else:
            sys.exit(f"spurningRibbon not setup for {PlayableCharacters.SpurningRibbon}")

