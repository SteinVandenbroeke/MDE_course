mm_classes = """
    ### Classes ###

    Course:Class {
        lower_cardinality = 1;
        upper_cardinality = 5;
        constraint = ```
            get_slot_value(this, "students") > 0
        ```;
    }

    Instructor:Class

    CourseType:Class {
        abstract = True;
    }
    
    Lab:Class
    :Inheritance (Lab -> CourseType)

    Lecture:Class
    :Inheritance (Lecture -> CourseType)

    Room:Class {
        abstract = True;
    }

    ComputerRoom:Class
    :Inheritance (ComputerRoom -> Room)

    Auditorium:Class
    :Inheritance (Auditorium -> Room)

    ### Attributes ###

    Course_coursename:AttributeLink (Course -> String) {
        name = "coursename";
        optional = False;
    }

    Course_students:AttributeLink (Course -> Integer) {
        name = "students";
        optional = False;
    }

    Room_seats:AttributeLink (Room -> String) {
        name = "seats";
        optional = False;
    }

    ### Associations ###

    courseinstructor:Association (Course -> Instructor) {
        target_lower_cardinality = 1;
        target_upper_cardinality = 2;
    }

    coursetype:Association (Course -> CourseType) {
        target_lower_cardinality = 1;
        target_upper_cardinality = 1;
    }

    courseroom:Association (Course -> Room) {
        target_lower_cardinality = 1;
        target_upper_cardinality = 1;
        source_upper_cardinality = 3;
    
        constraint = ```
            course = get_source(this)
            room = get_target(this)
            
            roomtype_valid = True
            # First fetch the roomtype and check if it is a ComputerRoom
            roomtype = get_type_name(room)
            if roomtype == "ComputerRoom":
                # Fetch the course type
                course_type = get_target(get_outgoing(course, "coursetype")[0])
                typename = get_type_name(course_type)
                roomtype_valid = typename == "Lab"

            enough_seats = get_slot_value(course, "students") <= get_slot_value(room, "seats")

            roomtype_valid and enough_seats                            
        ```;
    }

    ### Global Constraints ###

    totalStudentUnder200:GlobalConstraint {
        constraint = ```
            total_students = 0
            for _, course_id in get_all_instances("Course"):
                total_students += get_slot_value(course_id, "students")
            
            total_students <= 200
        ```;
    }
"""

m1 = """
    smith:Instructor
    meyer:Instructor

    labtype:Lab
    lecturetype:Lecture

    comproom:ComputerRoom {
        seats = 20;
    }
    auditorium1:Auditorium {
        seats = 50;
    }
    auditorium2:Auditorium {
        seats = 100;
    }

    programming1:Course {
        coursename = "Programming 1";
        students = 30;
    }
    :courseinstructor (programming1 -> smith)
    :coursetype (programming1 -> lecturetype)
    progroom:courseroom(programming1 -> auditorium1)

    programmingLab:Course {
        coursename = "Programming Lab";
        students = 10;
    }
    :courseinstructor (programmingLab -> smith)
    :courseinstructor (programmingLab -> meyer)
    :coursetype (programmingLab -> labtype)
    :courseroom(programmingLab -> comproom)

    stochastics:Course {
        coursename = "Stochastics";
        students = 60;
    }
    :courseinstructor (stochastics -> smith):courseinstructor (stochastics -> smith)
    :courseinstructor (stochastics -> meyer)
    :coursetype (stochastics -> lecturetype)
    stochroom:courseroom(stochastics -> auditorium2)

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
mm = parser.parse_od(state, m_text=mm_classes, mm=mmm)
print("Done")

print("Parsing Model")
m = parser.parse_od(state, m_text=m1, mm=mm)
print("Done")

print("Valid?")
conf = Conformance(state, m, mm)
print(render_conformance_check_result(conf.check_nominal()))

uml = plantuml.render_package("Courses Meta-model", plantuml.render_class_diagram(state, mm))
uml += plantuml.render_package("Courses Model", plantuml.render_object_diagram(state, m, mm)) 
uml += plantuml.render_trace_conformance(state, m, mm)
print(make_url(uml))