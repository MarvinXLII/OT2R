import random
from Nothing import Nothing
from Assets import Data
from DataTable import DataTable
from Battles import Battles
from Nothing import Nothing

def preventMoneySoftlocks():
    ship = DataTable.getInstance('LinerShipRoute')
    shopDB = Data.getInstance('PurchaseItemTable')
    enemyDB = DataTable.getInstance('EnemyDB')

    # Boat travel costs -- theoretically a softlock, but probably not necessary
    for row in ship.table:
        row.Price = 1

    # Unfinished boat -- not really a softlock, but perhaps a bit tedious
    shopDB.table.NPC_SHO_EX1_0120_NPCBUY_01.FCPrice = 1

    # Partitio boss -- require gaining at least 1 leaf
    enemyDB.table.ENE_BOS_MER_C05_010.Money = 1


def preventExpSoftlocks():
    shopDB = Data.getInstance('PurchaseItemTable')
    hearDB = Data.getInstance('NPCHearData')
    battleDB = Data.getInstance('NPCBattleData')
    enemyDB = DataTable.getInstance('EnemyDB')

    # Osvald's Chapter 3 -- not really softlocks, just 50-70% rates
    hearDB.table.FC_INFO_NPC_GAK_40_0100.SearchBaseProbability = 100.0 # Harvey's Whereabouts
    hearDB.table.FC_INFO_NPC_GAK_40_0200.SearchBaseProbability = 100.0 # An Eyewitness to Harvey
    hearDB.table.FC_INFO_NPC_GAK_40_0300.SearchBaseProbability = 100.0 # Library Rumor

    # Throne's Chapter 2 -- not really softlock, 65%
    shopDB.table.NPC_TOU_2A_0100_NPCBUY_01.ProperSteal = -15 # Horse Coin

    # Throne's Chapter 2 -- Father's Route
    battleDB.table.FC_B_NPC_TOU_2B_0100.AssassinateNeedLevel = 1 # Thug
    battleDB.table.FC_B_NPC_TOU_2B_0200.AssassinateNeedLevel = 1 # Lookout
    battleDB.table.FC_B_NPC_TOU_2B_0300.AssassinateNeedLevel = 1 # Thug
    battleDB.table.FC_B_NPC_TOU_2B_0400.AssassinateNeedLevel = 1 # Thug

    # Throne's Chapter 4
    battleDB.table.FC_B_NPC_TOU_40_0100.AssassinateNeedLevel = 1 # Blacksnake

    # Agnea Chapter 2
    shopDB.table.NPC_ODO_20_0100_NPCBUY_01.ProperBeg = 1 # Theater Ticket

    # Agnea Chapter 4
    shopDB.table.NPC_ODO_40_0100_NPCBUY_01.ProperBeg = 1 # Cute Shoes

    # Castti Chapter 2
    hearDB.table.FC_INFOLINK_NPC_KUS_2B_0100.HearNeedLevel = 1 # Young Man
    hearDB.table.FC_INFOLINK_NPC_KUS_2B_0200.HearNeedLevel = 1 # Young Woman
    hearDB.table.FC_INFOLINK_NPC_KUS_2B_0300.HearNeedLevel = 1 # Elderly Woman
    hearDB.table.FC_INFOLINK_NPC_KUS_2B_0700.HearNeedLevel = 1 # Rosa
    hearDB.table.FC_INFOLINK_NPC_KUS_2B_0800.HearNeedLevel = 1 # Melia (11)
    hearDB.table.FC_INFOLINK_NPC_KUS_2B_0810.HearNeedLevel = 1 # Melia (12)

    # Castti Chapter 2 - Sai Route
    hearDB.table.FC_INFO_NPC_KUS_2A_0100.HearNeedLevel = 1 # Mao
    hearDB.table.FC_INFO_NPC_KUS_2A_0200.HearNeedLevel = 1 # Griff


def preventWeaponSoftlocks():
    enemyDB = DataTable.getInstance('EnemyDB').table
    jobDB = DataTable.getInstance('JobData')

    ## Can Latent Powers be used at this point? Include just in case.
    ## MAKE SURE THIS IS WEAPON ONLY!
    ## OTHERWISE MIGHT BE LIMITED TO MAGIC THAT MUST BE BOUGHT WITH JP
    ## TOO EARLY TO GRIND!
    enemyDB.ENE_NPC_SIN_10_0400.addWeaponWeaknessToPC(jobDB.temenos)
    ## Can use other jobs at this point, so no softlock
    # enemyDB.ENE_NPC_SIN_20_100.addWeaknessToPC(jobDB.temenos)

    # Ochette's Ch 1 battle with the Iguana
    enemyDB.ENE_EVE_HUN_ISD_010.addWeaponWeaknessToPC(jobDB.ochette)
    enemyDB.ENE_EVE_HUN_ISD_020.addWeaknessToPC(jobDB.ochette)

    # include Ch 1 bosses
    # -- doesn't include summoned enemies, e.g. Ochette's boss
    enemyDB.ENE_BOS_DAN_C01_010.addWeaknessToPC(jobDB.agnea)
    enemyDB.ENE_BOS_DAN_C01_020.addWeaknessToPC(jobDB.agnea)
    enemyDB.ENE_BOS_APO_C01_010.addWeaknessToPC(jobDB.castti)
    enemyDB.ENE_BOS_APO_C01_020.addWeaknessToPC(jobDB.castti)
    enemyDB.ENE_BOS_WAR_C01_010.addWeaknessToPC(jobDB.hikari)
    enemyDB.ENE_BOS_WAR_C01_020.addWeaknessToPC(jobDB.hikari)
    enemyDB.ENE_BOS_MER_C01_010.addWeaknessToPC(jobDB.partitio)
    enemyDB.ENE_BOS_MER_C01_020.addWeaknessToPC(jobDB.partitio)
    enemyDB.ENE_BOS_MER_C01_030.addWeaknessToPC(jobDB.partitio)
    enemyDB.ENE_BOS_HUN_C01_010.addWeaknessToPC(jobDB.ochette)
    enemyDB.ENE_BOS_SCH_C01_010.addWeaknessToPC(jobDB.osvald)
    enemyDB.ENE_BOS_SCH_C01_020.addWeaknessToPC(jobDB.osvald)
    enemyDB.ENE_BOS_SCH_C01_030.addWeaknessToPC(jobDB.osvald)
    enemyDB.ENE_BOS_CLE_C01_010.addWeaknessToPC(jobDB.temenos)
    enemyDB.ENE_BOS_THI_C01_010.addWeaknessToPC(jobDB.throne)
