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
