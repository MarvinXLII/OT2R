from DataTable import Row
from Manager import Manager


class SupportRow(Row):
    @property
    def name(self):
        text_db = Manager.get_instance('GameTextEN').table
        return text_db.get_text(self.DisplayName)
