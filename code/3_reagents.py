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
