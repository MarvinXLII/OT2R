from Manager import Manager
from Nothing import Nothing

def formationMenuOn(events):
    for event in events:
        event.toggleFlagOff(415)
    gameTextTable = Manager.getInstance('GameTextEN').table
    gameTextTable.PARTYMENU_LOCK_JOIN_CHARA.replaceSubstring('local tavern', 'main menu')
    gameTextTable.ADD_PARTY_DIALOG.replaceSubstring('at the tavern', 'in the main menu')
    gameTextTable.BREAK_PARTY_DIALOG.replaceSubstring('at the tavern', 'in the main menu')


def protagonistUnlocked():
    # Allow first character to be removed from party
    widget = Manager.getData('ListCharacterWidget.uexp')
    widget.patchInt32(0x14072, 1045) # CanGetOutOfMainMember: remove protagonist
    widget.patchInt32(0x1a744, 165) # CanGetOutOfMainMember_1stSelect: swap lead with idle party member

    # Remove the lock icons on the protagonist (and lead character when a new PC joins the party)
    panel = Manager.getAssetOnly('PartyCharacterPanel')
    panel.patchInt8(0x45e0, 2)


class InitialEvents:
    formationMenu = Nothing
    protagonist = Nothing

    def __init__(self):
        self.events = [
            Manager.getJson('MS_GAK_10_0100'),
            Manager.getJson('MS_KAR_10_0200'),
            Manager.getJson('MS_KEN_10_0100'),
            Manager.getJson('MS_KUS_10_0100'),
            Manager.getJson('MS_ODO_10_0100'),
            Manager.getJson('MS_SHO_10_0100'),
            Manager.getJson('MS_SIN_10_0100'),
            Manager.getJson('MS_TOU_10_0100'),
        ]

    def run(self):
        InitialEvents.formationMenu(self.events)
        InitialEvents.protagonist()
