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
