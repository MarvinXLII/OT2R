import random
from Nothing import Nothing
from Manager import Manager
from DataTable import DataTable
from Battles import Battles
from Nothing import Nothing


def prevent_money_softlocks():
    # ship_db = Manager.get_instance('LinerShipRoute').table
    # shop_db = Manager.get_instance('PurchaseItemTable').table
    enemy_db = Manager.get_instance('EnemyDB').table

    # # Boat travel costs -- theoretically a softlock, but probably not necessary
    # for row in ship_db:
    #     row.Price = 1

    # # Unfinished boat -- not really a softlock, but perhaps a bit tedious
    # shop_db.NPC_SHO_EX1_0120_NPCBUY_01.FCPrice = 1

    # Partitio boss -- require gaining at least 1 leaf
    enemy_db.ENE_BOS_MER_C05_010.Money = 1


def prevent_exp_softlocks():
    shop_db = Manager.get_instance('PurchaseItemTable').table
    hear_db = Manager.get_instance('NPCHearData').table
    battle_db = Manager.get_instance('NPCBattleData').table

    # Osvald's Chapter 3 -- not really softlocks, just 50-70% rates
    hear_db.FC_INFO_NPC_GAK_40_0100.SearchBaseProbability = 100.0 # Harvey's Whereabouts
    hear_db.FC_INFO_NPC_GAK_40_0200.SearchBaseProbability = 100.0 # An Eyewitness to Harvey
    hear_db.FC_INFO_NPC_GAK_40_0300.SearchBaseProbability = 100.0 # Library Rumor

    # Throne's Chapter 2 -- not really softlock, 65%
    shop_db.NPC_TOU_2A_0100_NPCBUY_01.ProperSteal = -15 # Horse Coin

    # Throne's Chapter 2 -- Father's Route
    battle_db.FC_B_NPC_TOU_2B_0100.AssassinateNeedLevel = 1 # Thug
    battle_db.FC_B_NPC_TOU_2B_0200.AssassinateNeedLevel = 1 # Lookout
    battle_db.FC_B_NPC_TOU_2B_0300.AssassinateNeedLevel = 1 # Thug
    battle_db.FC_B_NPC_TOU_2B_0400.AssassinateNeedLevel = 1 # Thug

    # Throne's Chapter 4
    battle_db.FC_B_NPC_TOU_40_0100.AssassinateNeedLevel = 1 # Blacksnake

    # Agnea Chapter 2
    shop_db.NPC_ODO_20_0100_NPCBUY_01.ProperBeg = 1 # Theater Ticket

    # Agnea Chapter 4
    shop_db.NPC_ODO_40_0100_NPCBUY_01.ProperBeg = 1 # Cute Shoes

    # Castti Chapter 2
    hear_db.FC_INFOLINK_NPC_KUS_2B_0100.HearNeedLevel = 1 # Young Man
    hear_db.FC_INFOLINK_NPC_KUS_2B_0200.HearNeedLevel = 1 # Young Woman
    hear_db.FC_INFOLINK_NPC_KUS_2B_0300.HearNeedLevel = 1 # Elderly Woman
    hear_db.FC_INFOLINK_NPC_KUS_2B_0700.HearNeedLevel = 1 # Rosa
    hear_db.FC_INFOLINK_NPC_KUS_2B_0800.HearNeedLevel = 1 # Melia (11)
    hear_db.FC_INFOLINK_NPC_KUS_2B_0810.HearNeedLevel = 1 # Melia (12)

    # Castti Chapter 2 - Sai Route
    hear_db.FC_INFO_NPC_KUS_2A_0100.HearNeedLevel = 1 # Mao
    hear_db.FC_INFO_NPC_KUS_2A_0200.HearNeedLevel = 1 # Griff

    # Temenos & Throne
    battle_db.FC_B_NPC_COP_ST2_0100.AssassinateNeedLevel = 1 # Guard

    # Agnea & Hikari Ch 2
    shop_db.NPC_Twn_Dst_3_1_A_TALK_0510_NPCBUY_03.ProperBeg = 1 # Citizen
    shop_db.NPC_Twn_Dst_3_1_A_TALK_0310_NPCBUY_04.ProperBeg = 1 # Carpenter
    shop_db.NPC_Twn_Dst_3_1_B_TALK_0610_NPCBUY_03.ProperBeg = 1 # Official
    battle_db.FC_B_NPC_COP_OK2_0500.BattleNeedLevel = 1 # Yomi


# TODO: change all weakness updates to be done by group rather than enemy
def prevent_weapon_softlocks():
    enemy_db = Manager.get_instance('EnemyDB').table
    enemy_group_db = Manager.get_instance('EnemyGroupData').table
    job_db = Manager.get_instance('JobData').table

    # Temenos Coerce battles
    enemy_db.ENE_NPC_SIN_10_0400.add_weapon_weakness_to_pc(job_db.temenos)
    # SHOULD have job_db/lychees at this point
    enemy_db.ENE_NPC_SIN_20_100.add_weakness_to_pc(job_db.temenos)
    enemy_db.ENE_NPC_COP_ST1_040.add_weakness_to_pc(job_db.temenos)

    # Ochette's Ch 1 battle with the Iguana
    enemy_db.ENE_EVE_HUN_ISD_010.add_weapon_weakness_to_pc(job_db.ochette)
    enemy_db.ENE_EVE_HUN_ISD_020.add_weakness_to_pc(job_db.ochette)

    # include Ch 1 bosses
    # - add allies?
    # - those with allies don't really need the weapon only constraint, but it could be added later
    #   -- agnea's ally can heal her SP easily
    # - meh, if a PC has multiple magic spells, players can pick the wrong magic and sort of get stuck...
    #   make all weapon_only just because...
    enemy_group_db.ENG_BOS_DAN_C01_010.update_weakness_to_pcs(job_db.agnea, job_db.gus, weapon_only=True)
    enemy_group_db.ENG_BOS_APO_C01_010.update_weakness_to_pcs(job_db.castti, weapon_only=True)
    enemy_group_db.ENG_BOS_WAR_C01_010.update_weakness_to_pcs(job_db.hikari, weapon_only=True)
    enemy_group_db.ENG_BOS_MER_C01_010.update_weakness_to_pcs(job_db.partitio, weapon_only=True)
    enemy_group_db.ENG_BOS_HUN_C01_010.update_weakness_to_pcs(job_db.ochette, weapon_only=True)
    enemy_group_db.ENG_BOS_SCH_C01_010.update_weakness_to_pcs(job_db.osvald, job_db.emerald, weapon_only=True)
    enemy_group_db.ENG_BOS_CLE_C01_010.update_weakness_to_pcs(job_db.temenos, job_db.crick, weapon_only=True)
    enemy_group_db.ENG_BOS_THI_C01_010.update_weakness_to_pcs(job_db.throne, weapon_only=True)

    # Other mandatory battles in Chapter 1 too early for guaranteeing magic weaknesses
    enemy_db.ENE_NPC_GAK_10_020.add_weapon_weakness_to_pc(job_db.osvald)
    enemy_db.ENE_EVE_SCH_SNW_010.add_weapon_weakness_to_pc(job_db.osvald, job_db.emerald)

    # Other mandatory battles
    enemy_db.ENE_NPC_KEN_40_010.add_weapon_weakness_to_pc(job_db.hikari_flashback) # Jin Mei, Hikari's Ch 4 flashback

    # Other mandatory groups
    enemy_group_db.ENG_EVE_WAR_C01_010.update_weakness_to_pcs(job_db.hikari, job_db.ritsu, weapon_only=True) # Hikari Ch. 1 battle 1
    enemy_group_db.ENG_EVE_WAR_C01_020.update_weakness_to_pcs(job_db.hikari, job_db.ritsu, job_db.rai_mei, weapon_only=True) # Hikari Ch. 1 battle 2
    enemy_group_db.ENG_EVE_WAR_C01_030.update_weakness_to_pcs(job_db.hikari, job_db.ritsu, job_db.rai_mei, weapon_only=True) # Hikari Ch. 1 battle 3
    enemy_group_db.ENG_NPC_TWN_DST_3_1_A_050.update_weakness_to_pcs(job_db.hikari, weapon_only=True) # Hikari Ch. 1 challenge

    ##### MAKE SURE BOSS ALLIES ARE WEAK TO THE PC'S WEAPONS TOO!
    def update_enemy_called_allies(job, group):
        boss = getattr(enemy_db, group.enemy_keys[0]).key
        if boss == 'ENE_BOS_DAN_C01_010': # Agnea et al vs Duorduor
            enemy_db.ENE_BOS_DAN_C01_020.add_weapon_weakness_to_pc(job)
        elif boss == 'ENE_BOS_HUN_C01_010': # Ochette vs Dark Entity
            enemy_db.ENE_BOS_HUN_C01_020.add_weapon_weakness_to_pc(job)
        elif boss == 'ENE_BOS_WAR_C01_010': # Hikari vs Ritsu
            pass
        elif boss == 'ENE_BOS_MER_C01_010': # Partitio vs Giff
            pass
        elif boss == 'ENE_BOS_SCH_C01_010': # Osvald vs Warden Davids
            enemy_db.ENE_BOS_SCH_C01_030.add_weapon_weakness_to_pc(job)
        elif boss == 'ENE_BOS_APO_C01_010': # Castti vs Veron & Doron
            pass
        elif boss == 'ENE_BOS_CLE_C01_010': # Temenos et al vs Felvarg
            pass
        elif boss == 'ENE_BOS_MER_C01_010': # Throne vs Pirro
            pass

    update_enemy_called_allies(job_db.agnea, enemy_group_db.ENG_BOS_DAN_C01_010)
    update_enemy_called_allies(job_db.castti, enemy_group_db.ENG_BOS_APO_C01_010)
    update_enemy_called_allies(job_db.hikari, enemy_group_db.ENG_BOS_WAR_C01_010)
    update_enemy_called_allies(job_db.partitio, enemy_group_db.ENG_BOS_MER_C01_010)
    update_enemy_called_allies(job_db.ochette, enemy_group_db.ENG_BOS_HUN_C01_010)
    update_enemy_called_allies(job_db.osvald, enemy_group_db.ENG_BOS_SCH_C01_010)
    update_enemy_called_allies(job_db.temenos, enemy_group_db.ENG_BOS_CLE_C01_010)
    update_enemy_called_allies(job_db.throne, enemy_group_db.ENG_BOS_THI_C01_010)


def prevent_overpowered_early_bosses():
    # Vanilla stats for reference
    # Duorduor: 3600 HP
    # Dark Entity: 2500 HP
    # Ritsu: 1850 HP
    # Giff: 1050 HP
    # Warden Davids: 2700 HP
    # Veron/Doron: 950 each
    # Felvarg: 3600 HP
    # Pirro: 2100 HP
    enemy_group = Manager.get_instance('EnemyGroupData').table
    enemy_db = Manager.get_instance('EnemyDB').table

    def increase_stats_for_team(group):
        bosses = [getattr(enemy_db, e) for e in group.enemy_keys]
        enemies = group.enemy_keys
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

    def decrease_stats_for_solo(group):
        bosses = [getattr(enemy_db, e) for e in group.enemy_keys]
        enemies = group.enemy_keys
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
            ability_db = Manager.get_instance('AbilityData').table
            ailments = ability_db.ABI_BOS_SCH_C01_010_005.Ailment
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

    increase_stats_for_team(enemy_group.early_agnea)
    increase_stats_for_team(enemy_group.early_osvald)
    increase_stats_for_team(enemy_group.early_temenos)
    decrease_stats_for_solo(enemy_group.early_hikari)
    decrease_stats_for_solo(enemy_group.early_ochette)
    decrease_stats_for_solo(enemy_group.early_castti)
    decrease_stats_for_solo(enemy_group.early_partitio)
    decrease_stats_for_solo(enemy_group.early_throne)


def prologue_shops_update_weapons():
    shop_list_db = Manager.get_instance('ShopList').table
    shop_db = Manager.get_instance('PurchaseItemTable').table
    job_db = Manager.get_instance('JobData').table

    # Change slots so each weapon type is available
    shop_db.NPC_KEN_PrologueSHOP_03.ItemLabel = 'ITM_EQP_SWD_041'
    shop_db.NPC_KUS_PrologueSHOP_03.ItemLabel = 'ITM_EQP_ROD_040'

    # Update shop inventory
    shop_list_db.prologue_agnea.add_prologue_shop_weapons(job_db.agnea.equippable_weapons)
    shop_list_db.prologue_castti.add_prologue_shop_weapons(job_db.castti.equippable_weapons)
    shop_list_db.prologue_hikari.add_prologue_shop_weapons(job_db.hikari.equippable_weapons)
    shop_list_db.prologue_ochette.add_prologue_shop_weapons(job_db.ochette.equippable_weapons)
    shop_list_db.prologue_osvald.add_prologue_shop_weapons(job_db.osvald.equippable_weapons)
    shop_list_db.prologue_partitio.add_prologue_shop_weapons(job_db.partitio.equippable_weapons)
    shop_list_db.prologue_temenos.add_prologue_shop_weapons(job_db.temenos.equippable_weapons)
    shop_list_db.prologue_throne.add_prologue_shop_weapons(job_db.throne.equippable_weapons)


def prologue_shops_add_stones():
    shop_list_db = Manager.get_instance('ShopList').table

    # Adds all stones, might be overkill; maybe limit to boss weakness?
    def add_stones(shop_name, n=None):
        shop = getattr(shop_list_db, shop_name)
        shop.add_fire_soulstone()
        shop.add_ice_soulstone()
        shop.add_thunder_soulstone()
        shop.add_wind_soulstone()
        shop.add_light_soulstone()
        shop.add_dark_soulstone()

    add_stones('prologue_agnea')
    add_stones('prologue_castti')
    add_stones('prologue_hikari')
    add_stones('prologue_ochette')
    add_stones('prologue_osvald')
    add_stones('prologue_partitio')
    add_stones('prologue_temenos')
    add_stones('prologue_throne')
