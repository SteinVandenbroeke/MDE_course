from api.od import ODAPI
from bootstrap.scd import bootstrap_scd
from state.devstate import DevState
from util.loader import parse_and_check

from models import mm_rpg_def, m_rpg_def, rt_mm_rpg_def, rt_m_rpg_def
from simulator import RPGSimulator

from assignment4 import get_actions, termination_condition


def render_text(od: ODAPI):
    # TODO: Implement, so a short description of the current state is printed
    txt = ""
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
