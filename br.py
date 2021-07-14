from openpyxl import load_workbook
from itertools import islice
from collections import OrderedDict
import json
import uuid
import random

rules_filename = "deckfight2.xlsx"
cards_filename = "cards.json"


# open xls
# load cards

##########################################


class Player:

    def __init__(self, card_data, layers, all_combos, all_playing_cards):
        self.params = {
            "combo_group": 0,
            "character_type": 0,
            "crit": 0
        }

        self.data = card_data
        dna = (card_data["layer_image"].split("/")[-1]).split(".")[0]
        self.params["dna"] = dna
        self.params["card_id"] = card_data["id"]

        self.params["health"] = int(layers[("0" + dna[0:2])]["value"])

        self.params["deck_limit"] = int(layers[("1" + dna[2:4])]["value"])

        self.params["combo_group"] = int(layers[("2" + dna[4:6])]["value"])

        self.params["character_type"] = int(layers[("3" + dna[6:8])]["value"])

        self.params["crit"] = int(layers[("4" + dna[8:10])]["value"])

        self.params["combos"] = []

        self.params["playing_cards"] = []

        for combo in all_combos:
            if combo["type"] == self.params["combo_group"]:
                self.params["combos"].append(combo)

        for playing_card in all_playing_cards:
            if playing_card["character_type"] == self.params["character_type"]:
                self.params["playing_cards"].append(playing_card)

        self.params["deck"] = []
        self.params["deck_cost"] = 0;

    def generate_random_deck(self):
        deck = []
        deck_cost = 0
        for card_counter in range(self.params["deck_limit"]):
            random_card = random.choice(self.params["playing_cards"])
            deck_cost += random_card["cost"]
            deck.append(random_card)
        self.params["deck"] = deck
        self.params["deck_cost"] = deck_cost
        return deck

    def character(self):
        return (self.params)


class BattlingPlayerObject:
    def __init__(self, player):
        # initializing permanent components
        self.player_combos = player.params["combos"]
        self.player_dna = player.params["dna"]
        self.player_max_health = player.params["health"]

        # initializing changing components for player1
        self.player_deck = player.params["deck"]
        self.player_health = player.params["health"]
        self.player_shield = 0
        self.player_combo_string = ""
        self.active_boosts = []
        self.player_crit_chance = player.params["crit"]
        self.player_current_deck_size = len(self.player_deck)
        print(self.player_dna, " has: ", self.player_health, " health points")


class Boost:
    def __init__(self, boost_card):
        self.boost_card = boost_card
        self.unique_id = uuid.uuid4()
        self.attack_boost = None
        self.shield_boost = None
        self.life_boost = None
        self.crit_boost = None
        self.special_boost = None
        self.combo_boost = None
        self.evaluate_boost_card_information(self.boost_card)

    def evaluate_boost_card_information(self, boost_card):
        if boost_card["target_type"] == "combo":
            self.combo_boost = ComboBoost(boost_card, self.unique_id)
        elif "special" in boost_card:
            self.special_boost = SpecialBoost(boost_card, self.unique_id)
        else:
            if "shield" in boost_card:
                self.shield_boost = ShieldBoost(boost_card, self.unique_id)
            if "life" in boost_card:
                self.life_boost = LifeBoost(boost_card, self.unique_id)
            if "attack" in boost_card:
                self.attack_boost = AttackBoost(boost_card, self.unique_id)
            if "crit" in boost_card:
                self.attack_boost = CritBoost(boost_card, self.unique_id)


class AttackBoost:
    def __init__(self, boost_card, id):
        self.boost_card = boost_card
        self.unique_id = id
        self.target_type = boost_card["target_type"]
        self.target_opp = ["target_opp"]
        self.action_type = boost_card["attack"]["action"]
        self.amount = int(boost_card["attack"]["amount"])
        self.card_timing = 0
        self.card_count = 0

        if self.target_type != "player":
            self.card_timing = int(boost_card["card_timing"])
            self.card_count = int(boost_card["card_count"])


class ComboBoost:
    def __init__(self, boost_card, id):
        self.boost_card = boost_card
        self.unique_id = id
        self.target_type = boost_card["target_type"]
        self.attack_action_type = ""
        self.attack_action_amount = 0
        self.shield_action_type = ""
        self.shield_action_amount = 0
        self.crit_action_amount = ""
        self.crit_action_amount = 0

        self.card_timing = 0
        self.card_count = 0

        if self.target_type != "player":
            self.card_timing = int(boost_card["card_timing"])
            self.card_count = int(boost_card["card_count"])

        if "attack" in boost_card:
            self.attack_action_type = boost_card["attack"]["action"]
            self.attack_action_amount = int(boost_card["attack"]["amount"])

        if "crit" in boost_card:
            self.crit_action_type = boost_card["crit"]["action"]
            self.crit_action_amount = int(boost_card["crit"]["amount"])

        if "shield" in boost_card:
            self.shield_action_type = boost_card["shield"]["action"]
            self.shield_action_amount = int(boost_card["shield"]["amount"])


class LifeBoost:
    def __init__(self, boost_card, id):
        self.boost_card = boost_card
        self.unique_id = id
        self.target_type = boost_card["target_type"]
        self.target_opp = boost_card["target_opp"]
        self.action_type = boost_card["life"]["action"]
        self.amount = int(boost_card["life"]["amount"])

        self.card_timing = 0
        self.card_count = 0

        if self.target_type != "player":
            self.card_timing = int(boost_card["card_timing"])
            self.card_count = int(boost_card["card_count"])


class ShieldBoost:
    def __init__(self, boost_card, id):
        self.boost_card = boost_card
        self.unique_id = id
        self.target_type = boost_card["target_type"]
        self.target_opp = boost_card["target_opp"]
        self.action_type = boost_card["shield"]["action"]
        self.amount = int(boost_card["shield"]["amount"])

        self.card_timing = 0
        self.card_count = 0

        if self.target_type != "player":
            self.card_timing = int(boost_card["card_timing"])
            self.card_count = int(boost_card["card_count"])


class CritBoost:
    def __init__(self, boost_card, id):
        self.boost_card = boost_card
        self.unique_id = id
        self.target_type = boost_card["target_type"]
        self.target_opp = boost_card["target_opp"]
        self.action_type = boost_card["crit"]["action"]
        self.amount = int(boost_card["crit"]["amount"])


class SpecialBoost:
    def __init__(self, boost_card, id):
        self.boost_card = boost_card
        self.unique_id = id
        self.target_type = boost_card["target_type"]
        self.target_opp = boost_card["target_opp"]
        self.special = boost_card["special"]


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
        "seq": "str",
        "code": "str",
        "Type": "str",
        "value": "str"
    }
    ls = fetch_values(sheet, columns)
    layers = {}
    for layer in ls:
        k = str(int(layer["seq"]))
        c = layer["code"]
        if isinstance(c, int):
            c = int(c)
        c = str(c)
        k = k + c
        layers[k] = layer

    return (layers)


def load_cards(sheet):
    columns = {
        "id": "str",
        "name": "str",
        "character_type": "str",
        "card_type": "str",
        "combo_sign": "str",
        "attack_action": "str",
        "attack_amount": "str",
        "attack_extra": "str",
        "shield_action": "str",
        "shield_amount": "str",
        "shield_extra": "str",
        "life_action": "str",
        "life_amount": "str",
        "life_extra": "str",
        "crit_action": "str",
        "crit_amount": "str",
        "crit_extra": "str",
        "special": "str",
        "target_opp": "str",
        "target_type": "str",
        "target_subtype": "str",
        "card_timing": "str",
        "card_count": "str",
        "cost": "str"
    }
    cards_data = fetch_values(sheet, columns)
    cards = []
    for cd in cards_data:
        card = {}
        if cd["attack_action"] is not None:
            card["attack"] = {
                "action": cd["attack_action"],
                "amount": int(cd["attack_amount"]),
            }
            if cd["attack_extra"] is not None:
                card["attack"]["extra"] = int(cd["attack_extra"])
        if cd["shield_action"] is not None:
            card["shield"] = {
                "action": cd["shield_action"],
                "amount": int(cd["shield_amount"]),
            }
            if cd["shield_extra"] is not None:
                card["shield"]["extra"] = int(cd["shield_extra"])
        if cd["life_action"] is not None:
            card["life"] = {
                "action": cd["life_action"],
                "amount": int(cd["life_amount"]),
            }
            if cd["life_extra"] is not None:
                card["life"]["extra"] = int(cd["life_extra"])
        if cd["crit_action"] is not None:
            card["crit"] = {
                "action": cd["crit_action"],
                "amount": int(cd["crit_amount"]),
            }
            if cd["crit_extra"] is not None:
                card["crit"]["extra"] = int(cd["crit_extra"])
        if cd["special"] is not None:
            card["special"] = cd["special"]
        if cd["target_opp"] is not None:
            card["target_opp"] = cd["target_opp"]
        if cd["target_type"] is not None:
            card["target_type"] = cd["target_type"]
            if (cd["target_type"] == "card") or (cd["target_type"] == "combo"):
                card["target_subtype"] = cd["target_subtype"]
                card["card_timing"] = int(cd["card_timing"])
                card["card_count"] = int(cd["card_count"])
        card["cost"] = int(cd["cost"])
        card["character_type"] = int(cd["character_type"])
        card["name"] = cd["name"]
        card["card_type"] = cd["card_type"]
        card["combo_sign"] = cd["combo_sign"]
        cards.append(card)

    return cards


def load_combos(sheet):
    columns = {
        "type": "str",
        "combo": "str",
        "attack_action": "str",
        "attack_amount": "str",
        "attack_extra": "str",
        "shield_action": "str",
        "shield_amount": "str",
        "shield_extra": "str",
        "life_action": "str",
        "life_amount": "str",
        "life_extra": "str",
        "crit_action": "str",
        "crit_amt": "str"
    }
    cs = fetch_values(sheet, columns)
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
        combo["combo_code"] = c["combo"]
        combos.append(combo)
    return combos


def battle(player1, player2):
    round_counter = 1
    battling_player1 = BattlingPlayerObject(player1)
    battling_player2 = BattlingPlayerObject(player2)
    print("----------------------------")
    print("Round ", round_counter, ": ")
    round_counter += 1
    while evaluate_round(battling_player1, battling_player2):
        print("----------------------------")
        print("Round ", round_counter, ": ")
        round_counter += 1
    return determine_winner(battling_player1, battling_player2)


def evaluate_round(battling_player1, battling_player2):
    # game over condition
    if (battling_player1.player_health < 1 or battling_player2.player_health < 1) or \
            (battling_player1.player_current_deck_size == 0 and battling_player2.player_current_deck_size == 0):
        return False

    if len(battling_player1.player_deck) != 0:
        battling_player1_card_to_play = battling_player1.player_deck.pop(0)
        battling_player1.player_current_deck_size -= 1
        print(battling_player1.player_dna, " plays ", battling_player1_card_to_play["combo_sign"])
    else:
        battling_player1_card_to_play = None

    if len(battling_player2.player_deck) != 0:
        battling_player2_card_to_play = battling_player2.player_deck.pop(0)
        battling_player2.player_current_deck_size -= 1
        print(battling_player2.player_dna, " plays ", battling_player2_card_to_play["combo_sign"])

    else:
        battling_player2_card_to_play = None

    evaluate_cards(battling_player1, battling_player1_card_to_play, battling_player2, battling_player2_card_to_play)

    return True


def evaluate_cards(battling_player1, battling_player1_card_to_play, battling_player2, battling_player2_card_to_play):
    # technically revealing the two cards and adding their combo signs to the string
    if battling_player1_card_to_play is not None:
        battling_player1.player_combo_string += battling_player1_card_to_play["combo_sign"]
    if battling_player2_card_to_play is not None:
        battling_player2.player_combo_string += battling_player2_card_to_play["combo_sign"]

    # evaluate neutralizer phase

    # evaluate boost phase
    (battling_player1, battling_player2) = evaluate_boost_phase(battling_player1, battling_player1_card_to_play,
                                                                battling_player2, battling_player2_card_to_play)

    # evaluate combo phase
    (battling_player1, battling_player2) = evaluate_combo_phase(battling_player1, battling_player2)

    # evaluate defense phase
    (battling_player1, battling_player2) = evaluate_defense_phase(battling_player1, battling_player1_card_to_play,
                                                                  battling_player2, battling_player2_card_to_play)

    # evaluate attack phase
    (battling_player1, battling_player2) = evaluate_attack_phase(battling_player1, battling_player1_card_to_play,
                                                                 battling_player2, battling_player2_card_to_play)

    return battling_player1, battling_player2


def evaluate_boost_phase(battling_player1, battling_player1_card_to_play,
                         battling_player2, battling_player2_card_to_play):
    if battling_player1_card_to_play is not None:
        if battling_player1_card_to_play["combo_sign"] == "B":
            print("boost card is being played by ", battling_player1.player_dna)
            boost = Boost(battling_player1_card_to_play)
            battling_player1.active_boosts.append(boost)

    if battling_player2_card_to_play is not None:
        if battling_player2_card_to_play["combo_sign"] == "B":
            print("boost card is being played by : ", battling_player2.player_dna)
            boost = Boost(battling_player2_card_to_play)
            battling_player2.active_boosts.append(boost)

    print(len(battling_player1.active_boosts), "; ", len(battling_player2.active_boosts))

    return battling_player1, battling_player2


def remove_boost(active_player, boost_id):
    boost_to_remove_index = None
    for index in range(len(active_player.active_boosts)):
        if active_player.active_boosts[index].unique_id == boost_id:
            boost_to_remove_index = index
    if boost_to_remove_index is not None:
        active_player.active_boosts.pop(boost_to_remove_index)

    return active_player


def evaluate_combo_phase(battling_player1, battling_player2):
    # check for level1 combo
    if len(battling_player1.player_combo_string) > 2:
        level1_combo_string = battling_player1.player_combo_string[len(battling_player1.player_combo_string) - 3:]
        for combo in battling_player1.player_combos:
            if combo["combo_code"] == level1_combo_string:
                battling_player1.player_combo_string = ""
                print("Found a level1 combo: ", level1_combo_string)

    if len(battling_player2.player_combo_string) > 2:
        level1_combo_string = battling_player2.player_combo_string[len(battling_player2.player_combo_string) - 3:]
        for combo in battling_player2.player_combos:
            if combo["combo_code"] == level1_combo_string:
                battling_player2.player_combo_string = ""
                print("Found a level1 combo: ", level1_combo_string)
    # -----------------------------------------------------------------------------------------
    # check for level2 combo
    if len(battling_player1.player_combo_string) > 3:
        level2_combo_string = battling_player1.player_combo_string[len(battling_player1.player_combo_string) - 4:]
        for combo in battling_player1.player_combos:
            if combo["combo_code"] == level2_combo_string:
                battling_player1.player_combo_string = ""
                print("Found a level2 combo: ", level2_combo_string)

    if len(battling_player2.player_combo_string) > 3:
        level2_combo_string = battling_player2.player_combo_string[len(battling_player2.player_combo_string) - 4:]
        for combo in battling_player2.player_combos:
            if combo["combo_code"] == level2_combo_string:
                battling_player2.player_combo_string = ""
                print("Found a level2 combo: ", level2_combo_string)
    # -----------------------------------------------------------------------------------------
    # check for level3 combo

    if len(battling_player1.player_combo_string) > 4:
        level3_combo_string = battling_player1.player_combo_string[len(battling_player1.player_combo_string) - 5:]
        for combo in battling_player1.player_combos:
            if combo["combo_code"] == level3_combo_string:
                battling_player1.player_combo_string = ""
                print("Found a level3 combo: ", level3_combo_string)

    if len(battling_player2.player_combo_string) > 3:
        level3_combo_string = battling_player2.player_combo_string[len(battling_player2.player_combo_string) - 5:]
        for combo in battling_player2.player_combos:
            if combo["combo_code"] == level3_combo_string:
                battling_player2.player_combo_string = ""
                print("Found a level3 combo: ", level3_combo_string)
    # -----------------------------------------------------------------------------------------
    # check for level4 combo

    if len(battling_player1.player_combo_string) > 5:
        level4_combo_string = battling_player1.player_combo_string[len(battling_player1.player_combo_string) - 6:]
        for combo in battling_player1.player_combos:
            if combo["combo_code"] == level4_combo_string:
                battling_player1.player_combo_string = ""
                print("Found a level4 combo: ", level4_combo_string)

    if len(battling_player2.player_combo_string) > 5:
        level4_combo_string = battling_player2.player_combo_string[len(battling_player2.player_combo_string) - 6:]
        for combo in battling_player2.player_combos:
            if combo["combo_code"] == level4_combo_string:
                battling_player2.player_combo_string = ""
                print("Found a level4 combo: ", level4_combo_string)
    # -----------------------------------------------------------------------------------------
    # check for level5 combo
    if len(battling_player1.player_combo_string) > 6:
        level5_combo_string = battling_player1.player_combo_string[len(battling_player1.player_combo_string) - 7:]
        for combo in battling_player1.player_combos:
            if combo["combo_code"] == level5_combo_string:
                battling_player1.player_combo_string = ""
                print("Found a level5 combo: ", level5_combo_string)

    if len(battling_player2.player_combo_string) > 6:
        level5_combo_string = battling_player2.player_combo_string[len(battling_player2.player_combo_string) - 7:]
        for combo in battling_player2.player_combos:
            if combo["combo_code"] == level5_combo_string:
                battling_player2.player_combo_string = ""
                print("Found a level1 combo: ", level5_combo_string)

    return battling_player1, battling_player2


def evaluate_defense_phase(battling_player1, battling_player1_card_to_play, battling_player2,
                           battling_player2_card_to_play):
    # evaluate defense for player1
    if battling_player1_card_to_play is not None:
        if battling_player1_card_to_play["combo_sign"] == "D":
            life_boosts = []
            shield_boosts = []
            if len(battling_player1.active_boosts) > 0:
                for boost in battling_player1.active_boosts:
                    if boost.shield_boost is not None:
                        shield_boosts.append(boost.shield_boost)
                    if boost.life_boost is not None:
                        life_boosts.append(boost.life_boost)

            if len(shield_boosts) > 0 or len(life_boosts):
                evaluate_defense_card(battling_player1, battling_player1_card_to_play, life_boosts, shield_boosts)
            else:
                evaluate_defense_card(battling_player1, battling_player1_card_to_play)

    # evaluate defense for player2
    if battling_player2_card_to_play is not None:
        if battling_player2_card_to_play["combo_sign"] == "D":
            life_boosts = []
            shield_boosts = []
            if len(battling_player2.active_boosts) > 0:
                for boost in battling_player2.active_boosts:
                    if boost.shield_boost is not None:
                        shield_boosts.append(boost.shield_boost)
                    if boost.life_boost is not None:
                        life_boosts.append(boost.life_boost)

            if len(shield_boosts) > 0 or len(life_boosts):
                evaluate_defense_card(battling_player2, battling_player2_card_to_play, life_boosts, shield_boosts)
            else:
                evaluate_defense_card(battling_player2, battling_player2_card_to_play)

    return battling_player1, battling_player2


def evaluate_defense_card(active_player, card_to_play, life_boosts=[], shield_boosts=[]):
    # check if the card is of type shield
    if "shield" in card_to_play:
        # calculating final shield value
        min_shield_value = card_to_play["shield"]["amount"]
        max_shield_value = card_to_play["shield"]["extra"]
        random_shield_array = []
        for shield_value in range(min_shield_value, max_shield_value):
            random_shield_array.append(shield_value)
        final_shield_value = random.choice(random_shield_array)

        # TODO check if the boost is shield or life type
        # evaluating shield boost
        # REDDOOOO
        if len(shield_boosts) > 0:
            final_shield_value, active_player = evaluate_shield_boost(final_shield_value, active_player, shield_boosts)
        # apply shield to player
        active_player.player_shield += final_shield_value
        print(active_player.player_dna, " gained ", final_shield_value, "shield, his current total is: ",
              active_player.player_shield)

    else:
        if "life" in card_to_play:

            # calculating final life value
            min_life_value = card_to_play["life"]["amount"]
            max_life_value = card_to_play["life"]["extra"]
            random_life_array = []
            for life_value in range(min_life_value, max_life_value):
                random_life_array.append(life_value)
            final_life_value = random.choice(random_life_array)

            # evaluating life boost
            if len(life_boosts) > 0:
                final_life_value, active_player = evaluate_life_boost(final_life_value, active_player, life_boosts)

            # apply life to player
            active_player.player_health += final_life_value

            # capping the hp
            if active_player.player_health > active_player.player_max_health:
                health_surplus = active_player.player_health - active_player.player_max_health
                active_player.player_health = active_player.player_max_health
                final_life_value -= health_surplus
            print(active_player.player_dna, " gained ", final_life_value, " life, his total is now: ",
                  active_player.player_health)


def evaluate_life_boost(final_value, active_player, active_life_boosts):
    # evaluate the life boosts that add flat value
    for life_boost in active_life_boosts:
        if life_boost.action_type == "+":
            final_value += life_boost.amount
            active_player = remove_boost(active_player, life_boost.unique_id)
            print("Life boosted by +", life_boost.amount, " new final_life_value is: ", final_value)
    # evaluate the life boosts that multiply the value
    for life_boost in active_life_boosts:
        if life_boost.action_type == "x":
            final_value = final_value * life_boost.amount
            active_player = remove_boost(active_player, life_boost.unique_id)
            print("Life boosted by x", life_boost.amount, " new final_life_value is: ", final_value)

    return final_value, active_player


def evaluate_shield_boost(final_value, active_player, active_shield_boosts):
    # evaluate the shield boosts that add flat value
    for shield_boost in active_shield_boosts:
        if shield_boost.action_type == "+":
            final_value += shield_boost.amount
            active_player = remove_boost(active_player, shield_boost.unique_id)
            print("Shield boosted by +", shield_boost.amount, " new final_shield_value is: ", final_value)
    # evaluate the shield boosts that multiply the value
    for shield_boost in active_shield_boosts:
        if shield_boost.action_type == "x":
            final_value = final_value * shield_boost.amount
            active_player = remove_boost(active_player, shield_boost.unique_id)
            print("Shield boosted by x", shield_boost.amount, " new final_shield_value is: ", final_value)

    return final_value, active_player


def evaluate_attack_phase(battling_player1, battling_player1_card_to_play, battling_player2,
                          battling_player2_card_to_play):
    # evaluate attack for player1
    if battling_player1_card_to_play is not None:
        if battling_player1_card_to_play["combo_sign"] == "A":
            attack_boosts = []
            if len(battling_player1.active_boosts) > 0:
                for boost in battling_player1.active_boosts:
                    if boost.attack_boost is not None:
                        attack_boosts.append(boost.attack_boost)
            if len(attack_boosts) > 0:
                evaluate_attack_card(battling_player1, battling_player2, battling_player1_card_to_play,
                                     battling_player1.player_crit_chance, attack_boosts)
            else:
                evaluate_attack_card(battling_player1, battling_player2, battling_player1_card_to_play,
                                     battling_player1.player_crit_chance)

    # evaluate attack for player2
    if battling_player2_card_to_play is not None:
        if battling_player2_card_to_play["combo_sign"] == "A":
            evaluate_attack_card(battling_player1, battling_player2_card_to_play, battling_player2.player_crit_chance)

    return battling_player1, battling_player2


def evaluate_attack_card(attacking_player, defending_player, card_to_play, attacking_player_crit_ratio,
                         active_boosts=[]):
    # calculating the final damage based on crit ration and attack range
    min_attack_damage = card_to_play["attack"]["amount"]
    max_attack_damage = card_to_play["attack"]["extra"]
    random_array = [0] * 100
    for i in range(attacking_player_crit_ratio):
        random_array[i] = 1
    is_crit = random.choice(random_array)
    if is_crit:
        final_damage = max_attack_damage
    else:
        damage_array = []
        for d in range(min_attack_damage, max_attack_damage):
            damage_array.append(d)
        final_damage = random.choice(damage_array)
    # evaluating attack boost
    if len(active_boosts) > 0:
        final_damage, attacking_player = evaluate_attack_boost(final_damage, attacking_player, active_boost)

    # taking player shield into consideration
    if defending_player.player_shield > 0:
        if defending_player.player_shield >= final_damage:
            damage_blocked = final_damage
            defending_player.player_shield -= final_damage
            print(defending_player.player_dna, " blocked ", damage_blocked, "and  took ", 0, " damage, his HP now is: ",
                  defending_player.player_health, "and shield: ", defending_player.player_shield)
        else:
            damage_blocked = defending_player.player_shield
            final_damage -= defending_player.player_shield
            defending_player.player_shield = 0
            defending_player.player_health -= final_damage
            print(defending_player.player_dna, " blocked ", damage_blocked, "and  took ", final_damage,
                  " damage, his HP now is: ", defending_player.player_health, "and shield: ",
                  defending_player.player_shield)
    else:
        defending_player.player_health -= final_damage
        print(defending_player.player_dna, " took ", final_damage, " damage, his HP now is: ",
              defending_player.player_health, "and shield: ", defending_player.player_shield)


def evaluate_attack_boost(final_damage, attacking_player, active_boosts):
    # evaluate flat bonus damage
    for attack_boost in active_boosts:
        if attack_boost.action_type == "+":
            final_value += attack_boost.amount
            attacking_player = remove_boost(attacking_player, attack_boost.unique_id)
            print("Attack boosted by +", attack_boost.amount, " new attack_final_value is: ", final_value)

    # evaluate multiplayer bonus damage
    for attack_boost in active_boosts:
        if attack_boost.action_type == "+":
            final_value += attack_boost.amount
            attacking_player = remove_boost(attacking_player, attack_boost.unique_id)
            print("Attack boosted by +", attack_boost.amount, " new attack_final_value is: ", final_value)

    return final_damage, attacking_player


def determine_winner(battling_player1, battling_player2):
    if battling_player1.player_health > battling_player2.player_health:
        return battling_player1.player_dna
    elif battling_player1.player_health < battling_player2.player_health:
        return battling_player2.player_dna
    else:
        if battling_player1.player_shield > battling_player2.player_shield:
            return battling_player1.player_dna
        elif battling_player1.player_shield < battling_player2.player_shield:
            return battling_player2.player_dna
        else:
            return "DRAW"


workbook = load_workbook(filename=rules_filename)
layers = load_layers(workbook["layers"])

print("processed layers:", len(layers))

combos = load_combos(workbook["combos"])
playing_cards = load_cards(workbook["cards"])
print("processed combos:", len(combos))
print("--------------")
print(combos)
print("--------------")

print("todo: select players")
# load cards
with open(cards_filename, encoding='utf-8') as json_file:
    nft_cards = json.load(json_file)

# load 2 random nft_cards
nft_card1 = random.choice(nft_cards)
nft_card2 = random.choice(nft_cards)

# create players based on nft cards
player1 = Player(nft_card1, layers, combos, playing_cards)
player2 = Player(nft_card2, layers, combos, playing_cards)
player1.generate_random_deck()
player2.generate_random_deck()
print("player1:", player1.character())
print("player1 combos: ", player1.params["combos"])
print("player1 playing_cards: ", player1.params["playing_cards"])
print("player1 random deck: ", player1.params["deck"])
print("player1 random deck cost: ", player1.params["deck_cost"])
print("player 1 deck size: ", len(player1.params["deck"]))
print("--------------")
print("player2:", player2.character())
print("player2 combos: ", player2.params["combos"])
print("player2 playing_cards: ", player2.params["playing_cards"])
print("player2 random deck: ", player2.params["deck"])
print("player2 random deck cost: ", player2.params["deck_cost"])
print("player2 deck size: ", len(player2.params["deck"]))
print("-----------------")
print("Test battle simulated between player1 and player2")

for i in range(15):
    # load 2 random nft_cards
    nft_card1 = random.choice(nft_cards)
    nft_card2 = random.choice(nft_cards)

    # create players based on nft cards
    player1 = Player(nft_card1, layers, combos, playing_cards)
    player2 = Player(nft_card2, layers, combos, playing_cards)
    player1.generate_random_deck()
    player2.generate_random_deck()
    print("The winner is: ", battle(player1, player2))

