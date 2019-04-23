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
