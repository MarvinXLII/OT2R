from DataTable import Table, Row


class ReminiscenceRow(Row):
    def addToBackpack(self, item, num):
        for i, f in enumerate(self.FirstBackpackItemLabel):
            if f == 'None':
                break
        else:
            sys.exit(f'Backpack of {self.key} is full!')

        self.FirstBackpackItemLabel[i] = item
        self.FirstBackpackItemNum[i] = num

    def removeFromBackpack(self, item):
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
        return self.getRow('DANCER_PROLOGUE')

    @property
    def castti(self):
        return self.getRow('ALCHEMIST_PROLOGUE')

    @property
    def hikari(self):
        return self.getRow('FENCER_PROLOGUE')

    @property
    def partitio(self):
        return self.getRow('MERCHANT_PROLOGUE')

    @property
    def ochette(self):
        return self.getRow('HUNTER_PROLOGUE')

    @property
    def osvald(self):
        return self.getRow('PROFESSOR_PROLOGUE')

    @property
    def temenos(self):
        return self.getRow('PRIEST_PROLOGUE')

    @property
    def throne(self):
        return self.getRow('THIEF_PROLOGUE')
