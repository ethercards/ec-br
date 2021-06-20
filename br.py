from openpyxl import load_workbook
from itertools import islice
from collections import OrderedDict
import json


rules_filename = "deckfight.xlsx"

# open xls
# load cards

##########################################

def count_rows(worksheet):
    row_count = 0
    for row_cells in worksheet.iter_rows():
        if row_cells[0].value is None:
            break
        row_count += 1
    return row_count


def fetch_values(sheet, columns):
    # List to hold dictionaries
    dict_list = []
    # Iterate through non empty rows in worksheet and fetch values into dict
    row_count = count_rows(sheet)
    for row in islice(sheet.values, 1, row_count):
        dict = OrderedDict()
        for value, column in zip(row, columns.keys()):
            # all number is float by default
            if columns[column] == "int":
                if value is not None and not isinstance(value, int):
                    print(
                        f"Invalid int value: ({value}), type: ({type(value)}), column: ({column}) was generated as 0..."
                    )
                    value = None
                dict[column] = int(value) if value is not None else value
            else:
                dict[column] = value
        dict_list.append(dict)
    return dict_list

##########################################
def load_layers(sheet):
    columns = {
            "seq"  : "str",
            "code" : "str",
            "Type" : "str",
            "value": "str"
            }
    layers = fetch_values(sheet,columns)
    return(layers)


def load_combos(sheet):
    columns = {
            "type"          :   "str",
            "combo"         :   "str",
            "attack_action" :   "str",
            "attack_amount" :   "str",
            "attack_extra"  :   "str",
            "shield_action" :   "str",
            "shield_amount" :   "str",
            "shield_extra"  :   "str",
            "life_action"   :   "str",
            "life_amount"   :   "str",
            "life_extra"    :   "str",
            "crit_action"   :   "str",
            "crit_amt"      :   "str"
            }
    combos = fetch_values(sheet,columns)
    return(combos)



workbook = load_workbook(filename=rules_filename)
layers = load_layers(workbook["layers"])

print(len(layers))


combos = load_combos(workbook["combos"])
print(combos)

