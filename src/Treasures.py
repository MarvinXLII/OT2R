import random
from Shuffler import Shuffler, Slot, no_weights
from Manager import Manager
from EventsAndItems import EventsAndItems


def check_money(w, s, c):
    if c.is_money:
        for si, slot in enumerate(s):
            w[si] *= slot.money_allowed
            
def separate_chapter(w, s, c):
    for si, slot in enumerate(s):
        w[si] *= slot.ring == c.ring

def keep_chapter_one_separate(w, s, c):
    if c.ring == 1:
        for si, slot in enumerate(s):
            w[si] *= si.ring == 1
    else:
        for si, slot in enumerate(s):
            w[si] *= si.ring > 1

def rusty_always_accessible(w, s, c):
    if c.is_rusty:
        for si, slot in enumerate(s):
            w[si] *= slot.always_accessible

def inventor_always_accessible(w, s, c):
    if c.is_inventor_item:
        for si, slot in enumerate(s):
            w[si] *= slot.always_accessible

def license_always_accessible(w, s, c):
    if c.is_license:
        for si, slot in enumerate(s):
            w[si] *= slot.always_accessible


def license_price():
    return random.randint(1, 10) * 5000


class ItemSlot(Slot):
    @property
    def is_knowledge(self):
        return 'ITM_INF' in self.item_label

    @property
    def is_valuable(self):
        return 'ITM_TRE' in self.item_label

    @property
    def is_key_item(self):
        maybe_key_item = self.is_knowledge or self.is_valuable
        not_key_item = self.is_rusty or self.is_inventor_item
        return False if not_key_item else maybe_key_item

    @property
    def item_has_little_value(self):
        return self.item_label in [
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
    def is_rusty(self):
        return '_WPM_' in self.item_label

    @property
    def is_inventor_item(self):
        return '_PARTS_' in self.item_label

    @property
    def is_license(self):
        return '_JOB_' in self.item_label

    def random_price(self, sell_price, buy_price):
        min_price = sell_price * 4 // 5  #  80%
        max_price = buy_price * 5 // 4  # 120%
        price = random.randint(min_price, max_price)
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
        self.item_label = other.item_label
        self.count = other.count
        self.is_money = other.is_money
        self.price = other.price



class ItemObject(ItemSlot):
    def __init__(self, obj):
        self.key = obj.key
        self.slot = obj

        # Must be patched
        self.item_label = self.slot.HaveItemLabel
        self.count = self.slot.HaveItemCnt
        self.is_money = self.slot.IsMoney

        # Constraints
        item_db = Manager.get_instance('ItemDB').table
        valid_slot = item_db.get_name(self.slot.HaveItemLabel) or self.slot.IsMoney
        self.skip = obj.ObjectType in [0, 5, 8] or not valid_slot
        self.skip |= self.is_event_item # e.g. Angea's purse
        self.skip |= self.is_key_item # Knowledge/Valuable except rusty weapon or inventor item
        self.skip |= not obj.is_valid
        self.ring = obj.ring
        self.money_allowed = True
        self.always_accessible = obj.is_always_accessible

        # Other data needed if this slot becomes a NPC item
        row = item_db.get_row(self.item_label)
        if row:
            assert row.BuyPrice >= row.SellPrice
            if not self.skip:
                self.price = self.random_price(row.SellPrice, row.BuyPrice)
        else:
            self.price = 42

    @property
    def is_event_item(self):
        return 'EventItem' in self.slot.key

    def patch(self):
        self.slot.HaveItemLabel = self.item_label
        self.slot.HaveItemCnt = self.count
        self.slot.IsMoney = self.is_money


class ItemNPC(ItemSlot):
    def __init__(self, item):
        self.key = item.key
        self.slot = item

        # Must be patched
        self.item_label = self.slot.ItemLabel
        self.price = self.slot.FCPrice

        # Constraints
        item_db = Manager.get_instance('ItemDB').table
        item_name = item_db.get_name(self.slot.ItemLabel)
        self.skip = self.slot.ItemLabel == 'None' or not item_name
        self.skip |= self.is_key_item
        self.skip |= item.dont_shuffle
        self.skip |= not item.is_valid
        self.ring = item.ring
        self.money_allowed = False
        self.always_accessible = item.is_always_accessible

        # Other data needed if this slot becomes an Object 
        self.count = 1
        self.is_money = False


    def patch(self):
        self.slot.ItemLabel = self.item_label
        self.slot.FCPrice = self.price


class ItemGuild(ItemSlot):
    def __init__(self, guild):
        self.key = guild.key
        self.slot = guild

        # Must be patches
        self.item_label = self.slot.LicenseItem

        # Constraints
        self.skip = False
        self.ring = 2
        self.money_allowed = False
        self.always_accessible = True

        # Other data
        self.count = 1
        self.is_money = False
        self.price = license_price()

    def patch(self):
        self.slot.LicenseItem = self.item_label


class ItemGuildAdv(ItemSlot):
    def __init__(self, item, json_file):
        self.guild = Manager.get_json(json_file)
        self.vanilla = item
        self.item_label = item

        self.skip = False
        self.ring = 2
        self.money_allowed = False
        self.always_accessible = True

        self.count = 1
        self.is_money = False
        self.price = license_price()

    def patch(self):
        for command in self.guild.json_list:
            for i, value in enumerate(command.opt):
                if value == self.vanilla:
                    command.opt[i] = self.item_label


class ItemArmsmaster(ItemSlot):
    def __init__(self):
        self.slot = Manager.get_asset_only('BP_WeaponMasterUtil')
        self.item_label = 'ITM_EQP_JOB_0008'

        # Constraints
        self.skip = False
        self.ring = 2
        self.money_allowed = False
        self.always_accessible = True

        # Other data
        self.count = 1
        self.is_money = False
        self.price = license_price()

    def patch(self):
        self.slot.uasset.replace_index('ITM_EQP_JOB_0008', self.item_label)
        value = self.slot.uasset.get_index(self.item_label)
        self.slot.patch_int64(0x50b6, value)


# Currently ONLY used for the Rusty Sword
# TODO: Look through sidequests, requirements, and rewards,
# and consider adding all of them to the randomizer
class ItemSideQuest(ItemSlot):
    def __init__(self):
        self.item_label = 'ITM_TRE_WPM_01' # Rusty Sword

        self.skip = False
        self.ring = 2
        self.money_allowed = False
        self.always_accessible = True

        self.count = 1
        self.is_money = False
        self.price = random.randint(1, 5) * 10000

    def patch(self):
        substories = Manager.get_table('SubStoryTask')
        substories.SS_SNW2_0200.RewardParam[0] = self.item_label


# Chests, hidden items, and stealing/bargaining
# TODO: redesign classes to allow for copying, or allow
# for making slots and candidates the same objects (e.g.
# store all vanilla stuff when instantiating)
class Treasures(Shuffler):
    check_chapter = no_weights
    include_licenses = False
    include_inventor_parts = False
    include_rusty_weapons = False

    def __init__(self):
        self.object_db = Manager.get_instance('ObjectData').table
        self.shop_db = Manager.get_instance('PurchaseItemTable').table
        self.guild_db = Manager.get_instance('GuildData').table

        slots = []
        candidates = []

        # Chests & Hidden Items
        for obj in self.object_db:
            slots.append(ItemObject(obj))
            candidates.append(ItemObject(obj))

        # NPC shops
        for shop in self.shop_db:
            if shop.is_npc:
                slots.append(ItemNPC(shop))
                candidates.append(ItemNPC(shop))

        # Sidequests -- Rusty Sword only
        slots.append(ItemSideQuest())
        candidates.append(ItemSideQuest())

        # Guild/Licenses
        self.proof_of_conjurer = None
        if self.include_licenses:
            for guild in self.guild_db:
                if guild.LicenseItem != 'None':
                    slots.append(ItemGuild(guild))
                    candidates.append(ItemGuild(guild))

            slots.append(ItemGuildAdv('ITM_EQP_JOB_0009', 'SYS_WIZ_GUILD_0000'))
            candidates.append(ItemGuildAdv('ITM_EQP_JOB_0009', 'SYS_WIZ_GUILD_0000'))

            slots.append(ItemGuildAdv('ITM_EQP_JOB_0010', 'SYS_SHA_GUILD_0100'))
            candidates.append(ItemGuildAdv('ITM_EQP_JOB_0010', 'SYS_SHA_GUILD_0100'))
            self.proof_of_conjurer = slots[-1] # Will need to edit multiple files later

            slots.append(ItemGuildAdv('ITM_EQP_JOB_0011', 'SYS_INV_GUILD_0010'))
            candidates.append(ItemGuildAdv('ITM_EQP_JOB_0011', 'SYS_INV_GUILD_0010'))

            slots.append(ItemArmsmaster())
            candidates.append(ItemArmsmaster())

        # Might be cleaner to turn these items on if necessary
        # i.e. skips are True by default and set to False if needed
        if not self.include_rusty_weapons or EventsAndItems.include_guilds or EventsAndItems.include_guild_spawn:
            counter = 0
            for s, c in zip(slots, candidates):
                if s.is_rusty and not s.skip:
                    s.skip = True
                    c.skip = True
                    counter += 1
            assert counter == 6

        if not self.include_inventor_parts or EventsAndItems.include_guilds or EventsAndItems.include_guild_spawn:
            counter = 0
            for s, c in zip(slots, candidates):
                if s.is_inventor_item and not s.skip:
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

    def generate_weights(self):
        super().generate_weights(check_money, Treasures.check_chapter,
                                rusty_always_accessible, inventor_always_accessible,
                                license_always_accessible)

    def finalize_licenses(self):
        # Only consider slots with pointless items as candidates
        # for second and third licenses of base jobs
        candidates = []
        for slot in self.slots:
            if slot.item_has_little_value and slot.always_accessible:
                candidates.append(slot)

        #### TODO:
        # add check to see if a license ended up in a guild
        # in that case, don't add 2 extra licenses anywhere!
        #
        # if the license ended up not at a guild
        # don't let any of the two additional slots be at a guild!
        # e.g. filter out guild slots in the loop above!

        slots = random.sample(candidates, 16)
        slots[0].item_label = 'ITM_EQP_JOB_0000' # Merchant
        slots[1].item_label = 'ITM_EQP_JOB_0000'
        slots[2].item_label = 'ITM_EQP_JOB_0001' # Thief
        slots[3].item_label = 'ITM_EQP_JOB_0001'
        slots[4].item_label = 'ITM_EQP_JOB_0002' # Warrior
        slots[5].item_label = 'ITM_EQP_JOB_0002'
        slots[6].item_label = 'ITM_EQP_JOB_0003' # Hunter
        slots[7].item_label = 'ITM_EQP_JOB_0003'
        slots[8].item_label = 'ITM_EQP_JOB_0004' # Cleric
        slots[9].item_label = 'ITM_EQP_JOB_0004'
        slots[10].item_label = 'ITM_EQP_JOB_0005' # Dancer
        slots[11].item_label = 'ITM_EQP_JOB_0005'
        slots[12].item_label = 'ITM_EQP_JOB_0006' # Scholar
        slots[13].item_label = 'ITM_EQP_JOB_0006'
        slots[14].item_label = 'ITM_EQP_JOB_0007' # Apothecary
        slots[15].item_label = 'ITM_EQP_JOB_0007'
        for slot in slots:
            slot.price = license_price()

        # Update flags in first events to ensure subjobs can be equipped before
        # going to a guild
        gak = Manager.get_json('MS_GAK_10_0100')
        kar = Manager.get_json('MS_KAR_10_0200')
        ken = Manager.get_json('MS_KEN_10_0100')
        kus = Manager.get_json('MS_KUS_10_0100')
        odo = Manager.get_json('MS_ODO_10_0100')
        sho = Manager.get_json('MS_SHO_10_0100')
        sin = Manager.get_json('MS_SIN_10_0100')
        tou = Manager.get_json('MS_TOU_10_0100')

        gak.change_flag(406, 411) # 406 stays off, 411 gets turned on
        kar.change_flag(406, 411)
        ken.change_flag(406, 411)
        kus.change_flag(406, 411)
        odo.change_flag(406, 411)
        sho.change_flag(406, 411)
        sin.change_flag(406, 411)
        tou.change_flag(406, 411)

        # Have all PCs start with first 2 inventor abilities.
        # This is way simpler than finding the right place in event scripts
        # to add the apprioriate commands.
        reminiscence = Manager.get_instance('ReminiscenceSetting').table
        reminiscence.agnea.add_to_backpack('ITM_TRE_INV_01', 1)
        reminiscence.agnea.add_to_backpack('ITM_TRE_INV_02', 1)
        reminiscence.castti.remove_from_backpack('ITM_MRL_REV_0010') # Grape Leaf
        reminiscence.castti.add_to_backpack('ITM_TRE_INV_01', 1)
        reminiscence.castti.add_to_backpack('ITM_TRE_INV_02', 1)
        reminiscence.hikari.add_to_backpack('ITM_TRE_INV_01', 1)
        reminiscence.hikari.add_to_backpack('ITM_TRE_INV_02', 1)
        reminiscence.partitio.add_to_backpack('ITM_TRE_INV_01', 1)
        reminiscence.partitio.add_to_backpack('ITM_TRE_INV_02', 1)
        reminiscence.ochette.add_to_backpack('ITM_TRE_INV_01', 1)
        reminiscence.ochette.add_to_backpack('ITM_TRE_INV_02', 1)
        reminiscence.osvald.add_to_backpack('ITM_TRE_INV_01', 1)
        reminiscence.osvald.add_to_backpack('ITM_TRE_INV_02', 1)
        reminiscence.temenos.add_to_backpack('ITM_TRE_INV_01', 1)
        reminiscence.temenos.add_to_backpack('ITM_TRE_INV_02', 1)
        reminiscence.throne.add_to_backpack('ITM_TRE_INV_01', 1)
        reminiscence.throne.add_to_backpack('ITM_TRE_INV_02', 1)

        ##### Update all event files that give the Proof of Conjurer
        if self.proof_of_conjurer:
            guild = ItemGuildAdv('ITM_EQP_JOB_0010', 'SC_SS_TDesert31_0400_1000')
            guild.item_label = self.proof_of_conjurer.item_label
            guild.patch()


    def finalize(self):
        if self.include_licenses:
            self.finalize_licenses()
