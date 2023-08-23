from DataTable import Table, Row

class TextRow(Row):
    def __init__(self, *args):
        super().__init__(*args)

    def set_text(self, string):
        self.Text = string

    def replace_substring(self, targ, repl):
        if targ in self.Text:
            self.Text = self.Text.replace(targ, repl)
            return True
        return False

    def in_string(self, substring):
        return substring in self.Text

class TextTable(Table):
    def __init__(self, data, row_class):
        super().__init__(data, row_class)

    def get_text(self, key):
        row = self.get_row(key)
        if row:
            return row.Text

    def set_text(self, key, string):
        row = self.get_row(key)
        row.Text = string

    def replace_substring(self, key, targ, repl):
        row = self.get_row(key)
        row.Text = row.Text.replace(targ, repl)


# class TalkData:
#     def __init__(self):
#         self.table = Manager.get_table('TalkData_EN')

#     def get_text(self, key):
#         row = self.table.get_row(key)
#         if row:
#             assert len(row.Text) == 1
#             return row.Text[0]

#     def set_text(self, key, string):
#         row = self.table.get_row(key)
#         row.Text[0] = string

#     def replace_substring(self, key, targ, repl):
#         row = self.table.get_row(key)
#         row.Text[0] = row.Text[0].replace(targ, repl)
