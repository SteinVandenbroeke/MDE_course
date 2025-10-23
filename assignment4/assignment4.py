import random
from functools import partial
from api.od import ODAPI
from transformation.cloner import clone_od


def precondition_creature_alive(od: ODAPI, creature: str):
    # Example for a pre-condition
    return od.get_slot_value(od.get(creature), "lives") > 0


def precondition_can_use_door(od: ODAPI, door: str):
    # TODO: Check whether the door can be used by the Hero: Do they have the matching Key?
    raise NotImplementedError


def precondition_creature_can_move(od: ODAPI, target_tile: str):
    # TODO: Check whether the target_tile can be occupied by a creature, i.e. it's not an Obstacle
    raise NotImplementedError


def precondition_fight_possible(od: ODAPI):
    # TODO: Check whether two creatures are on the same Tile so fighting is possible in the current state
    raise NotImplementedError


def mark_as_moved(od: ODAPI, creature_name: str):
    # TODO: Implement the Helper function to mark the creature as moved
    raise NotImplementedError


def action_use_door(od: ODAPI, door: str):
    # TODO: Move the Hero to the connected Door
    raise NotImplementedError


def action_move_monster(od: ODAPI, monster: str, target_tile: str):
    # TODO: Move the monster to the target_tile
    raise NotImplementedError


def action_move_hero(od: ODAPI, target_tile_name: str):
    # TODO: Handle a move of the Hero, incl. all side effects when stepping on special Tiles
    raise NotImplementedError


def action_fight(od: ODAPI, hero_name: str, monster_name: str):
    # TODO: Determine the winner of the fight and adjust lives accordingly
    raise NotImplementedError


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

    # If no other action is possible, add the (one and only) choice to advance time
    if len(actions) == 0:
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

    return None
