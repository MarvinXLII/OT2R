from Manager import Manager
from Nothing import Nothing
from Scripts import Script
from FLAGS import DUMMY

def formation_menu_on(events):
    for event in events:
        # event.toggle_flag_off(415) # turn off HIDE_MAINMENU_CHANGEMEMBER
        event.change_flag(415, 605) # HIDE_MAINMENU_CHANGEMEMBER to PERMISSION_EIGHT_PARTY
    gametext_db = Manager.get_table('GameTextEN')
    gametext_db.PARTYMENU_LOCK_JOIN_CHARA.replace_substring('local tavern', 'main menu')
    gametext_db.ADD_PARTY_DIALOG.replace_substring('at the tavern', 'in the main menu')
    gametext_db.BREAK_PARTY_DIALOG.replace_substring('at the tavern', 'in the main menu')


def protagonist_unlocked():
    # Allow first character to be removed from party
    widget = Manager.get_data('ListCharacterWidget.uexp')
    widget.patch_int32(0x14072, 1045) # CanGetOutOfMainMember: remove protagonist
    widget.patch_int32(0x1a744, 165) # CanGetOutOfMainMember_1stSelect: swap lead with idle party member

    # Remove the lock icons on the protagonist (and lead character when a new PC joins the party)
    panel = Manager.get_asset_only('PartyCharacterPanel')
    panel.patch_int8(0x45e0, 2)


def skip_tutorials(events):
    tutorial_flags = Manager.get_table('TutorialFlagPart')
    placement = Manager.get_table('PlacementData')

    new_flags = set()
    for entry in tutorial_flags:
        new_flags.add(entry.TutorialListFlag)
        new_flags.add(entry.TutorialOpenedFlag)
        entry.TutorialListFlag = DUMMY
        entry.TutorialOpenedFlag = DUMMY
    new_flags.remove(0)
    if DUMMY in new_flags:
        new_flags.remove(DUMMY)

    patch_flags = Script.load('scripts/patch_flags')
    for script in events:
        script.insert_script(patch_flags, 0)

    for p in placement:
        if 'TUTO_TRIGGER' in p.key:
            p.SpawnStartFlag = DUMMY
            p.SpawnEndFlag = DUMMY

    # Special Hikari Ch. 1
    # Without trigger script running, a necessary NPC cannot be bribed
    # placement.EV_TRIGGER_MS_KEN_10_1110.SpawnStartFlag = DUMMY
    # placement.EV_TRIGGER_MS_KEN_10_1110.SpawnEndFlag = DUMMY
    # placement.NPC_KEN_10_1000_N000.EventStartFlag_A = placement.NPC_KEN_10_1000_N000.SpawnStartFlag


class InitialEvents:
    formation_menu = Nothing
    skip_tutorials = Nothing
    protagonist = Nothing

    def __init__(self):
        self.events = [
            Manager.get_json('MS_GAK_10_0100'),
            Manager.get_json('MS_KAR_10_0200'),
            Manager.get_json('MS_KEN_10_0100'),
            Manager.get_json('MS_KUS_10_0100'),
            Manager.get_json('MS_ODO_10_0100'),
            Manager.get_json('MS_SHO_10_0100'),
            Manager.get_json('MS_SIN_10_0100'),
            Manager.get_json('MS_TOU_10_0100'),
        ]

    def run(self):
        InitialEvents.formation_menu(self.events)
        InitialEvents.skip_tutorials(self.events)
        InitialEvents.protagonist()
