import random
from functools import partial
from api.od import ODAPI
from transformation.cloner import clone_od


def precondition_creature_alive(od: ODAPI, creature: str):
    # Example for a pre-condition
    return od.get_slot_value(od.get(creature), "lives") > 0


def precondition_can_use_door(od: ODAPI, door: str):
    # TODO: Check whether the door can be used by the Hero: Do they have the matching Key?

    _, hero = od.get_all_instances("Hero")[0]
    hero_items = od.get_outgoing(hero, "HeroCollectsItems")
    door_key = od.get_target(od.get_outgoing(od.get(door), "DoorToKey")[0])

    for item in hero_items:
        if door_key == od.get_target(item):
            return True

    return False


def precondition_creature_can_move(od: ODAPI, target_tile: str):
    # TODO: Check whether the target_tile can be occupied by a creature, i.e. it's not an Obstacle
    target_tile = od.get_type_name(od.get(target_tile))

    return target_tile != "Obstacle"


def precondition_fight_possible(od: ODAPI):
    # TODO: Check whether two creatures are on the same Tile so fighting is possible in the current state

    # Hero tile
    _, hero = od.get_all_instances("Hero")[0]
    hero_tile = od.get_target(od.get_outgoing(hero, "CreaturesTile")[0])

    # Is there any monster alive? (in the same tile)
    for _, monster in od.get_all_instances("Monster"):
        if od.get_slot_value(monster, "lives") <= 0:
            continue
        monster_tile = od.get_target(od.get_outgoing(monster, "CreaturesTile")[0])
        if monster_tile == hero_tile:
            return True

    return False


def mark_as_moved(od: ODAPI, creature_name: str):
    # TODO: Implement the Helper function to mark the creature as moved
    creature = od.get(creature_name)
    creature_state = od.get_source(od.get_incoming(creature, "CreatureStateToCreature")[0])
    od.set_slot_value(creature_state, "moved", True)


def action_use_door(od: ODAPI, door: str):
    # TODO: Move the Hero to the connected Door
    current_door_item = od.get(door)
    to_door_item = od.get_target(od.get_outgoing(current_door_item, "DoorToDoor")[0])
    _, hero = od.get_all_instances("Hero")[0]
    level = od.get_source(od.get_incoming(to_door_item, "LevelToTile")[0])

    od.delete(od.get_outgoing(hero, "CreaturesTile")[0])
    od.create_link("H_T", "CreaturesTile", hero, to_door_item)
    mark_as_moved(od, od.get_name(hero))
    return [f"Going through door, you now entered level {od.get_name(level)}"]


def action_move_monster(od: ODAPI, monster: str, target_tile: str):
    # TODO: Move the monster to the target_tile
    monster_item = od.get(monster)
    target_item = od.get(target_tile)

    od.delete(od.get_outgoing(monster_item, "CreaturesTile")[0])
    od.create_link(f"{od.get_name(monster_item)}_{od.get_name(target_item)}", "CreaturesTile", monster_item, target_item)

def action_move_monster_random(od: ODAPI, monster_name: str):
    # Moves a monster to a random valid adjacent tile (Listening phase). No combat.
    monster_item = od.get(monster_name)
    current_tile = od.get_target(od.get_outgoing(monster_item, "CreaturesTile")[0])

    valid_targets = []
    for link in od.get_outgoing(current_tile, "TileToTile"):
        target_tile = od.get_target(link)
        if precondition_creature_can_move(od, od.get_name(target_tile)):
            valid_targets.append((link, target_tile))

    if not valid_targets:
        mark_as_moved(od, od.get_name(monster_item))
        return [f"{od.get_name(monster_item)} has no valid adjacent tiles to move."]

    link, chosen_tile = random.choice(valid_targets)
    try:
        direction = od.get_slot_value(link, "direction")
    except Exception:
        direction = "unknown"

    action_move_monster(od, od.get_name(monster_item), od.get_name(chosen_tile))
    mark_as_moved(od, od.get_name(monster_item))

    return [f"{od.get_name(monster_item)} moved {direction} to tile {od.get_name(chosen_tile)} ({od.get_type_name(chosen_tile)})"]



def action_move_hero(od: ODAPI, target_tile_name: str):
    # TODO: Handle a move of the Hero, incl. all side effects when stepping on special
    return_list = []

    _, hero = od.get_all_instances("Hero")[0]
    _, world_state = od.get_all_instances("WorldState")[0]
    target_tile = od.get(target_tile_name)

    #Check move
    if not precondition_creature_can_move(od, target_tile_name):
        return ["Hero cannot move to this tile"]

    #Move hero
    od.delete(od.get_outgoing(hero, "CreaturesTile")[0])
    od.create_link(f"{od.get_name(hero)}_{od.get_name(target_tile)}", "CreaturesTile", hero, target_tile)
    mark_as_moved(od, od.get_name(hero)) # Mark the Hero as already moved
    return_list.append(f"Moved hero {od.get_type_name(hero)} to tile {od.get_name(target_tile)} of type {od.get_type_name(target_tile)}")

    #execute actions for specific tile items
    match od.get_type_name(target_tile):
        case "StandardTile":
            #Move item into inventory
            if len(od.get_outgoing(target_tile, "StandardToTileItem")) > 0:
                tile_item = od.get_target(od.get_outgoing(target_tile, "StandardToTileItem")[0])
                od.delete(od.get_outgoing(target_tile, "StandardToTileItem")[0])
                od.create_link(f"{od.get_name(hero)}_{od.get_name(tile_item)}", "HeroCollectsItems", hero, tile_item)
                return_list.append(f"Captured  {od.get_type_name(tile_item)} from tile with name {od.get_name(tile_item)}")

                if od.get_type_name(tile_item) == "Objective":
                    print(od.get_slot_value(world_state, "collectedpoints"))
                    print(od.get_slot_value(tile_item, "points"))
                    od.set_slot_value(world_state, "collectedpoints",  od.get_slot_value(world_state, "collectedpoints") + od.get_slot_value(tile_item, "points"))
                    return_list.append("\n"f"Moved hero {od.get_type_name(hero)} to tile {od.get_name(target_tile)} of type {od.get_type_name(target_tile)}""\n")
        case "Trap":
            #remove a life
            od.set_slot_value(hero, "lives", od.get_slot_value(hero, "lives") - 1)
            return_list.append("\n"f"Hero step on a trap and lost a life, {od.get_slot_value(hero, 'lives')} remaining lives""\n")

    return return_list


def action_fight(od: ODAPI, hero_name: str, monster_name: str):
    # TODO: Determine the winner of the fight and adjust lives accordingly
    hero = od.get(hero_name)
    monster = od.get(monster_name)

    hero_lives = od.get_slot_value(hero, "lives")
    monster_lives = od.get_slot_value(monster, "lives")

    if hero_lives > monster_lives:
        od.set_slot_value(monster, "lives", monster_lives - 1)
        result = "\nHero won the fight :)"
    elif monster_lives > hero_lives:
        od.set_slot_value(hero, "lives", hero_lives - 1)
        result = "Monster won the fight :("
    else:
        result = "\nIt's a tie.\n"

    # Advance time
    _, clock = od.get_all_instances("Clock")[0]
    od.set_slot_value(clock, "time", od.get_slot_value(clock, "time") + 1)

    #reset creatures moved state
    for _, creature_state in od.get_all_instances("CreatureState"):
        od.set_slot_value(creature_state, "moved", False)

    return [
        result,
        f"Hero lives: {od.get_slot_value(hero, 'lives')}",
        f"Monster lives: {od.get_slot_value(monster, 'lives')}\n",
    ]


def action_advance_time(od: ODAPI):
    # Example for an action: This advances the time and resets all creatures
    _, clock = od.get_all_instances("Clock")[0]
    time = od.get_slot_value(clock, "time")
    new_time = time + 1
    od.set_slot_value(clock, "time", new_time)
    for _, creature_state in od.get_all_instances("CreatureState"):
        od.set_slot_value(creature_state, "moved", False)

    return [f"Time updated to {new_time}"]


def get_actions(od: ODAPI):
    """
        Retrieve the actions that are possible in the current state
    """
    # Dictionary mapping "Action text" to the (partial) function that is executed
    actions = {}

    # TODO: Determine the currently possible actions and add them to the actions dictionary

    # Hero info
    _, hero = od.get_all_instances("Hero")[0]
    currentTile = od.get_target(od.get_outgoing(hero, "CreaturesTile")[0])

    hero_state = od.get_source(od.get_incoming(hero, "CreatureStateToCreature")[0])
    hero_moved = od.get_slot_value(hero_state, "moved")

    # Hero movements
    if not hero_moved:
        possibleTileMoves = od.get_outgoing(currentTile, "TileToTile")
        for possible_move_tile_to_tile in possibleTileMoves:
            possible_move = od.get_target(possible_move_tile_to_tile)
            if precondition_creature_can_move(od, od.get_name(possible_move)):
                actions[f"Move {od.get_slot_value(possible_move_tile_to_tile, 'direction')} to tile type {od.get_type_name(possible_move)} {od.get_name(possible_move)}"] = partial(
                    action_move_hero, target_tile_name=od.get_name(possible_move)
                )

        if od.get_type_name(currentTile) == "Door" and precondition_can_use_door(od, od.get_name(currentTile)):
            actions["Open door"] = partial(action_use_door, door=od.get_name(currentTile))

        if len(actions) > 0:
            return make_actions_pure(actions.items(), od)

    # Listening for monsters
    hero_level = od.get_source(od.get_incoming(currentTile, "LevelToTile")[0])
    monster_to_move = None
    for _, monster in od.get_all_instances("Monster"):
        if od.get_slot_value(monster, "lives") > 0:
            monster_state = od.get_source(od.get_incoming(monster, "CreatureStateToCreature")[0])
            if od.get_slot_value(monster_state, "moved"):
                continue
            monster_tile = od.get_target(od.get_outgoing(monster, "CreaturesTile")[0])
            monster_level = od.get_source(od.get_incoming(monster_tile, "LevelToTile")[0])
            if monster_level == hero_level:
                monster_to_move = monster
                break

    if monster_to_move is not None:
        actions["Listening for monsters..."] = partial(
            action_move_monster_random,
            monster_name=od.get_name(monster_to_move)
        )
        return make_actions_pure(actions.items(), od)

    #fight after listening
    if precondition_fight_possible(od):
        _, hero = od.get_all_instances("Hero")[0]
        currentTile = od.get_target(od.get_outgoing(hero, "CreaturesTile")[0])

        same_tile_monster = None
        for _, monster in od.get_all_instances("Monster"):
            if od.get_slot_value(monster, "lives") <= 0:
                continue
            monster_tile = od.get_target(od.get_outgoing(monster, "CreaturesTile")[0])
            if monster_tile == currentTile:
                same_tile_monster = monster
                break

        if same_tile_monster is not None:
            actions["Fight!"] = partial(
                action_fight,
                hero_name=od.get_name(hero),
                monster_name=od.get_name(same_tile_monster)
            )
            return make_actions_pure(actions.items(), od)

    # If no other action is possible, add the (one and only) choice to advance time
    actions["Continue..."] = action_advance_time
    return make_actions_pure(actions.items(), od)




def make_actions_pure(actions, od):
    """
        Adjust the actions so they are executed on a cloned OD
    """
    # Copy model before modifying it
    def exec_pure(action_to_exec, original_od):
        cloned_rt_m = clone_od(original_od.state, original_od.m, original_od.mm)
        new_od = ODAPI(original_od.state, cloned_rt_m, original_od.mm)
        msgs = action_to_exec(new_od)
        return new_od, msgs

    for descr, action in actions:
        yield descr, partial(exec_pure, action, od)


def termination_condition(od: ODAPI):
    # TODO: implement the termination conditions, returning None means no termination condition is satisfied
    # Otherwise, return a string with the reason for termination
    hero_name, hero = od.get_all_instances("Hero")[0]
    if not precondition_creature_alive(od, hero_name):
        return "\nYou are out of lives :(\n"

    #All objectives are collected
    objective_count = False
    for item in od.get_outgoing(hero, "HeroCollectsItems"):
        objective_count += od.get_type_name(od.get_target(item)) == "Objective" #Add one to objective count if objective

    print("Objective counts", len(od.get_all_instances("Objective")), objective_count)
    if len(od.get_all_instances("Objective")) == objective_count:
        return "\nAll objectives found! :)\n"


    return None

