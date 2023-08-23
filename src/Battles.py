import random
from Nothing import Nothing
from Assets import Data

def shuffler(enemies, *attributes):
    stuff = []
    stuffBosses = []
    mainEnemies = []
    bossEnemies = []
    for enemy in enemies.table:
        if 'TEST' in enemy.key:
            continue

        data = []
        for attr in attributes:
            v = getattr(enemy, attr)
            data.append(v)

        if 'ENE_BOS' in enemy.key:
            stuffBosses.append(data)
            bossEnemies.append(enemy)
        else:
            stuff.append(data)
            mainEnemies.append(enemy)

    random.shuffle(stuff)
    random.shuffle(stuffBosses)

    for data, enemy in zip(stuff, mainEnemies):
        for value, attr in zip(data, attributes):
            setattr(enemy, attr, value)

    for data, enemy in zip(stuffBosses, bossEnemies):
        for value, attr in zip(data, attributes):
            setattr(enemy, attr, value)


def dropItem(enemies):
    shuffler(enemies, 'HaveItemID', 'DropProbability')

def stealItem(enemies):
    shuffler(enemies, 'StealGuard', 'StealItemID')

def stealMoney(enemies):
    shuffler(enemies, 'StealMoneyGuard', 'StealMoney')
        
def bribeMoney(enemies):
    shuffler(enemies, 'BribeGuard', 'BribeMoney')


def dropItemRate(enemies):
    for enemy in enemies.table:
        enemy.DropProbability = 100


class Battles:
    scaleExp = 1
    scaleJP = 1
    scaleLeaves = 1
    scaleEnemyHP = 1
    scaleEnemyATK = 1
    scaleEnemyMATK = 1
    scaleEnemyDEF = 1
    scaleEnemyMDEF = 1
    scaleEnemyACC = 1
    scaleEnemyEVA = 1
    scaleEnemyAGI = 1
    alwaysDropItem = Nothing
    shuffleDropItem = Nothing
    shuffleStealItem = Nothing
    shuffleStealMoney = Nothing
    shuffleBribeMoney = Nothing
    
    def __init__(self):
        self.enemyDB = Data.getInstance('EnemyDB')

    def run(self):
        # Non-random stuff
        self._scale()
        Battles.alwaysDropItem(self.enemyDB)

        # Randomized stuff
        Battles.shuffleDropItem(self.enemyDB)
        Battles.shuffleStealItem(self.enemyDB)
        Battles.shuffleStealMoney(self.enemyDB)
        Battles.shuffleBribeMoney(self.enemyDB)

    def _scale(self):
        for enemy in self.enemyDB.table:
            enemy.Exp = int(Battles.scaleExp * enemy.Exp)
            enemy.JobPoint = int(Battles.scaleJP * enemy.JobPoint)
            enemy.Money = int(Battles.scaleLeaves * enemy.Money)
            enemy.Param['HP'] = int(Battles.scaleEnemyHP * enemy.Param['HP'])
            enemy.Param['ATK'] = int(Battles.scaleEnemyATK * enemy.Param['ATK'])
            enemy.Param['MATK'] = int(Battles.scaleEnemyMATK * enemy.Param['MATK'])
            enemy.Param['DEF'] = int(Battles.scaleEnemyDEF * enemy.Param['DEF'])
            enemy.Param['MDEF'] = int(Battles.scaleEnemyMDEF * enemy.Param['MDEF'])
            enemy.Param['ACC'] = int(Battles.scaleEnemyACC * enemy.Param['ACC'])
            enemy.Param['EVA'] = int(Battles.scaleEnemyEVA * enemy.Param['EVA'])
            enemy.Param['AGI'] = int(Battles.scaleEnemyAGI * enemy.Param['AGI'])
