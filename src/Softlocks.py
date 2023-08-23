import random
from Nothing import Nothing
from Manager import Manager
from DataTable import DataTable
from Battles import Battles
from Nothing import Nothing


def preventMoneySoftlocks():
    shipTable = Manager.getInstance('LinerShipRoute').table
    shopTable = Manager.getInstance('PurchaseItemTable').table
    enemyTable = Manager.getInstance('EnemyDB').table

    # Boat travel costs -- theoretically a softlock, but probably not necessary
    for row in shipTable:
        row.Price = 1

    # Unfinished boat -- not really a softlock, but perhaps a bit tedious
    shopTable.NPC_SHO_EX1_0120_NPCBUY_01.FCPrice = 1

    # Partitio boss -- require gaining at least 1 leaf
    enemyTable.ENE_BOS_MER_C05_010.Money = 1


def preventExpSoftlocks():
    shopTable = Manager.getInstance('PurchaseItemTable').table
    hearTable = Manager.getInstance('NPCHearData').table
    battleTable = Manager.getInstance('NPCBattleData').table
    enemyTable = Manager.getInstance('EnemyDB').table

    # Osvald's Chapter 3 -- not really softlocks, just 50-70% rates
    hearTable.FC_INFO_NPC_GAK_40_0100.SearchBaseProbability = 100.0 # Harvey's Whereabouts
    hearTable.FC_INFO_NPC_GAK_40_0200.SearchBaseProbability = 100.0 # An Eyewitness to Harvey
    hearTable.FC_INFO_NPC_GAK_40_0300.SearchBaseProbability = 100.0 # Library Rumor

    # Throne's Chapter 2 -- not really softlock, 65%
    shopTable.NPC_TOU_2A_0100_NPCBUY_01.ProperSteal = -15 # Horse Coin

    # Throne's Chapter 2 -- Father's Route
    battleTable.FC_B_NPC_TOU_2B_0100.AssassinateNeedLevel = 1 # Thug
    battleTable.FC_B_NPC_TOU_2B_0200.AssassinateNeedLevel = 1 # Lookout
    battleTable.FC_B_NPC_TOU_2B_0300.AssassinateNeedLevel = 1 # Thug
    battleTable.FC_B_NPC_TOU_2B_0400.AssassinateNeedLevel = 1 # Thug

    # Throne's Chapter 4
    battleTable.FC_B_NPC_TOU_40_0100.AssassinateNeedLevel = 1 # Blacksnake

    # Agnea Chapter 2
    shopTable.NPC_ODO_20_0100_NPCBUY_01.ProperBeg = 1 # Theater Ticket

    # Agnea Chapter 4
    shopTable.NPC_ODO_40_0100_NPCBUY_01.ProperBeg = 1 # Cute Shoes

    # Castti Chapter 2
    hearTable.FC_INFOLINK_NPC_KUS_2B_0100.HearNeedLevel = 1 # Young Man
    hearTable.FC_INFOLINK_NPC_KUS_2B_0200.HearNeedLevel = 1 # Young Woman
    hearTable.FC_INFOLINK_NPC_KUS_2B_0300.HearNeedLevel = 1 # Elderly Woman
    hearTable.FC_INFOLINK_NPC_KUS_2B_0700.HearNeedLevel = 1 # Rosa
    hearTable.FC_INFOLINK_NPC_KUS_2B_0800.HearNeedLevel = 1 # Melia (11)
    hearTable.FC_INFOLINK_NPC_KUS_2B_0810.HearNeedLevel = 1 # Melia (12)

    # Castti Chapter 2 - Sai Route
    hearTable.FC_INFO_NPC_KUS_2A_0100.HearNeedLevel = 1 # Mao
    hearTable.FC_INFO_NPC_KUS_2A_0200.HearNeedLevel = 1 # Griff

    # Temenos & Throne
    battleTable.FC_B_NPC_COP_ST2_0100.AssassinateNeedLevel = 1 # Guard

    # Agnea & Hikari Ch 2
    shopTable.NPC_Twn_Dst_3_1_A_TALK_0510_NPCBUY_03.ProperBeg = 1 # Citizen
    shopTable.NPC_Twn_Dst_3_1_A_TALK_0310_NPCBUY_04.ProperBeg = 1 # Carpenter
    shopTable.NPC_Twn_Dst_3_1_B_TALK_0610_NPCBUY_03.ProperBeg = 1 # Official
    battleTable.FC_B_NPC_COP_OK2_0500.BattleNeedLevel = 1 # Yomi


# TODO: change all weakness updates to be done by group rather than enemy
def preventWeaponSoftlocks():
    enemyTable = Manager.getInstance('EnemyDB').table
    enemyGroupTable = Manager.getInstance('EnemyGroupData').table
    jobTable = Manager.getInstance('JobData').table
    pcTable = Manager.getInstance('PlayableCharacterDB').table

    ## Can Latent Powers be used at this point? Include just in case.
    enemyTable.ENE_NPC_SIN_10_0400.addWeaponWeaknessToPC(jobTable.temenos)
    ## Can use other jobs at this point, so no softlock
    # enemyTable.ENE_NPC_SIN_20_100.addWeaknessToPC(jobTable.temenos)

    # Ochette's Ch 1 battle with the Iguana
    enemyTable.ENE_EVE_HUN_ISD_010.addWeaponWeaknessToPC(jobTable.ochette)
    enemyTable.ENE_EVE_HUN_ISD_020.addWeaknessToPC(jobTable.ochette)

    # include Ch 1 bosses
    # -- doesn't include summoned enemies, e.g. Ochette's boss
    enemyTable.ENE_BOS_DAN_C01_010.addWeaknessToPC(jobTable.agnea)
    enemyTable.ENE_BOS_DAN_C01_020.addWeaknessToPC(jobTable.agnea)
    enemyTable.ENE_BOS_APO_C01_010.addWeaknessToPC(jobTable.castti)
    enemyTable.ENE_BOS_APO_C01_020.addWeaknessToPC(jobTable.castti)
    enemyTable.ENE_BOS_WAR_C01_010.addWeaknessToPC(jobTable.hikari)
    enemyTable.ENE_BOS_WAR_C01_020.addWeaknessToPC(jobTable.hikari)
    enemyTable.ENE_BOS_MER_C01_010.addWeaknessToPC(jobTable.partitio)
    enemyTable.ENE_BOS_MER_C01_020.addWeaknessToPC(jobTable.partitio)
    enemyTable.ENE_BOS_MER_C01_030.addWeaknessToPC(jobTable.partitio)
    enemyTable.ENE_BOS_HUN_C01_010.addWeaknessToPC(jobTable.ochette)
    enemyTable.ENE_BOS_SCH_C01_010.addWeaknessToPC(jobTable.osvald)
    enemyTable.ENE_BOS_SCH_C01_020.addWeaknessToPC(jobTable.osvald)
    enemyTable.ENE_BOS_SCH_C01_030.addWeaknessToPC(jobTable.osvald)
    enemyTable.ENE_BOS_CLE_C01_010.addWeaknessToPC(jobTable.temenos)
    enemyTable.ENE_BOS_THI_C01_010.addWeaknessToPC(jobTable.throne)


    # Other mandatory battles in Chapter 1 too early for guaranteeing magic weaknesses
    enemyTable.ENE_NPC_GAK_10_020.addWeaponWeaknessToPC(jobTable.osvald)
    # enemyTable.ENE_EVE_SCH_SNW_010.addWeaponWeaknessToPC(jobTable.osvald) ## Weak to Emerald by default

    # Other mandatory battles
    enemyTable.ENE_NPC_KEN_40_010.addWeaponWeaknessToPC(jobTable.getRow('eGUEST_JOB_008')) # Jin Mei, Hikari's Ch 4 flashback

    # Other mandatory groups
    enemyGroupTable.ENG_EVE_WAR_C01_010.updateWeaknessToPCs(weaponOnly=True) # Hikari Ch. 1 battle 1
    enemyGroupTable.ENG_EVE_WAR_C01_020.updateWeaknessToPCs(weaponOnly=True) # Hikari Ch. 1 battle 2
    enemyGroupTable.ENG_EVE_WAR_C01_030.updateWeaknessToPCs(weaponOnly=True) # Hikari Ch. 1 battle 3
    enemyGroupTable.ENG_NPC_TWN_DST_3_1_A_050.updateWeaknessToPCs(weaponOnly=True) # Hikari Ch. 1 challenge
