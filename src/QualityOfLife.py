from Manager import Manager
from FLAGS import NEVERUSE

def more_fast_travel():
    wmt = Manager.get_table('WorldMapTable')

    for w in wmt:
        if 'eDUNGEON' in w.MapIconType:
            w.CanFastTravel = True

    # Lighthouse Island
    wmt.eMAP_Fld_Ocn_1_2.CanFastTravel = True
    # The Lost Isle
    wmt.eMAP_Fld_Ocn_1_3.CanFastTravel = True
    # ???
    wmt.eMAP_Fld_Ocn_1_4.CanFastTravel = True
    # Flamechurch: Cathedral
    wmt.eMAP_Twn_Mnt_1_2.CanFastTravel = True


# Roughly equivalent to Evasive Maneuvers
def reduce_encounter_rate():
    table = Manager.get_table('LevelTable')
    p = 2.5
    for r in table:
        r.EncountStepMin = int(r.EncountStepMin * p)
        r.RandomStepA = int(r.RandomStepA * p)
        r.RandomStepB = int(r.RandomStepB * p)


def black_market():
    placement = Manager.get_table('PlacementData')
    placement.NPC_Fld_Cty_1_2_TALK_0200_N000.SpawnStartFlag = 9000 # 25500 -- armor
    placement.NPC_Fld_Cty_1_2_TALK_0300_N000.SpawnStartFlag = 9000 # 25500 -- accessories
    placement.NPC_Fld_Cty_1_2_TALK_0500_N000.SpawnStartFlag = 9000 # 25501 -- weapons
    placement.NPC_Fld_Cty_1_2_TALK_0600_N000.SpawnStartFlag = 9000 # 25501 -- herbs/flowers
    placement.NPC_Fld_Cty_1_2_TALK_0800_N000.SpawnStartFlag = 9000 # 25502 -- shady grape/plum
    placement.NPC_Fld_Cty_1_2_TALK_0900_N000.SpawnStartFlag = 9000 # 25503 -- soulstones
    placement.NPC_Fld_Cty_1_2_TALK_1000_N000.SpawnStartFlag = 9000 # 25503 -- bottles
    placement.NPC_Fld_Cty_1_2_TALK_0200_N010.SpawnStartFlag = NEVERUSE # 25501 -- armor (same as 0200_N000)

    placement.NPC_Fld_Cty_1_2_TALK_0400_N000.SpawnStartFlag = NEVERUSE # 25500
    placement.NPC_Fld_Cty_1_2_TALK_0400_N010.SpawnStartFlag = 9000 # 25501
    placement.NPC_Fld_Cty_1_2_TALK_0700_N000.SpawnStartFlag = 9000 # 25501

    # weapons
    placement.NPC_Fld_Cty_1_2_TALK_0500_N000.SpawnPosX = 2600
    placement.NPC_Fld_Cty_1_2_TALK_0500_N000.SpawnPosY = -100

    # armor
    placement.NPC_Fld_Cty_1_2_TALK_0200_N000.SpawnPosX = 2200
    placement.NPC_Fld_Cty_1_2_TALK_0200_N000.SpawnPosY = 50
    placement.NPC_Fld_Cty_1_2_TALK_0200_N000.SpawnDir = 'RIGHT'

    # accessories
    placement.NPC_Fld_Cty_1_2_TALK_0300_N000.SpawnPosX = 2500
    placement.NPC_Fld_Cty_1_2_TALK_0300_N000.SpawnPosY = 800
    placement.NPC_Fld_Cty_1_2_TALK_0300_N000.SpawnDir = 'LEFT'

    # items
    placement.NPC_Fld_Cty_1_2_TALK_0600_N000.SpawnPosX = 2100
    placement.NPC_Fld_Cty_1_2_TALK_0600_N000.SpawnPosY = 450
    placement.NPC_Fld_Cty_1_2_TALK_0800_N000.SpawnPosX = 2100
    placement.NPC_Fld_Cty_1_2_TALK_0800_N000.SpawnPosY = 650

    # nuns -- most used, so just keep them where they are for convenience
    # placement.NPC_Fld_Cty_1_2_TALK_0900_N000.SpawnPosX = 2200
    # placement.NPC_Fld_Cty_1_2_TALK_0900_N000.SpawnPosY = 900
    # placement.NPC_Fld_Cty_1_2_TALK_1000_N000.SpawnPosX = 2200
    # placement.NPC_Fld_Cty_1_2_TALK_1000_N000.SpawnPosY = 1000
