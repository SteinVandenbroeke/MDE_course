mm_rgp = """
    ### Classes ###
    Hero:Class {
        lower_cardinality = 1;
        upper_cardinality = 1;
        constraint = ```
            get_slot_value(this, "lives") >= 0
        ```;
    }
    
    Hero_lives:AttributeLink (Hero -> Integer) {
        name = "lives";
        optional = False;
    }
    
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
    
    HeroTile:Association (Hero -> Tile) {
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
"""

comform_m = """
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
   D0:Door
   D1:Door

   D0_D1:DoorToDoor (D0 -> D1)
   D0_D2:DoorToDoor (D1 -> D0)

   L1_T1:LevelToTile (L1 -> T1)
   L1_T2:LevelToTile (L1 -> T2)
   L1_T3:LevelToTile (L1 -> T3)
   L1_T4:LevelToTile (L1 -> T4)
   L1_T5:LevelToTile (L1 -> D0)
   
   T1_T2:TileToTile (T1 -> T2){
    direction = "up";
   }

   T5:StandardTile
   T6:StandardTile
   T7:StandardTile
   
   L2_T5:LevelToTile (L2 -> T5)
   L2_T6:LevelToTile (L2 -> T6)
   L2_T7:LevelToTile (L2 -> T7)
   L2_D1:LevelToTile (L2 -> D1)
   
   T5_T6:TileToTile (T5 -> T6){
    direction = "up";
   }
   
   T6_T5:TileToTile (T6 -> T5){
    direction = "down";
   }
   
   T5_T7:TileToTile (T5 -> T7){
    direction = "left";
   }
   
   T7_T5:TileToTile (T7 -> T5){
    direction = "right";
   }
   
   H_T0:HeroTile (H -> T1)

   K0:Key
   K1:Key
   T2_K0:StandardToTileItem (T2 -> K0)
   T3_K1:StandardToTileItem (T3 -> K1)
   D0_K0:DoorToKey (D0 -> K0)
   D1_K1:DoorToKey (D1 -> K1)
   
   O1:Objective{
        points = 50;
   }
   
   
   O2:Objective{
        points = 50;
   }
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

    H_T0:HeroTile (H -> T1)
    H_T1:HeroTile (H -> T2)

    K:Key
    T2_K:StandardToTileItem (T2 -> K)
    D0_K:DoorToKey (D0 -> K)
    D1_K:DoorToKey (D1 -> K)

    O1:Objective{
        points = 60;
    }

    O2:Objective{
        points = 60;
    }
"""



from state.devstate import DevState
from bootstrap.scd import bootstrap_scd
from concrete_syntax.textual_od import parser
from framework.conformance import Conformance, render_conformance_check_result
from concrete_syntax.plantuml import renderer as plantuml
from concrete_syntax.plantuml.make_url import make_url


state = DevState()
print("Load SCD")
mmm = bootstrap_scd(state)
print("Done")

print("Parsing MM")
mm = parser.parse_od(state, m_text=mm_rgp, mm=mmm)
print("Done")

print("Parsing Model (Conforming model)")
m = parser.parse_od(state, m_text=comform_m, mm=mm)
print("Done")

print("Parsing Model (Non-conforming model)")
non_m = parser.parse_od(state, m_text=nonconform_m, mm=mm)
print("Done")

print("Valid? (Conforming model)")
conf = Conformance(state, m, mm)
print(render_conformance_check_result(conf.check_nominal()))

print("Valid? (Non-conforming model)")
conf_2 = Conformance(state, non_m, mm)
print(render_conformance_check_result(conf_2.check_nominal()))

uml = plantuml.render_package("Courses Meta-model", plantuml.render_class_diagram(state, mm))
uml += plantuml.render_package("Courses Model", plantuml.render_object_diagram(state, m, mm))
uml += plantuml.render_trace_conformance(state, m, mm)
print("UML (Conforming):")
print(make_url(uml))

uml_2 = plantuml.render_package("Courses Meta-model", plantuml.render_class_diagram(state, mm))
uml_2 += plantuml.render_package("Courses Model", plantuml.render_object_diagram(state, non_m, mm))
uml_2 += plantuml.render_trace_conformance(state, non_m, mm)
print("UML (Non-conforming):")
print(make_url(uml_2))