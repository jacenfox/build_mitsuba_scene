import csv


class ConditionParser():

    def __init__(self):
        pass

    def load(self, fname):
        self.fname_condition = fname
        data = open(self.fname_condition, 'r')
        self.conditions = list(csv.DictReader(data, delimiter='\t'))
