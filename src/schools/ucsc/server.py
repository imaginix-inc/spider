from .utils import handle_tba, retrieve_list_from_pickle, save_list_to_pickle
from src.models import BaseDB, UCSCCourseDB
import requests
import aiohttp
import asyncio
from tqdm.asyncio import tqdm
from typing import List
from src.process import post_process

class Course:
    def __init__(self, id, subject, number, display_name, instruction_mode, academic_group, start_date, end_date,
                 status, enrolled_count, max_enroll, waitlisted_count, max_waitlist, description, instructor_name,
                 course_name, term, days, start_time, end_time, units):
        self.id = id
        self.subject = subject
        self.number = number
        self.display_name = display_name
        self.instruction_mode = instruction_mode
        self.academic_group = academic_group
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.enrolled_count = enrolled_count
        self.max_enroll = max_enroll
        self.waitlisted_count = waitlisted_count
        self.max_waitlist = max_waitlist
        self.description = description
        self.instructor_name = instructor_name
        self.course_name = course_name
        self.term = term
        self.days = days
        self.start_time = start_time
        self.end_time = end_time
        self.units = units

    def to_dict(self):
        """Convert the course object to a dictionary."""
        return self.__dict__


course_number_file_path = "./cached_course_numbers_ucsc_2025_winter.pkl"
base_url = "https://my.ucsc.edu/PSIGW/RESTListeningConnector/PSFT_CSPRD/SCX_CLASS_DETAIL.v1/2250"
instructor_base_url = "https://campusdirectory.ucsc.edu/api/uid"

# Define the table schema
table_name = "rumi_ucsc_class_schedule_2025_winter"

# Define the connection string (database)
connection_string = "host=127.0.0.1 port=15432 dbname=defaultdb user=doadmin password=AVNS_EOZHj-v6YwugeWM8P2m connect_timeout=10 sslmode=prefer"

# Read the list from the file
cached_course_numbers = retrieve_list_from_pickle(course_number_file_path)

# Asynchronous wrapper for get_course_info
async def get_course_info(course_number, semaphore=None):
    if semaphore:
        async with semaphore:
            return await fetch_course(course_number)
    else:
        return await fetch_course(course_number)


# Helper function for fetching course data
async def fetch_course(course_number):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/{course_number}") as resp:
            if resp.status == 200:
                data = await resp.json()
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
    )

    return course

def map_course_to_db(course: Course) -> UCSCCourseDB:
    return UCSCCourseDB(id=course.id, source_url=f"https://literature.ucsc.edu/courses/?d={course.subject}&t=2250",
                        remark=course.description, instructor_name=course.instructor_name, subject=course.subject,
                        number=course.number, display_name=course.display_name, instruction_mode=course.instruction_mode,
                        academic_group=course.academic_group, start_date=course.start_date, end_date=course.end_date,
                        status=course.status, enrolled_count=course.enrolled_count, max_enroll=course.max_enroll,
                        waitlist_count=course.waitlisted_count, max_waitlist=course.max_waitlist, course_name=course.course_name,
                        term=course.term, days=course.days, start_time=course.start_time, end_time=course.end_time, units=course.units)


# Asynchronous main function with tqdm and optional semaphore
async def main() -> List[BaseDB]:
    ucsc_data = []
    tasks = []
    cached = not not cached_course_numbers
    semaphore = asyncio.Semaphore(5)  # Limit concurrency to 5 requests

    # Create tasks for cached or range of course numbers
    course_numbers = cached_course_numbers if cached else range(30000, 34000)
    for course_number in course_numbers:
        tasks.append(get_course_info(course_number, semaphore))

    new_cached_course_numbers = []

    # Use tqdm for progress tracking
    for result in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Fetching courses for UCSC"):
        course = await result
        if course:
            ucsc_data.append(course)
            if not cached:
                new_cached_course_numbers.append(course.id)

    all_course_data = []
    for course in ucsc_data:
        all_course_data.append(map_course_to_db(course))
    all_course_data = await post_process(all_course_data, [course.course_name for course in ucsc_data], [course.course_name for course in ucsc_data])

    if not cached:
        save_list_to_pickle(course_number_file_path, new_cached_course_numbers)
    return all_course_data
