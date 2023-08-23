from Manager import Manager
import sys

class SkipTutorials:
    @staticmethod
    def run():
        sys.exit("Has side effect with unlocking the Support menu. Don't use this option!")
        tutorialFlagTable = Manager.getTable('TutorialFlagPart')
        for row in tutorialFlagTable:
            row.PageDataLabel = ['None'] * 8
