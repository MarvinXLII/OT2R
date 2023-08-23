from DataTable import Table, Row
from Manager import Manager

class GuildRow(Row):
    def __init__(self, *args):
        super().__init__(*args)

    @property
    def license(self):
        itemDB = Manager.getInstance('ItemDB').table
        return itemDB.getName(self.LicenseItem)
        

class GuildTable(Table):
    def __init__(self, data, rowClass):
        super().__init__(data, rowClass)

        # Map job name to guild row
        # Important for guilds that require mastered jobs
        # as they check that the last skill is learned
        self.guildMap = {
            'eFENCER': self.getRow('GUILD_000'),
            'eHUNTER': self.getRow('GUILD_001'),
            'eALCHEMIST': self.getRow('GUILD_002'),
            'eMERCHANT': self.getRow('GUILD_003'),
            'ePRIEST': self.getRow('GUILD_004'),
            'ePROFESSOR': self.getRow('GUILD_005'),
            'eTHIEF': self.getRow('GUILD_006'),
            'eDANCER': self.getRow('GUILD_007'),
        }
