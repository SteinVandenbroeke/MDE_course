m_rpg_def_mini = """
    W:World

    H:Hero{ lives = 3; }
    M:Monster{ lives = 2; }

    L:Level{ name = "L"; }

    W_L:WorldToLevel (W -> L)

    T1:StandardTile
    T2:StandardTile
    T3:StandardTile

    L_T1:LevelToTile (L -> T1)
    L_T2:LevelToTile (L -> T2)
    L_T3:LevelToTile (L -> T3)

    T1_T3:TileToTile (T1 -> T3){ direction = "right"; }
    T2_T3:TileToTile (T2 -> T3){ direction = "left"; }

    H_T:CreaturesTile (H -> T1)
    M_T:CreaturesTile (M -> T2)
"""

rt_m_rpg_def_mini = m_rpg_def_mini + """
    C:Clock { time = 0; }

    WS:WorldState{ collectedpoints = 0; }
    WS_W:WorldStateToWorld (WS -> W)

    CSH:CreatureState { moved = False; }
    CS_H:CreatureStateToCreature (CSH -> H)

    CSM:CreatureState { moved = False; }
    CS_M:CreatureStateToCreature (CSM -> M)
"""
