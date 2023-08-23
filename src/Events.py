from Manager import Manager
from Nothing import Nothing

def formation_menu_on(events):
    for event in events:
        event.toggle_flag_off(415)
    gametext_db = Manager.get_instance('GameTextEN').table
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


class InitialEvents:
    formation_menu = Nothing
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
        InitialEvents.protagonist()
