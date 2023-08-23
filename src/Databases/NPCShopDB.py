from DataTable import Table

class NPCShopTable(Table):
    def get_npc_shop(self, key):
        row = self.get_row(key)
        if row:
            return row
