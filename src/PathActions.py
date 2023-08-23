import random
from Nothing import Nothing
from Manager import Manager


def nerf(x, attribute, value, include_zero=False):
    for xi in x.table:
        default_value = getattr(xi, attribute)
        if include_zero or default_value != 0:
            setattr(xi, attribute, value)

def nerf_entreat(shops):
    nerf(shops, 'ProperBeg', 1)

def nerf_steal(shops):
    nerf(shops, 'ProperSteal', -15, include_zero=True)

def nerf_purchase(shops):
    nerf(shops, 'FCPrice', 1)

def nerf_inquire(hear):
    nerf(hear, 'HearNeedLevel', 1)
    
def nerf_bribe(hear):
    nerf(hear, 'BriberyBuyPrice', 1)
    
def nerf_scrutinize(hear):
    nerf(hear, 'SearchBaseProbability', 100.0)

def nerf_allure(lead):
    nerf(lead, 'LureBaseProbability', 100.0)

def nerf_hire(lead):
    nerf(lead, 'HirePrice', 1)
    
def nerf_guide(lead):
    nerf(lead, 'LeadNeedLevel', 1)

def nerf_befriend(lead):
    for npc in lead.table:
        assert len(npc.PlacateNeedItems) == 1
        if npc.PlacateNeedItems[0]['ItemNum'].value > 0:
            if npc.PlacateNeedItems[0]['ItemLabel'].value == 'ITM_TRE_KAR_10_0010': # Skip friendship jerkey
                continue
            npc.PlacateNeedItems[0]['ItemLabel'].value = 'ITM_CSM_0010'
            npc.PlacateNeedItems[0]['ItemNum'].value = 1

def nerf_challenge(battle):
    nerf(battle, 'BattleNeedLevel', 1)

def nerf_ambush(battle):
    nerf(battle, 'AssassinateNeedLevel', 1)
    
def nerf_soothe(battle):
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
        self.shop_db = Manager.get_instance('PurchaseItemTable')
        self.hear_db = Manager.get_instance('NPCHearData')
        self.lead_db = Manager.get_instance('NPCLeadData')
        self.battle_db = Manager.get_instance('NPCBattleData')

    def run(self):
        PathActions.entreat(self.shop_db) # Agnea
        PathActions.steal(self.shop_db) # Throne
        PathActions.purchase(self.shop_db) # Partitio
        PathActions.inquire(self.hear_db) # Castti
        PathActions.bribe(self.hear_db) # Hikari
        PathActions.scrutinize(self.hear_db) # Osvald
        PathActions.allure(self.lead_db) # Agnea
        PathActions.hire(self.lead_db) # Partitio
        PathActions.guide(self.lead_db) # Temenos
        PathActions.befriend(self.lead_db) # Ochette
        PathActions.challenge(self.battle_db) # Hikari
        PathActions.ambush(self.battle_db) # Throne
        PathActions.soothe(self.battle_db) # Castti
