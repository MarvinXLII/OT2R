from Manager import Manager
from Nothing import Nothing

def formationMenuOn(events):
    for event in events:
        event.toggleFlagOff(415)
    gameTextTable = Manager.getInstance('GameTextEN').table
    gameTextTable.PARTYMENU_LOCK_JOIN_CHARA.replaceSubstring('local tavern', 'main menu')
    gameTextTable.ADD_PARTY_DIALOG.replaceSubstring('at the tavern', 'in the main menu')
    gameTextTable.BREAK_PARTY_DIALOG.replaceSubstring('at the tavern', 'in the main menu')

class InitialEvents:
    formationMenu = Nothing

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
        self.protaganist()
        InitialEvents.formationMenu(self.events)

    def protaganist(self):
        widget = Manager.getData('ListCharacterWidget.uexp')
        widget.patchInt32(0x14072, 0x415)
        
