from DataTable import Table, Row


class ReminiscenceRow(Row):
    def add_to_backpack(self, item, num):
        for i, f in enumerate(self.FirstBackpackItemLabel):
            if f == 'None':
                break
        else:
            sys.exit(f'Backpack of {self.key} is full!')

        self.FirstBackpackItemLabel[i] = item
        self.FirstBackpackItemNum[i] = num

    def remove_from_backpack(self, item):
        for i, f in enumerate(self.FirstBackpackItemLabel):
            if f == item:
                break
        else:
            sys.exit(f'Item {item} not in backpack!')

        self.FirstBackpackItemLabel[i] = 'None'
        self.FirstBackpackItemNum[i] = 0

        for i, fi in enumerate(self.FirstBackpackItemLabel[:-1]):
            if fi == 'None':
                self.FirstBackpackItemLabel[i], self.FirstBackpackItemLabel[i+1] = self.FirstBackpackItemLabel[i+1], self.FirstBackpackItemLabel[i]
                self.FirstBackpackItemNum[i], self.FirstBackpackItemNum[i+1] = self.FirstBackpackItemNum[i+1], self.FirstBackpackItemNum[i]        


class ReminiscenceTable(Table):
    @property
    def agnea(self):
        return self.get_row('DANCER_PROLOGUE')

    @property
    def castti(self):
        return self.get_row('ALCHEMIST_PROLOGUE')

    @property
    def hikari(self):
        return self.get_row('FENCER_PROLOGUE')

    @property
    def partitio(self):
        return self.get_row('MERCHANT_PROLOGUE')

    @property
    def ochette(self):
        return self.get_row('HUNTER_PROLOGUE')

    @property
    def osvald(self):
        return self.get_row('PROFESSOR_PROLOGUE')

    @property
    def temenos(self):
        return self.get_row('PRIEST_PROLOGUE')

    @property
    def throne(self):
        return self.get_row('THIEF_PROLOGUE')
