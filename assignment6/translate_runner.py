import os
import shutil

from bootstrap.scd import bootstrap_scd
from concrete_syntax.textual_od import parser, renderer
from state.devstate import DevState
from transformation.ramify import ramify
from transformation.rule import RuleMatcherRewriter
from util import loader

from models import rt_m_rpg_def

CWD = os.path.dirname(__file__)

state = DevState()
scd_mm = bootstrap_scd(state)

print("Loading merged MM")
with open(f"{CWD}/merged_mm.od") as mm_cs:
    merged_mm = loader.parse_and_check(state, mm_cs.read(), scd_mm, "RPG+PN MM", check_conformance=False)

print("Ramifying")
ramified_merged_mm = ramify(state, merged_mm)

rule_names = [
    "tile_translation",
    "adjacent_tile_translation",
    "hero_tile",
    "monster_tile",
    "key_place",
    "key_tile",
    "hero_collect_key",
    "hero_use_door",
    "move_order_states",
    "connect_move_hero_state",
    "connect_move_monster_state",
    "level",
    "monster_same_level",
    "hero_lives",
    "hero_must_be_alive_to_move",
    "trap_tile_lose_life"
]

print("Loading rules")
rules = loader.load_rules(state, lambda name, kind: f"{CWD}/translation/r_{name}_{kind}.od",
                          ramified_merged_mm, rule_names)
print("Loading initial model")
game_rt_initial = loader.parse_and_check(state, rt_m_rpg_def, merged_mm, "Initial Game", check_conformance=False)
match_rewriter = RuleMatcherRewriter(state, merged_mm, ramified_merged_mm)

print("### Start Transformation ###")
rt_model = game_rt_initial
for i, rule_name in enumerate(rule_names):
    snapshot = f"{CWD}/snapshots/snapshot_{rule_name}.od"
    print(f"Rule {rule_name}")
    rule = rules[rule_name]
    try:
        with open(snapshot, "r") as s:
            rt_model = parser.parse_od(state, s.read(), merged_mm)
        print("Skipped rule, snapshot found")
    except FileNotFoundError:
        while True:
            result = match_rewriter.exec_on_first_match(rt_model, rule, rule_name, in_place=True)
            if not result:
                print("No matches...")
                break
            else:
                rt_model, lhs_match, _ = result
                print(" Rewrote", lhs_match)
        txt = renderer.render_od(state, rt_model, merged_mm)
        with open(snapshot, "w") as s:
            s.write(txt)
            print("Wrote to snapshot")

shutil.copyfile(f"{CWD}/snapshots/snapshot_{rule_names.pop()}.od", f'{CWD}/snapshots/final.od')