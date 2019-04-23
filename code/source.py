import os
import sys
import random
import roman
import datetime
import webcolors
import json

effects_name_to_type = {}
reagents_name_to_type = {}
# npcs_by_name = {}
npcs_by_type = {}
items_by_name = {}
items_name_to_type = {}
events_by_name = {}
events_by_location = {"Overworld": {}, "Dungeon": {}, "Village": {}}
pools = {"Generic": {}, "Treasure": {}, "Devil": {}, "Angel": {}}
forced_events = []
event = None
previous_event = None
previous_previous_event = None
death_reaction = None
previous_sin = 0

tick = 0
log = []


def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def get_colour_name(requested_colour):
    try:
        color_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        color_name = closest_colour(requested_colour)
    return color_name


def Clamp(value, min_, max_):
    return max(min(value, max_), min_)


def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


def tick2time(tick):
    day = tick // 86400
    hour = (tick - (day * 86400)) // 3600
    min_ = (tick - ((day * 86400) + (hour * 3600))) // 60 
    seconds = tick - ((day * 86400) + (hour * 3600) + (min_ * 60))

    return datetime.time(hour, min_, seconds)


def prob(chance):
    roll = random.randint(0, 100)
    if(roll < chance):
        return True
    return False


def clear_output():
    if('idlelib.run' in sys.modules):
        print("\n" * 100)
    else:
        # for windows
        if(os.name == 'nt'):
            os.system('cls')
        # for mac and linux(here, os.name is 'posix')
        else:
            os.system('clear')


def log_fight(attacker, victim, dam, item):
    item_string = ""
    if(item):
        item_string = " using " + item.name
    if(attacker == player):
        add_to_log("You had attacked " + victim.display_name + item_string + " for (" + str(dam) + ") damage.")
    elif(victim == player):
        add_to_log(attacker.display_name + " had attacked you" + item_string + " for (" + str(dam) + ") damage.")
    else:
        add_to_log(attacker.display_name + " had attacked " + victim.display_name + item_string + " for (" + str(dam) + ") damage.")


def log_action(being, string):
    if(being == player):
        add_to_log("You had performed " + string)
    else:
        add_to_log(being.display_name + " had performed " + string)


def add_to_log(string):
    global tick
    global log

    log.append("[" + str(tick2time(player.life_ticks)) + "] " + string)


def force_event(event, force_put=False, check_req=False, force_pos=-1):
    global forced_events

    if(check_req and not events_by_name[event].check_requirements()):
        return

    if(force_pos != -1):
        if(force_put or (event not in forced_events)):
            forced_events.insert(force_pos, event)
            return

    if(force_put or (event not in forced_events)):
        forced_events.append(event)


def pick_event():
    global forced_events
    global event
    global previous_event
    global previous_previous_event

    if(previous_event):
        previous_previous_event = previous_event

    if(event and not event.isTechnical()):
        previous_event = event

    if(player.health <= 0):
        return events_by_name["Death"]

    if(len(forced_events) != 0):
        next_event = forced_events.pop(0)
        if(next_event):
            return events_by_name[next_event]
        else:
            pick_event()
    else:
        pick = random.choice(list(events_by_location[player.location].values()))
        if(pick.check_requirements()):
            return pick
        else:
            return pick_event()
class Event:
    def __init__(self):
        global events_by_name
        global events_by_location

        self.locations = None
        self.default_choices = {"1": "Open inventory.", "2": "Open log.", "3": "Walk past."}
        self.initialize_event()
        self.choices = {}
        events_by_name[self.name] = self
        if(self.locations):
            for location in self.locations:
                events_by_location[location][self.name] = self
        else:
            for location in events_by_location.keys():
                events_by_location[location][self.name] = self

    def initialize_event(self):
        self.name = "Event"
        self.locations = None  # None will make it location-independent.
        self.default_choices = {"1": "Open inventory.", "2": "Open log.", "3": "Walk past."}

    def check_requirements(self):
        if(self.locations and player.location not in self.locations):
            return False
        return self.check_special_requirements()

    def reset(self):
        return

    def full_reset(self):
        self.reset()

    def check_special_requirements(self):
        return True

    def introduce_event(self):
        return

    def generate_choices(self):
        return {"1": "No choices here."}

    def on_choice(self, choice, choice_num):
        return

    def add_choice(self, num, choice):
        self.choices[str(num)] = choice

    def isTechnical(self):  # Return True if an event should not be saved as previous.
        return False

    def return_save_data(self, event_info):
        event_info['name'] = self.name

    def load_save_data(event_info):
        events_by_name[event_info['name']].on_load_save_data(event_info)

    def on_load_save_data(self, event_info):
        return

    def doLifeTick(self):
        return not self.isTechnical()

class Introduction(Event):
    def initialize_event(self):
        self.name = "Introduction"
        self.default_choices = {"1": "Open inventory.", "2": "Open log."}

    def introduce_event(self):
        if(not death_reaction):
            if(player.name == "stranger"):
                print("*Welcome to a life full of adventure, stranger!")
            else:
                print("*Welcome to a life full of adventure, "+ player.display_name +"!*")
        else:
            print("*\"" + death_reaction + "\" were your last words, huh?")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        if(not death_reaction):
            self.add_choice(choice_num, "Okay.")
            choice_num += 1
        else:
            self.add_choice(choice_num, "What?")
            choice_num += 1
        if(player.name == "stranger"):
            self.add_choice(choice_num, "I have a name.")
        else:
            self.add_choice(choice_num, "That is not my name.")

    def on_choice(self, choice, choice_num):
        if(choice == "I have a name."):
            player.name = input()
            if(player.name == "stranger"):
                force_event("Bad Choice")
            else:
                if(not load_from_savefile(player.name)):
                    player.deaths = 0
                    player.title = ""
        elif(choice == "That is not my name."):
            player.name = input()
            if(player.name == "stranger"):
                force_event("Bad Choice")
            else:
                if(not load_from_savefile(player.name)):
                    player.deaths = 0
                    player.title = ""
        force_event("Grassfields", force_put=True, force_pos=0)

    def check_special_requirements(self):
        return False


class Death(Event):
    def initialize_event(self):
        self.name = "Death"
        self.default_choices = {"1": "Okay."}

    def introduce_event(self):
        print("*You have died.*")
        if(npcs_by_type["Death"].amount <= 0):
            print("*But Death did not come.*")
        else:
            if(previous_event and previous_event.name == "Death"):
                print(npcs_by_type["Death"].name + " says, \"Trying to cheat me, huh?\"")
            else:
                for log_entry in log:
                    print(log_entry)

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1

        if(previous_event and previous_event.name == "Death"):
            if(npcs_by_type["Death"].cheated <= 6):
                self.add_choice(choice_num, "Yes.")
            else:
                self.add_choice(choice_num, "Fight them. (F)")

    def on_choice(self, choice, choice_num):
        global death_reaction

        if(choice == "Okay."):
            if(npcs_by_type["Death"].amount >= 1):
                clear_output()
                print("+++++++++++++++++++++++++++++++++++++")
                print("Game over.")
                print("+++++++++++++++++++++++++++++++++++++")
                death_reaction = input()
                reset()
            else:
                player.addHealth(1)
        elif(choice == "Yes."):
            player.title = " the Cheater"
            npcs_by_type["Death"].cheated += 1
            clear_output()
            print("+++++++++++++++++++++++++++++++++++++")
            print("Game over.")
            print("+++++++++++++++++++++++++++++++++++++")
            death_reaction = input()
            reset()
        elif(choice == "Fight them. (F)"):
            events_by_name["Fight"].instigate(npcs_by_type["Death"])

    def check_special_requirements(self):
        return False

    def isTechnical(self):
        return True


class Log(Event):
    def initialize_event(self):
        self.name = "Log"
        self.default_choices = {"1": "Close log."}

    def introduce_event(self):
        global log

        print("*You begin recounting past events.*")
        for log_entry in log:
            print(log_entry)

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1

    def on_choice(self, choice, choice_num):
        if(choice == "Close log."):
            force_event(previous_event.name, force_put=True, force_pos=0)

    def check_special_requirements(self):
        return False

    def isTechnical(self):
        return True


class Fight(Event):
    def initialize_event(self):
        self.name = "Fight"
        self.default_choices = {"1": "Open inventory.", "2": "Disengage.", "3": "Run away. H- F=0"}
        self.npc = None  # What NPC are we fighting?

    def introduce_event(self):
        print("*You engage in a fight, your opponent is " + self.npc.name + "*")
        self.npc.show_stats()
        self.npc.in_fight = True
        print("*You are picking a weapon to attack with.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1

        self.choices_items = {}

        self.add_choice(choice_num, "Bare hands.")
        choice_num += 1

        for item in player.get_all_items():
            self.add_choice(choice_num, item.getDisplayName())
            self.choices_items[str(choice_num)] = item
            choice_num += 1

    def on_choice(self, choice, choice_num):
        global forced_events
        global previous_event
        global player

        if(choice == "Disengage."):
            force_event(previous_event.name, force_put=True, force_pos=0)
        elif(choice == "Bare hands."):
            player.hit(self.npc)
            self.npc.retaliate(player)
        elif(choice == "Run away. H- F=0"):
            player.walk()
            player.addHealth(-1)
            forced_events = list()
            player.food = 0
        else:
            player.hit_with(self.npc, self.choices_items[choice_num])
            self.npc.retaliate(player)
        self.npc.in_fight = False  # We only get this status if the fight continues.

    def check_special_requirements(self):
        return False

    def instigate(self, npc):
        self.npc = npc
        force_event("Fight", force_put=True, force_pos=0)

    def isTechnical(self):
        return True

    def doLifeTick(self):
        return True


class Victory(Event):
    def initialize_event(self):
        self.name = "Victory"
        self.default_choices = {"1": "Open inventory.", "2": "Okay."}
        self.npc = None

    def introduce_event(self):
        add_to_log("You had defeated " + self.npc.display_name + ".")
        print("*You have won in the fight.*")
        self.npc.in_fight = False

    def setup(self, npc):
        self.npc = npc

    def generate_choices(self):
        self.choices = dict(self.default_choices)

    def on_choice(self, choice, choice_num):
        return

    def check_special_requirements(self):
        return False

    def isTechnical(self):
        return True


class Inventory(Event):
    def initialize_event(self):
        self.name = "Inventory"
        self.default_choices = {"1": "Close inventory."}

    def introduce_event(self):
        print("*You have opened your inventory.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1

        self.choices_items = {}

        for item in player.get_all_items():
            self.add_choice(choice_num, item.getDisplayName())
            self.choices_items[str(choice_num)] = item
            choice_num += 1

    def on_choice(self, choice, choice_num):
        if(choice == "Close inventory."):
            force_event(previous_event.name, force_put=True, force_pos=0)
        else:
            item = self.choices_items[choice_num]
            log_action(player, "Use " + choice + ".") 
            item.use()
            force_event("Inventory", force_put=True, force_pos=0)

    def check_special_requirements(self):
        return False

    def isTechnical(self):
        return True


class Devil_Room(Event):
    def initialize_event(self):
        self.name = "Devil Room"
        self.locations = ["Overworld", "Dungeon"]

    def introduce_event(self):
        print("*You are greeted by " + npcs_by_type["Devil"].name + " the Devil, himself.*")
        print(npcs_by_type["Devil"].name + " says, \"Have to inform you, " + (player.display_name + "," if player.name != "stranger" else "stranger,") + " I own " + str(npcs_by_type["Devil"].get_soul_percentage()) + "% of shares that are your soul.\"")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        self.add_choice(choice_num, "Give your soul up. H- S+ ???")
        choice_num += 1
        self.add_choice(choice_num, "Trade your soul for money. H- M+ S+")
        choice_num += 1
        self.add_choice(choice_num, "Trade your soul for food. H- F+ S+")
        choice_num += 1

        d6 = player.get_item("D6")
        if(d6):
            self.add_choice(choice_num, "Reroll them.")
            choice_num += 1

        self.add_choice(choice_num, "Fight them. (F)")

    def on_choice(self, choice, choice_num):
        if(choice == "Walk past."):
            player.walk()
        elif(choice == "Give your soul up. H- S+ ???"):
            player.addSin(1)
            if(prob(100 - npcs_by_type["Devil"].get_soul_percentage())):
                player.loot("Devil")
            player.addHealth(-1)
            self.gather_soul()
        elif(choice == "Trade your soul for money. H- M+ S+"):
            player.addHealth(-1)
            player.addMoney(1)
            player.addSin(1)
            self.gather_soul()
        elif(choice == "Trade your soul for food. H- F+ S+"):
            player.addHealth(-1)
            player.addFood(1)
            player.addSin(1)
            self.gather_soul()
        elif(choice == "Reroll them."):
            npcs_by_type["Devil"].amount += 1
            npcs_by_type["Devil"].die()
        elif(choice == "Fight them. (F)"):
            events_by_name["Fight"].instigate(npcs_by_type["Devil"])

    def check_special_requirements(self):
        return (npcs_by_type["Devil"].get_soul_percentage() <= 100) and ("Black Salt" not in player.inventory.keys()) and npcs_by_type["Devil"].amount >= 1

    def gather_soul(self):
        npcs_by_type["Devil"].souls += 1
        if(npcs_by_type["Devil"].souls >= 12):
            npcs_by_type["Devil"].amount += 1
            npcs_by_type["Devil"].die()  # Get a new one.


class Angel_Room(Event):
    def initialize_event(self):
        self.name = "Angel Room"
        self.locations = ["Overworld", "Dungeon"]

    def introduce_event(self):
        print("*You are greeted by " + npcs_by_type["Angel"].name + " the Angel.*")
        print(npcs_by_type["Angel"].name + " says, \"Stay good.\"")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        if(player.sin <= 0):
            self.add_choice(choice_num, "Receive a blessing. S+")
            choice_num += 1
        self.add_choice(choice_num, "Repent. H- S-")
        choice_num += 1
        if(player.money >= 1):
            self.add_choice(choice_num, "Pay indulgence. M- S-")
            choice_num += 1

        d12 = player.get_item("D12")
        if(d12):
            self.add_choice(choice_num, "Reroll them.")
            choice_num += 1

        self.add_choice(choice_num, "Fight them. (F)")

    def on_choice(self, choice, choice_num):
        if(choice == "Walk past."):
            player.walk()
        elif(choice == "Repent. H- S-"):
            player.addHealth(-1)
            player.addSin(-1)
        elif(choice == "Pay indulgence. M- S-"):
            player.addMoney(-1)
            player.addSin(-1)
        elif(choice == "Receive a blessing. S+"):
            player.addSin(1)  # If you put it the other way around player getting a Holy Cross may die.
            player.loot("Angel")
        elif(choice == "Reroll them."):
            npcs_by_type["Angel"].amount += 1
            npcs_by_type["Angel"].die()
        elif(choice == "Fight them. (F)"):
            events_by_name["Fight"].instigate(npcs_by_type["Angel"])

    def check_special_requirements(self):
        return prob(100 - npcs_by_type["Devil"].get_soul_percentage()) and npcs_by_type["Angel"].amount >= 1


class Starvation(Event):
    def initialize_event(self):
        self.name = "Starvation"
        self.default_choices = {"1": "Open inventory.", "2": "Open log."}

    def introduce_event(self):
        print("*You seem to be starving.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        self.add_choice(choice_num, "Starve. H-")
        choice_num += 1
        self.add_choice(choice_num, "Pray. ???")
        choice_num += 1
        if(player.money >= 1):
            self.add_choice(choice_num, "Chew on your gold. H- F+ M-")
            choice_num += 1
        if(player.food >= 1):
            self.add_choice(choice_num, "Am I?")

    def on_choice(self, choice, choice_num):
        if(choice == "Pray. ???"):
            if(prob(npcs_by_type["Devil"].get_soul_percentage()) and ("Black Salt" not in player.inventory.keys())):
                force_event("Devil Room")
            else:
                force_event("Angel Room")
        elif(choice == "Chew on your gold. H- F+ M-"):
            player.addHealth(-1)
            player.addFood(1)
            player.addMoney(-1)
        elif(choice == "Starve. H-"):
            player.addHealth(-1)
            if(player.health <= 0):
                player.title = " the Starved"
        elif(choice == "Am I?"):
            player.error += 1

    def check_special_requirements(self):
        return player.food <= 0


class Bad_Choice(Event):
    def initialize_event(self):
        self.name = "Bad Choice"
        self.default_choices = {"1": "Open inventory.", "2": "Open log."}

    def introduce_event(self):
        print(random.choice(["*You seem to have made a terrible mistake.*", "*You seem to not be able to count.*", "*What was your score on math test?*"]))

    def check_special_requirements(self):
        return False

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        self.add_choice(choice_num, "Give up. ???")
        choice_num += 1
        if(player.money >= 1):
            self.add_choice(choice_num, "Pay for it. M-")
            choice_num += 1
        if("Jar of Blood" in player.inventory.keys()):
            jar = player.get_item("Jar of Blood")
            if(jar.stored_blood >= 1):
                self.add_choice(choice_num, "Pay with blood.")

    def on_choice(self, choice, choice_num):
        if(choice == "Pay for it. M-"):
            player.addMoney(-1)
        elif(choice == "Pay with blood."):
            jar = player.get_item("Jar of Blood")
            jar.stored_blood -= 1
        elif(choice == "Give up. ???"):
            player.title = " the Wrong"
            player.die()


class Village_Entrance(Event):
    def initialize_event(self):
        self.name = "Village Entrance"
        self.locations = ["Overworld"]

    def introduce_event(self):
        print("*You stumble upon a village.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        if(player.money >= 1):
            self.add_choice(choice_num, "Buy food from locals. F+ M-")
            choice_num += 1
            self.add_choice(choice_num, "Donate money to the village. M- S-")
            choice_num += 1
        self.add_choice(choice_num, "Enter the village.")

    def on_choice(self, choice, choice_num):
        if(choice == "Buy food from locals. F+ M-"):
            player.addFood(1)
            player.addMoney(-1)
        elif(choice == "Donate money to the village. M- S-"):
            player.addMoney(-1)
            npcs_by_type["Villager"].addMoney(1)
            npcs_by_type["Buyer"].addMoney(1)
            player.addSin(-1)
        elif(choice == "Walk past."):
            player.walk()
        elif(choice == "Enter the village."):
            player.location = "Village"
            player.walk()


class Village_Exit(Event):
    def initialize_event(self):
        self.name = "Village Exit"
        self.locations = ["Village"]

    def introduce_event(self):
        print("*You stumble upon the village exit.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        if(player.money >= 1):
            self.add_choice(choice_num, "Buy food from locals. F+ M-")
            choice_num += 1
            self.add_choice(choice_num, "Donate money to the village. M- S-")
            choice_num += 1
        self.add_choice(choice_num, "Exit the village.")

    def on_choice(self, choice, choice_num):
        if(choice == "Buy food from locals. F+ M-"):
            player.addFood(1)
            player.addMoney(-1)
        elif(choice == "Donate money to the village. M- S-"):
            player.addMoney(-1)
            npcs_by_type["Villager"].addMoney(1)
            npcs_by_type["Buyer"].addMoney(1)
            player.addSin(-1)
        elif(choice == "Walk past."):
            player.walk()
        elif(choice == "Exit the village."):
            player.location = "Overworld"
            player.walk()


class Lone_Villager(Event):
    def initialize_event(self):
        self.name = "Villager"
        self.locations = ["Village"]
        self.default_choices = {"1": "Open inventory.", "2": "Open log.", "3": "Walk past."}

    def introduce_event(self):
        print("*You encounter a villager.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        if(player.money >= 1):
            self.add_choice(choice_num, "Give them money. M- S-")
            choice_num += 1

        if(npcs_by_type["Villager"].money >= 1):
            self.add_choice(choice_num, "Work with them. F- M+")
            choice_num += 1

        if(player.location == "Village"):
            self.add_choice(choice_num, "Return to village exit.")
            choice_num += 1

        self.add_choice(choice_num, "Fight them. (F)")

    def on_choice(self, choice, choice_num):
        if(choice == "Give them money. M- S-"):
            player.addMoney(-1)
            npcs_by_type["Villager"].addMoney(1)
            npcs_by_type["Buyer"].addMoney(1)
            player.addSin(-1)
        elif(choice == "Work with them. F- M+"):
            player.addFood(-1)
            player.addMoney(1)
            npcs_by_type["Villager"].addMoney(-1)
        elif(choice == "Return to village exit."):
            player.walk()
            force_event("Village Exit", force_put=True, force_pos=0)
        elif(choice == "Fight them. (F)"):
            events_by_name["Fight"].instigate(npcs_by_type["Villager"])
        elif(choice == "Walk past."):
            player.walk()

    def check_special_requirements(self):
        return npcs_by_type["Villager"].amount >= 1


class Grassfields(Event):
    def initialize_event(self):
        self.name = "Grassfields"
        self.locations = ["Overworld"]

    def introduce_event(self):
        print("*You stumble upon a field of grass village nearby.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        if(player.food >= 1):
            self.add_choice(choice_num, "Work the field. F+")

    def on_choice(self, choice, choice_num):
        if(choice == "Work the field. F+"):
            player.addFood(1)
            if(prob(75)):
                force_event("Village Entrance")
            else:
                force_event("Bandits")  # Got you while you were working.
        elif(choice == "Walk past."):
            player.walk()


class Desert(Event):
    def initialize_event(self):
        self.name = "Desert"
        self.locations = ["Overworld"]
        self.default_choices = {"1": "Open inventory.", "2": "Open log."}

    def introduce_event(self):
        print("*You stumble upon a desert.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        self.add_choice(choice_num, "Walk through it. H-")
        choice_num += 1
        if(previous_event and previous_event.check_requirements()):
            self.add_choice(choice_num, "Turn back.")
            choice_num += 1
        if("Jar of Blood" in player.inventory.keys()):
            jar = player.get_item("Jar of Blood")
            if(jar.stored_blood >= 1):
                self.add_choice(choice_num, "Sip blood.")

    def on_choice(self, choice, choice_num):
        if(choice == "Walk through it. H-"):
            player.addHealth(-1)
        elif(choice == "Turn back."):
            player.walk()
            force_event(previous_event.name, force_put=True, force_pos=0)
        elif(choice == "Sip blood."):
            jar = player.get_item("Jar of Blood")
            jar.stored_blood -= 1


class Bandits(Event):
    def initialize_event(self):
        self.name = "Bandits"
        self.locations = ["Overworld"]
        self.default_choices = {"1": "Open inventory.", "2": "Open log."}
        self.reputation = 0
        self.bandits_amount = random.randint(1, 4)

    def introduce_event(self):
        self.bandits_amount = random.randint(2, 4)
        print("*You encounter a gang of " + str(self.bandits_amount) + " bandits.*")

    def reset(self):
        self.reputation = 0

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        if(player.money >= 1):
            self.add_choice(choice_num, "Pay them off. M-")
            choice_num += 1
        if(self.reputation < 10):
            if(previous_event and previous_event.check_requirements() and player.food >= 1):
                self.add_choice(choice_num, "Run back. H- 50% F-")
                choice_num += 1
        else:
            self.add_choice(choice_num, "Walk past.")
            choice_num += 1

        if("Cloak" in player.inventory.keys()):
            if(npcs_by_type["Bandit"].money >= 1):
                self.add_choice(choice_num, "Blend in. M+")
            else:
                self.add_choice(choice_num, "Blend in.")
            choice_num += 1

        self.add_choice(choice_num, "Fight them.")

    def on_choice(self, choice, choice_num):
        if(choice == "Pay them off. M-"):
            self.reputation += 1
            npcs_by_type["Bandit"].addMoney(1)
            player.addMoney(-1)
        elif(choice == "Run back. H- 50% F-"):
            player.addFood(-1)
            if(prob(50)):
                player.addHealth(-1)
            player.walk()
            force_event(previous_event.name, force_put=True, force_pos=0)
        elif(choice == "Blend in."):
            self.reputation += 1
        elif(choice == "Blend in. M+"):
            player.addMoney(1)
            npcs_by_type["Bandit"].addMoney(-1)
            self.reputation += 1
        elif(choice == "Fight them."):
            for i in range(0, self.bandits_amount):
                force_event("Bandit", force_put=True, check_req=True, force_pos=0)
        elif(choice == "Walk past."):
            player.walk()
            self.reputation -= 1

    def check_special_requirements(self):
        return npcs_by_type["Bandit"].amount >= 4  # Since max in a gang is four.

    def return_save_data(self, event_info):
        event_info['name'] = self.name
        event_info['reputation'] = self.reputation

    def on_load_save_data(self, event_info):
        event.reputation = event_info['reputation']


class Lone_Bandit(Event):
    def initialize_event(self):
        self.name = "Bandit"
        self.locations = ["Overworld", "Dungeon"]
        self.default_choices = {"1": "Open inventory.", "2": "Open log."}
        self.reputation = 0
        self.bandits_amount = random.randint(1, 4)

    def reset(self):
        self.reputation = 0

    def introduce_event(self):
        self.bandits_amount = random.randint(2, 4)
        print("*You encounter a bandit.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        if(player.money >= 1):
            self.add_choice(choice_num, "Pay them off. M-")
            choice_num += 1

        if(previous_event and previous_event.check_requirements() and player.food >= 1):
            self.add_choice(choice_num, "Run back. H- 50% F-")
            choice_num += 1

        self.add_choice(choice_num, "Fight them. (F)")

    def on_choice(self, choice, choice_num):
        if(choice == "Pay them off. M-"):
            self.reputation += 1
            npcs_by_type["Bandit"].addMoney(1)
            player.addMoney(-1)
        elif(choice == "Run back. H- 50% F-"):
            player.addFood(-1)
            if(prob(50)):
                player.addHealth(-1)
            player.walk()
            force_event(previous_event.name, force_put=True, force_pos=0)
        elif(choice == "Fight them. (F)"):
            events_by_name["Fight"].instigate(npcs_by_type["Bandit"])

    def check_special_requirements(self):
        return npcs_by_type["Bandit"].amount >= 1

    def return_save_data(self, event_info):
        event_info['name'] = self.name
        event_info['reputation'] = self.reputation

    def on_load_save_data(self, event_info):
        event.reputation = event_info['reputation']


class It_Summon(Event):
    def initialize_event(self):
        self.name = "It Summon"
        self.default_choices = {"1": "Yes."}
        self.walked_past_times = 0

    def reset(self):
        self.walked_past_times = 0

    def introduce_event(self):
        print("*You encounter a beast.*")
        if(self.walked_past_times < 3):
            print("??? says, \"You have summoned me.\"")
        elif(self.walked_past_times < 6):
            print("??? says, \"You can not go away.\"")
        elif(self.walked_past_times == 6):
            print("??? says, \"Doom.\"")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1

        self.add_choice(choice_num, "Fight them. (F)")

    def on_choice(self, choice, choice_num):
        if(choice == "Walk past."):
            if(self.walked_past_times < 6):
                force_event("It Summon")
            else:
                force_event("Doom", force_put=True, force_pos=0)
            self.walked_past_times += 1
            player.walk()
        elif(choice == "Yes."):
            player.title = " the Summoner"
            force_event("Doom", force_put=True, force_pos=0)
        elif(choice == "Fight them. (F)"):
            events_by_name["Fight"].instigate(npcs_by_type["It"])

    def check_special_requirements(self):
        return npcs_by_type["It"].amount >= 1 and npcs_by_type["It"].is_summoned

    def return_save_data(self, event_info):
        event_info['name'] = self.name
        event_info['walked_past_times'] = self.walked_past_times

    def on_load_save_data(self, event_info):
        event.reputation = event_info['walked_past_times']


class Doom(Event):
    def initialize_event(self):
        self.name = "Doom"
        self.default_choices = {}

    def introduce_event(self):
        print("*Rocks fall everybody dies.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        self.add_choice(choice_num, "...")

    def on_choice(self, choice, choice_num):
        reset()

    def check_special_requirements(self):
        return False


class Keykeeper_Room(Event):
    def initialize_event(self):
        self.name = "Keykeeper Room"

    def introduce_event(self):
        print("*You encounter a person willing to trade.*")
        print(npcs_by_type["Keykeeper"].name + " says, \"Keys... Keys, I sell keys! Yeah... Keys.\"")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1

        self.choices_items = {}

        if(player.money >= 2 and npcs_by_type["Keykeeper"].keys >= 1):
            self.add_choice(choice_num, "Buy a key. M-- K+")
            choice_num += 1

        for item in player.get_all_items():
            if(item.getMoneyCost() > int(npcs_by_type["Keykeeper"].keys / 2)):
                break
            if(item.getMoneyCost() == 0):
                continue
            self.add_choice(choice_num, "Sell " + item.getDisplayName())
            self.choices_items[str(choice_num)] = item
            choice_num += 1

        if(player.location == "Village"):
            self.add_choice(choice_num, "Return to village exit.")
            choice_num += 1

        self.add_choice(choice_num, "Fight them. (F)")

    def on_choice(self, choice, choice_num):
        if(choice == "Walk past."):
            player.walk()
        elif(choice == "Buy a key. M-- K+"):
            player.addMoney(-2)
            player.addKeys(1)
            npcs_by_type["Keykeeper"].addKeys(-1)
            npcs_by_type["Buyer"].addMoney(2)
        elif(choice == "Fight them. (F)"):
            events_by_name["Fight"].instigate(npcs_by_type["Keykeeper"])
        elif(choice == "Return to village exit."):
            player.walk()
            force_event("Village Exit", force_put=True, force_pos=0)
        else:
            sell_pos = choice.find("Sell ")
            if(sell_pos != -1):
                item = self.choices_items[choice_num]
                player.remove_item(item)
                player.addKeys(int(item.getMoneyCost() / 2))
                if("Treasure" in item.item_pools):
                    if(prob(50)):
                        npcs_by_type["Treasury Vendor"].loot("Treasure")
                    else:
                        npcs_by_type["Treasury Vendor"].receive_item(item.name)

    def check_special_requirements(self):
        return npcs_by_type["Keykeeper"].keys >= 1 and npcs_by_type["Keykeeper"].amount >= 1


class Buyer_Room(Event):
    def initialize_event(self):
        self.name = "Buyer Room"

    def introduce_event(self):
        print("*You encounter a person willing to trade.*")
        if(len(player.inventory.keys()) > 0):
            print(npcs_by_type["Buyer"].name + " says, \"Oh I like your " + random.choice(player.get_all_item_names()) + "!\"")
        else:
            print(npcs_by_type["Buyer"].name + " says, \"Oh what a coincidence we met, I hope we do not, you are broke.\"")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1

        self.choices_items = {}

        if(player.keys >= 1 and npcs_by_type["Buyer"].money >= 2):
            self.add_choice(choice_num, "Sell a key. M++ K-")
            choice_num += 1

        for item in player.get_all_items():
            if(item.getMoneyCost() > npcs_by_type["Buyer"].money):
                break
            if(item.getMoneyCost() == 0):
                continue
            self.add_choice(choice_num, "Sell " + item.getDisplayName())
            self.choices_items[str(choice_num)] = item
            choice_num += 1

        if(player.location == "Village"):
            self.add_choice(choice_num, "Return to village exit.")
            choice_num += 1

        self.add_choice(choice_num, "Fight them. (F)")

    def on_choice(self, choice, choice_num):
        if(choice == "Walk past."):
            player.walk()
        elif(choice == "Sell a key. M++ K-"):
            player.addMoney(2)
            player.addKeys(-1)
            npcs_by_type["Keykeeper"].addKeys(1)
            npcs_by_type["Buyer"].addMoney(-2)
            npcs_by_type["Villager"].addMoney(2)
        elif(choice == "Fight them. (F)"):
            events_by_name["Fight"].instigate(npcs_by_type["Buyer"])
        elif(choice == "Return to village exit."):
            player.walk()
            force_event("Village Exit", force_put=True, force_pos=0)
        else:
            sell_pos = choice.find("Sell ")
            if(sell_pos != -1):
                item = self.choices_items[choice_num]
                player.remove_item(item)
                player.addMoney(item.getMoneyCost())
                npcs_by_type["Villager"].addMoney(item.getMoneyCost())
                if("Treasure" in item.item_pools):
                    if(prob(50)):
                        npcs_by_type["Treasury Vendor"].loot("Treasure")
                    else:
                        npcs_by_type["Treasury Vendor"].receive_item(item.name)

    def check_special_requirements(self):
        return npcs_by_type["Buyer"].money >= 1 and npcs_by_type["Buyer"].amount >= 1 and len(player.inventory.keys()) > 0


class Treasury_Vendor_Room(Event):
    def initialize_event(self):
        self.name = "Treasury Vendor Room"

    def introduce_event(self):
        print("*You encounter a person willing to trade.*")
        if(len(npcs_by_type["Treasury Vendor"].inventory.keys())):
            print(npcs_by_type["Treasury Vendor"].name + " says, \"Treasures for sale!\"")
        else:
            print(npcs_by_type["Treasury Vendor"].name + " says, \"No treasures for sale.\"")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1

        self.choices_items = {}

        for item in npcs_by_type["Treasury Vendor"].get_all_items():
            if(item.getMoneyCost() > player.money):
                break
            if(item.getMoneyCost() == 0):  # Don't sell what's free.
                continue
            self.add_choice(choice_num, "Buy " + item.getDisplayName())
            self.choices_items[str(choice_num)] = item
            choice_num += 1

        if(player.location == "Village"):
            self.add_choice(choice_num, "Return to village exit.")
            choice_num += 1

        self.add_choice(choice_num, "Fight them. (F)")

    def on_choice(self, choice, choice_num):
        if(choice == "Walk past."):
            player.walk()
        elif(choice == "Fight them. (F)"):
            events_by_name["Fight"].instigate(npcs_by_type["Treasury Vendor"])
        elif(choice == "Return to village exit."):
            player.walk()
            force_event("Village Exit", force_put=True, force_pos=0)
        else:
            buy_pos = choice.find("Buy ")
            if(buy_pos != -1):
                item = self.choices_items[choice_num]
                npcs_by_type["Treasury Vendor"].remove_item(item)
                player.addMoney(-item.getMoneyCost())
                player.receive_item(item=item)
                npcs_by_type["Treasury Vendor"].addMoney(item.getMoneyCost())
                npcs_by_type["Buyer"].addMoney(item.getMoneyCost())

    def check_special_requirements(self):
        return len(npcs_by_type["Treasury Vendor"].inventory) >= 1 and npcs_by_type["Treasury Vendor"].amount >= 1


class Locked_Chest(Event):
    def initialize_event(self):
        self.name = "Locked Chest"
        self.locations = ["Overworld", "Dungeon"]

    def introduce_event(self):
        print("*You stumble upon a locked golden chest.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        if(player.keys >= 1):
            self.add_choice(choice_num, "Open the chest. K-")
            choice_num += 1
        if("Master Key" in player.inventory.keys()):
            self.add_choice(choice_num, "Use Master Key.")

    def on_choice(self, choice, choice_num):
        if(choice == "Walk past."):
            player.walk()
            npcs_by_type["Keykeeper"].addKeys(1)  # Saves between runs which is cool I guess.
        elif(choice == "Open the chest. K-"):
            player.addKeys(-1)
            player.loot("Treasure")
        elif(choice == "Use Master Key."):
            player.loot("Treasure")


class Dungeon_Entrance(Event):
    def initialize_event(self):
        self.name = "Dungeon Entrance"
        self.locations = ["Overworld"]

    def introduce_event(self):
        print("*You stumble upon a giant dungeon entrance.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        self.add_choice(choice_num, "Enter the dungeon.")

    def on_choice(self, choice, choice_num):
        if(choice == "Walk past."):
            player.walk()
        elif(choice == "Enter the dungeon."):
            player.walk()
            player.location = "Dungeon"


class Dungeon_Empty_Room(Event):
    def initialize_event(self):
        self.name = "Dungeon Empty Room"
        self.locations = ["Dungeon"]

    def introduce_event(self):
        print("*You enter an empty dungeon room.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        self.add_choice(choice_num, "Turn back.")

    def on_choice(self, choice, choice_num):
        if(choice == "Walk past."):
            player.walk()
        elif(choice == "Turn back."):
            player.walk()
            force_event(previous_event.name, force_put=True, force_pos=0)


class Dungeon_Exit(Event):
    def initialize_event(self):
        self.name = "Dungeon Exit"
        self.locations = ["Dungeon"]

    def introduce_event(self):
        print("*You stumble upon a dungeon exit.*")

    def generate_choices(self):
        self.choices = dict(self.default_choices)
        choice_num = len(self.default_choices) + 1
        self.add_choice(choice_num, "Exit the dungeon.")

    def on_choice(self, choice, choice_num):
        if(choice == "Walk past."):
            player.walk()
        elif(choice == "Exit the dungeon."):
            player.walk()
            player.location = "Overworld"
version = 1

def save_to_savefile(save_name):
    global version
    global player
    global forced_events
    global event
    global previous_event
    global previous_sin
    global tick
    global log

    savefile = {}
    savefile['version'] = version
    savefile['player_name'] = player.name
    savefile['player_title'] = player.title
    savefile['player_deaths'] = player.deaths

    savefile['npcs'] = []
    for npc in npcs_by_type.values():
        npc_info = {}
        npc.return_save_data(npc_info)

        savefile['npcs'].append(npc_info)

    savefile['events'] = []
    for event in events_by_name.values():
        event_info = {}
        event.return_save_data(event_info)

        savefile['events'].append(event_info)

    savefile['items'] = []
    for item in items_by_name.values():
        item_info = {}
        item.return_save_data(item_info)

        savefile['items'].append(item_info)

    with open('../savefiles/' + save_name + '.txt', 'w') as outfile:
        json.dump(savefile, outfile, sort_keys=True, indent=4, separators=(',', ': '))

def load_from_savefile(save_name):
    global version
    global player
    global forced_events
    global event
    global previous_event
    global previous_sin
    global tick
    global log

    exists = os.path.isfile('../savefiles/' + save_name + '.txt')
    if exists:
        with open('../savefiles/' + save_name + '.txt') as infile:  
            savefile = json.load(infile)

            if(savefile['version'] < version):
                update_to_version(save_name)

            player.name = savefile['player_name']
            player.title = savefile['player_title']
            player.deaths = savefile['player_deaths']

            for npc_info in savefile['npcs']:
                Being.load_save_data(npc_info)

            for event_info in savefile['events']:
                Event.load_save_data(event_info)

            for item_info in savefile['items']:
                Item.load_save_data(item_info)

        return True
    else:
        return False

def update_to_version(save_name):
    return

def reset():
    global player
    global forced_events
    global event
    global previous_event
    global previous_sin
    global tick
    global log

    if(player.name != "stranger"):
        save_to_savefile(player.name)

    if(player.error >= 3):
        player.title = " the 01100101 01110010 01110010"

    if(player.deaths > 0):
        player.display_name = player.name + " " + roman.toRoman(player.deaths) + player.title
    else:
        player.display_name = player.name

    previous_sin = player.sin

    player.health = 5
    player.deaths += 1
    player.kills = 0
    player.food = 5
    player.money = 2
    player.keys = 1
    player.sin = 0
    player.inventory = {}
    player.walked_past = 0
    player.error = 0
    player.location = "Overworld"
    player.effects = {}
    player.dodge_chance = 0

    player.blood_vessel = Reagents(1000, "blood")
    player.stomach_vessel = Reagents(1000, "stomach")
    player.skin_vessel = Reagents(1000, "skin")

    tick = 0
    log = []

    forced_events = list()
    event = None
    previous_event = None

    force_event("Introduction", force_put=True, force_pos=0)
    clear_output()

def full_reset():
    global player
    global forced_events
    global event
    global previous_event
    global previous_sin
    global tick
    global log

    for npc in npcs_by_type.values():
        npc.full_reset()

    for item in items_by_name.values():
        item.full_reset()

    for event in events_by_name.values():
        event.full_reset()

    reset()
class Being_Effects:
    def __init__(self):
        self.ticks = 0
        self.severity = 0
        self.initialize_effect()
        effects_name_to_type[self.name] = type(self)

    def initialize_effect(self):
        self.name = "Effect"

    def set_effect(being, name, severity, ticks):  # Do not override this method.
        effect = None
        if(name in being.effects.keys()):
            effect = being.effects[name]
            effect.on_stack(severity, ticks, being)
        else:
            effect = name()
            effect.on_add(severity, ticks, being)
            being.effects[name] = effect
        return effect

    def remove_effect(being, name):  # Do not override this method.
        effect = being.effects.pop(name)
        if(effect):
            effect.on_remove(being)

    def on_life(self, being):  # Do not override this method.
        self.on_being_life(being)
        self.ticks -= 1
        if(self.ticks <= 0 or self.severity <= 0):
            Being_Effects.remove_effect(being, type(self))

    def on_walk(self, being):  # Do not override this method.
        self.on_being_walk(being)

    def on_add(self, severity, ticks, being):
        self.severity = severity
        self.ticks += ticks
        if(being == player):
            add_to_log("You had conjured " + self.name + "(" + str(self.severity) + "): " + str(self.ticks) + ".")
        elif(event.name == "Fight" and event.npc == being):
            add_to_log(being.display_name + " had conjured " + self.name + "(" + str(self.severity) + "): " + str(self.ticks) + ".")
        self.on_being_add(being)

    def on_stack(self, severity, ticks, being):
        self.severity = max(self.severity, severity)
        self.ticks += ticks
        if(being == player):
            add_to_log("You had stacked " + self.name + "(" + str(self.severity) + "): " + str(self.ticks) + ".")
        elif(event.name == "Fight" and event.npc == being):
            add_to_log(being.display_name + " had stacked " + self.name + "(" + str(self.severity) + "): " + str(self.ticks) + ".")
        self.on_being_stack(being)

    def on_remove(self, being):
        self.severity = 0
        self.ticks = 0
        if(being == player):
            add_to_log("You had " + self.name + "(" + str(self.severity) + "): " + str(self.ticks) + " wear off.")
        elif(event.name == "Fight" and event.npc == being):
            add_to_log(being.display_name + " had " + self.name + "(" + str(self.severity) + "): " + str(self.ticks) + " wear off.")
        self.on_being_remove(being)

    # Methods bellow can be overriden freely.
    def on_being_add(self, being):
        return

    def on_being_stack(self, being):
        return

    def on_being_remove(self, being):
        return

    def on_being_life(self, being):
        return

    def on_being_walk(self, being):
        return

    def on_add_sin(self, being, count):
        return

    def return_save_data(self, effect_info):
        effect_info['name'] = self.name
        effect_info['ticks'] = self.ticks
        effect_info['severity'] = self.severity

    def load_save_data(effect_info, being):
        self.on_load_save_data(effect_info, being)

    def on_load_save_data(self, effect_info, being):
        Being_Effects.set_effect(being, effects_name_to_type[effect_info['name']], effect_info['severity'], effect_info['ticks'])


class No_Heal(Being_Effects):
    def initialize_effect(self):
        # self.name = "I can't decide on a name that would fit this effect please send suggestions over to my e-mail adress which I will not give you for privacy reasons."
        self.name = "Incurable"  # ^^^ Bam. Problem solved.


class Bleeding(Being_Effects):
    def initialize_effect(self):
        self.name = "Bleeding"

    def on_being_life(self, being):
        being.addHealth(-self.severity)


class Healing(Being_Effects):
    def initialize_effect(self):
        self.name = "Healing"

    def on_being_life(self, being):
        being.addHealth(self.severity)


class Immortality(Being_Effects):
    def initialize_effect(self):
        self.name = "Immortality"
        self.old_min_health = 0

    def on_being_add(self, being):
        self.old_min_health = being.min_health
        being.min_health = self.severity

    def on_being_stack(self, being):
        being.min_health = self.severity

    def on_being_remove(self, being):
        being.min_health = self.old_min_health

    def return_save_data(self, effect_info):
        super().return_save_data(effect_info)
        effect_info['old_min_health'] = self.old_min_health

    def on_load_save_data(self, effect_info, being):
        effect = Being_Effects.set_effect(being, effects_name_to_type[effect_info['name']], effect_info['severity'], effect_info['ticks'])
        effect.old_min_health = effect_info['old_min_health']


class Saturation(Being_Effects):
    def initialize_effect(self):
        self.name = "Saturation"

    def on_being_life(self, being):
        being.addFood(self.severity)
class Reagents:
    def __init__(self, max_amount=0, type_=""):
        self.max_amount = max_amount
        self.reagents = {}
        self.type = type_

    def transfer_any(self, target, amount, being=None, spill_target=None):
        to_transfer = min(min(amount, self.get_amount()), target.max_amount - target.get_amount())
        if(to_transfer != 0):
            transfered_amount = 0
            while(transfered_amount < to_transfer):
                if(self.get_amount() <= 0):
                    return
                reagent_name = random.choice(list(self.reagents.keys()))
                self.reduct_reagent(reagent_name, 1, being, spill_target)
                target.add_reagent(reagent_name, 1, being, spill_target)
                transfered_amount += 1

    def get_amount(self):
        output = 0
        for reagent in self.reagents.values():
            output += reagent.amount
        return output

    def get_reagent(self, reagent_name):
        return self.reagents[reagent_name]

    def add_reagent(self, reagent_name, amount, being=None, spill_target=None):
        can_add = self.max_amount - self.get_amount()
        to_add = min(can_add, amount)

        reagent = None
        if(to_add <= 0):
            reagent = reagent_name(self)
            reagent.on_add(amount, spill_target)
            reagent.on_spill(amount, spill_target, spill_target)
            return reagent
        elif(to_add != amount):
            reagent = reagent_name(self)
            reagent.on_add(amount - to_add, spill_target)
            reagent.on_spill(amount - to_add, spill_target, spill_target)

        if(reagent_name in self.reagents.keys()):
            reagent = self.get_reagent(reagent_name)
            self.reagents[reagent_name].on_stack(to_add, spill_target)
        else:
            reagent = reagent_name(self)
            reagent.on_add(to_add, spill_target)
            self.reagents[reagent_name] = reagent
        return reagent

    def reduct_reagent(self, reagent_name, amount, being=None, spill_target=None):
        self.reagents[reagent_name].on_remove(amount, spill_target)

    def remove_reagent(self, reagent_name):
        reagent = self.reagents.pop(reagent_name)
        if(reagent):
            reagent.reagents = None

    def get_cost(self):
        output = 0
        for reagent in self.reagents.values():
            output += reagent.cost * reagent.amount
        return output

    def get_color(self):
        r_ = 0
        g_ = 0
        b_ = 0
        total_weight = 0
        weights = []
        for reagent in self.reagents.values():
            reagent_weight = reagent.amount * reagent.thickness + 1  # So we'll never get a 0.
            total_weight += reagent_weight
            weights.append(reagent_weight)

        listsum = 0
        i = 0
        for reagent in self.reagents.values():
            listsum += weights[i]
            i += 1
        i = 0
        for reagent in self.reagents.values():
            weights[i] = weights[i] / listsum
            i += 1
        i = 0
        for reagent in self.reagents.values():
            r_ += weights[i] * reagent.red
            g_ += weights[i] * reagent.green
            b_ += weights[i] * reagent.blue
            i += 1

        r_ = Clamp(int(r_), 0, 255)
        g_ = Clamp(int(g_), 0, 255)
        b_ = Clamp(int(b_),0, 255)

        return get_colour_name((r_, g_, b_))

    def get_smell(self):
        swe = 0
        bit = 0
        sme = 0
        total_weight = 0
        weights = []
        for reagent in self.reagents.values():
            reagent_weight = reagent.amount * reagent.smell_potency
            total_weight += reagent_weight
            weights.append(reagent_weight)

        listsum = 0
        i = 0
        for reagent in self.reagents.values():
            listsum += weights[i]
            i += 1
        i = 0
        for reagent in self.reagents.values():
            weights[i] = weights[i] / listsum
            i += 1
        i = 0
        for reagent in self.reagents.values():
            swe += weights[i] * reagent.sweetness
            bit += weights[i] * reagent.bitterness
            sme += weights[i] * reagent.smellyness
            i += 1

        swe = Clamp(swe, 0, 100)
        bit = Clamp(bit, 0, 100)
        sme = Clamp(sme, 0, 100)

        if(sme > swe and sme > bit):
            return "smelly"
        elif(bit > swe and bit > sme):
            return "bitter"
        elif(swe > sme and swe > bit):
            return "sweet"
        return "weird"

    def on_life(self, being):
        for reagent in list(self.reagents.values()):
            reagent.on_life(being, self.type)

    def on_walk(self, being):
        for reagent in list(self.reagents.values()):
            reagent.on_walk(being, self.type)

    def return_save_data(self, reagents_info):
        reagents_info['max_amount'] = self.max_amount
        reagents_info['type'] = self.type

        reagents_info['reagents'] = []
        for reagent in self.reagents.values():
            reagent_info = {}
            reagent.return_save_data(reagent_info)
            reagents_info['reagents'].append(reagent_info)

    def load_save_data(reagents_info, being=None, spill_target=None):
        reagents = Reagents(reagents_info['max_amount'], reagents_info['type'])

        for reagent_info in reagents_info['reagents']:
            reagent = reagents.add_reagent(reagents_name_to_type[reagent_info['name']], reagent_info['amount'], being, spill_target)
            reagent.on_load_save_data(reagent_info, reagents, being, spill_target)

        return reagents


class Reagent:
    def __init__(self, reagents):
        self.name = ""
        self.formula = ""
        self.amount = 0
        self.reagents = reagents

        self.cost = 0

        # Coloring.
        self.red = 0
        self.green = 0
        self.blue = 0
        self.thickness = 0

        # Taste and smell.
        self.sweetness = 0
        self.bitterness = 0
        self.smellyness = 0
        self.smell_potency = 0
        self.initialize_reagent()
        reagents_name_to_type[self.name] = type(self)

    def on_life(self, being, type_=""):  # Do not override this method.
        self.on_being_life(being, type_)
        self.reagents.reduct_reagent(type(self), 1)

    def on_walk(self, being, type_=""):  # Do not override this method.
        self.on_being_walk(being, type_)

    def on_spill(self, amount, being=None, spill_target=None, type_=""):
        self.on_being_spill(amount, being, spill_target)
        if(spill_target):
            spill_target.skin_vessel.add_reagent(type(self), amount)
        self.amount -= amount

    def on_stack(self, amount, being=None):
        if(being):
            self.on_being_stack(being, amount)
        self.amount += amount

    def on_add(self, amount, being=None):
        if(being):
            self.on_being_add(being, amount)
        self.amount += amount

    def on_remove(self, amount, being=None):
        self.amount -= amount
        if(being):
            self.on_being_remove(being, amount)
        if(self.amount <= 0):
            self.reagents.remove_reagent(type(self))

    # Override the methods below as much as you wish.
    def on_being_life(self, being, type_=""):
        return

    def on_being_walk(self, being, type_=""):
        return

    def on_being_stack(self, being, amount):
        return

    def on_being_add(self, being, amount):
        return

    def on_being_remove(self, being, amount):
        return

    def on_being_spill(self, amount, being=None, spill_target=None):
        return

    def return_save_data(self, reagent_info):
        reagent_info['name'] = self.name
        reagent_info['formula'] = self.formula
        reagent_info['amount'] = self.amount
        reagent_info['cost'] = self.cost
        reagent_info['red'] = self.red
        reagent_info['green'] = self.green
        reagent_info['blue'] = self.blue
        reagent_info['thickness'] = self.thickness
        reagent_info['sweetness'] = self.sweetness
        reagent_info['bitterness'] = self.bitterness
        reagent_info['smellyness'] = self.smellyness
        reagent_info['smell_potency'] = self.smell_potency

    def on_load_save_data(self, reagent_info, reagents, being = None, spill_target = None):
        self.formula = reagent_info['formula']
        self.amount = reagent_info['amount']
        self.cost = reagent_info['cost']
        self.red = reagent_info['red']
        self.green = reagent_info['green']
        self.blue = reagent_info['blue']
        self.thickness = reagent_info['thickness']
        self.sweetness = reagent_info['sweetness']
        self.bitterness = reagent_info['bitterness']
        self.smellyness = reagent_info['smellyness']
        self.smell_potency = reagent_info['smell_potency']


class Wine(Reagent):
    def initialize_reagent(self):
        self.name = "Wine"

        self.red = 200
        self.blue = 30
        self.thickness = 1

        self.cost = 1

        self.sweetness = 80
        self.smell_potency = 2

    def on_being_life(self, being, type_=""):
        if(type_ == "stomach"):
            Being_Effects.set_effect(being, Saturation, 1, 2)
        elif(type == "skin"):
            if("Bleeding" in being.effects.keys()):
                bleeding = being.effects["Bleeding"]
                bleeding.severity -= 1


class Health_Potion(Reagent):
    def initialize_reagent(self):
        self.name = "Health Potion"

        self.red = 255
        self.green = 10
        self.blue = 10
        self.thickness = 1

        self.cost = 2

        self.sweetness = 100
        self.smell_potency = 1

    def on_being_add(self, being, amount):
        being.addHealth(amount)

    def on_being_stack(self, being, amount):
        being.addHealth(amount)


class Regen_Potion(Reagent):
    def initialize_reagent(self):
        self.name = "Regeneration Potion"

        self.red = 255
        self.green = 10
        self.blue = 150
        self.thickness = 1

        self.cost = 2

        self.sweetness = 75
        self.bitterness = 25
        self.smell_potency = 1

    def on_being_life(self, being, type_=""):
        if(type_ == "stomach" or type_ == "skin"):
            Being_Effects.set_effect(being, Healing, 1, 2)


class Immortality_Potion(Reagent):
    def initialize_reagent(self):
        self.name = "Immortality Potion"

        self.red = 200
        self.green = 200
        self.blue = 200
        self.thickness = 1

        self.cost = 4

        self.bitterness = 50
        self.smell_potency = 1

    def on_being_life(self, being, type_=""):
        if(type_ == "stomach" or type_ == "skin"):
            Being_Effects.set_effect(being, Immortality, 1, 2)


class Harm_Potion(Reagent):
    def initialize_reagent(self):
        self.name = "Harm Potion"

        self.red = 10
        self.green = 10
        self.blue = 50
        self.thickness = 1

        self.cost = 2

        self.smellyness = 100
        self.smell_potency = 1

    def on_being_add(self, being, amount):
        being.addHealth(-amount)

    def on_being_stack(self, being, amount):
        being.addHealth(-amount)


class Bleeding_Potion(Reagent):
    def initialize_reagent(self):
        self.name = "Bleeding Potion"

        self.red = 50
        self.green = 10
        self.blue = 10
        self.thickness = 1

        self.cost = 2

        self.bitterness = 25
        self.smellyness = 75
        self.smell_potency = 1

    def on_being_life(self, being, type_=""):
        if(type_ == "stomach" or type_ == "skin"):
            Being_Effects.set_effect(being, Bleeding, 1, 2)


class No_Heal_Potion(Reagent):
    def initialize_reagent(self):
        self.name = "Incurability Potion"

        self.red = 10
        self.green = 255
        self.blue = 100
        self.cost = 4

        self.bitterness = 75
        self.smellyness = 75
        self.smell_potency = 1

    def on_being_life(self, being, type_=""):
        if(type_ == "stomach" or type_ == "skin"):
            Being_Effects.set_effect(being, No_Heal, 1, 2)


class Reagent_Reaction:
    reactants = {}
    catalysts = {}
    results = {}
class Bodypart:
    def __init__(self, owner):
        self.child_organs = []
        self.child_bodyparts = []
        self.initialize_bodypart(owner)
        self.parent_bodypart = owner.get_bodypart(parent_name)
        self.on_add(owner)

    def initialize_bodypart(self, owner):
        self.min_health = 0
        self.max_health = 10
        self.health = 10

        self.name = "Lower Torso"
        self.parent_bodypart_name = "Upper Torso"

    def on_add(self, owner):  # Do not override this method.
        owner.bodyparts.append(self)
        owner.bodyparts_by_name[self.name] = self
        self.on_owner_add(owner)
        self.owner = owner

    def on_remove(self):  # Do not override this method.
        self.owner.bodyparts.remove(self)
        self.owner.bodyparts_by_name.pop(self)

        for organ in self.child_organs:
            self.owner.remove_organ(organ)

        for bodypart in self.child_bodyparts:
            self.owner.remove_bodypart(bodypart)

        self.owner = None

    # Methods bellow can be overriden freely.
class Being:
    def __init__(self):
        self.location = "Overworld"
        self.display_name = ""
        self.name = "Being"
        self.type = ""
        self.health = 0
        self.max_health = 5
        self.min_health = 0
        self.food = 0
        self.max_food = 10
        self.min_food = 0
        self.money = 0
        self.max_money = 99
        self.min_money = 0
        self.keys = 0
        self.max_keys = 99
        self.min_keys = 0
        self.sin = 0
        self.max_sin = 666
        self.min_sin = -333
        self.inventory = {}
        self.effects = {}

        self.hunger_rate = 10
        self.metabolism_speed = 1
        self.metabolism_tick = 0

        self.life_ticks = 0
        self.NPC = True

        self.blood_vessel = Reagents(1000, "blood")
        self.stomach_vessel = Reagents(1000, "stomach")
        self.skin_vessel = Reagents(1000, "skin")

        # Combat related blah-blah.
        self.dodge_chance = 0
        self.hit_chance = 100
        self.damage = 1

        self.bodyparts = []
        self.bodyparts_by_name = {}
        self.organs = []
        self.organs_by_name = {}

        self.set_organs()

    def set_organs(self):
        for bodypart in self.get_bodypart_types():
            bodypart(self)
        for organ in self.get_organ_types():
            organ(self)

    def get_bodypart_types(self):
        return []

    def get_organ_types(self):
        return []

    def get_bodypart(self, bodypart_name):
        return self.bodyparts_by_name[bodypart_name]

    def get_organ(self, organ_name):
        return self.organs_by_name[organ_name]

    def remove_bodypart(self, bodypart):
        bodypart.on_remove()

    def remove_organ(self, organ):
        organ.on_remove()

    def show_stats(self):
        print("-------------------------------------")
        print("Health: " + str(self.health) + "/" + str(self.max_health) + "\tFood: " + str(self.food) + "/" + str(self.max_food) + "\tMoney: " + str(self.money) + "/" + str(self.max_money) + "\tKeys: " + str(self.keys) + "/" + str(self.max_keys) + "\tSin: " + str(self.sin) + "/" + str(self.max_sin))
        effects_string = ""
        effect_num = 0
        for effect in self.effects.values():
            if(effect_num % 2 == 0):
                effects_string += effect.name + "(" + str(effect.severity) + "): " + str(effect.ticks) + "\t\t"
            else:
                effects_string += effect.name + "(" + str(effect.severity) + "): " + str(effect.ticks) + "\t"
            effect_num += 1
        if(effects_string != ""):
            print(effects_string)
        print("Inventory: " + str(self.get_all_item_names()))
        print("-------------------------------------")

    def life(self):  # Do not override this method.
        for effect in list(self.effects.values()):
            effect.on_life(self)
        for item in list(self.get_all_items()):
            item.on_life(self)

        self.blood_vessel.on_life(self)
        self.stomach_vessel.on_life(self)
        self.skin_vessel.on_life(self)

        if(self.metabolism_tick >= self.hunger_rate):
            self.metabolism_tick = 0
            if(self.food <= 0):
                if(self == player):
                    add_to_log("You had lost 1 Health Point due to starvation.")
                self.addHealth(-1)
            self.addFood(-1)

        self.on_life()
        self.life_ticks += 1
        self.metabolism_tick += self.getMetabolismSpeed()

    def walk(self):  # Do not override this method.
        for effect in list(self.effects.values()):
            effect.on_walk(self)
        for item in list(self.get_all_items()):
            item.on_walk(self)

        self.blood_vessel.on_walk(self)
        self.stomach_vessel.on_walk(self)
        self.skin_vessel.on_walk(self)

        self.on_walk()

    def loot(self, pool):
        if(len(pools[pool].values())):
            if(not self.NPC):
                if("Deck of Fateful Cards" in self.inventory.keys()):
                    attempts = len(self.inventory["Deck of Fateful Cards"])
                    for i in range(0, attempts):
                        print("-------------------------------------")
                        print("*You are choosing an item.*")
                        print("-------------------------------------")
                        items_choices = {}
                        choice_num = 1

                        for item in pools[pool].values():
                            items_choices[str(choice_num)] = item
                            choice_num += 1

                        print("-------------------------------------")

                        for choice_num, choice in items_choices.items():
                            print(choice_num + ": " + choice.getDisplayName())

                        print("-------------------------------------")

                        choice = input()
                        if(choice in items_choices.keys()):
                            self.receive_item(items_choices[choice].name)
                    return

                elif(("D6" in self.inventory.keys()) or ("D100" in self.inventory.keys())):
                    attempts = 0
                    if("D6" in self.inventory.keys()):
                        attempts += len(self.inventory["D6"])
                    if("D100" in self.inventory.keys()):
                        attempts += len(self.inventory["D100"])
                    for i in range(0, attempts):
                        item_name = random.choice(list(pools[pool].keys()))
                        print("-------------------------------------")
                        print("*You have looted: " + items_by_name[item_name].getDisplayName() + ".*")
                        print("*Care to reroll? (" + str(attempts) + ").*")
                        print("-------------------------------------")

                        choices = {"1": "Yes.", "2": "No."}

                        for choice_num, choice in choices.items():
                            print(choice_num + ": " + choice)

                        choice = input()
                        if(choice in choices.keys()):
                            if(choice == "1"):
                                continue
                            else:
                                self.receive_item(item_name)
                                return
                        else:
                            self.receive_item(item_name)
                            return

            item_name = random.choice(list(pools[pool].keys()))
            self.receive_item(item_name)

    def receive_item(self, item_name="", item=None):
        if(not item):
            if(items_by_name[item_name] in self.get_all_items()):
                item = items_name_to_type[item_name]()
            else:
                item = items_by_name[item_name]
        else:
            item_name = item.name
        if(item_name in self.inventory.keys()):
            self.inventory[item_name].append(item)
            item.on_receive(self)
        else:
            self.inventory[item_name] = [item]
            item.on_receive(self)
        if(self == player):
            add_to_log("You had received " + item.getDisplayName() + ".")
        return item

    def remove_item(self, item):
        if(item.name in self.inventory.keys()):
            items_by_name[item.name] = item
            self.inventory[item.name].remove(item)
            if(len(self.inventory[item.name]) == 0):
                self.inventory.pop(item.name)

    def get_item(self, item_name):
        if(item_name in self.inventory.keys()):
            return self.inventory[item_name][0]

    def get_all_items(self):
        output = []
        for item_name in self.inventory.keys():
            for item in self.inventory[item_name]:
                output.append(item)
        return output

    def get_all_item_names(self):
        output = []
        for item_name in self.inventory.keys():
            for item in self.inventory[item_name]:
                output.append(item.getDisplayName())
        return output

    def addHealth(self, count):
        if("Incurable" in self.effects.keys()):  # See No_Heal effect.
            coount = 0
        count = Clamp(count, self.min_health - self.health, self.max_health - self.health)
        self.on_add_health(count)
        self.health += count
        if(self.health <= 0):  # You can be at your min health yet not die(see Immortality effect).
            self.die()
            return False  # Return False if the being died.
        return True

    def addFood(self, count):
        count = Clamp(count, self.min_food - self.food, self.max_food - self.food)
        self.on_add_food(count)
        self.food += count

    def addMoney(self, count):
        count = Clamp(count, self.min_money - self.money, self.max_money - self.money)
        self.on_add_money(count)
        self.money += count

    def addKeys(self, count):
        count = Clamp(count, self.min_keys - self.keys, self.max_keys - self.keys)
        self.on_add_keys(count)
        self.keys += count

    def addSin(self, count):
        count = Clamp(count, self.min_sin - self.sin, self.max_sin - self.sin)
        self.on_add_sin(count)
        self.sin += count

    def hitby(self, being, item=None):
        dam = being.damage
        if(item):
            dam += item.getDamage()
            item.on_hit(being, self, dam)
        self.on_hitby(being, dam, item)
        if(event.name == "Fight" and event.npc == self or player == self):
            log_fight(being, self, dam, item)
        self.receiveDamage(dam, item)

    def retaliate(self, being):
        return

    def nextNPC(self):  # Called when an NPC dies.
        self.name = "Bill"

    def die(self):  # Do not override this method.
        self.life_ticks = 0
        self.on_death()

    # Methods below can be freely overriden.

    def reroll_consumables(self):
        consumambles_total = self.food + self.money + self.keys

        self.food = 0
        self.money = 0
        self.keys = 0

        i = 0
        while(i < consumambles_total):
            consumable = random.choice(["food", "money", "keys"])
            if(consumable == "food"):
                self.addFood(1)
            elif(consumable == "money"):
                self.addMoney(1)
            else:
                self.addKeys(1)
            i += 1

    def reroll_inventory(self):
        reroll_pools = []
        for item in self.get_all_items():
            if(len(item.item_pools) > 0):
                reroll_pools.append(random.choice(item.item_pools))  # Don't care enough to preserve information about what pool item was received from.
            self.remove_item(item)

        for pool in reroll_pools:
            self.loot(pool)

    def reroll_effects(self):
        values = 0
        effects = {}
        for effect in self.effects.values():
            values += effect.severity
            values += effect.ticks
            effects[type(effect)] = {"severity": 0, "ticks": 0}
            Being_Effects.remove_effect(self, type(effect))

        i = 0
        while(i < values):
            effect = random.choice(effects.keys())
            effects[effect][random.choice["severity", "ticks"]] += 1
            i += 1

        for effect in effects.keys():
            Being_Effects.set_effect(self, effect, effects[effect]["severity"], effects[effect]["ticks"])

    def on_retaliate(self, being, damage):
        return

    def on_hitby(self, being, damage, item=None):
        return

    def on_life(self):
        return

    def on_death(self):
        return

    def on_walk(self):
        return

    def receiveDamage(self, damage, npc):
        return

    def on_add_health(self, count):
        return

    def on_add_food(self, count):
        return

    def on_add_money(self, count):
        return

    def on_add_keys(self, count):
        return

    def on_add_sin(self, count):
        for effect in self.effects.values():
            effect.on_add_sin(self, count)
        for item in self.get_all_items():
            item.on_add_sin(self, count)

    def getMetabolismSpeed(self):
        return self.metabolism_speed

    def return_save_data(self, npc_info):
        npc_info['type'] = self.type
        npc_info['health'] = self.health
        npc_info['max_health'] = self.max_health
        npc_info['min_health'] = self.min_health
        npc_info['food'] = self.food
        npc_info['max_food'] = self.max_food
        npc_info['min_food'] = self.min_food
        npc_info['money'] = self.money
        npc_info['max_money'] = self.max_money
        npc_info['min_money'] = self.min_money
        npc_info['keys'] = self.keys
        npc_info['max_keys'] = self.max_keys
        npc_info['min_keys'] = self.min_keys
        npc_info['sin'] = self.sin
        npc_info['max_sin'] = self.max_sin
        npc_info['min_sin'] = self.min_sin
        npc_info['dodge_chance'] = self.dodge_chance
        npc_info['hit_chance'] = self.hit_chance
        npc_info['damage'] = self.damage
        npc_info['amount'] = self.amount

        npc_info['inventory'] = []
        for item in self.get_all_items():
            item_info = {}
            item.return_save_data(item_info)
            npc_info['inventory'].append(item_info)

        npc_info['effects'] = []
        for effect in self.effects.values():
            effect_info = {}
            effect.return_save_data(effect_info)
            npc_info['effects'].append(effect_info)

        blood_vessel_info = {}
        stomach_vessel_info = {}
        skin_vessel_info = {}
        self.blood_vessel.return_save_data(blood_vessel_info)
        self.stomach_vessel.return_save_data(stomach_vessel_info)
        self.skin_vessel.return_save_data(skin_vessel_info)

        npc_info['blood_vessel'] = blood_vessel_info
        npc_info['stomach_vessel'] = stomach_vessel_info
        npc_info['skin_vessel'] = skin_vessel_info

    def load_save_data(npc_info):
        npc = npcs_by_type[npc_info['type']]
        npc.health = npc_info['health']
        npc.max_health = npc_info['max_health']
        npc.min_health = npc_info['min_health']
        npc.food = npc_info['food']
        npc.max_food = npc_info['max_food']
        npc.min_food = npc_info['min_food']
        npc.money = npc_info['money']
        npc.max_money = npc_info['max_money']
        npc.min_money = npc_info['min_money']
        npc.keys = npc_info['keys']
        npc.max_keys = npc_info['max_keys']
        npc.min_keys = npc_info['min_keys']
        npc.sin = npc_info['sin']
        npc.max_sin = npc_info['max_sin']
        npc.min_sin = npc_info['min_sin']
        npc.dodge_chance = npc_info['dodge_chance']
        npc.hit_chance = npc_info['hit_chance']
        npc.damage = npc_info['damage']
        npc.amount = npc_info['amount']

        for item_info in npc_info['inventory']:
            Item.load_save_data(item_info, npc)

        for effect_info in npc_info['effects']:
            Being_Effects.load_save_data(effect_info, npc)

        npc.blood_vessel = Reagents.load_save_data(npc_info['blood_vessel'], npc, npc)
        npc.stomach_vessel = Reagents.load_save_data(npc_info['stomach_vessel'], npc, npc)
        npc.skin_vessel = Reagents.load_save_data(npc_info['skin_vessel'], npc, npc)

        npc.on_load_save_data(npc_info)

    def on_load_save_data(self, npc_info):
        return
class Player(Being):
    def __init__(self):
        super().__init__()
        # self.location = "Overworld"
        # self.display_name = ""
        self.name = "stranger"
        self.title = ""
        self.deaths = -1  # So after reset it becomes 0.
        self.kills = 0
        self.health = 5
        self.food = 5
        self.money = 2
        self.keys = 1
        self.sin = 0
        self.inventory = {}
        self.effects = {}
        self.walked_past = 0
        self.error = 0

        self.NPC = False

        # Combat related blah-blah.
        self.dodge_chance = 10

    def show_stats(self):
        print("Health: " + str(self.health) + "/" + str(self.max_health) + "\tFood: " + str(self.food) + "/" + str(self.max_food) + "\tMoney: " + str(self.money) + "/" + str(self.max_money) + "\tKeys: " + str(self.keys) + "/" + str(self.max_keys) + "\tSin: " + str(self.sin) + "/" + str(self.max_sin))
        effects_string = ""
        effect_num = 0
        for effect in self.effects.values():
            if(effect_num % 2 == 0):
                effects_string += effect.name + "(" + str(effect.severity) + "): " + str(effect.ticks) + "\t\t"
            else:
                effects_string += effect.name + "(" + str(effect.severity) + "): " + str(effect.ticks) + "\t"
            effect_num += 1
        if(effects_string != ""):
            print(effects_string)
        print("Inventory: " + str(self.get_all_item_names()))
        print("-------------------------------------")

    def show_choices(self):
        for choice_num, choice in event.choices.items():
            print(choice_num + ": " + choice)
        print("-------------------------------------")

    def on_life(self):
        if(self.food <= 0):
            force_event("Starvation", check_req=True)

    def on_death(self):
        force_event("Death", force_put=True, force_pos=0)

    def hit(self, npc):
        npc.hitby(self)

    def hit_with(self, npc, item):
        npc.hitby(self, item)

    def receiveDamage(self, damage, npc):
        self.addHealth(-damage)

    def on_walk(self):
        if(self.walked_past >= 3):
            if("Blessed Sandals" in self.inventory.keys()):
                self.addHealth(len(self.inventory["Blessed Sandals"]))  # I guess they can revive a Player. I call it a feature.
            self.addFood(-1)
            self.walked_past = 0
        else:
            self.walked_past += 1
class NPC(Being):
    def __init__(self):
        super().__init__()
        self.village_bound = False  # Buyer, Keykeeper, Villager, Treasury Vendor. Replace with a Faction system later.
        self.in_fight = False
        self.initialize_npc()
        self.display_name = self.name
        # npcs_by_name[self.name] = self
        npcs_by_type[self.type] = self

    def initialize_npc(self):
        self.reset()

    def receiveDamage(self, damage, item=None):
        if(not self.addHealth(-damage)):
            if(self.in_fight):
                player.kills += 1
                if(item):
                    item.on_kill(self)
        elif(self.in_fight):
            force_event("Fight", force_put=True, force_pos=0)

    def retaliate(self, being):
        if(prob(self.hit_chance - being.dodge_chance)):
            dam = self.damage
            self.on_retaliate(being, dam)
            being.hitby(self)

    def on_death(self):
        self.food = 0
        self.money = 0
        self.keys = 0

        effects = {}

        if(self.in_fight):
            self.amount -= 1
            self.set_rewards()
            events_by_name["Victory"].setup(self)
            force_event("Victory", force_pos=0)
        else:
            if(npcs_by_type["Treasury Vendor"].amount >= 1):
                for item in self.get_all_items():
                    if("Treasure" in item.item_pools):
                        if(prob(50)):
                            npcs_by_type["Treasury Vendor"].loot("Treasure")
                        else:
                            npcs_by_type["Treasury Vendor"].receive_item(item.name)
                    self.remove_item(item)
        if(self.amount >= 0):
            self.nextNPC()

        self.blood_vessel = Reagents(1000, "blood")
        self.stomach_vessel = Reagents(1000, "stomach")
        self.skin_vessel = Reagents(1000, "skin")

        self.inventory = {}
        self.effects = {}

    def nextNPC(self):  # Called when an NPC dies.
        self.name = "Bill"

    def reset(self):
        self.type = "Human"
        self.name = "Bob"
        self.amount = 0  # How many such NPCs you can encounter throughout a run.

    def full_reset(self):
        self.inventory = {}
        self.effects = {}

        self.blood_vessel = Reagents(1000, "blood")
        self.stomach_vessel = Reagents(1000, "stomach")
        self.skin_vessel = Reagents(1000, "skin")

        self.reset()

    def set_rewards(self):  # Do not override this method.
        self.on_set_rewards()
        for item in self.get_all_items():
            player.receive_item(item.name)
        player.addFood(self.food)
        player.addMoney(self.money)
        player.addKeys(self.keys)

    def on_set_rewards(self):
        return


class Devil(NPC):
    def reset(self):
        self.type = "Devil"
        self.name = random.choice(["Abbadon", "Asmodeus", "Baphomet", "Beelzebub", "Loki", "Namaah"]) + " the Devil"
        self.health = 6
        self.max_health = 6
        self.max_food = 0
        self.sin = self.max_sin
        self.souls = 0
        self.amount = 6
        self.damage = 2
        self.dodge_chance = 10

        self.metabolism_speed = 0

    def on_hitby(self, being, damage, item=None):
        being.addSin(-damage)

    def on_retaliate(self, being, damage):
        Being_Effects.set_effect(being, No_Heal, 1, 2)

    def nextNPC(self):
        self.name = random.choice(["Abbadon", "Asmodeus", "Baphomet", "Beelzebub", "Loki", "Namaah"]) + " the Devil"
        self.health = 6
        self.souls = 0

    def on_set_rewards(self):
        if(player.sin > 0):
            player.addSin(-player.sin)

    def return_save_data(self, npc_info):
        super().return_save_data(npc_info)
        npc_info["souls"] = self.souls

    def on_load_save_data(self, npc_info):
        super().on_load_save_data(npc_info)
        self.souls = npc_info['souls']

    def get_soul_percentage(self):
        return int((self.souls + player.sin) * 5)  # 10 sin and 10 souls = 20. 100 / 20 = 5. I mean, M A G I C.

class Angel(NPC):
    def reset(self):
        self.type = "Angel"
        self.name = random.choice(["Barachiel", "Cassiel", "Daniel", "Mebahiah", "Muriel", "Sariel"]) + " the Angel"
        self.health = 12
        self.sin = self.min_sin
        self.max_health = 12
        self.max_food = 0
        self.amount = 12
        self.dodge_chance = 10

        self.metabolism_speed = 1

    def on_hitby(self, being, damage, item=None):
        being.addSin(damage)

    def nextNPC(self):
        self.name = random.choice(["Barachiel", "Cassiel", "Daniel", "Mebahiah", "Muriel", "Sariel"]) + " the Angel"
        self.health = 12

    def on_set_rewards(self):
        player.addSin(player.max_sin - player.sin)
        dagger = player.get_item("Sacrificial Dagger")
        if(dagger and dagger.strength < 666):
            dagger.strength = 666


class Death_NPC(NPC):
    def reset(self):
        self.type = "Death"
        self.name = "Death"
        self.health = 1
        self.max_health = 1
        self.min_health = 1
        self.max_food = 0
        self.amount = 1
        self.damage = 1

        self.metabolism_speed = 1

        self.dodge_chance = 100

        self.cheated = 0

    def on_hitby(self, being, damage, item=None):
        being.die()

    def nextNPC(self):
        return

    def on_set_rewards(self):
        force_event("Doom", force_put=True, force_pos=0)

    def return_save_data(self, npc_info):
        super().return_save_data(npc_info)
        npc_info["cheated"] = self.cheated

    def on_load_save_data(self, npc_info):
        super().on_load_save_data(npc_info)
        self.cheated = npc_info['cheated']


class It(NPC):
    def reset(self):
        self.type = "It"
        self.name = "It"
        self.health = 666
        self.max_health = 666
        self.max_food = 666
        self.food = self.max_food
        self.amount = 1
        self.damage = 10

        self.metabolism_speed = 6  # It gets hungry quickly.

        self.is_summoned = False

    def on_retaliate(self, being, damage):
        if(being.food > being.min_food):
            self.addFood(being.food)
            being.addFood(-being.food)
        self.addFood(damage)

    def nextNPC(self):
        return

    def on_life(self):
        if(self.is_summoned and self.food < self.max_food):
            npc = random.choice(list(npcs_by_type.values()))
            if(npc == self):
                return
            if(npc.village_bound):
                self.retaliate(npc)
                npc.retaliate(self)


    def getMetabolismSpeed(self):
        if(self.is_summoned):
            return self.metabolism_speed
        return 0

    def on_set_rewards(self):
        full_reset()

    def return_save_data(self, npc_info):
        super().return_save_data(npc_info)
        npc_info["is_summoned"] = self.is_summoned

    def on_load_save_data(self, npc_info):
        super().on_load_save_data(npc_info)
        self.is_summoned = npc_info['is_summoned']


class Keykeeper(NPC):
    def reset(self):
        self.type = "Keykeeper"
        self.name = random.choice(["Celes", "Nøgle", "Klawisz", "Klyuch", "Key", "Llave"]) + " the Keykeeper"
        self.keys = 0
        self.health = 3
        self.food = random.randint(1, self.max_food)
        self.amount = 7
        self.hit_chance = 30

        self.village_bound = True

        for i in range(0, random.randint(0, 2)):
            self.loot("Generic")

    def nextNPC(self):
        self.name = random.choice(["Celes", "Nøgle", "Klawisz", "Klyuch", "Key", "Llave"]) + " the Keykeeper"
        self.keys = 0
        self.health = 3
        self.food = random.randint(1, self.max_food)

        for i in range(0, random.randint(0, 2)):
            self.loot("Generic")


class Buyer(NPC):
    def reset(self):
        self.type = "Buyer"
        self.name = random.choice(["Henry", "James", "John", "Marco", "William"]) + " the Buyer of Goods"
        self.money = 0
        self.health = 3
        self.max_health = 3
        self.food = random.randint(1, self.max_food)
        self.amount = 7
        self.hit_chance = 30

        self.village_bound = True

        for i in range(0, random.randint(0, 2)):
            self.loot("Generic")

    def nextNPC(self):
        self.name = random.choice(["Henry", "James", "John", "Marco", "William"]) + " the Buyer of Goods"
        self.money = 0
        self.health = 3
        self.food = random.randint(1, self.max_food)

        for i in range(0, random.randint(0, 2)):
            self.loot("Generic")



class Treasury_Vendor(NPC):
    def reset(self):
        self.type = "Treasury Vendor"
        self.name = random.choice(["Lootbag", "Bootycollector", "Tallyman"]) + " the Seller of Treasure"
        self.money = 0
        self.health = 3
        self.max_health = 3
        self.food = random.randint(1, self.max_food)
        self.amount = 7
        self.hit_chance = 30
        self.inventory = {}

        self.village_bound = True

        for i in range(0, random.randint(0, 2)):
            self.loot("Generic")

    def nextNPC(self):
        self.name = random.choice(["Lootbag", "Bootycollector", "Tallyman"]) + " the Seller of Treasure"
        self.health = 3
        self.food = random.randint(1, self.max_food)

        for i in range(0, random.randint(0, 2)):
            self.loot("Generic")


class Villager(NPC):
    def reset(self):
        self.type = "Villager"
        self.name = random.choice(["Alan", "Alex", "Bob", "Bill", "Cara", "Eric", "Jack", "Jill"]) + " the Villager"
        self.health = 3
        self.max_health = 3
        self.food = random.randint(1, self.max_food)
        self.amount = 30
        self.money = random.randint(1, 2)
        self.hit_chance = 30

        for i in range(0, random.randint(0, 2)):
            self.loot("Generic")

    def on_life(self):  # Running the economy so human NPCs won't starve.
        total_food_gathered = self.amount

        for npc in npcs_by_type.values():
            if(total_food_gathered <= 0):
                break
            if(npc.amount == 0):
                continue
            if(not npc.village_bound):
                continue
            if(npc.food < npc.max_food):
                reqs_food = (npc.max_food - npc.food) * npc.amount  # Since all of them eat.
                can_buy = min(total_food_gathered, reqs_food)
                if(npc.type == "Villager"):
                    total_food_gathered -= can_buy
                    npc.addFood(int(can_buy / npc.amount))
                else:
                    can_buy = min(can_buy, npc.money * npc.amount)
                    npcs_by_type["Buyer"].addMoney(int(can_buy / (2 * npc.amount)))  # They split the share in half.
                    npcs_by_type["Villager"].addMoney(int(can_buy / (2 * npc.amount)))
                    npc.addFood(int(can_buy / npc.amount))


    def nextNPC(self):
        self.name = random.choice(["Alan", "Alex", "Bob", "Bill", "Cara", "Eric", "Jack", "Jill"]) + " the Villager"
        self.health = 3
        self.food = random.randint(1, self.max_food)
        self.money = random.randint(1, 2)

        for i in range(0, random.randint(0, 2)):
            self.loot("Generic")


class Bandit(NPC):
    def reset(self):
        self.type = "Bandit"
        self.name = random.choice(["Billy", "Bonnie", "Clyde", "Jesse", "Ned"]) + " the Bandit"
        self.health = random.randint(3, 5)
        self.food = random.randint(1, self.max_food)
        self.max_health = 5
        self.amount = 15
        self.money = random.randint(1, 3)
        self.hit_chance = 90
        self.dodge_chance = 10

        for i in range(0, random.randint(0, 2)):
            self.loot("Generic")

    def on_life(self):  # Robbing the villages and vendors.
        for i in range(0, self.amount):
            if(prob(75) and self.food < self.max_food and npcs_by_type["Villager"].food >= 1):
                self.addFood(1)
                npcs_by_type["Villager"].addFood(-1)
            if(prob(50) and self.money < self.max_money and npcs_by_type["Villager"].money >= 1):
                self.addMoney(1)
                npcs_by_type["Villager"].addMoney(-1)
            if(prob(25) and len(npcs_by_type["Villager"].inventory.keys())):
                item = random.choice(list(npcs_by_type["Villager"].inventory.values()))
                npcs_by_type["Bandit"].receive_item(item=item)
                npcs_by_type["Villager"].remove_item(item)

    def nextNPC(self):
        self.name = random.choice(["Billy", "Bonnie", "Clyde", "Jesse", "Ned"]) + " the Bandit"
        self.health = random.randint(3, 5)
        self.food = random.randint(1, self.max_food)
        self.money = random.randint(1, 3)

        for i in range(0, random.randint(0, 2)):
            self.loot("Generic")
class Item:
    def __init__(self):
        self.damage = 0
        self.initialize_item()
        self.display_name = self.name
        for pool in self.item_pools:
            pools[pool][self.name] = self
        items_by_name[self.name] = self
        items_name_to_type[self.name] = type(self)

    def reset(self):
        return

    def full_reset(self):
        self.reset()

    def getDisplayName(self):
        return self.display_name

    def getMoneyCost(self):
        return self.money_cost

    def on_receive(self, being):
        return

    def on_life(self, being):
        return

    def on_hit(self, attacker, victim, dam):
        return

    def on_kill(self, npc):
        return

    def on_add_sin(self, being, count):
        return

    def on_walk(self, being):
        return

    def getDamage(self):
        return self.damage

    def initialize_item(self):
        self.name = "Item"
        self.item_pools = []
        self.money_cost = 0
        self.damage = 0

    def isLiquidContainer(self):
        return False

    def use(self):
        return

    def return_save_data(self, item_info):
        item_info['name'] = self.name

    def load_save_data(item_info, being=None):
        item = None
        if(being):
            item = being.receive_item(item_info['name'])
        else:
            item = items_name_to_type[item_info['name']]()
            items_by_name[item.name] = item
        item.on_load_save_data(item_info, being)

    def on_load_save_data(self, item_info, being=None):
        return


class Jar_Of_Blood(Item):
    def initialize_item(self):
        self.name = "Jar of Blood"
        self.item_pools = ["Devil"]
        self.money_cost = 0
        self.stored_blood = 0
        self.damage = 0

    def reset(self):
        self.stored_blood = 0

    def use(self):
        print("=====================================")
        print("*Jar of Blood.*")
        print("Stored blood: " + str(self.stored_blood))
        choices = {"1": "Quit.", "2": "Dump.", "3": "Store blood."}
        if(self.stored_blood >= 1):
            choices["4"] = "Take blood."

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)
            if(choice == "3"):
                player.addHealth(-1)
                self.stored_blood += 1
            elif(choice == "4"):
                player.addHealth(1)
                self.stored_blood -= 1

    def return_save_data(self, item_info):
        item_info['name'] = self.name
        item_info['stored_blood'] = self.stored_blood

    def on_load_save_data(self, item_info, being=None):
        self.stored_blood = item_info['stored_blood']


class Red_Sleeping_Roll(Item):
    def initialize_item(self):
        self.name = "Red Sleeping Roll"
        self.item_pools = ["Devil"]
        self.money_cost = 2
        self.damage = -1

    def use(self):
        print("=====================================")
        print("*Red Sleeping Roll.*")
        print("Attracts all kinds of evil.")
        choices = {"1": "Quit.", "2": "Dump.", "3": "Get a rest. H+ ???"}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)
            if(choice == "3"):
                player.addHealth(1)
                if(prob(50)):
                    force_event("Bandits", force_put=True, check_req=True)


class Sacrificial_Dagger(Item):
    def initialize_item(self):
        self.name = "Sacrificial Dagger"
        self.item_pools = ["Devil"]
        self.money_cost = 4
        self.strength = 0
        self.damage = 6

    def reset(self):
        self.strength = 0

    def on_kill(self, npc):
        self.strength += 1
        player.addSin(1)
        if("Jar of Blood" in player.inventory.keys()):
            jar = player.get_item("Jar of Blood")
            jar.stored_blood += 1
        force_event("Devil Room", check_req=True)

    def use(self):
        print("=====================================")
        print("*Sacrificial Dagger.*")
        print("The more blood it sheed, the stronger it is.")
        choices = {"1": "Quit.", "2": "Dump.", "3": "Cut yourself. H- ???"}

        if(self.strength >= 666 and not npcs_by_type["It"].is_summoned):
            choices["4"] = "Summon It. H- ???"

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)
            if(choice == "3"):
                player.addHealth(-1)
                self.strength += 1
                force_event("Devil Room", check_req=True)
            elif(choice == "4"):
                player.addHealth(-1)
                self.strength = 0
                force_event("It Summon", force_put=True, force_pos=0)

    def return_save_data(self, item_info):
        item_info['name'] = self.name
        item_info['strength'] = self.strength

    def on_load_save_data(self, item_info, being=None):
        self.strength = item_info['strength']


class Black_Salt(Item):
    def initialize_item(self):
        self.name = "Black Salt"
        self.item_pools = ["Devil", "Angel"]
        self.money_cost = 0
        self.damage = -1

    def on_hit(self, attacker, victim, damage):
        player.remove_item(self)  # Poof.

    def use(self):
        print("=====================================")
        print("*Black Salt.*")
        print("Keeps the Devil away.")
        choices = {"1": "Quit.", "2": "Dump."}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)


class Goat_Head(Item):
    def initialize_item(self):
        self.name = "Goat Head"
        self.item_pools = ["Devil"]
        self.money_cost = 0
        self.damage = 1

    def use(self):
        print("=====================================")
        print("*Goat Head.*")
        print("Deal with the Devil.")
        choices = {"1": "Quit.", "2": "Dump.", "3": "Make an offering."}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)
            elif(choice == "3"):
                force_event("Devil Room", force_pos=0)  # If there are no forced Devil Rooms down the line, make the next encounter a Devil Room.


class Master_Key(Item):
    def initialize_item(self):
        self.name = "Master Key"
        self.item_pools = ["Treasure"]
        self.money_cost = 4
        self.damage = -1

    def use(self):
        print("=====================================")
        print("*Master Key.*")
        print("Unlocks what's locked.")
        choices = {"1": "Quit.", "2": "Dump."}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)


class Little_Locked_Chest(Item):
    def initialize_item(self):
        self.name = "Little Locked Chest"
        self.item_pools = ["Generic", "Treasure", "Devil", "Angel"]
        self.money_cost = 4
        self.damage = 0

    def on_hit(self, attacker, victim, damage):
        if(prob(1)):  # Sometimes it opens when you hit with it.
            attacker.remove_item(self)
            attacker.receive_item("Little Opened Chest")
            attacker.loot("Treasure")

    def use(self):
        print("=====================================")
        print("*Little Locked Chest.*")
        print("It's locked.")
        choices = {"1": "Quit.", "2": "Dump."}

        if(player.keys >= 1):
            choices["3"] = "Open it."

        if("Master Key" in player.inventory.keys()):
            choices["4"] = "Use Master Key."

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)
            elif(choice == "3"):
                player.addKeys(-1)
                player.remove_item(self)
                player.receive_item("Little Opened Chest")
                player.loot("Treasure")  # Yes, you can find a Little Locked Chest inside one...
            elif(choice == "4"):
                player.remove_item(self)
                player.receive_item("Little Opened Chest")
                player.loot("Treasure")


class Little_Opened_Chest(Item):
    def initialize_item(self):
        self.name = "Little Opened Chest"
        self.item_pools = ["Generic", "Treasure", "Devil", "Angel"]
        self.money_cost = 2
        self.damage = 0

    def use(self):
        print("=====================================")
        print("*Little Opened Chest.*")
        print("It's open.")
        choices = {"1": "Quit.", "2": "Dump."}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)


class Blessed_Sandals(Item):
    def initialize_item(self):
        self.name = "Blessed Sandals"
        self.item_pools = ["Angel"]
        self.money_cost = 2

    def use(self):
        print("=====================================")
        print("*Blessed Sandals.*")
        print("Movement is life.")
        choices = {"1": "Quit.", "2": "Dump."}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)


class Holy_Cross(Item):
    def initialize_item(self):
        self.name = "Holy Cross"
        self.item_pools = ["Angel"]
        self.money_cost = 2
        self.damage = -2  # It actually heals the enemy!

    def use(self):
        print("=====================================")
        print("*Holy Cross.*")
        print("Sin is harm, repentance is good.")
        choices = {"1": "Quit.", "2": "Dump."}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)

    def on_add_sin(self, being, count):
        being.addHealth(-count)


class Rusty_Knife(Item):
    def initialize_item(self):
        self.name = "Rusty Knife"
        self.item_pools = ["Generic", "Devil"]
        self.money_cost = 0
        self.damage = 1

    def on_hit(self, attacker, victim, damage):
        Being_Effects.set_effect(victim, Bleeding, 1, 3)

    def use(self):
        print("=====================================")
        print("*Rusty Knife.*")
        print("Damn, this must make one's life tough.")
        choices = {"1": "Quit.", "2": "Dump.", "3": "Cut yourself. H- (B)"}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)
            if(choice == "3"):
                Being_Effects.set_effect(player, Bleeding, 1, 3)


class Liquid_Container(Item):
    def initialize_item(self):
        self.name = "Liquid Container"
        self.item_pools = []
        self.max_amount = 0
        self.reagents = Reagents(self.max_amount, "container")

    def reset(self):
        self.reagents = Reagents(self.max_amount, "container")

    def isLiquidContainer(self):
        return True

    def getMoneyCost(self):
        return self.reagents.get_cost()

    def return_save_data(self, item_info):
        item_info['name'] = self.name
        item_info['max_amount'] = self.max_amount
        reagents_info = {}
        self.reagents.return_save_data(reagents_info)
        item_info['reagents'] = reagents_info

    def on_load_save_data(self, item_info, being=None):
        self.max_amount = item_info['max_amount']
        self.reagents = Reagents.load_save_data(item_info['reagents'])


class Health_Bottle(Item):
    def initialize_item(self):
        self.name = "Bottle of Potion of Health"
        self.item_pools = ["Generic", "Treasure", "Angel"]
        self.money_cost = 8

    def on_receive(self, being):
        health_units = random.randint(1, 4)
        item = being.receive_item("Bottle")
        item.reagents.add_reagent(Health_Potion, health_units)
        being.remove_item(self)


class Regen_Bottle(Item):
    def initialize_item(self):
        self.name = "Bottle of Potion of Regeneration"
        self.item_pools = ["Generic", "Treasure", "Angel"]
        self.money_cost = 8

    def on_receive(self, being):
        health_units = random.randint(1, 4)
        item = being.receive_item("Bottle")
        item.reagents.add_reagent(Regen_Potion, health_units)
        being.remove_item(self)


class Harm_Bottle(Item):
    def initialize_item(self):
        self.name = "Bottle of Potion of Harm"
        self.item_pools = ["Generic", "Treasure", "Devil"]
        self.money_cost = 8

    def on_receive(self, being):
        harm_units = random.randint(1, 4)
        item = being.receive_item("Bottle")
        item.reagents.add_reagent(Harm_Potion, harm_units)
        being.remove_item(self)


class Bleeding_Bottle(Item):
    def initialize_item(self):
        self.name = "Bottle of Potion of Bleeding"
        self.item_pools = ["Generic", "Treasure", "Devil"]
        self.money_cost = 8

    def on_receive(self, being):
        harm_units = random.randint(1, 4)
        item = being.receive_item("Bottle")
        item.reagents.add_reagent(Bleeding_Potion, harm_units)
        being.remove_item(self)


class Immortality_Bottle(Item):
    def initialize_item(self):
        self.name = "Bottle of Potion of Immortality"
        self.item_pools = ["Treasure", "Angel"]
        self.money_cost = 16

    def on_receive(self, being):
        health_units = random.randint(1, 4)
        item = being.receive_item("Bottle")
        item.reagents.add_reagent(Immortality_Potion, health_units)
        being.remove_item(self)


class No_Heal_Bottle(Item):
    def initialize_item(self):
        self.name = "Bottle of Potion of Incurability"
        self.item_pools = ["Treasure", "Devil"]
        self.money_cost = 16

    def on_receive(self, being):
        harm_units = random.randint(1, 4)
        item = being.receive_item("Bottle")
        item.reagents.add_reagent(No_Heal_Potion, harm_units)
        being.remove_item(self)


class Wine_Bottle(Item):
    def initialize_item(self):
        self.name = "Bottle of Wine"
        self.item_pools = ["Angel"]
        self.money_cost = 4

    def on_receive(self, being):
        wine_units = random.randint(1, 4)
        item = being.receive_item("Bottle")
        item.reagents.add_reagent(Wine, wine_units)
        being.remove_item(self)


class Bottle(Liquid_Container):
    def initialize_item(self):
        self.name = "Bottle"
        self.item_pools = ["Generic", "Treasure"]
        self.money_cost = 0
        self.damage = 1
        self.max_amount = 4
        self.reagents = Reagents(self.max_amount, "container")

    def getDisplayName(self):
        am = self.reagents.get_amount()
        if(am == 0):
            output = "Empty bottle"
        else:
            if(len(self.reagents.reagents) == 1):
                for reagent in self.reagents.reagents.values():
                    output = ("Bottle of " + reagent.name)
            else:
                output = self.reagents.get_color().capitalize() + " " + self.reagents.get_smell().capitalize() + " Bottle"
        return output

    def on_hit(self, attacker, victim, damage):
        self.reagents.transfer_any(victim.skin_vessel, self.reagents.get_amount(), attacker, victim)
        attacker.remove_item(self)
        attacker.receive_item("Broken Bottle")

    def use(self):
        print("=====================================")
        am = self.reagents.get_amount()
        if(am == 0):
            print("*Empty bottle.*")
            print("Either fully empty or not filled at all.")
        else:
            if(len(self.reagents.reagents) == 1):
                for reagent in self.reagents.reagents.values():
                    print("*Bottle of " + reagent.name + ".*")
            else:
                print("*" + self.reagents.get_color().capitalize() + " " + self.reagents.get_smell().capitalize() + " Bottle.*")
            if(am == self.max_amount):
                print("The bottle is full.")
            elif(am >= self.max_amount * 0.75):
                print("The bottle is missing a quarter.")
            elif(am >= self.max_amount / 2):
                print("The bottle is half empty.")
            elif(am >= self.max_amount / 4):
                print("The bottle is filled to a quarter.")

        choices = {"1": "Quit.", "2": "Dump.", "3": "Break."}
        choice_num = 4

        if(am > 0):
            choices[str(choice_num)] = "Transfer liquid to another container."
            choice_num += 1
            choices[str(choice_num)] = "Sip from bottle."
            choice_num += 1
            choices[str(choice_num)] = "Apply to skin."
            choice_num += 1
        if(am < self.reagents.max_amount):
            choices[str(choice_num)] = "Transfer liquid from another container."


        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            choice = choices[choice]
            if(choice == "Dump."):
                player.remove_item(self)
            elif(choice == "Break."):
                player.remove_item(self)
                player.receive_item("Broken Bottle")
            elif(choice == "Transfer liquid to another container."):
                transfer_choices = {}
                transfer_choices_items = {}
                choice_num = 1
                for item in player.get_all_items():
                    if(item == self):
                        continue
                    if(not item.isLiquidContainer()):
                        continue
                    transfer_choices[str(choice_num)] = item.getDisplayName()
                    transfer_choices_items[str(choice_num)] = item
                    choice_num += 1

                if(len(transfer_choices)):
                    for transfer_num, transfer_choice in transfer_choices.items():
                        print(transfer_num + ": " + transfer_choice)

                    choice = input()
                    if(choice in transfer_choices.keys()):
                        max_ = min(self.reagents.get_amount(), transfer_choices_items[choice].max_amount - transfer_choices_items[choice].reagents.get_amount())
                        print("Amount from 0 to " + str(max_))
                        am = int(input())
                        if(am > max_ or am < 0):
                            return
                        self.reagents.transfer_any(transfer_choices_items[choice].reagents, am, player, player)

            elif(choice == "Transfer liquid from another container."):
                transfer_choices = {}
                transfer_choices_items = {}
                choice_num = 1
                for item in player.get_all_items():
                    if(item == self):
                        continue
                    if(not item.isLiquidContainer()):
                        continue
                    if(item.reagents.get_amount() == 0):
                        continue
                    transfer_choices[str(choice_num)] = item.getDisplayName()
                    transfer_choices_items[str(choice_num)] = item
                    choice_num += 1

                if(len(transfer_choices)):
                    for transfer_num, transfer_choice in transfer_choices.items():
                        print(transfer_num + ": " + transfer_choice)

                    choice = input()
                    if(choice in transfer_choices.keys()):
                        max_ = min(self.reagents.max_amount, transfer_choices_items[choice].reagents.get_amount())
                        print("Amount from 1 to " + str(max_))
                        am = int(input())
                        if(am > max_ or am < 1):
                            return
                        transfer_choices_items[choice].reagents.transfer_any(self.reagents, am, player, player)

            elif(choice == "Sip from bottle."):
                self.reagents.transfer_any(player.stomach_vessel, 1, player, player)
            elif(choice == "Apply to skin."):
                self.reagents.transfer_any(player.skin_vessel, 1, player, player)


class Broken_Bottle(Item):
    def initialize_item(self):
        self.name = "Broken Bottle"
        self.item_pools = ["Generic"]
        self.money_cost = 0
        self.damage = 2

    def use(self):
        print("=====================================")
        print("*Broken bottle.*")
        print("Fully broken.")
        choices = {"1": "Quit.", "2": "Dump."}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)


class Cloak(Item):
    def initialize_item(self):
        self.name = "Cloak"
        self.item_pools = ["Generic", "Treasure"]
        self.money_cost = 2
        self.damage = -1

    def use(self):
        print("=====================================")
        print("*Cloak.*")
        print("Go back unnoticed.")
        choices = {"1": "Quit.", "2": "Dump."}

        if(previous_previous_event and previous_previous_event.check_requirements()):
            choices["3"] = "Go back."

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)
            elif(choice == "3"):
                force_event(previous_previous_event.name, force_put=True, force_pos=0)


class Deck_Of_Fateful_Cards(Item):
    def initialize_item(self):
        self.name = "Deck of Fateful Cards"
        self.item_pools = ["Treasure"]
        self.money_cost = 2
        self.damage = -1

    def use(self):
        print("=====================================")
        print("*Deck of Fateful Cards.*")
        print("Make a pick.")
        choices = {"1": "Quit.", "2": "Dump."}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)


class D4(Item):
    def initialize_item(self):
        self.name = "D4"
        self.item_pools = ["Generic", "Treasure"]
        self.money_cost = 1
        self.damage = 2  # Pointy.

    def use(self):
        print("=====================================")
        print("*D4.*")
        print("Pointy.")
        choices = {"1": "Quit.", "2": "Dump.", "3": "Reroll inventory."}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)
            elif(choice == "3"):
                player.reroll_inventory()


class D6(Item):
    def initialize_item(self):
        self.name = "D6"
        self.item_pools = ["Generic", "Treasure"]
        self.money_cost = 1
        self.damage = -1

    def use(self):
        print("=====================================")
        print("*D6.*")
        print("Reroll an item.")
        choices = {"1": "Quit.", "2": "Dump."}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)


class D12(Item):
    def initialize_item(self):
        self.name = "D12"
        self.item_pools = ["Generic", "Treasure"]
        self.money_cost = 1
        self.damage = -1

    def on_hit(self, attacker, victim, damage):
        if(attacker == player and event.name == "Fight"):
            event.npc = random.choice(list(npcs_by_type.values()))

    def use(self):
        print("=====================================")
        print("*D12.*")
        print("Apply to enemy to reroll them.")
        choices = {"1": "Quit.", "2": "Dump."}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)


class D20(Item):
    def initialize_item(self):
        self.name = "D20"
        self.item_pools = ["Generic", "Treasure"]
        self.money_cost = 1
        self.damage = -1

    def use(self):
        print("=====================================")
        print("*D20.*")
        print("Reroll consumables.")
        choices = {"1": "Quit.", "2": "Dump.", "3": "Reroll consumables."}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)
            elif(choice == "3"):
                player.reroll_consumables()


class D100(Item):
    def initialize_item(self):
        self.name = "D100"
        self.item_pools = ["Generic", "Treasure"]
        self.money_cost = 1
        self.damage = -1

    def use(self):
        print("=====================================")
        print("*D100.*")
        print("Reroll everything.")
        choices = {"1": "Quit.", "2": "Dump.", "3": "Reroll everything."}

        for choice_num, choice in choices.items():
            print(choice_num + ": " + choice)

        print("=====================================")

        choice = input()
        if(choice in choices.keys()):
            if(choice == "2"):
                player.remove_item(self)
            elif(choice == "3"):
                player.reroll_consumables()
                player.reroll_inventory()
                player.reroll_effects()
for effect in get_all_subclasses(Being_Effects):
    effect()

for reagent in get_all_subclasses(Reagent):
    reagent(None)

for npc in get_all_subclasses(NPC):
    npc()

for item in get_all_subclasses(Item):
    item()

for event in get_all_subclasses(Event):
    event()

player = Player()
reset()

# player.receive_item("Deck of Fateful Cards")

while(True):
    tick += 1

    if(event and event.doLifeTick()):
        player.life()

        for npc in npcs_by_type.values():
            npc.life()

    player.show_stats()
    event = pick_event()
    forced_event = ""
    event.generate_choices()
    event.introduce_event()
    player.show_choices()

    reaction = input()
    if(reaction in event.choices.keys()):
        log_action(player, event.choices[reaction])
        if(event.choices[reaction] == "Open inventory."):
            force_event("Inventory", force_put=True, force_pos=0)
        elif(event.choices[reaction] == "Open log."):
            force_event("Log", force_put=True, force_pos=0)
        else:
            event.on_choice(event.choices[reaction], reaction)
    else:
        force_event("Bad Choice")
    clear_output()
