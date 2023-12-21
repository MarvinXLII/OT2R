import random
from Manager import Manager
import sys

class AdvJPNerf:
    def __init__(self):
        self.job_db = Manager.get_instance('JobData')

    def run(self):
        for jKey in self.job_db.adv_job_keys:
            row = self.job_db.table.get_row(jKey)
            row.JPCost = [0, 0, 30, 100, 500, 1000, 3000, 5000]


class JPCosts:
    def __init__(self):
        self.job_db = Manager.get_instance('JobData')

    def run(self):
        for row in self.job_db.table:
            row.JPCost = list(map(self._random_cost, row.JPCost))

    def _random_cost(self, value):
        if value == 0:
            return 0
        if value == 1:
            return 1
        if value == 30:
            return random.randint(1, 5) * 10
        if value == 100:
            return random.randint(6, 14) * 10
        if value == 500:
            return random.randint(40, 60) * 10
        if value == 1000:
            return random.randint(80, 120) * 10
        if value == 2000:
            return random.randint(160, 240) * 10
        if value == 3000:
            return random.randint(240, 360) * 10
        if value == 5000:
            return random.randint(400, 600) * 10
        sys.exit(f"JP cost {value} is not setup")
