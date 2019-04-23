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
