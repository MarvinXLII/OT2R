from DataTable import Table, Row
import hjson
from Utility import get_filename
from Manager import Manager

class SidequestRow(Row):

    def __init__(self, *args):
        super().__init__(*args)
        self.gametext = Manager.get_instance('GameTextEN').table
        self.item_db = Manager.get_instance('ItemDB').table
        self.vanilla_1 = self.get_reward_text(1)
        self.vanilla_2 = self.get_reward_text(2)
        self.vanilla_3 = self.get_reward_text(3)
        self.vanilla_money = self.get_money_text()

        self.sq_name = self.gametext.get_text(self.TitleTextLabel)
        self.is_travelers_bag = self.sq_name == "The Traveler's Bag"
        self.is_sidequest = self.sq_name is not None

    def get_reward_text(self, n):
        assert n > 0 and n < 4
        index = n * 2 - 2
        item_label =  self.RewardParam[index]
        if item_label == 'None':
            return ''
        
        name = self.item_db.get_name(item_label)
        assert name != 'None'
        assert name != None

        count = int(self.RewardParam[index+1])
        if count > 1:
            return f'{name} x{count}'
        return name

    def get_money_text(self):
        return f'{self.RewardMoney} leaves'

    def __gt__(self, other):
        return self.sq_name > other.sq_name
        

class SidequestTable(Table):
    pass
