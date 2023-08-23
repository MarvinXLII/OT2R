import random
from Shuffler import Shuffler, Slot, noWeights
from Manager import Manager


def CheckMoney(w, s, c):
    if c.isMoney:
        for si, slot in enumerate(s):
            w[si] *= slot.moneyAllowed
            
def separateChapter(w, s, c):
    for si, slot in enumerate(s):
        w[si] *= slot.ring == c.ring

def keepChapterOneSeparate(w, s, c):
    if c.ring == 1:
        for si, slot in enumerate(s):
            w[si] *= si.ring == 1
    else:
        for si, slot in enumerate(s):
            w[si] *= si.ring > 1

def rustyAlwaysAccessible(w, s, c):
    if c.isRusty:
        for si, slot in enumerate(s):
            w[si] *= slot.alwaysAccessible

def inventorAlwaysAccessible(w, s, c):
    if c.isInventorItem:
        for si, slot in enumerate(s):
            w[si] *= slot.alwaysAccessible

def licenseAlwaysAccessible(w, s, c):
    if c.isLicense:
        for si, slot in enumerate(s):
            w[si] *= slot.alwaysAccessible


def licensePrice():
    return random.randint(1, 10) * 5000


class ItemSlot(Slot):
    @property
    def isKnowledge(self):
        return 'ITM_INF' in self.itemLabel

    @property
    def isValuable(self):
        return 'ITM_TRE' in self.itemLabel

    @property
    def isKeyItem(self):
        mayBeKeyItem = self.isKnowledge or self.isValuable
        notKeyItem = self.isRusty or self.isInventorItem
        return False if notKeyItem else mayBeKeyItem

    @property
    def itemHasLittleValue(self):
        return self.itemLabel in [
            'ITM_CSM_0010', # Healing Grape
            'ITM_CSM_0030', # Inspiriting Plum
            'ITM_CSM_0220', # Empowering Lychee
            'ITM_CSM_0150', # Herb of Healing
            'ITM_CSM_0160', # Herb of Clamor
            'ITM_CSM_0170', # Herb of Light
            'ITM_CSM_0180', # Herb of Clarity
            'ITM_CSM_0190', # Herb of Awakening
            'ITM_CSM_0200', # Herb of Valor
            'ITM_CSM_0210', # Herb of Revival
            'ITM_CSM_0250', # Bottle of Poison Dust
            'ITM_CSM_0260', # Bottle of Blinding Dust
            'ITM_CSM_0270', # Bottle of Befuddling Dust
            'ITM_CSM_0280', # Bottle of Sleeping Dust
            'ITM_CSM_0290', # Fire Soulstone
            'ITM_CSM_0320', # Ice Soulstone
            'ITM_CSM_0350', # Thunder Soulstone
            'ITM_CSM_0380', # Wind Soulstone
            'ITM_CSM_0410', # Light Soulstone
            'ITM_CSM_0440', # Dark Soulstone
            'ITM_FLV_0250', # Stone
        ]

    @property
    def isRusty(self):
        return '_WPM_' in self.itemLabel

    @property
    def isInventorItem(self):
        return '_PARTS_' in self.itemLabel

    @property
    def isLicense(self):
        return '_JOB_' in self.itemLabel

    def randomPrice(self, sellPrice, buyPrice):
        minPrice = sellPrice * 4 // 5  #  80%
        maxPrice = buyPrice * 5 // 4  # 120%
        price = random.randint(minPrice, maxPrice)
        p = price
        if price < 100:
            price = price // 5 * 5
        elif price < 1000:
            price = price // 50 * 50
        elif price < 10000:
            price = price // 100 * 100
        else:
            price = price // 1000 * 1000
        return price

    def copy(self, other):
        self.itemLabel = other.itemLabel
        self.count = other.count
        self.isMoney = other.isMoney
        self.price = other.price



class ItemObject(ItemSlot):
    def __init__(self, obj):
        self.key = obj.key
        self.slot = obj

        # Must be patched
        self.itemLabel = self.slot.HaveItemLabel
        self.count = self.slot.HaveItemCnt
        self.isMoney = self.slot.IsMoney

        # Constraints
        itemTable = Manager.getInstance('ItemDB').table
        validSlot = itemTable.getName(self.slot.HaveItemLabel) or self.slot.IsMoney
        self.skip = obj.ObjectType in [0, 5, 8] or not validSlot
        self.skip |= self.isEventItem # e.g. Angea's purse
        self.skip |= self.isKeyItem # Knowledge/Valuable except rusty weapon or inventor item
        self.skip |= not obj.isValid
        self.ring = obj.ring
        self.moneyAllowed = True
        self.alwaysAccessible = obj.isAlwaysAccessible

        # Other data needed if this slot becomes a NPC item
        row = itemTable.getRow(self.itemLabel)
        if row:
            assert row.BuyPrice >= row.SellPrice
            if not self.skip:
                self.price = self.randomPrice(row.SellPrice, row.BuyPrice)
        else:
            self.price = 42

    @property
    def isEventItem(self):
        return 'EventItem' in self.slot.key

    def patch(self):
        self.slot.HaveItemLabel = self.itemLabel
        self.slot.HaveItemCnt = self.count
        self.slot.IsMoney = self.isMoney


class ItemNPC(ItemSlot):
    def __init__(self, item):
        self.key = item.key
        self.slot = item

        # Must be patched
        self.itemLabel = self.slot.ItemLabel
        self.price = self.slot.FCPrice

        # Constraints
        itemTable = Manager.getInstance('ItemDB').table
        itemName = itemTable.getName(self.slot.ItemLabel)
        self.skip = self.slot.ItemLabel == 'None' or not itemName
        self.skip |= self.isKeyItem
        self.skip |= item.dontShuffle
        self.skip |= not item.isValid
        self.ring = item.ring
        self.moneyAllowed = False
        self.alwaysAccessible = item.isAlwaysAccessible

        # Other data needed if this slot becomes an Object 
        self.count = 1
        self.isMoney = False


    def patch(self):
        self.slot.ItemLabel = self.itemLabel
        self.slot.FCPrice = self.price


class ItemGuild(ItemSlot):
    def __init__(self, guild):
        self.key = guild.key
        self.slot = guild

        # Must be patches
        self.itemLabel = self.slot.LicenseItem

        # Constraints
        self.skip = False
        self.ring = 2
        self.moneyAllowed = False
        self.alwaysAccessible = True

        # Other data
        self.count = 1
        self.isMoney = False
        self.price = licensePrice()

    def patch(self):
        self.slot.LicenseItem = self.itemLabel


class ItemGuildAdv(ItemSlot):
    def __init__(self, item, jsonFile):
        self.guild = Manager.getJson(jsonFile)
        self.vanilla = item
        self.itemLabel = item

        self.skip = False
        self.ring = 2
        self.moneyAllowed = False
        self.alwaysAccessible = True

        self.count = 1
        self.isMoney = False
        self.price = licensePrice()

    def patch(self):
        for command in self.guild.jsonList:
            for i, value in enumerate(command.opt):
                if value == self.vanilla:
                    command.opt[i] = self.itemLabel


class ItemArmsmaster(ItemSlot):
    def __init__(self):
        self.slot = Manager.getAssetOnly('BP_WeaponMasterUtil')
        self.itemLabel = 'ITM_EQP_JOB_0008'

        # Constraints
        self.skip = False
        self.ring = 2
        self.moneyAllowed = False
        self.alwaysAccessible = True

        # Other data
        self.count = 1
        self.isMoney = False
        self.price = licensePrice()

    def patch(self):
        self.slot.uasset.replaceIndex('ITM_EQP_JOB_0008', self.itemLabel)
        value = self.slot.uasset.getIndex(self.itemLabel)
        self.slot.patchInt64(0x50b6, value)


# Currently ONLY used for the Rusty Sword
# TODO: Look through sidequests, requirements, and rewards,
# and consider adding all of them to the randomizer
class ItemSideQuest(ItemSlot):
    def __init__(self):
        self.itemLabel = 'ITM_TRE_WPM_01' # Rusty Sword

        self.skip = False
        self.ring = 2
        self.moneyAllowed = False
        self.alwaysAccessible = True

        self.count = 1
        self.isMoney = False
        self.price = random.randint(1, 5) * 10000

    def patch(self):
        substories = Manager.getTable('SubStoryTask')
        substories.SS_SNW2_0200.RewardParam[0] = self.itemLabel


# Chests, hidden items, and stealing/bargaining
# TODO: redesign classes to allow for copying, or allow
# for making slots and candidates the same objects (e.g.
# store all vanilla stuff when instantiating)
class Treasures(Shuffler):
    CheckChapter = noWeights
    IncludeLicenses = False
    IncludeInventorParts = False
    IncludeRustyWeapons = False

    def __init__(self):
        self.objectTable = Manager.getInstance('ObjectData').table
        self.shopTable = Manager.getInstance('PurchaseItemTable').table
        self.guildTable = Manager.getInstance('GuildData').table

        slots = []
        candidates = []

        # Chests & Hidden Items
        for obj in self.objectTable:
            slots.append(ItemObject(obj))
            candidates.append(ItemObject(obj))

        # NPC shops
        for shop in self.shopTable:
            if shop.isNPC:
                slots.append(ItemNPC(shop))
                candidates.append(ItemNPC(shop))

        # Sidequests -- Rusty Sword only
        slots.append(ItemSideQuest())
        candidates.append(ItemSideQuest())

        # Guild/Licenses
        if self.IncludeLicenses:
            for guild in self.guildTable:
                if guild.LicenseItem != 'None':
                    slots.append(ItemGuild(guild))
                    candidates.append(ItemGuild(guild))
            slots.append(ItemGuildAdv('ITM_EQP_JOB_0009', 'SYS_WIZ_GUILD_0000'))
            candidates.append(ItemGuildAdv('ITM_EQP_JOB_0009', 'SYS_WIZ_GUILD_0000'))
            slots.append(ItemGuildAdv('ITM_EQP_JOB_0010', 'SYS_SHA_GUILD_0100'))
            candidates.append(ItemGuildAdv('ITM_EQP_JOB_0010', 'SYS_SHA_GUILD_0100'))
            slots.append(ItemGuildAdv('ITM_EQP_JOB_0011', 'SYS_INV_GUILD_0010'))
            candidates.append(ItemGuildAdv('ITM_EQP_JOB_0011', 'SYS_INV_GUILD_0010'))
            slots.append(ItemArmsmaster())
            candidates.append(ItemArmsmaster())

        # Might be cleaner to turn these items on if necessary
        # i.e. skips are True by default and set to False if needed
        if not self.IncludeRustyWeapons:
            counter = 0
            for s, c in zip(slots, candidates):
                if s.isRusty and not s.skip:
                    s.skip = True
                    c.skip = True
                    counter += 1
            assert counter == 6

        if not self.IncludeInventorParts:
            counter = 0
            for s, c in zip(slots, candidates):
                if s.isInventorItem and not s.skip:
                    s.skip = True
                    c.skip = True
                    counter += 1
            assert counter == 6

        # Remove key items/events
        self.slots = list(filter(lambda x: not x.skip, slots))
        self.candidates = list(filter(lambda x: not x.skip, candidates))
            
        # Other stuff to be used for shuffling
        self.vacant = None
        self.weights = None

    def generateWeights(self):
        super().generateWeights(CheckMoney, Treasures.CheckChapter,
                                rustyAlwaysAccessible, inventorAlwaysAccessible,
                                licenseAlwaysAccessible)

    def finalizeLicenses(self):
        # Only consider slots with pointless items as candidates
        # for second and third licenses of base jobs
        candidates = []
        for slot in self.slots:
            if slot.itemHasLittleValue and slot.alwaysAccessible:
                candidates.append(slot)

        slots = random.sample(candidates, 16)
        slots[0].itemLabel = 'ITM_EQP_JOB_0000' # Merchant
        slots[1].itemLabel = 'ITM_EQP_JOB_0000'
        slots[2].itemLabel = 'ITM_EQP_JOB_0001' # Thief
        slots[3].itemLabel = 'ITM_EQP_JOB_0001'
        slots[4].itemLabel = 'ITM_EQP_JOB_0002' # Warrior
        slots[5].itemLabel = 'ITM_EQP_JOB_0002'
        slots[6].itemLabel = 'ITM_EQP_JOB_0003' # Hunter
        slots[7].itemLabel = 'ITM_EQP_JOB_0003'
        slots[8].itemLabel = 'ITM_EQP_JOB_0004' # Cleric
        slots[9].itemLabel = 'ITM_EQP_JOB_0004'
        slots[10].itemLabel = 'ITM_EQP_JOB_0005' # Dancer
        slots[11].itemLabel = 'ITM_EQP_JOB_0005'
        slots[12].itemLabel = 'ITM_EQP_JOB_0006' # Scholar
        slots[13].itemLabel = 'ITM_EQP_JOB_0006'
        slots[14].itemLabel = 'ITM_EQP_JOB_0007' # Apothecary
        slots[15].itemLabel = 'ITM_EQP_JOB_0007'
        for slot in slots:
            slot.price = licensePrice()

        # Update flags in first events to ensure subjobs can be equipped before
        # going to a guild
        gak = Manager.getJson('MS_GAK_10_0100')
        kar = Manager.getJson('MS_KAR_10_0200')
        ken = Manager.getJson('MS_KEN_10_0100')
        kus = Manager.getJson('MS_KUS_10_0100')
        odo = Manager.getJson('MS_ODO_10_0100')
        sho = Manager.getJson('MS_SHO_10_0100')
        sin = Manager.getJson('MS_SIN_10_0100')
        tou = Manager.getJson('MS_TOU_10_0100')

        gak.changeFlag(406, 411) # 406 stays off, 411 gets turned on
        kar.changeFlag(406, 411)
        ken.changeFlag(406, 411)
        kus.changeFlag(406, 411)
        odo.changeFlag(406, 411)
        sho.changeFlag(406, 411)
        sin.changeFlag(406, 411)
        tou.changeFlag(406, 411)

        # Have all PCs start with first 2 inventor abilities.
        # This is way simpler than finding the right place in event scripts
        # to add the apprioriate commands.
        reminiscence = Manager.getInstance('ReminiscenceSetting').table
        reminiscence.agnea.addToBackpack('ITM_TRE_INV_01', 1)
        reminiscence.agnea.addToBackpack('ITM_TRE_INV_02', 1)
        reminiscence.castti.removeFromBackpack('ITM_MRL_REV_0010') # Grape Leaf
        reminiscence.castti.addToBackpack('ITM_TRE_INV_01', 1)
        reminiscence.castti.addToBackpack('ITM_TRE_INV_02', 1)
        reminiscence.hikari.addToBackpack('ITM_TRE_INV_01', 1)
        reminiscence.hikari.addToBackpack('ITM_TRE_INV_02', 1)
        reminiscence.partitio.addToBackpack('ITM_TRE_INV_01', 1)
        reminiscence.partitio.addToBackpack('ITM_TRE_INV_02', 1)
        reminiscence.ochette.addToBackpack('ITM_TRE_INV_01', 1)
        reminiscence.ochette.addToBackpack('ITM_TRE_INV_02', 1)
        reminiscence.osvald.addToBackpack('ITM_TRE_INV_01', 1)
        reminiscence.osvald.addToBackpack('ITM_TRE_INV_02', 1)
        reminiscence.temenos.addToBackpack('ITM_TRE_INV_01', 1)
        reminiscence.temenos.addToBackpack('ITM_TRE_INV_02', 1)
        reminiscence.throne.addToBackpack('ITM_TRE_INV_01', 1)
        reminiscence.throne.addToBackpack('ITM_TRE_INV_02', 1)

    def finalize(self):
        if self.IncludeLicenses:
            self.finalizeLicenses()
