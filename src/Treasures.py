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

def separate_treasure_shuffle(w, s, c):
    for si, slot in enumerate(s):
        w[si] *= type(slot) == type(c)


class ItemSlot(Slot):
    @property
    def is_knowledge(self):
        return 'ITM_INF' in self.item_label

    @property
    def is_valuable(self):
        return 'ITM_TRE' in self.item_label

    @property
    def is_key_item(self):
        return self.is_knowledge or self.is_valuable or self.is_rusty or self.is_inventor_item or self.is_license

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

    def get_item_price(self, item_label):
        # Other data needed if this slot becomes a NPC item
        item_db = Manager.get_instance('ItemDB').table
        row = item_db.get_row(self.item_label)
        if row:
            assert row.BuyPrice >= row.SellPrice
            return self.random_price(row.SellPrice, row.BuyPrice)
        return 42

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
        self.skip |= self.is_key_item
        self.skip |= not obj.is_valid
        self.ring = obj.ring
        self.money_allowed = True
        self.always_accessible = obj.is_always_accessible
        self.price = self.get_item_price(self.item_label)

    @property
    def is_event_item(self):
        return 'EventItem' in self.slot.key

    def patch(self):
        self.slot.HaveItemLabel = self.item_label
        self.slot.HaveItemCnt = self.count
        self.slot.IsMoney = self.is_money


class ItemChest(ItemObject):
    def __init__(self, obj):
        assert obj.is_chest
        super().__init__(obj)


class ItemHidden(ItemObject):
    def __init__(self, obj):
        assert obj.is_hidden
        super().__init__(obj)


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


# TODO: must ensure "The Traveler's Bag" only gets include once in the candidates/slots!
# then must update all others to have the same new item!
# TODO: find way to shuffle number of rewards per sidequest (ensure each has at least 1 always, plus money)
class ItemSideQuest(ItemSlot):
    def __init__(self, sq, index):
        self.key = sq.key
        self.slot = sq
        self.index = index

        self.item_label = sq.RewardParam[index]
        self.skip = self.item_label == 'None' or self.is_key_item
        self.count = 'None' if self.skip else int(sq.RewardParam[index+1])

        assert isinstance(sq.RewardParam[index+1], str)
        self.money_allowed = False # Money is handled separately in each row
        self.always_accessible = True
        self.is_money = False
        self.price = self.get_item_price(self.item_label)

        # TODO: will need to set rings
        self.ring = 2

    def patch(self):
        self.slot.RewardParam[self.index] = self.item_label
        self.slot.RewardParam[self.index+1] = str(self.count)


# Chests, hidden items, and stealing/bargaining
# TODO: redesign classes to allow for copying, or allow
# for making slots and candidates the same objects (e.g.
# store all vanilla stuff when instantiating)
class Treasures(Shuffler):
    check_chapter = no_weights
    shuffle_treasures_separately = no_weights

    include_chests = False
    include_hidden = False
    include_npc_shops = False
    include_sidequests = False

    def __init__(self):
        self.object_db = Manager.get_instance('ObjectData').table
        self.shop_db = Manager.get_instance('PurchaseItemTable').table
        self.sidequest_db = Manager.get_instance('SubStoryTask').table

        slots = []
        candidates = []

        if self.include_chests:
            for obj in self.object_db:
                if obj.is_chest:
                    slots.append(ItemChest(obj))
                    candidates.append(ItemChest(obj))

        if self.include_hidden:
            for obj in self.object_db:
                if obj.is_hidden:
                    slots.append(ItemHidden(obj))
                    candidates.append(ItemHidden(obj))

        if self.include_npc_shops:
            for shop in self.shop_db:
                if shop.is_npc:
                    slots.append(ItemNPC(shop))
                    candidates.append(ItemNPC(shop))

        # Sidequests
        self.sq_travelers_bag = []
        self.sq_travelers_bag_1 = None
        self.sq_travelers_bag_2 = None
        self.sq_travelers_bag_3 = None
        if self.include_sidequests:
            for sq in self.sidequest_db:
                if sq.sq_name is not None:
                    assert len(sq.RewardParam) == 6
                    s1 = ItemSideQuest(sq, 0)
                    s2 = ItemSideQuest(sq, 2)
                    s3 = ItemSideQuest(sq, 4)
                    c1 = ItemSideQuest(sq, 0)
                    c2 = ItemSideQuest(sq, 2)
                    c3 = ItemSideQuest(sq, 4)
                    if sq.is_travelers_bag:
                        if self.sq_travelers_bag_1:
                            # These sidequests will be patched after shuffling
                            self.sq_travelers_bag.append(s1)
                            self.sq_travelers_bag.append(s2)
                            self.sq_travelers_bag.append(s3)
                        else:
                            self.sq_travelers_bag_1 = s1
                            self.sq_travelers_bag_2 = s2
                            self.sq_travelers_bag_3 = s3
                            assert self.sq_travelers_bag_1.index == 0
                            assert self.sq_travelers_bag_2.index == 2
                            assert self.sq_travelers_bag_3.index == 4
                            # Only shuffle these rewards for 1 of the 9 sidequests
                            slots.append(s1)
                            slots.append(s2)
                            slots.append(s3)
                            candidates.append(c1)
                            candidates.append(c2)
                            candidates.append(c3)
                    else:
                        slots.append(s1)
                        slots.append(s2)
                        slots.append(s3)
                        candidates.append(c1)
                        candidates.append(c2)
                        candidates.append(c3)

        # Remove key items/events
        self.slots = list(filter(lambda x: not x.skip, slots))
        self.candidates = list(filter(lambda x: not x.skip, candidates))
            
        # Other stuff to be used for shuffling
        self.vacant = None
        self.weights = None

    def generate_weights(self):
        super().generate_weights(check_money, Treasures.check_chapter,
                                 Treasures.shuffle_treasures_separately)

    def finalize_sidequests(self):
        # Make all Traveler's Bag rewards be the same
        slots = iter(self.sq_travelers_bag)
        n = len(self.sq_travelers_bag)
        assert n % 3 == 0
        while n:
            next(slots).copy(self.sq_travelers_bag_1)
            next(slots).copy(self.sq_travelers_bag_2)
            next(slots).copy(self.sq_travelers_bag_3)
            n -= 3
        # Shuffle money rewards
        sidequests = sorted(set([s.slot for s in self.slots if isinstance(s, ItemSideQuest)]))
        for i, si in enumerate(sidequests):
            sj = random.sample(sidequests[i:], 1)[0]
            si.RewardMoney, sj.RewardMoney = sj.RewardMoney, si.RewardMoney
        slot_tb = self.sq_travelers_bag_1.slot
        slots = sorted(set([s.slot for s in self.sq_travelers_bag]))
        slots.sort()
        for si in slots:
            si.RewardMoney = slot_tb.RewardMoney

    def finalize(self):
        if self.include_sidequests:
            self.finalize_sidequests()

    def finish(self):
        super().finish()
        for slot in self.sq_travelers_bag:
            slot.patch()
