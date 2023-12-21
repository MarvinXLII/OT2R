from DataTable import Table, Row
from Manager import Manager
import sys

class NPCHearRow(Row):

    def __init__(self, *args):
        super().__init__(*args)
        self.hear_info = self._get_hear_info()

    def _get_hear_info(self):
        assert self.HearInfoIDs[1] == 'None'
        assert self.HearInfoIDs[2] == 'None'
        hear_info = Manager.get_instance('NPCHearInfoData').table
        if hasattr(hear_info, self.HearInfoIDs[0]):
            return getattr(hear_info, self.HearInfoIDs[0])
        return None

    @property
    def item(self):
        if self.hear_info == None:
            return None
        if self.hear_info.ItemID == 'None':
            return None
        item_db = Manager.get_instance('ItemDB').table
        assert hasattr(item_db, self.hear_info.ItemID), type(self.hear_info.ItemID)
        return getattr(item_db, self.hear_info.ItemID)

    @property
    def is_hidden_item(self):
        if self.item:
            return self.item.name == 'A Hidden Item'
        return False

    @property
    def is_knowledge(self):
        if self.hear_info:
            return 'ITM_INF' in self.hear_info.ItemID
        return False
        
    @property
    def is_valuable(self):
        if self.hear_info:
            return 'ITM_TRE' in self.hear_info.ItemID
        return False

    @property
    def is_rusty(self):
        if self.hear_info:
            return '_WPM_' in self.hear_info.ItemID
        return False

    @property
    def is_inventor_item(self):
        if self.hear_info:
            return '_PARTS_' in self.hear_info.ItemID
        return False

    @property
    def is_license(self):
        if self.hear_info:
            return '_JOB_' in self.hear_info.ItemID
        return False

    @property
    def is_key_item(self):
        return self.is_knowledge or self.is_valuable \
            or self.is_rusty or self.is_inventor_item \
            or self.is_license

    # Hikari
    def set_default_bribe(self):
        if self.BriberyBuyPrice > 0:
            self.BriberyBuyPrice = min(100, self.BriberyBuyPrice)

    # Castti
    def set_default_inquire(self):
        if self.HearNeedLevel > 0:
            self.HearNeedLevel = min(1, self.HearNeedLevel)

    # Osvald
    def set_default_scrutinize(self):
        if self.SearchBaseProbability > 0:
            self.SearchBaseProbability = max(55.0, self.SearchBaseProbability)

    def set_default_path_actions(self):
        self.set_default_bribe()
        self.set_default_inquire()
        self.set_default_scrutinize()


class NPCHearTable(Table):
    pass
