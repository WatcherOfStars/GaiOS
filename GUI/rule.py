from fake_data import dataPoint
from enum import Enum

class ruleTypes(Enum):
    GREATER_THAN = 1
    LESS_THAN = 2
    EQUAL_TO = 3
    NOT_EQUAL_TO = 4

class dataRule:
    #rule observes a data point and triggers a function (set in another class) upon a certain condition being met. Multiple rules can be assigned to one data point
    def __init__(self, data_point):
        self.data_point = data_point
        self.trigger_func = "enter function to trigger"
        self.compare_val = 0
        self.rule_type = ruleTypes.GREATER_THAN
    
    def update(self):

        # test latest value against compare value depending on the selected rule type. If none satified, return false
        last_val = self.data_point.values[-1]

        if (self.rule_type == ruleTypes.GREATER_THAN) and (last_val > self.compare_val):
            return True
        if (self.rule_type == ruleTypes.LESS_THAN) and (last_val < self.compare_val):
            return True
        if (self.rule_type == ruleTypes.EQUAL_TO) and (last_val == self.compare_val):
            return True
        if (self.rule_type == ruleTypes.NOT_EQUAL_TO) and (last_val != self.compare_val):
            return True
        
        return False