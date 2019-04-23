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
