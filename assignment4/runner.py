from api.od import ODAPI
from bootstrap.scd import bootstrap_scd
from state.devstate import DevState
from util.loader import parse_and_check

from models import mm_rpg_def, m_rpg_def, rt_mm_rpg_def, rt_m_rpg_def
from simulator import RPGSimulator

from assignment4 import get_actions, termination_condition


def render_text(od: ODAPI):
    # TODO: Implement, so a short description of the current state is printed

    # Hero info
    _, hero = od.get_all_instances("Hero")[0]
    currentTile = od.get_target(od.get_outgoing(hero, "CreaturesTile")[0])
    currentLevel = od.get_source(od.get_incoming(currentTile, "LevelToTile")[0])
    inventory = [f"{od.get_type_name(od.get_target(item))}: {od.get_name(od.get_target(item))}" for item in od.get_outgoing(hero, "HeroCollectsItems")]
    word = od.get_source(od.get_incoming(currentLevel, "WorldToLevel")[0])
    world_state = od.get_source(od.get_incoming(word, "WorldStateToWorld")[0])
    collected_points = od.get_slot_value(world_state, "collectedpoints")

    # Monsters info
    monsters_info = []
    for _, monster in od.get_all_instances("Monster"):
        monsterTile  = od.get_target(od.get_outgoing(monster, "CreaturesTile")[0])
        monsterLevel = od.get_source(od.get_incoming(monsterTile, "LevelToTile")[0])
        monsterLives = od.get_slot_value(monster, 'lives')
        monsters_info.append(
            f"{od.get_name(monster)} (Lives: {monsterLives}) -> "
            f"Tile {od.get_name(monsterTile)} | Level {od.get_name(monsterLevel)}"
        )

    monsters_text = "\n".join(monsters_info) if monsters_info else "    - None"

    txt = (
        "=== HERO STATUS ===\n"
        f"Location: {od.get_type_name(currentTile)} {od.get_name(currentTile)}\n"
        f"Lives: {od.get_slot_value(hero, 'lives')}\n"
        f"Inventory: {inventory}\n"
        f"Level: {od.get_name(currentLevel)}\n"
        f"Total collected points: {collected_points}\n"
        "====================\n\n"
        "=== MONSTERS STATUS ===\n"
        f"Monsters:\n{monsters_text}"
    )

    return txt


state = DevState()
scd_mm = bootstrap_scd(state)

# Static Models
rpg_mm = parse_and_check(state, mm_rpg_def, scd_mm, "MM for RPG")
rpg_m = parse_and_check(state, m_rpg_def, rpg_mm, "Model for RPG")
# Runtime Models
rt_rpg_mm = parse_and_check(state, rt_mm_rpg_def, scd_mm, "Runtime MM for RPG")
rt_rpg_m = parse_and_check(state, rt_m_rpg_def, rt_rpg_mm, "Runtime Model for RPG")

sim = RPGSimulator(
    action_generator=get_actions,
    termination_condition=termination_condition,
    renderer=render_text
)

rpg_od = ODAPI(state, rt_rpg_m, rt_rpg_mm)
sim.run(rpg_od)
