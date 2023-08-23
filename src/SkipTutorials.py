from Manager import Manager
import sys

class SkipTutorials:
    @staticmethod
    def run():
        sys.exit("Has side effect with unlocking the Support menu. Don't use this option!")
        tutorial_flag_db = Manager.get_table('TutorialFlagPart')
        for row in tutorial_flag_db:
            row.PageDataLabel = ['None'] * 8
