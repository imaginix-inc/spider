import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import  List
from src.models import BaseDB, UCSDCourseDB

departments = ["AIP", "AAS", "AWP", "ANES", "ANTH", "AAPI", "ASTR", "AUDL", "BENG", "BIOL", "BIOM", "CMM", "CHEM",
               "CHIN", "CLAS", "CCS", "CLPH", "CLIN", "CLRE", "COGS", "COMM", "CSS", "CSE", "CCE", "CGS", "CAT", "DSC",
               "DERM", "DOC", "DDPM", "ECON", "EDS", "ERC", "ECE", "EMED", "ENVR", "ESYS", "ETHN", "FMPH", "FPM",
               "FILM", "GLBH", "GPS", "GSS", "HIST", "SPH", "HDS", "HUM", "INTL", "JAPN", "JWSP", "LATI", "LAWS",
               "LING", "LIT", "MMW", "MBC", "MATS", "MSED", "MATH", "MAE", "MED", "MCWP", "MUS", "NENG", "NEU", "OBG",
               "OPTH", "ORTH", "PAEP", "PATH", "PEDS", "PHAR", "PHIL", "PHYS", "POLI", "PSY", "PSYC", "RMAS", "RAD",
               "RSM", "RELI", "RMED", "REV", "SOMI", "SOE", "SOMC", "SIO", "SEV", "SOC", "SE", "SURG", "SYN", "THEA",
               "TMC", "UNAF", "USP", "UROL", "VIS", "WCWP", "WES"]


async def get_courses_by_department(department: str, YearTerm="WI25") -> List[UCSDCourseDB]:
    """Get all courses for a given department and term."""
    url = "https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudentResult.htm"
    
    payload = {
        "selectedTerm": YearTerm,
        "xsoc_term": "",
        "loggedIn": "false",
        "tabNum": "tabs-dept",
        "_selectedSubjects": "1",
        "schedOption1": "true",
        "_schedOption1": "on",
        "_schedOption11": "on",
        "_schedOption12": "on",
        "schedOption2": "true",
        "_schedOption2": "on",
        "_schedOption4": "on",
        "_schedOption5": "on",
        "_schedOption3": "on",
        "_schedOption7": "on",
        "_schedOption8": "on",
        "_schedOption13": "on",
        "_schedOption10": "on",
        "_schedOption9": "on",
        "schDay": ["M", "T", "W", "R", "F", "S"],
        "_schDay": "on",
        "schStartTime": "12:00",
        "schStartAmPm": "0",
        "schEndTime": "12:00", 
        "schEndAmPm": "0",
        "selectedDepartments": department,
        "_selectedDepartments": "1",
        "schedOption1Dept": "true",
        "_schedOption1Dept": "on",
        "_schedOption11Dept": "on",
        "_schedOption12Dept": "on",
        "schedOption2Dept": "true",
        "_schedOption2Dept": "on",
        "_schedOption4Dept": "on",
        "_schedOption5Dept": "on",
        "_schedOption3Dept": "on",
        "_schedOption7Dept": "on",
        "_schedOption8Dept": "on",
        "_schedOption13Dept": "on",
        "_schedOption10Dept": "on",
        "_schedOption9Dept": "on",
        "schDayDept": ["M", "T", "W", "R", "F", "S"],
        "_schDayDept": "on",
        "schStartTimeDept": "12:00",
        "schStartAmPmDept": "0", 
        "schEndTimeDept": "12:00",
        "schEndAmPmDept": "0",
        "courses": "",
        "sections": "",
        "instructorType": "begin",
        "instructor": "",
        "titleType": "contain",
        "title": "",
        "_hideFullSec": "on",
        "_showPopup": "on"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data=payload)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            courses = []
            tables = soup.find_all('table', class_='tbrdr')
            
            current_course_number = None
            current_course_title = None
            current_units = None
            current_restriction_codes = None
            
            for table in tables:
                # Find course headers first
                items = table.find_all('tr')
                for item in items:
                    tds = item.find_all('td')
                    if len(tds) >= 3 and 'class' in tds[0].attrs and tds[0]['class'] == ['crsheader']:
                        # Parse course header
                        header_link = tds[2].find('a')
                        # Convert restriction codes string to list and remove empty strings
                        spans = tds[0].find_all('span')
                        current_restriction_codes = [span.text.strip() for span in spans if span.text.strip()]
                        current_course_number = tds[1].text.strip()
                        if header_link:
                            current_course_title = header_link.find('span', class_='boldtxt').text.strip()
                            # Extract units from the text after the span
                            current_units = header_link.next_sibling
                        # print(f'course info: {current_course_number} - {current_course_title} - {current_units}')
                    elif len(tds) >= 12 and 'class' in item.attrs and 'sectxt' in item['class']:
                        # Parse section row
                        section_id = tds[2].text.strip()
                        meeting_type = tds[3].text.strip()
                        section = tds[4].text.strip()
                        days = tds[5].text.strip()
                        time = tds[6].text.strip()
                        building = tds[7].text.strip() 
                        room = tds[8].text.strip()
                        instructor_name = tds[9].text.strip() if len(tds) > 9 else None
                        seats_available = tds[10].text.strip() if len(tds) > 10 else None
                        seats_limit = tds[11].text.strip() if len(tds) > 11 else None
                        source_url = url
                        payload = str(payload)
                    elif len(tds) >= 10 and 'colspan' in tds[5].attrs and tds[5]['colspan'] == '4':
                        section_id = tds[2].text.strip()
                        meeting_type = tds[3].text.strip()
                        section = tds[4].text.strip()
                        days = tds[5].text.strip()
                        time = "TBA"
                        building = "TBA"
                        room = "TBA"
                        instructor_name = tds[6].text.strip() if len(tds) > 9 else None
                        seats_available = tds[7].text.strip() if len(tds) > 10 else None
                        seats_limit = tds[8].text.strip() if len(tds) > 11 else None
                        source_url = url
                        # payload = str(payload)

                        course = UCSDCourseDB(
                            course_number=current_course_number,
                            course_title=current_course_title,
                            units=current_units,
                            restriction_codes=current_restriction_codes,
                            section_id=section_id,
                            meeting_type=meeting_type,
                            section=section,
                            days=days,
                            time=time,
                            building=building,
                            room=room,
                            instructor_name=instructor_name,
                            seats_available=seats_available,
                            seats_limit=seats_limit,
                            source_url=source_url,
                            payload=payload
                        )
                        print(course.__dict__)
                        courses.append(course)
            
            print(f"Found {len(courses)} courses for department {department}")
            return courses
            
        except Exception as e:
            print(f"Error fetching courses for department {department}:")
            print(f"Exception: {str(e)}")
            return []

async def get_all_courses() -> List[UCSDCourseDB]:
    """Get all courses for all departments."""
    all_courses = []
    for department in departments:
        courses = await get_courses_by_department(department)
        all_courses.extend(courses)
    print(f"Total courses found: {len(all_courses)}")
    return all_courses

async def main() -> List[BaseDB]:
    """Main entry point for UCSD course scraping."""
    all_courses = await get_all_courses()
    return all_courses

if __name__ == "__main__":
    asyncio.run(main())
