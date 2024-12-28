import requests
import psycopg2
from datetime import datetime
from utils import handle_tba, retrieve_list_from_pickle, save_list_to_pickle
from src.models import BaseDB, UCSCCourseDB


course_number_file_path = "./cached_course_numbers_ucsc_2025_winter.pkl"
base_url = "https://my.ucsc.edu/PSIGW/RESTListeningConnector/PSFT_CSPRD/SCX_CLASS_DETAIL.v1/2250"
instructor_base_url = "https://campusdirectory.ucsc.edu/api/uid"

# Define the table schema
table_name = "rumi_ucsc_class_schedule_2025_winter"

# Define the connection string (database)
connection_string = "host=127.0.0.1 port=15432 dbname=defaultdb user=doadmin password=AVNS_EOZHj-v6YwugeWM8P2m connect_timeout=10 sslmode=prefer"

# Read the list from the file
cached_course_numbers = retrieve_list_from_pickle(course_number_file_path)


def get_course_info(course_number):
    resp = requests.get(f"{base_url}/{course_number}")
    if resp.status_code == 200:
        data = resp.json()
        return parse_course(data)
    return None


# Parse the JSON data to create a Course instance
def parse_course(json_data):
    primary_section = json_data.get("primary_section", {})
    meetings = json_data.get("meetings", [])
    first_meeting = meetings[0] if meetings else None
    secondary_sections = json_data.get("secondary_sections", [])
    notes = json_data.get("notes", [])

    # Extract instructor name from the first meeting
    instructor_name = None
    if meetings:
        instructors = meetings[0].get("instructors", [])
        if instructors and instructors[0].get("cruzid"):
            instructor_id = instructors[0].get("cruzid")
            instructor_resp = requests.get(f"{instructor_base_url}/{instructor_id}")
            data = instructor_resp.json()
            instructor_name = data.get("givenname", [])[0] + " " + data.get("sn", [])[0]
        else:
            instructor_name = None  # Null if no cruzid

    # Create the Course object
    course = Course(
        id=primary_section.get("class_nbr"),
        subject=primary_section.get("subject"),
        number=primary_section.get("catalog_nbr"),
        display_name=primary_section.get("title_long"),
        instruction_mode=primary_section.get("component"),
        academic_group=primary_section.get("acad_career"),
        start_date=primary_section.get("start_date"),
        end_date=primary_section.get("end_date"),
        status=primary_section.get("enrl_status"),
        enrolled_count=int(primary_section.get("enrl_total", 0)),
        max_enroll=int(primary_section.get("capacity", 0)),
        waitlisted_count=int(primary_section.get("waitlist_total", 0)),
        max_waitlist=int(primary_section.get("waitlist_capacity", 0)),
        description=primary_section.get("description"),
        instructor_name=instructor_name,
        course_name=primary_section.get("title"),
        term=primary_section.get("strm"),
        days=handle_tba(first_meeting.get("days"), "text") if first_meeting else None,
        start_time=handle_tba(first_meeting.get("start_time"), "time") if first_meeting else None,
        end_time=handle_tba(first_meeting.get("end_time"), "time") if first_meeting else None,
        units=primary_section.get("credits"),
        created_at=datetime.now(),
    )

    return course


ucsc_data = []

if cached_course_numbers:
    for course_number in cached_course_numbers:
        course = get_course_info(course_number)
        if course:
            print(course.to_dict())
            ucsc_data.append(course)
else:
    for course_number in range(30000, 40000):
        course = get_course_info(course_number)
        if course:
            print(course.to_dict())
            cached_course_numbers.append(course_number)
            ucsc_data.append(course)
        else:
            print(course_number)

    save_list_to_pickle(course_number_file_path, cached_course_numbers)


# Establish the connection
conn = psycopg2.connect(connection_string)
cursor = conn.cursor()
print("Connected to the database successfully.")

drop_table_query = f"DROP TABLE IF EXISTS {table_name};"

create_table_query = f"""
CREATE TABLE {table_name} (
    id TEXT PRIMARY KEY,
    subject TEXT,
    number TEXT,
    source_url TEXT,
    display_name TEXT,
    instruction_mode TEXT,
    academic_group TEXT,
    start_date DATE,
    end_date DATE,
    status TEXT,
    enrolled_count INTEGER,
    max_enroll INTEGER,
    waitlisted_count INTEGER,
    max_waitlist INTEGER,
    description TEXT,
    instructor_name TEXT,
    course_name TEXT,
    term TEXT,
    days TEXT,
    start_time TIME,
    end_time TIME,
    units INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id INTEGER,
    name_vector VECTOR DEFAULT NULL,
    search_vector TSVECTOR DEFAULT NULL
);
"""

# Execute the queries
try:
    cursor.execute(drop_table_query)
    cursor.execute(create_table_query)
    conn.commit()
    print(f"Table '{table_name}' created successfully.")
except Exception as e:
    conn.rollback()
    print(f"Error creating table: {e}")

# Define the insert query
insert_query = f"""
INSERT INTO {table_name} (
    id, subject, number, source_url, display_name, instruction_mode, academic_group, start_date, end_date,
    status, enrolled_count, max_enroll, waitlisted_count, max_waitlist, description,
    instructor_name, course_name, term, days, start_time, end_time, units, created_at, tenant_id
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0
);
"""


# Function to insert course data into the database
def insert_course_to_db(course):
    source_url = f"https://literature.ucsc.edu/courses/?d={course.subject}&t=2250"
    try:
        cursor.execute(insert_query, (
            course.id, course.subject, course.number, source_url, course.display_name, course.instruction_mode, course.academic_group,
            course.start_date, course.end_date, course.status, course.enrolled_count, course.max_enroll,
            course.waitlisted_count, course.max_waitlist, course.description, course.instructor_name,
            course.course_name, course.term, course.days, course.start_time, course.end_time, course.units, course.created_at
        ))
        conn.commit()
        print(f"Inserted course with ID: {course.id}")
    except Exception as e:
        conn.rollback()
        print(f"Error inserting course with ID {course.id}: {e}")


# Example usage
for course in ucsc_data:
    insert_course_to_db(course)



