import sys
from pathlib import Path
# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import httpx
import asyncio
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from typing import Optional, List, Set
# from src.models import BaseDB, UCDCourseDB

class Course(BaseModel):
    """Information about a UC Davis course."""

    title: Optional[str] = Field(
        default=None, description="The title of the course"
    )
    subject_area: Optional[str] = Field(
        default=None, description="The subject area code"
    )
    term: Optional[str] = Field(
        default=None, description="The term the course is offered"
    )
    crn: Optional[str] = Field(
        default=None, description="Course Reference Number"
    )
    instructor: Optional[str] = Field(
        default=None, description="The name of the instructor"
    )
    units: Optional[str] = Field(
        default=None, description="The number of units for the course"
    )
    ge_credits: Optional[List[str]] = Field(
        default=None, description="List of GE credits fulfilled by the course"
    )
    open_seats: Optional[str] = Field(
        default=None, description="Number of open seats"
    )
    reserved_seats: Optional[str] = Field(
        default=None, description="Number of reserved seats"
    )
    waitlist: Optional[str] = Field(
        default=None, description="Waitlist information"
    )
    max_enrollment: Optional[str] = Field(
        default=None, description="Maximum enrollment capacity"
    )
    final_exam: Optional[str] = Field(
        default=None, description="Final exam information"
    )
    course_drop: Optional[str] = Field(
        default=None, description="Course drop information"
    )
    course_materials: Optional[str] = Field(
        default=None, description="Link to course materials"
    )
    description: Optional[str] = Field(
        default=None, description="Course description"
    )
    prerequisites: Optional[str] = Field(
        default=None, description="Prerequisites information link"
    )
    course_cross_listing: Optional[str] = Field(
        default=None, description="Cross-listing information link"
    )
    meeting_times: Optional[List[dict]] = Field(
        default=None, description="List of meeting times with day, time, and location"
    )
    canvas_link: Optional[str] = Field(
        default=None, description="Link to Canvas course page"
    )

subjects = [
    "AAS", "AMR", "AGC", "ARE", "AGE", "AED", "ASE", "AGR", "AMS",
    "ANB", "ABI", "ABG", "ANG", "ANS", "ANT", "ABS", "ABT", "ARB", "AHI",
    "ART", "ASA", "AST", "ATM", "AVS", "BCB", "BMB", "BIS", "BIO", "BPT",
    "BPH", "BST", "BIT", "DEB", "BAX", "CAN", "CDB", "CEL", "CHE", "CHI",
    "CHN", "CTS", "CDM", "CLA", "CLH", "CGS", "LTS", "CLR", "CMN", "CRD",
    "COM", "CNE", "CNS", "CRI", "CRO", "CSM", "CST", "DAN", "DSC", "DES",
    "DRA", "EAS", "ECL", "ECN", "EJS", "EDU", "EAP", "EDO", "EGG", "ENG",
    "EAE", "EAD", "EAL", "EBS", "BIM", "ECH", "ECM", "ECI", "ECS", "EEC",
    "EMS", "EME", "MAE", "ENL", "ENT", "ENH", "EVH", "ENP", "ENV", "ERS",
    "ESM", "ESMC", "ESME", "ESP", "EST", "ETX", "EPI", "EVE", "EXB", "EXS",
    "FPS", "FMS", "LFA", "FAH", "FST", "FSM", "FOR", "FRE", "FRS", "FSE",
    "GSW", "GGG", "GEO", "GEL", "GER", "GDB", "GLO", "GRD", "GRK", "MHI",
    "HEB", "HND", "HIN", "HIS", "HPS", "HNR", "HRT", "HDE", "HMR", "HUM",
    "HUN", "HYD", "IMM", "IPM", "IST", "IAD", "ICL", "IRE", "ITA", "JPN",
    "JST", "LED", "LDA", "LAT", "LAH", "LAW", "LIN", "MGT", "MGV", "MGB",
    "MGP", "MPH", "MCN", "MPS", "MAT", "ANE", "BCM", "CHA", "CPS", "CMH",
    "DER", "EPP", "FAP", "HPH", "IMD", "CAR", "NCM", "EMR", "ENM", "GAS",
    "GMD", "HON", "IDI", "NEP", "PUL", "MMI", "PHA", "MDS", "NEU", "NSU",
    "OBG", "OEH", "OPT", "OSU", "OTO", "PMD", "PED", "PMR", "PSU", "PSY",
    "SPH", "RON", "RDI", "RNU", "RAL", "SUR", "URO", "MDD", "MDI", "MST",
    "MIC", "MMG", "MIB", "MSA", "MSC", "MCB", "MCP", "MUS", "NAS", "NAC",
    "NEM", "NPB", "NSC", "NRS", "NUT", "NGG", "NUB", "PFS", "PER", "PTX",
    "PHI", "PHE", "PAS", "PHY", "PGG", "PLB", "PBI", "PLP", "PPP", "PLS",
    "POL", "POM", "PBG", "POR", "ACC", "PSC", "PUN", "RMT", "RST", "RUS",
    "VET", "STS", "SAS", "STP", "STH", "SOC", "SSC", "SPA", "STA", "REL",
    "SAF", "SSB", "TCS", "TAE", "TXC", "TTP", "TRK", "UWP", "URD", "VCR",
    "DVM", "VMD", "VEN", "APC", "VME", "VMB", "PMI", "PHR", "MPM", "VSR",
    "WFB", "WFC", "WMS", "WLD"
]

async def fetch_crns(client: httpx.AsyncClient, term_code="202501", subject="-") -> Set[str]:
    """
    Fetch unique course CRNs from the UC Davis registrar using a POST request.
    """
    url = "https://registrar-apps.ucdavis.edu/courses/search/course_search_results.cfm"

    payload = {
        "termCode": term_code,
        "subject": subject,
        "runMe": "1",
        "clearMe": "1",
        "course_number": "",
        "multiCourse": "",
        "course_title": "",
        "instructor": "",
        "course_start_eval": "-",
        "course_start_time": "-",
        "course_end_eval": "-",
        "course_end_time": "-",
        "course_status": "-",
        "course_level": "-",
        "course_units": "-",
        "virtual": "-",
        "reorder": "",
        "gettingResults": "0"
    }

    try:
        response = await client.post(url, data=payload)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            crns = set()
            for td in soup.find_all('td', {'class': 'cs-view-course'}):
                onclick_content = td.get('onclick', '')
                if 'viewCourse' in onclick_content:
                    crn = onclick_content.split("'")[1]
                    crns.add(crn)
            return crns
        else:
            print(f"Request failed for subject {subject}")
            print(f"Status code: {response.status_code}")
            print(f"URL: {url}")
            print(f"Payload: {payload}")
            print(f"Response text: {response.text[:500]}...")  # Print first 500 chars of response
            return set()
    except Exception as e:
        print(f"Error fetching CRNs for subject {subject}:")
        print(f"URL: {url}")
        print(f"Payload: {payload}")
        print(f"Exception: {str(e)}")
        return set()

async def extract_course_data(client: httpx.AsyncClient, crn: str, term_code="202501") -> Course:
    """
    Extract course information by processing all <td> elements.
    """
    payload = {
        "termCode": term_code,
        "crn": crn
    }
    url = "https://registrar-apps.ucdavis.edu/courses/search/course.cfm"

    try:
        response = await client.post(url, data=payload)
        if response.status_code != 200:
            print(f"Request failed for CRN {crn}")
            print(f"Status code: {response.status_code}")
            print(f"URL: {url}")
            print(f"Payload: {payload}")
            print(f"Response text: {response.text[:500]}...")  # Print first 500 chars of response
            return Course()

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        course_data = {}

        # Get all <td> elements
        all_td = soup.find_all('td')

        # Extract title
        title_element = soup.find('h1', {'style': 'color:#BF9900!important;'})
        course_data['title'] = title_element.text.strip() if title_element else None

        # Iterate over all <td> elements to extract fields
        for td in all_td:
            text = td.get_text(strip=True)

            if text.startswith("Subject Area:"):
                course_data['subject_area'] = text.replace("Subject Area:", "").strip()

            elif text.startswith("Term:"):
                course_data['term'] = text.replace("Term:", "").strip()

            elif text.startswith("CRN:"):
                course_data['crn'] = text.replace("CRN:", "").strip()

            elif text.startswith("Instructor:"):
                course_data['instructor'] = text.replace("Instructor:", "").strip()

            elif text.startswith("Units:"):
                course_data['units'] = text.replace("Units:", "").strip()

            elif text.startswith("GE Credit:"):
                ge_credit_html = td.decode_contents()
                course_data['ge_credits'] = [
                    line.strip() for line in ge_credit_html.split('<BR />') if line.strip() and "GE Credit:" not in line
                ]

            elif text.startswith("Open Seats:"):
                course_data['open_seats'] = text.replace("Open Seats:", "").strip()

            elif text.startswith("Reserved Seats:"):
                course_data['reserved_seats'] = text.replace("Reserved Seats:", "").strip()

            elif text.startswith("Waitlist:"):
                course_data['waitlist'] = text.replace("Waitlist:", "").strip()

            elif text.startswith("Maximum Enrollment:"):
                course_data['max_enrollment'] = text.replace("Maximum Enrollment:", "").strip()

            elif text.startswith("Final Exam:"):
                course_data['final_exam'] = text.replace("Final Exam:", "").strip()

            elif text.startswith("Course Drop:"):
                course_data['course_drop'] = text.replace("Course Drop:", "").strip()

            elif "UC Davis Bookstore" in text:
                course_materials_link = td.find('a', string="UC Davis Bookstore")
                course_data['course_materials'] = course_materials_link['href'] if course_materials_link else None

            elif text.startswith("Description:"):
                description_element = td.find('strong', string="Description:")
                if description_element:
                    description = description_element.find_next_sibling(string=True)
                    course_data['description'] = description.strip() if description else None


            elif text.startswith("Prerequisite:"):
                prerequisite_link = td.find_next('a')
                course_data['prerequisites'] = prerequisite_link['href'] if prerequisite_link else None

            elif text.startswith("Course Cross Listing:"):
                cross_listing_link = td.find_next('a')
                course_data['course_cross_listing'] = cross_listing_link['href'] if cross_listing_link else None

        # Extract meeting times and locations
        course_data['meeting_times'] = []
        meeting_table = soup.find('table', {'width': '300'})
        if meeting_table:
            for row in meeting_table.find_all('tr')[1:]:
                columns = row.find_all('td')
                if len(columns) == 3:
                    day = columns[0].text.strip()
                    time = columns[1].text.strip()
                    location = columns[2].text.strip()
                    course_data['meeting_times'].append({'day': day, 'time': time, 'location': location})

        # Extract Canvas link
        canvas_link = soup.find('a', href="https://canvas.ucdavis.edu/")
        course_data['canvas_link'] = canvas_link['href'] if canvas_link else None

        # Convert dictionary to Course object
        return Course(**course_data)
    except Exception as e:
        print(f"Error extracting data for CRN {crn}:")
        print(f"URL: {url}")
        return Course()

async def process_subject(client: httpx.AsyncClient, subject: str, semaphore: asyncio.Semaphore) -> List[Course]:
    async with semaphore:
        crns = await fetch_crns(client, term_code="202501", subject=subject)
        tasks = []
        for crn in crns:
            tasks.append(extract_course_data(client, crn, term_code="202501"))
        return await asyncio.gather(*tasks)

async def main() :
    """
    Main function to extract all courses with concurrent processing.
    """
    all_courses = []
    semaphore = asyncio.Semaphore(5)  # Limit concurrent requests

    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = []
        for subject in subjects:
            tasks.append(process_subject(client, subject, semaphore))

        results = await asyncio.gather(*tasks)
        for courses in results:
            all_courses.extend(courses)

    print(all_courses)

    # Convert to database models and post-process
    # db_courses = [UCDCourseDB(**course.dict()) for course in all_courses]
    # db_courses = await post_process(
    #     db_courses,
    #     [course.title for course in all_courses],
    #     [course.title for course in all_courses]
    # )
    # return db_courses

if __name__ == "__main__":
    asyncio.run(main())
