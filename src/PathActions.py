import random
from Nothing import Nothing
from Manager import Manager


def nerf(x, attribute, value, includeZero=False):
    for xi in x.table:
        defaultValue = getattr(xi, attribute)
        if includeZero or defaultValue != 0:
            setattr(xi, attribute, value)

def nerfEntreat(shops):
    nerf(shops, 'ProperBeg', 1)

def nerfSteal(shops):
    nerf(shops, 'ProperSteal', -15, includeZero=True)

def nerfPurchase(shops):
    nerf(shops, 'FCPrice', 1)

def nerfInquire(hear):
    nerf(hear, 'HearNeedLevel', 1)
    
def nerfBribe(hear):
    nerf(hear, 'BriberyBuyPrice', 1)
    
def nerfScrutinize(hear):
    nerf(hear, 'SearchBaseProbability', 100.0)

def nerfAllure(lead):
    nerf(lead, 'LureBaseProbability', 100.0)

def nerfHire(lead):
    nerf(lead, 'HirePrice', 1)
    
def nerfGuide(lead):
    nerf(lead, 'LeadNeedLevel', 1)

def nerfBefriend(lead):
    for npc in lead.table:
        assert len(npc.PlacateNeedItems) == 1
        if npc.PlacateNeedItems[0]['ItemNum'].value > 0:
            if npc.PlacateNeedItems[0]['ItemLabel'].value == 'ITM_TRE_KAR_10_0010': # Skip friendship jerkey
                continue
            npc.PlacateNeedItems[0]['ItemLabel'].value = 'ITM_CSM_0010'
            npc.PlacateNeedItems[0]['ItemNum'].value = 1

def nerfChallenge(battle):
    nerf(battle, 'BattleNeedLevel', 1)

def nerfAmbush(battle):
    nerf(battle, 'AssassinateNeedLevel', 1)
    
def nerfSoothe(battle):
    for i, npc in enumerate(battle.table):
        if npc.DoseItemNum > 0:
            # Castti Ch 1 -- Lychanthe Antipyretic
            if npc.key == 'FC_B_NPC_KUS_10_1000': continue
            if npc.key == 'FC_B_NPC_KUS_10_1100': continue
            if npc.key == 'FC_B_NPC_KUS_10_1200': continue
            # Castti Ch 2 -- Rosa's Medicine
            if npc.key == 'FC_B_NPC_KUS_2B_0700': continue
            npc.DoseItemID = 'ITM_CSM_0010' # Healing Grape
            npc.DoseItemNum = 1
    
    
class PathActions:
    entreat = Nothing
    steal = Nothing
    purchase = Nothing
    inquire = Nothing
    bribe = Nothing
    scrutinize = Nothing
    allure = Nothing
    hire = Nothing
    guide = Nothing
    befriend = Nothing
    challenge = Nothing
    ambush = Nothing
    soothe = Nothing

    def __init__(self):
        self.shopDB = Manager.getInstance('PurchaseItemTable')
        self.hearDB = Manager.getInstance('NPCHearData')
        self.leadDB = Manager.getInstance('NPCLeadData')
        self.battleDB = Manager.getInstance('NPCBattleData')

    def run(self):
        PathActions.entreat(self.shopDB) # Agnea
        PathActions.steal(self.shopDB) # Throne
        PathActions.purchase(self.shopDB) # Partitio
        PathActions.inquire(self.hearDB) # Castti
        PathActions.bribe(self.hearDB) # Hikari
        PathActions.scrutinize(self.hearDB) # Osvald
        PathActions.allure(self.leadDB) # Agnea
        PathActions.hire(self.leadDB) # Partitio
        PathActions.guide(self.leadDB) # Temenos
        PathActions.befriend(self.leadDB) # Ochette
        PathActions.challenge(self.battleDB) # Hikari
        PathActions.ambush(self.battleDB) # Throne
        PathActions.soothe(self.battleDB) # Castti
