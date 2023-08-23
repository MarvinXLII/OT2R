from Assets import Data
from DataTable import DataTable, Row

class Text(Row):
    def __init__(self, *args):
        super().__init__(*args)

    def setText(self, string):
        self.Text = string

    def replaceSubstring(self, targ, repl):
        if targ in self.Text:
            self.Text = self.Text.replace(targ, repl)
            return True
        return False

    def inString(self, substring):
        return substring in self.Text

class GameText(DataTable):
    Row = Text

    def __init__(self):
        super().__init__('GameTextEN.uasset')

    def getText(self, key):
        row = self.table.getRow(key)
        if row:
            return row.Text

    def setText(self, key, string):
        row = self.table.getRow(key)
        row.Text = string

    def replaceSubstring(self, key, targ, repl):
        row = self.table.getRow(key)
        row.Text = row.Text.replace(targ, repl)


class TalkData(DataTable):
    def __init__(self):
        super().__init__("TalkData_EN.uasset")

    def getText(self, key):
        row = self.table.getRow(key)
        if row:
            assert len(row.Text) == 1
            return row.Text[0]

    def setText(self, key, string):
        row = self.table.getRow(key)
        row.Text[0] = string

    def replaceSubstring(self, key, targ, repl):
        row = self.table.getRow(key)
        row.Text[0] = row.Text[0].replace(targ, repl)
