from concrete_syntax.textual_od.parser import parse_od
from transformation.matcher import match_od
from transformation.ramify import ramify
from transformation.rule import RuleMatcherRewriter, PriorityActionGenerator
from util.loader import load_rules
import os.path


def get_filename(name, kind):
    file_dir = os.path.dirname(__file__)
    return f"{file_dir}/rules/r_{name}_{kind}.od"


def get_rules(current_state, rt_mm):
    print("Loading rules")
    rt_mm_ramified = ramify(current_state, rt_mm)
    matcher_rewriter = RuleMatcherRewriter(current_state, rt_mm, rt_mm_ramified)

    # TODO: Load other rules grouped by priority, add to action generator in order of priority
    # Start with rules_0 = ...
    # This rule should come last!
    rules_x = load_rules(current_state, get_filename, rt_mm_ramified,
                         ['advance_time'])
    
    rules_monster_move = load_rules(current_state, get_filename, rt_mm_ramified,
                                 ['monster_move'])

    fight_hero_wins = load_rules(current_state, get_filename, rt_mm_ramified,
                                 ['hero_wins'])
    
    fight_monster_wins = load_rules(current_state, get_filename, rt_mm_ramified,
                                 ['monster_wins'])

    rules_hero_move = load_rules(current_state, get_filename, rt_mm_ramified,
                         ['hero_move_to_standard_tile_no_item', 'hero_move_to_standard_tile_with_item', 'hero_move_to_trap_tile', "hero_move_to_door_tile", "move_through_door"])

    reset_hero_move = load_rules(current_state, get_filename, rt_mm_ramified,
                         ['reset_hero_move_TODO'])

    #return PriorityActionGenerator(matcher_rewriter, [rules_monster_move, rules_hero_move, reset_hero_move])
    return PriorityActionGenerator(matcher_rewriter, [rules_monster_move, fight_hero_wins, fight_monster_wins, rules_hero_move, reset_hero_move])


class TerminationCondition:
    def __init__(self, state, rt_mm):
        self.state = state
        self.rt_mm_ramified = ramify(state, rt_mm)

        # Dict in the format "cause": "pattern"
        patterns_cs = {
            # TODO: Put the patterns for your termination conditions here
        }

        self.patterns = {cause: parse_od(state, pattern_cs, self.rt_mm_ramified)
                         for cause, pattern_cs in patterns_cs.items()}

    def __call__(self, od):
        for cause in self.patterns:
            for match in match_od(self.state, od.m, od.mm, self.patterns[cause], self.rt_mm_ramified):
                # stop after the first match (no need to look for more matches):
                return cause
