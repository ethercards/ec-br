from openpyxl import load_workbook
from itertools import islice
from collections import OrderedDict
import json
import random

rules_filename = "deckfight.xlsx"
cards_filename = "cards.json"

# open xls
# load cards

##########################################
class Player:

    def __init__(self, card_data, layers, combos):
        self.params = {
            "combo_group"    : 0,
            "character_type" : 0,
            "crit"           : 0
        }
        
        self.data = card_data
        dna = (card_data["layer_image"].split("/")[-1]).split(".")[0] 
        self.params["dna"] = dna
        self.params["card_id"] = card_data["id"]

        self.params["health"]         = int(layers[("0"+dna[0:2])]["value"])
        
        self.params["deck_limit"]     = int(layers[("1"+dna[2:4])]["value"])
        
        self.params["combo_group"]    = int(layers[("2"+dna[4:6])]["value"])
        
        self.params["character_type"] = int(layers[("3"+dna[6:8])]["value"])
        
        self.params["crit"]           = int(layers[("4"+dna[8:10])]["value"])


    def character(self):
        return(self.params)



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
    ls = fetch_values(sheet,columns)
    layers = {}
    for layer in ls:
        k = str(int(layer["seq"]))
        c = layer["code"]
        if isinstance(c,int):
            c = int(c)
        c = str(c)
        k = k + c
        layers[k] = layer

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
    cs = fetch_values(sheet,columns)
    combos = []
    for c in cs:
        combo = {}
        combo["type"] = int(c["type"])

        # attack
        if c["attack_action"] is not None:
            combo["attack"] = {
                    "action": c["attack_action"],
                    "amount": int(c["attack_amount"]),
                    }
            if c["attack_extra"] is not None:
                combo["attack"]["extra"] = int(c["attack_extra"])

        # shield
        if c["shield_action"] is not None:
            combo["shield"] = {
                    "action": c["shield_action"],
                    "amount": int(c["shield_amount"]),
                    }
            if c["shield_extra"] is not None:
                combo["shield"]["extra"] = int(c["shield_extra"])

        # life
        if c["life_action"] is not None:
            combo["life"] = {
                    "action": c["life_action"],
                    "amount": int(c["life_amount"]),
                    }
            if c["life_extra"] is not None:
                combo["life"]["extra"] = int(c["life_extra"])

        # crit
        print(c)
        if c["crit_action"] is not None:
            combo["crit"] = {
                    "action": c["crit_action"],
                    "amount": int(c["crit_amt"]),
                    }
        
        combos.append(combo)
    return(combos)


workbook = load_workbook(filename=rules_filename)
layers = load_layers(workbook["layers"])

print("processed layers:",len(layers))

combos = load_combos(workbook["combos"])
print("processed combos:",len(combos))
print("--------------")
print(combos)
print("--------------")


print("todo: select players")
# load cards
with open(cards_filename) as json_file:                                                                                                                                                                                                                                                     
    cards = json.load(json_file)

# select two
card1 = random.choice(cards)
card2 = random.choice(cards)
player1 = Player(card1,layers,combos)
player2 = Player(card2,layers,combos)
print("player1:",player1.character())
print("--------------")
print("player2:",player2.character())
#print("--------------")
#print("card1:",card1)
#print("--------------")
#print("card2:",card2)

#print("todo: build profiles")
#print("todo: generate deck")
#print("todo: inititiate battlefield")
#print("todo: play battle")
