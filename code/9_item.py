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
