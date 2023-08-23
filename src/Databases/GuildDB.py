from Assets import Data
from DataTable import DataTable, Row


class Guild(Row):
    def __init__(self, *args):
        super().__init__(*args)

    @property
    def license(self):
        return self.itemDB.getName(self.LicenseItem)
        


class GuildDB(DataTable):
    Row = Guild

    def __init__(self):
        super().__init__('GuildData.uasset')

        # Map job name to guild row
        # Important for guilds that require mastered jobs
        # as they check that the last skill is learned
        self.guildMap = {
            'eFENCER': self.table.getRow('GUILD_000'),
            'eHUNTER': self.table.getRow('GUILD_001'),
            'eALCHEMIST': self.table.getRow('GUILD_002'),
            'eMERCHANT': self.table.getRow('GUILD_003'),
            'ePRIEST': self.table.getRow('GUILD_004'),
            'ePROFESSOR': self.table.getRow('GUILD_005'),
            'eTHIEF': self.table.getRow('GUILD_006'),
            'eDANCER': self.table.getRow('GUILD_007'),
        }
