import os
import sys
import random
import roman
import datetime
import webcolors
import json

effects_name_to_type = {}
reagents_name_to_type = {}
# npcs_by_name = {}
npcs_by_type = {}
items_by_name = {}
items_name_to_type = {}
events_by_name = {}
events_by_location = {"Overworld": {}, "Dungeon": {}, "Village": {}}
pools = {"Generic": {}, "Treasure": {}, "Devil": {}, "Angel": {}}
forced_events = []
event = None
previous_event = None
previous_previous_event = None
death_reaction = None
previous_sin = 0

tick = 0
log = []


def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def get_colour_name(requested_colour):
    try:
        color_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        color_name = closest_colour(requested_colour)
    return color_name


def Clamp(value, min_, max_):
    return max(min(value, max_), min_)


def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


def tick2time(tick):
    day = tick // 86400
    hour = (tick - (day * 86400)) // 3600
    min_ = (tick - ((day * 86400) + (hour * 3600))) // 60 
    seconds = tick - ((day * 86400) + (hour * 3600) + (min_ * 60))

    return datetime.time(hour, min_, seconds)


def prob(chance):
    roll = random.randint(0, 100)
    if(roll < chance):
        return True
    return False


def clear_output():
    if('idlelib.run' in sys.modules):
        print("\n" * 100)
    else:
        # for windows
        if(os.name == 'nt'):
            os.system('cls')
        # for mac and linux(here, os.name is 'posix')
        else:
            os.system('clear')


def log_fight(attacker, victim, dam, item):
    item_string = ""
    if(item):
        item_string = " using " + item.name
    if(attacker == player):
        add_to_log("You had attacked " + victim.display_name + item_string + " for (" + str(dam) + ") damage.")
    elif(victim == player):
        add_to_log(attacker.display_name + " had attacked you" + item_string + " for (" + str(dam) + ") damage.")
    else:
        add_to_log(attacker.display_name + " had attacked " + victim.display_name + item_string + " for (" + str(dam) + ") damage.")


def log_action(being, string):
    if(being == player):
        add_to_log("You had performed " + string)
    else:
        add_to_log(being.display_name + " had performed " + string)


def add_to_log(string):
    global tick
    global log

    log.append("[" + str(tick2time(player.life_ticks)) + "] " + string)


def force_event(event, force_put=False, check_req=False, force_pos=-1):
    global forced_events

    if(check_req and not events_by_name[event].check_requirements()):
        return

    if(force_pos != -1):
        if(force_put or (event not in forced_events)):
            forced_events.insert(force_pos, event)
            return

    if(force_put or (event not in forced_events)):
        forced_events.append(event)


def pick_event():
    global forced_events
    global event
    global previous_event
    global previous_previous_event

    if(previous_event):
        previous_previous_event = previous_event

    if(event and not event.isTechnical()):
        previous_event = event

    if(player.health <= 0):
        return events_by_name["Death"]

    if(len(forced_events) != 0):
        next_event = forced_events.pop(0)
        if(next_event):
            return events_by_name[next_event]
        else:
            pick_event()
    else:
        pick = random.choice(list(events_by_location[player.location].values()))
        if(pick.check_requirements()):
            return pick
        else:
            return pick_event()
