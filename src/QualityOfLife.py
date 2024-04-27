from Manager import Manager

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
