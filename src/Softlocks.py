import random
from Nothing import Nothing
from Manager import Manager
from DataTable import DataTable
from Battles import Battles
from Nothing import Nothing


def preventMoneySoftlocks():
    # shipTable = Manager.getInstance('LinerShipRoute').table
    # shopTable = Manager.getInstance('PurchaseItemTable').table
    enemies = Manager.getInstance('EnemyDB').table

    # # Boat travel costs -- theoretically a softlock, but probably not necessary
    # for row in shipTable:
    #     row.Price = 1

    # # Unfinished boat -- not really a softlock, but perhaps a bit tedious
    # shopTable.NPC_SHO_EX1_0120_NPCBUY_01.FCPrice = 1

    # Partitio boss -- require gaining at least 1 leaf
    enemies.ENE_BOS_MER_C05_010.Money = 1


def preventExpSoftlocks():
    shopTable = Manager.getInstance('PurchaseItemTable').table
    hearTable = Manager.getInstance('NPCHearData').table
    battleTable = Manager.getInstance('NPCBattleData').table

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
    enemies = Manager.getInstance('EnemyDB').table
    enemyGroups = Manager.getInstance('EnemyGroupData').table
    jobs = Manager.getInstance('JobData').table

    # Temenos Coerce battles
    enemies.ENE_NPC_SIN_10_0400.addWeaponWeaknessToPC(jobs.temenos)
    # SHOULD have jobs/lychees at this point
    # enemies.ENE_NPC_SIN_20_100.addWeaknessToPC(jobs.temenos)

    # Ochette's Ch 1 battle with the Iguana
    enemies.ENE_EVE_HUN_ISD_010.addWeaponWeaknessToPC(jobs.ochette)
    enemies.ENE_EVE_HUN_ISD_020.addWeaknessToPC(jobs.ochette)

    # include Ch 1 bosses
    # - add allies?
    # - those with allies don't really need the weapon only constraint, but it could be added later
    #   -- agnea's ally can heal her SP easily
    # - meh, if a PC has multiple magic spells, players can pick the wrong magic and sort of get stuck...
    #   make all weaponOnly just because...
    enemyGroups.ENG_BOS_DAN_C01_010.updateWeaknessToPCs(jobs.agnea, jobs.gus, weaponOnly=True)
    enemyGroups.ENG_BOS_APO_C01_010.updateWeaknessToPCs(jobs.castti, weaponOnly=True)
    enemyGroups.ENG_BOS_WAR_C01_010.updateWeaknessToPCs(jobs.hikari, weaponOnly=True)
    enemyGroups.ENG_BOS_MER_C01_010.updateWeaknessToPCs(jobs.partitio, weaponOnly=True)
    enemyGroups.ENG_BOS_HUN_C01_010.updateWeaknessToPCs(jobs.ochette, weaponOnly=True)
    enemyGroups.ENG_BOS_SCH_C01_010.updateWeaknessToPCs(jobs.osvald, jobs.emerald, weaponOnly=True)
    enemyGroups.ENG_BOS_CLE_C01_010.updateWeaknessToPCs(jobs.temenos, jobs.crick, weaponOnly=True)
    enemyGroups.ENG_BOS_THI_C01_010.updateWeaknessToPCs(jobs.throne, weaponOnly=True)

    # Other mandatory battles in Chapter 1 too early for guaranteeing magic weaknesses
    enemies.ENE_NPC_GAK_10_020.addWeaponWeaknessToPC(jobs.osvald)
    enemies.ENE_EVE_SCH_SNW_010.addWeaponWeaknessToPC(jobs.osvald, jobs.emerald)

    # Other mandatory battles
    enemies.ENE_NPC_KEN_40_010.addWeaponWeaknessToPC(jobs.hikariFlashback) # Jin Mei, Hikari's Ch 4 flashback

    # Other mandatory groups
    enemyGroups.ENG_EVE_WAR_C01_010.updateWeaknessToPCs(jobs.hikari, jobs.ritsu, weaponOnly=True) # Hikari Ch. 1 battle 1
    enemyGroups.ENG_EVE_WAR_C01_020.updateWeaknessToPCs(jobs.hikari, jobs.ritsu, jobs.raiMei, weaponOnly=True) # Hikari Ch. 1 battle 2
    enemyGroups.ENG_EVE_WAR_C01_030.updateWeaknessToPCs(jobs.hikari, jobs.ritsu, jobs.raiMei, weaponOnly=True) # Hikari Ch. 1 battle 3
    enemyGroups.ENG_NPC_TWN_DST_3_1_A_050.updateWeaknessToPCs(jobs.hikari, weaponOnly=True) # Hikari Ch. 1 challenge

    ##### MAKE SURE BOSS ALLIES ARE WEAK TO THE PC'S WEAPONS TOO!
    def updateEnemyCalledAllies(job, group):
        boss = getattr(enemies, group.enemyKeys[0]).key
        if boss == 'ENE_BOS_DAN_C01_010': # Agnea et al vs Duorduor
            enemies.ENE_BOS_DAN_C01_020.addWeaponWeaknessToPC(job)
        elif boss == 'ENE_BOS_HUN_C01_010': # Ochette vs Dark Entity
            enemies.ENE_BOS_HUN_C01_020.addWeaponWeaknessToPC(job)
        elif boss == 'ENE_BOS_WAR_C01_010': # Hikari vs Ritsu
            pass
        elif boss == 'ENE_BOS_MER_C01_010': # Partitio vs Giff
            pass
        elif boss == 'ENE_BOS_SCH_C01_010': # Osvald vs Warden Davids
            enemies.ENE_BOS_SCH_C01_030.addWeaponWeaknessToPC(job)
        elif boss == 'ENE_BOS_APO_C01_010': # Castti vs Veron & Doron
            pass
        elif boss == 'ENE_BOS_CLE_C01_010': # Temenos et al vs Felvarg
            pass
        elif boss == 'ENE_BOS_MER_C01_010': # Throne vs Pirro
            pass

    updateEnemyCalledAllies(jobs.agnea, enemyGroups.ENG_BOS_DAN_C01_010)
    updateEnemyCalledAllies(jobs.castti, enemyGroups.ENG_BOS_APO_C01_010)
    updateEnemyCalledAllies(jobs.hikari, enemyGroups.ENG_BOS_WAR_C01_010)
    updateEnemyCalledAllies(jobs.partitio, enemyGroups.ENG_BOS_MER_C01_010)
    updateEnemyCalledAllies(jobs.ochette, enemyGroups.ENG_BOS_HUN_C01_010)
    updateEnemyCalledAllies(jobs.osvald, enemyGroups.ENG_BOS_SCH_C01_010)
    updateEnemyCalledAllies(jobs.temenos, enemyGroups.ENG_BOS_CLE_C01_010)
    updateEnemyCalledAllies(jobs.throne, enemyGroups.ENG_BOS_THI_C01_010)


def preventOverpoweredEarlyBosses():
    # Vanilla stats for reference
    # Duorduor: 3600 HP
    # Dark Entity: 2500 HP
    # Ritsu: 1850 HP
    # Giff: 1050 HP
    # Warden Davids: 2700 HP
    # Veron/Doron: 950 each
    # Felvarg: 3600 HP
    # Pirro: 2100 HP
    enemyGroup = Manager.getInstance('EnemyGroupData').table
    enemyDB = Manager.getInstance('EnemyDB').table

    def increaseStatsForTeam(group):
        bosses = [getattr(enemyDB, e) for e in group.enemyKeys]
        enemies = group.enemyKeys
        if 'ENE_BOS_DAN_C01_010' in enemies: # Agnea et al vs Duorduor
            pass # It's the player's fault they boosted these stats
        elif 'ENE_BOS_HUN_C01_010' in enemies: # Ochette vs Dark Entity
            assert enemies[0] == 'ENE_BOS_HUN_C01_010'
            if bosses[0].Param['HP'] < 3500:
                bosses[0].Param['HP'] = 3500
        elif 'ENE_BOS_WAR_C01_010' in enemies: # Hikari vs Ritsu
            assert enemies[0] == 'ENE_BOS_WAR_C01_010'
            if bosses[0].Param['HP'] < 2500:
                bosses[0].Param['HP'] = 2500
        elif 'ENE_BOS_MER_C01_010' in enemies: # Partitio vs Giff
            assert enemies[0] == 'ENE_BOS_MER_C01_010'
            if bosses[0].Param['HP'] < 2500:
                bosses[0].Param['HP'] = 2500
        elif 'ENE_BOS_SCH_C01_010' in enemies: # Osvald vs Warden Davids
            pass # It's the player's fault they boosted these stats
        elif 'ENE_BOS_APO_C01_010' in enemies: # Castti vs Veron & Doron
            assert enemies[0] == 'ENE_BOS_APO_C01_010'
            assert enemies[1] == 'ENE_BOS_APO_C01_020'
            if bosses[0].Param['HP'] < 1500:
                bosses[0].Param['HP'] = 1500
            if bosses[1].Param['HP'] < 1500:
                bosses[1].Param['HP'] = 1500
        elif 'ENE_BOS_CLE_C01_010' in enemies: # Temenos et al vs Felvarg
            pass # It's the player's fault they boosted these stats
        elif 'ENE_BOS_MER_C01_010' in enemies: # Throne vs Pirro
            assert enemies[0] == 'ENE_BOS_MER_C01_010'
            if bosses[0].Param['HP'] < 2500:
                bosses[0].Param['HP'] = 2500

    def decreaseStatsForSolo(group):
        bosses = [getattr(enemyDB, e) for e in group.enemyKeys]
        enemies = group.enemyKeys
        if 'ENE_BOS_DAN_C01_010' in enemies: # Agnea et al vs Duorduor
            assert enemies[0] == 'ENE_BOS_DAN_C01_010'
            if bosses[0].Param['HP'] > 1800:
                bosses[0].Param['HP'] = 1800
        elif 'ENE_BOS_HUN_C01_010' in enemies: # Ochette vs Dark Entity
            pass # It's the player's fault if they boosted these stats
        elif 'ENE_BOS_WAR_C01_010' in enemies: # Hikari vs Ritsu
            pass # It's the player's fault if they boosted these stats
        elif 'ENE_BOS_MER_C01_010' in enemies: # Partitio vs Giff
            pass # It's the player's fault if they boosted these stats
        elif 'ENE_BOS_SCH_C01_010' in enemies: # Osvald vs Warden Davids
            assert enemies[0] == 'ENE_BOS_SCH_C01_010'
            if bosses[0].Param['HP'] > 1800:
                bosses[0].Param['HP'] = 1800
            # Remove 1 enemy
            group.EnemyID[2] = 'None'
            # Adjust Warden Davids' ability to call more enemies
            abilityDB = Manager.getInstance('AbilityData').table
            ailments = abilityDB.ABI_BOS_SCH_C01_010_005.Ailment
            ailments[1] = ailments[2]
        elif 'ENE_BOS_APO_C01_010' in enemies: # Castti vs Veron & Doron
            pass # It's the player's fault if they boosted these stats
        elif 'ENE_BOS_CLE_C01_010' in enemies: # Temenos et al vs Felvarg
            # This boss is very strong!
            # NB: one of his attacks is specifically for Temenos and will never hit the current PC.
            assert enemies[0] == 'ENE_BOS_CLE_C01_010'
            if bosses[0].Param['HP'] > 1600:
                bosses[0].Param['HP'] = 1600
        elif 'ENE_BOS_MER_C01_010' in enemies: # Throne vs Pirro
            pass # It's the player's fault if they boosted these stats

    increaseStatsForTeam(enemyGroup.earlyAgnea)
    increaseStatsForTeam(enemyGroup.earlyOsvald)
    increaseStatsForTeam(enemyGroup.earlyTemenos)
    decreaseStatsForSolo(enemyGroup.earlyHikari)
    decreaseStatsForSolo(enemyGroup.earlyOchette)
    decreaseStatsForSolo(enemyGroup.earlyCastti)
    decreaseStatsForSolo(enemyGroup.earlyPartitio)
    decreaseStatsForSolo(enemyGroup.earlyThrone)


def prologueShopsUpdateWeapons():
    shopList = Manager.getInstance('ShopList').table
    shopData = Manager.getInstance('PurchaseItemTable').table
    jobs = Manager.getInstance('JobData').table

    # Change slots so each weapon type is available
    shopData.NPC_KEN_PrologueSHOP_03.ItemLabel = 'ITM_EQP_SWD_041'
    shopData.NPC_KUS_PrologueSHOP_03.ItemLabel = 'ITM_EQP_ROD_040'

    # Update shop inventory
    shopList.prologueAgnea.addPrologueShopWeapons(jobs.agnea.equippableWeapons)
    shopList.prologueCastti.addPrologueShopWeapons(jobs.castti.equippableWeapons)
    shopList.prologueHikari.addPrologueShopWeapons(jobs.hikari.equippableWeapons)
    shopList.prologueOchette.addPrologueShopWeapons(jobs.ochette.equippableWeapons)
    shopList.prologueOsvald.addPrologueShopWeapons(jobs.osvald.equippableWeapons)
    shopList.prologuePartitio.addPrologueShopWeapons(jobs.partitio.equippableWeapons)
    shopList.prologueTemenos.addPrologueShopWeapons(jobs.temenos.equippableWeapons)
    shopList.prologueThrone.addPrologueShopWeapons(jobs.throne.equippableWeapons)


def prologueShopsAddStones():
    shopList = Manager.getInstance('ShopList').table

    # Adds all stones, might be overkill; maybe limit to boss weakness?
    def addStones(shopName, n=None):
        shop = getattr(shopList, shopName)
        shop.addFireSoulstone()
        shop.addIceSoulstone()
        shop.addThunderSoulstone()
        shop.addWindSoulstone()
        shop.addLightSoulstone()
        shop.addDarkSoulstone()

    addStones('prologueAgnea')
    addStones('prologueCastti')
    addStones('prologueHikari')
    addStones('prologueOchette')
    addStones('prologueOsvald')
    addStones('prologuePartitio')
    addStones('prologueTemenos')
    addStones('prologueThrone')
