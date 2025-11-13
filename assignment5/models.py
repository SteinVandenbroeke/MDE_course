# TODO: add your meta-model
mm_rpg_def = """
    ### Classes ###
    Creatures:Class {
        abstract=True;
        constraint = ```
            get_slot_value(this, "lives") >= 0
        ```;
    }
    
    Creatures_lives:AttributeLink (Creatures -> Integer) {
        name = "lives";
        optional = False;
    }
    
    Hero:Class {
        lower_cardinality = 1;
        upper_cardinality = 1;
    }
    :Inheritance (Hero -> Creatures)
    
    Monster:Class
    :Inheritance (Monster -> Creatures)
    
    Level:Class
    
    Level_name:AttributeLink (Level -> String) {
        name = "name";
        optional = False;
    }
    
    World:Class{
        lower_cardinality = 1;
        upper_cardinality = 1;
    }
    
    Tile:Class{
        abstract=True;
        constraint = ```
            no_dubble_directions = True
            items = set()
            for tileItem in get_incoming(this, "TileToTile"):
                if get_slot_value(tileItem, "direction") in items:
                    no_dubble_directions = False;
                items.add(get_slot_value(tileItem, "direction"))
            no_dubble_directions
        ```;
    }
    
    StandardTile:Class
    :Inheritance (StandardTile -> Tile)
    
    Door:Class
    :Inheritance (Door -> Tile)
    
    Trap:Class
    :Inheritance (Trap -> Tile)
    
    Obstacle:Class
    :Inheritance (Obstacle -> Tile)
    
    Item:Class{
        abstract=True;
    }
    
    Key:Class {
        constraint = ```
            len(get_incoming(this, "DoorToKey")) == 1
        ```;
    }
    :Inheritance (Key -> Item)
    
    Objective:Class {
        constraint = ```
            get_slot_value(this, "points") <= 100
        ```;
    }
    :Inheritance (Objective -> Item)
    
    Objective_points:AttributeLink (Objective -> Integer) {
        name = "points";
        optional = False;
    }
    
    ### Attributes ###
    
    CreaturesTile:Association (Creatures -> Tile) {
        target_lower_cardinality = 1;
        target_upper_cardinality = 1;
    }
    
    WorldToLevel:Association (World -> Level) {
        target_lower_cardinality = 1;
    }
    
    LevelToTile:Association (Level -> Tile) {
        target_lower_cardinality = 1;
        source_upper_cardinality = 1;
    }
    
    TileToTile:Association (Tile -> Tile) {
        target_upper_cardinality = 4;
        constraint = ```
            tile0 = get_source(this)
            tile1 = get_target(this)
            
            get_source(get_incoming(tile0, "LevelToTile")[0]) == get_source(get_incoming(tile1, "LevelToTile")[0])
        ```;
    }
    
    TileToTile_direction:AttributeLink (TileToTile -> String) {
        name = "direction";
        optional = False;
    }
    
    StandardToTileItem:Association (StandardTile -> Item) {
        target_lower_cardinality = 0;
        target_upper_cardinality = 1;
    }
    
    DoorToKey:Association (Door -> Key) {
        target_lower_cardinality = 1;
        target_upper_cardinality = 1;
        source_lower_cardinality = 1;
        source_upper_cardinality = 1;
    }
    
    DoorToDoor:Association (Door -> Door){
        target_lower_cardinality = 1;
        target_upper_cardinality = 1;
        
        constraint = ```
            door0 = get_source(this)
            door1 = get_target(this)
            
            DoorLevel0 = get_incoming(door0, "LevelToTile")[0]
            DoorLevel1 = get_incoming(door1, "LevelToTile")[0]
            DoorLevel0 != DoorLevel1
            ```;
    }
    
    
    ### Global Constraints ###


    AllObjectivesPointsUnder100:GlobalConstraint {
        constraint = ```
            total_amount_of_objective_points = 0
            for _, objective in get_all_instances("Objective"):
                total_amount_of_objective_points += get_slot_value(objective, "points")
            
            total_amount_of_objective_points <= 100
        ```;
    }
    
    AtMostOneMonsterPerLevel:GlobalConstraint {
        constraint = ```
            valid_constraint = True
            monster_levels = []
            for _, monster in get_all_instances("Monster"):
                monster_level = get_name(get_source(get_incoming(get_target(get_outgoing(monster, "CreaturesTile")[0]), "LevelToTile")[0]))
                if monster_level in monster_levels:
                    valid_constraint = False
                    break
                monster_levels.append(monster_level)
            
            valid_constraint
        ```;
    }
"""

# TODO: add your runtime-meta-model
rt_mm_rpg_def = mm_rpg_def + """
    Clock:Class {
        lower_cardinality = 1;
        upper_cardinality = 1;
    }
    
    Clock_time:AttributeLink (Clock -> Integer) {
        name = "time";
        optional = False;
    }
    
    State:Class {
        abstract = True;
    }
    
    WorldState:Class
    :Inheritance (WorldState -> State)
    
    WorldState_collectedpoints:AttributeLink (WorldState -> Integer) {
        name = "collectedpoints";
        optional = False;
    }
    
    CreatureState:Class
    :Inheritance (CreatureState -> State)
    
    CreatureState_moved:AttributeLink (CreatureState -> Boolean) {
        name = "moved";
        optional = False;
    }
    
    
    
    # Associations
    WorldStateToWorld:Association (WorldState -> World) {
        target_lower_cardinality = 1;
        target_upper_cardinality = 1;
    }
    
    CreatureStateToCreature:Association (CreatureState -> Creatures) {
        target_lower_cardinality = 1;
        target_upper_cardinality = 1;
    }
    
    HeroCollectsItems:Association (Hero -> Item)
    
    
    NoCreatureOnObstacle:GlobalConstraint {
        constraint = ```
            valid_constraint = True
            for _, monster in get_all_instances("Monster"):
                monster_tile_type = get_type_name(get_target(get_outgoing(monster, "CreaturesTile")[0]))
                valid_constraint = monster_tile_type != "Obstacle" and valid_constraint
            valid_constraint
        ```;
    }
"""

# TODO: add a valid instance of your meta-model
m_rpg_def = """
    W:World
    
    
    H:Hero{
        lives = 10;
    }
    
    M:Monster{
        lives = 3;
    }
    
    M2:Monster{
        lives = 10;
    }
    
    L1:Level{
        name = "level1";
    }
    
    L2:Level{
        name = "level2";
    }
    
    W_L1:WorldToLevel (W -> L1)
    W_L2:WorldToLevel (W -> L2)
    
    # Level 1: Start tile is T2
    
    # T1 T2 T3
    #    T5 D0

   T1:Trap
   T2:StandardTile
   T3:StandardTile
   T4:Obstacle
   T5:StandardTile
   D0:Door
   D1:Door

   D0_D1:DoorToDoor (D0 -> D1)
   D0_D2:DoorToDoor (D1 -> D0)
   
   L1_T1:LevelToTile (L1 -> T1)
   L1_T2:LevelToTile (L1 -> T2)
   L1_T3:LevelToTile (L1 -> T3)
   L1_T4:LevelToTile (L1 -> T4)
   L1_T5:LevelToTile (L1 -> T5)
   L1_D0:LevelToTile (L1 -> D0)
   
   T1_T2:TileToTile (T1 -> T2){
    direction = "right";
   }
   T2_T1:TileToTile (T2 -> T1){
    direction = "left";
   }
   
   T1_T4:TileToTile (T1 -> T4){
    direction = "down";
   }
   T4_T1:TileToTile (T4 -> T1){
    direction = "up";
   }
   
   T2_T5:TileToTile (T2 -> T5){
    direction = "down";
   }
   T5_T2:TileToTile (T5 -> T2){
    direction = "up";
   }
   
   T2_T3:TileToTile (T2 -> T3){
    direction = "right";
   }
   T3_T2:TileToTile (T3 -> T2){
    direction = "left";
   }
   
   T3_D0:TileToTile (T3 -> D0){
    direction = "down";
   }
   D0_T3:TileToTile (D0 -> T3){
    direction = "up";
   }


   T5_D0:TileToTile (T5 -> D0){
    direction = "right";
   }
   D0_T5:TileToTile (D0 -> T5){
    direction = "left";
   }


   T6:StandardTile
   T7:StandardTile
   T8:StandardTile
   
   L2_T6:LevelToTile (L2 -> T6)
   L2_T7:LevelToTile (L2 -> T7)
   L2_T8:LevelToTile (L2 -> T8)
   L2_D1:LevelToTile (L2 -> D1)

   
   H_T0:CreaturesTile (H -> T2)
   M_T0:CreaturesTile (M -> T3)
   M2_T0:CreaturesTile (M2 -> T6)

   K0:Key
   K1:Key
   T2_K0:StandardToTileItem (T3 -> K0)
   T3_K1:StandardToTileItem (T7 -> K1)
   D0_K0:DoorToKey (D0 -> K0)
   D1_K1:DoorToKey (D1 -> K1)
   
   O1:Objective{
        points = 50;
   }
   
   
   T5_O1:StandardToTileItem (T5 -> O1)
"""

nonconform_m = """
    W:World

    H:Hero{
        lives = 10;
    }

    L1:Level{
        name = "level1";
    }

    L2:Level{
        name = "level2";
    }

    W_L1:WorldToLevel (W -> L1)
    W_L2:WorldToLevel (W -> L2)

    T1:Trap
    T2:StandardTile
    T3:StandardTile
    T4:Obstacle
    
    T1_T2:TileToTile (T1 -> T2){
        direction = "right";
    }
    
    T3_T2:TileToTile (T3 -> T2){
        direction = "right";
    }
    
    D0:Door
    D1:Door

    D0_D1:DoorToDoor (D0 -> D1)
    D1_D0:DoorToDoor (D1 -> D0)

    L1_T1:LevelToTile (L1 -> T1)
    L1_T2:LevelToTile (L1 -> T2)
    L1_T3:LevelToTile (L1 -> T3)
    L1_T4:LevelToTile (L1 -> T4)
    L1_D0:LevelToTile (L1 -> D0)
    L1_D1:LevelToTile (L1 -> D1)

    L2_T1:LevelToTile (L2 -> T1)
    L2_T2:LevelToTile (L2 -> T2)
    L2_T3:LevelToTile (L2 -> T3)
    L2_T4:LevelToTile (L2 -> T4)

    H_T0:CreaturesTile (H -> T1)
    H_T1:CreaturesTile (H -> T2)

    K:Key
    T2_K:StandardToTileItem (T2 -> K)
    D0_K:DoorToKey (D0 -> K)
    D1_K:DoorToKey (D1 -> K)

    O1:Objective{
        points = 60;
    }
"""

# TODO: add a valid instance of the additional runtime-information
rt_m_rpg_def = m_rpg_def + """
    C:Clock {
        time = 0;
    }
    
    WS:WorldState{
        collectedpoints = 0;
    }
    
    WS_W:WorldStateToWorld (WS -> W)
    
    CSH:CreatureState {
        moved = False;
    }
    
    CS_H:CreatureStateToCreature (CSH -> H)
    
    CSM:CreatureState {
        moved = False;
    }
    
    CS_M:CreatureStateToCreature (CSM -> M)
    
    CSM2:CreatureState {
        moved = False;
    }
    
    S_M2:CreatureStateToCreature (CSM2 -> M2)
    
"""
