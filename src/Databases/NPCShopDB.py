from DataTable import Table

class NPCShopTable(Table):
    def getNPCShop(self, key):
        row = self.getRow(key)
        if row:
            return row
