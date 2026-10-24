import dearpygui.dearpygui as dpg
from rule import dataRule, ruleTypes

def add(parent, rule as dataRule):
    with dpg.collapsing_header(parent=parent, label=rule.data_point.dataType):
        with dpg.group(horizontal= True): 
            dpg.add_text(label="if"+dataRule.data_pont.rule_type)
            dpg.add_combo(items={"GREATER_THAN", "LESS_THAN", "EQUAL_TO", "NOT_EQUAL_TO"})

print("hi")
        
