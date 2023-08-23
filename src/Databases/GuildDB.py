from DataTable import Table, Row
from Manager import Manager

class GuildRow(Row):
    def __init__(self, *args):
        super().__init__(*args)

    @property
    def license(self):
        item_db = Manager.get_instance('ItemDB').table
        return item_db.get_name(self.LicenseItem)
        

class GuildTable(Table):
    def __init__(self, data, row_class):
        super().__init__(data, row_class)

        # Map job name to guild row
        # Important for guilds that require mastered jobs
        # as they check that the last skill is learned
        self.guild_map = {
            'eFENCER': self.get_row('GUILD_000'),
            'eHUNTER': self.get_row('GUILD_001'),
            'eALCHEMIST': self.get_row('GUILD_002'),
            'eMERCHANT': self.get_row('GUILD_003'),
            'ePRIEST': self.get_row('GUILD_004'),
            'ePROFESSOR': self.get_row('GUILD_005'),
            'eTHIEF': self.get_row('GUILD_006'),
            'eDANCER': self.get_row('GUILD_007'),
        }
