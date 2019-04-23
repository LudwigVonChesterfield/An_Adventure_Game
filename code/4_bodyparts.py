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
