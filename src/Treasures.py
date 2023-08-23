import random
from Shuffler import Shuffler, Slot, noWeights
from Assets import Data

def CheckMoney(w, s, c):
    for si, slot in enumerate(s):
        if c.isMoney:
            w[si] *= slot.moneyAllowed
            
def separateChapter(w, s, c):
    for si, slot in enumerate(s):
        w[si] *= slot.chapter == c.chapter


class ItemSlot(Slot):
    @property
    def isKnowledge(self):
        return 'ITM_INF' in self.itemLabel

    @property
    def isValuable(self):
        return 'ITM_TRE' in self.itemLabel

    def randomPrice(self, sellPrice, buyPrice):
        minPrice = sellPrice * 4 // 5  #  80%
        maxPrice = buyPrice * 5 // 4  # 120%
        price = random.randint(minPrice, maxPrice)
        p = price
        if price < 100:
            price = price // 5 * 5
        elif price < 1000:
            price = price // 50 * 50
        elif price << 10000:
            price = price // 100 * 100
        else:
            price = price // 1000 * 1000
        return price

    def copy(self, other):
        self.itemLabel = other.itemLabel
        self.count = other.count
        self.isMoney = other.isMoney
        self.price = other.price

    def printer(self, itemDB):
        s = self.itemLabel + '  '
        if self.skip:
            return
        if self.isMoney:
            s += str(self.count) + ' leaves'
        elif self.itemLabel:
            x = itemDB.getName(self.itemLabel)
            if x:
                s += x
            else:
                if not self.skip:
                    print('here')
                s += 'NAME RETURNED NONE'
        else:
            sys.exit()
        print(s)


class ItemObject(ItemSlot):
    def __init__(self, obj, itemDB):
        self.key = obj.key
        self.slot = obj

        # Must be patched
        self.itemLabel = self.slot.HaveItemLabel
        self.count = self.slot.HaveItemCnt
        self.isMoney = self.slot.IsMoney

        # Constraints
        validSlot = itemDB.getName(self.slot.HaveItemLabel) or self.slot.IsMoney
        self.skip = obj.ObjectType in [0, 5, 8] or not validSlot
        self.skip |= self.isEventItem # e.g. Angea's purse
        self.skip |= self.isKnowledge # potentially a key item
        self.skip |= self.isValuable # potentially a key item
        self.skip |= not obj.isPlaced
        obj.skipped = self.skip
        self.chapter = 0
        self.moneyAllowed = True

        # Other data needed if this slot becomes a NPC item
        row = itemDB.table.getRow(self.itemLabel)
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
    def __init__(self, item, itemDB):
        self.key = item.key
        self.slot = item

        # Must be patched
        self.itemLabel = self.slot.ItemLabel
        self.price = self.slot.FCPrice

        # Constraints
        itemName = itemDB.getName(self.slot.ItemLabel)
        self.skip = self.slot.ItemLabel == 'None' or not itemName
        self.skip |= self.isKnowledge
        self.skip |= self.isValuable
        self.skip |= item.dontShuffle
        self.chapter = 0
        self.moneyAllowed = False

        # Other data needed if this slot becomes an Object 
        self.count = 1
        self.isMoney = False

        item.skipped = self.skip

    def patch(self):
        self.slot.ItemLabel = self.itemLabel
        self.slot.FCPrice = self.price
        
        
# Chests, hidden items, and stealing/bargaining
class Treasures(Shuffler):
    CheckChapter = noWeights

    def __init__(self):
        self.objectDB = Data.getInstance('ObjectData')
        self.shopDB = Data.getInstance('PurchaseItemTable')
        self.itemDB = Data.getInstance('ItemDB')

        slots = []
        candidates = []
        for obj in self.objectDB.table:
            slots.append(ItemObject(obj, self.itemDB))
            candidates.append(ItemObject(obj, self.itemDB))
        for shop in self.shopDB.table:
            if shop.isNPC:
                slots.append(ItemNPC(shop, self.itemDB))
                candidates.append(ItemNPC(shop, self.itemDB))

        # Remove key items/events
        self.slots = list(filter(lambda x: not x.skip, slots))
        self.candidates = list(filter(lambda x: not x.skip, candidates))
            
        # Other stuff to be used for shuffling
        self.vacant = None
        self.weights = None

    def generateWeights(self):
        super().generateWeights(CheckMoney, Treasures.CheckChapter)
