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
