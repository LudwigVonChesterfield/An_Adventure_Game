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
