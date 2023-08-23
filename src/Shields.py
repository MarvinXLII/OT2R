import random
from Nothing import Nothing
from Assets import Data

class Shields:
    
    def __init__(self):
        self.enemyDB = Data.getInstance('EnemyDB')

    def run(self):
        for enemy in self.enemyDB.table:

            # Skip all bosses for now
            # add back individually when testing
            if enemy.isBoss:
                if enemy.key in [
                        # Temenos
                        'ENE_BOS_CLE_C01_010', # Ch 1
                        'ENE_BOS_CLE_C02_010', # Ch 2 -- Vados the Architect
                        'ENE_BOS_CLE_C02_020', # Ch 2 -- Red Wisp
                        'ENE_BOS_CLE_C02_030', # Ch 2 -- Black Wisp
                        'ENE_BOS_CLE_C02_040', # Ch 2 -- Red Elemental
                        'ENE_BOS_CLE_C02_050', # Ch 2 -- Black Elemental
                        'ENE_BOS_CLE_C03_010', # Ch 3 -- Deputy Cubaryi, only first phase
                        'ENE_BOS_CLE_C05_010', # Ch 5 -- Captain Kaldena (nothing for Kaldena of Night)

                        # Throne
                        'ENE_BOS_THI_C01_010', # Ch 1 -- Pirro
                        'ENE_BOS_THI_C02_020', # Ch 2 -- Bergomi's Lackey
                        'ENE_BOS_THI_C03_010', # Ch 2 -- Mother
                        'ENE_BOS_THI_C03_030', # Ch 2 -- Mother's Aide
                        'ENE_BOS_THI_C03_020', # Ch 3 -- Father
                        'ENE_BOS_THI_C05_010', # Ch 4 -- Claude
                        'ENE_BOS_THI_C05_020', # Ch 4 -- Phantom Snake (Man)
                        'ENE_BOS_THI_C05_030', # Ch 4 -- Phantom Snake (Mother)
                        'ENE_BOS_THI_C05_040', # Ch 4 -- Phantom Snake (Father)
                        'ENE_BOS_THI_C05_050', # Ch 4 -- Fake Snake (Parent)
                        'ENE_BOS_THI_C05_060', # Ch 4 -- Fake Snake (Child)

                        # Castti
                        'ENE_BOS_APO_C01_010', # Ch 1 -- Veron
                        'ENE_BOS_APO_C01_020', # Ch 1 -- Doron
                        'ENE_BOS_APO_C02_010', # Ch 2 -- Sand Lion
                        'ENE_BOS_APO_C02_030', # Ch 2 -- Mikk
                        'ENE_BOS_APO_C02_040', # Ch 2 -- Makk
                        'ENE_BOS_APO_C05_010', # Ch 5 -- Trousseau, only first phase

                        # Partitio
                        'ENE_BOS_MER_C01_010', # Ch 1 -- Giff
                        'ENE_BOS_MER_C01_020', # Ch 1 -- Giff's Lackey I
                        'ENE_BOS_MER_C01_030', # Ch 1 -- Giff's Lackey II
                        'ENE_BOS_MER_C01_040', # Ch 1 -- Giff's Lackey III
                        'ENE_BOS_MER_C02_010', # Ch 2 -- Garnet
                        'ENE_BOS_MER_C02_020', # Ch 2 -- Secretary (not sure if gets called)
                        'ENE_BOS_MER_C02_030', # Ch 2 -- Mysterious Bones (not sure if gets called)
                        'ENE_BOS_MER_C03_010', # Ch 3 -- steam machine
                        'ENE_BOS_MER_C03_030', # Ch 3 -- neo steam machine
                        'ENE_BOS_MER_C03_020', # Ch 3 -- enemy in the mist / thurston
                        'ENE_BOS_MER_C05_020', # Ch 5 -- Glacis Plate
                        'ENE_BOS_MER_C05_030', # Ch 5 -- Smokestack
                        'ENE_BOS_MER_C05_040', # Ch 5 -- Canon

                        # Agnea
                        'ENE_BOS_DAN_C01_010', # Ch 1 -- Duorduor
                        'ENE_BOS_DAN_C01_020', # Ch 1 -- Forest Marmot
                        'ENE_BOS_DAN_C02_020', # Ch 2 -- Troupe Dancer
                        'ENE_BOS_DAN_C02_030', # Ch 2 -- Troupe Musician
                        'ENE_BOS_DAN_C04_010', # Ch 4 -- Veronica
                        'ENE_BOS_DAN_C05_020', # Ch 5 -- Dolcinaea's Fan
                        'ENE_BOS_DAN_C05_040', # Ch 5 -- Hikari
                        'ENE_BOS_DAN_C05_050', # Ch 5 -- Ochette
                        'ENE_BOS_DAN_C05_060', # Ch 5 -- Temenos
                        'ENE_BOS_DAN_C05_070', # Ch 5 -- Osvald
                        'ENE_BOS_DAN_C05_080', # Ch 5 -- Castti
                        'ENE_BOS_DAN_C05_090', # Ch 5 -- Partitio
                        'ENE_BOS_DAN_C05_100', # Ch 5 -- Throne

                        # Hikari
                        'ENE_BOS_WAR_C01_010', # Ch 1 -- Ritsu
                        'ENE_BOS_WAR_C01_020', # Ch 1 -- Ritsu's Footman
                        'ENE_BOS_WAR_C05_010', # Ch 5 -- General Ritsu
                        'ENE_BOS_WAR_C05_020', # Ch 5 -- King Mugen

                        # Ochette
                        'ENE_BOS_HUN_C01_010', # Ch 1 -- Dark Entity
                        'ENE_BOS_HUN_C01_020', # Ch 1 -- Mysterious Fledgling
                        'ENE_BOS_HUN_C02_010', # Ch 2 -- Tera
                        'ENE_BOS_HUN_C02_030', # Ch 2 -- Blue Elemental
                        'ENE_BOS_HUN_C05_010', # Ch 3 -- Lajackal, first phase only
                        'ENE_BOS_HUN_C05_020', # Ch 3 -- Malamaowl, first phase only

                        # Osvald
                        'ENE_BOS_SCH_C01_010', # Ch 1 -- Warden Davids
                        'ENE_BOS_SCH_C01_020', # Ch 1 -- Prison Guard
                        'ENE_BOS_SCH_C01_030', # Ch 1 -- Prison Guard
                        'ENE_BOS_SCH_C03_020', # Ch 3 -- Stenvar's Footman
                        'ENE_BOS_SCH_C04_010', # Ch 4 -- Grieving Golem, first phase only
                        'ENE_BOS_SCH_C05_010', # Ch 5 -- Professor Harvey
                        'ENE_BOS_SCH_C05_020', # Ch 5 -- Pure Elemental

                        # Endgame
                        'ENE_BOS_LST_C02_040', # Ant, Servant of the Night
                        'ENE_BOS_LST_C02_050', # Howler, Servant of the Night
                        'ENE_BOS_LST_C02_070', # Mushroom, Servant of the Night
                        'ENE_BOS_LST_C02_080', # Condor, Servant of the Night
                        'ENE_BOS_LST_C03_060', # Vide, first phase only
                        'ENE_BOS_LST_C03_061', # Wrigling Tentacle
                        'ENE_BOS_LST_C03_062', # Creeping Tentacle
                        'ENE_BOS_LST_C03_063', # Lithe Tentacle
                        'ENE_BOS_LST_C03_064', # Thwarting Tentacle
                        'ENE_BOS_LST_C03_070', # Vide, the Wicked, first phase only
                        'ENE_BOS_LST_C03_071', # Wicked Right Arm
                        'ENE_BOS_LST_C03_072', # Wicked Left Arm
                        'ENE_BOS_LST_C03_073', # Wicked Right Arm
                        'ENE_BOS_LST_C03_074', # Wicked Left Arm

                        # Galdera
                        'ENE_BOS_EXT_LOW_010', # Omniscient Eye
                        'ENE_BOS_EXT_LOW_020', # Wailing Soul
                        'ENE_BOS_EXT_LOW_021', # Wailing Soul
                        'ENE_BOS_EXT_LOW_023', # Wailing Soul
                        'ENE_BOS_EXT_LOW_030', # Raging Soul
                        'ENE_BOS_EXT_LOW_031', # Raging Soul
                        'ENE_BOS_EXT_LOW_033', # Raging Soul
                        'ENE_BOS_EXT_LOW_040', # Screaming Soul
                        'ENE_BOS_EXT_LOW_041', # Screaming Soul
                        'ENE_BOS_EXT_LOW_043', # Screaming Soul
                        'ENE_BOS_EXT_UPP_010', # Galdera, the Fallen
                        'ENE_BOS_EXT_UPP_020', # Abyssal Maw
                        'ENE_BOS_EXT_UPP_030', # Sundering Arm
                        'ENE_BOS_EXT_UPP_040', # Blade of the Fallen
                ]:
                    print('Shuffling', enemy.key)
                elif enemy.key in [
                        # Hikari
                        'ENE_BOS_WAR_C02_010', # Ch 2
                        'ENE_BOS_WAR_C04_010', # Ch 4 -- Rai Mei
                        'ENE_BOS_WAR_C05_030', # Ch 5 -- Enshrouded King

                        # Throne
                        'ENE_BOS_THI_C02_010', # Ch 2 -- Bergomi

                        # Castti
                        'ENE_BOS_APO_C02_020', # Ch 2 -- Plukk

                        # Partitio
                        'ENE_BOS_MER_C05_010', # Ch 5 -- Steam Tank Obsidian

                        # Agnea
                        'ENE_BOS_DAN_C02_010', # Ch 2 -- La'mani
                        'ENE_BOS_DAN_C05_010', # Ch 5 -- Dolcinaea
                        'ENE_BOS_DAN_C05_030', # Ch 5 -- Dolcinaea the Star

                        # Ochette
                        'ENE_BOS_HUN_C02_020', # Ch 2 -- Glacis

                        # Osvald
                        'ENE_BOS_SCH_C03_010', # Ch 3 -- Stenvar

                        # Endgame
                        'ENE_BOS_LST_C02_020', # Arcanette

                        # Galdera
                        'ENE_BOS_EXT_LOW_022', # Wailing
                        'ENE_BOS_EXT_LOW_032', # Raging
                        'ENE_BOS_EXT_LOW_042', # Screaming
                ]:
                    print('Skipping', enemy.key, 'due to shield locks')
                    continue
                else:
                    print('Boss', enemy.key, 'not tested')
                    continue
            
            shields = enemy.shields
            random.shuffle(shields)
            enemy.shields = shields


            enemy.addWeaknessToPC()
