import sys
from pathlib import Path
# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import Optional, List, Set
from src.models import BaseDB, UCICourseDB

departments = ["AC ENG", "AFAM", "ANATOMY", "ANESTH", "ANTHRO", "ARABIC", "ARMN", "ART", "ART HIS", "ARTS", "ARTSHUM", "ASIANAM", "BANA", "BATS", "BIO SCI", "BIOCHEM", "BME", "CAMPREC", "CBE", "CBEMS", "CEM", "CHC/LAT", "CHEM", "CHINESE", "CLASSIC", "CLT&THY", "COGS", "COM LIT", "COMPSCI", "CRITISM", "CRM/LAW", "CSE", "DANCE", "DATA", "DERM", "DEV BIO", "DRAMA", "E ASIAN", "EARTHSS", "EAS", "ECO EVO", "ECON", "ECPS", "ED AFF", "EDUC", "EECS", "EHS", "ENGLISH", "ENGR", "ENGRCEE", "ENGRMAE", "ENGRMSE", "EPIDEM", "ER MED", "EURO ST", "FAM MED", "FIN", "FLM&MDA", "FRENCH", "GDIM", "GEN&SEX", "GERMAN", "GLBL ME", "GLBLCLT", "GREEK", "HEBREW", "HINDI", "HISTORY", "HUMAN", "HUMARTS", "I&C SCI", "IN4MATX", "INNO", "INT MED", "INTL ST", "IRAN", "ITALIAN", "JAPANSE", "KOREAN", "LATIN", "LAW", "LINGUIS", "LIT JRN", "LPS", "LSCI", "M&MG", "MATH", "MED", "MED ED", "MED HUM", "MGMT", "MGMT EP", "MGMT FE", "MGMT HC", "MGMTMBA", "MGMTPHD", "MIC BIO", "MOL BIO", "MPAC", "MSE", "MUSIC", "NET SYS", "NEURBIO", "NEUROL", "NUR SCI", "OB/GYN", "OPHTHAL", "PATH", "PED GEN", "PEDS", "PERSIAN", "PHARM", "PHILOS", "PHMD", "PHRMSCI", "PHY SCI", "PHYSICS", "PHYSIO", "PLASTIC", "PM&R", "POL SCI", "PORTUG", "PSCI", "PSY BEH", "PSYCH", "PUB POL", "PUBHLTH", "RADIO", "REL STD", "ROTC", "RUSSIAN", "SOC SCI", "SOCECOL", "SOCIOL", "SPANISH", "SPPS", "STATS", "SURGERY", "SWE", "TAGALOG", "TOX", "UCDC", "UNI AFF", "UNI STU", "UPPP", "VIETMSE", "VIS STD", "WRITING"]

async def get_courses_by_department(department: str, YearTerm="2025-03", max_retries=3) -> List[UCICourseDB]:
    """Get all courses for a given department and term."""
    url = "https://www.reg.uci.edu/perl/WebSoc"
    
    payload = {
        "YearTerm": YearTerm,
        "ShowComments": "on",
        "ShowFinals": "on",
        "Breadth": "ANY",
        "Dept": department,
        "CourseNum": "",
        "Division": "ANY",
        "CourseCodes": "",
        "InstrName": "",
        "CourseTitle": "",
        "ClassType": "ALL",
        "Units": "",
        "Days": "",
        "StartTime": "",
        "EndTime": "",
        "MaxCap": "",
        "FullCourses": "ANY",
        "FontSize": "100",
        "CancelledCourses": "Exclude",
        "Bldg": "",
        "Room": ""
    }

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, data=payload)
                response.raise_for_status()
                
                if not response.text:
                    raise ValueError("Empty response received")

                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all tables that contain course data
                tables = soup.find_all('table')
                courses = []
                
                # Debug information
                if not tables:
                    print(f"Warning: No tables found for department {department}")
                    print(f"Response content preview: {response.text[:200]}...")
                
                for table in tables:
                    # Look for rows that contain course data
                    rows = table.find_all('tr', attrs={'bgcolor': True})
                    
                    # Debug information
                    if not rows:
                        continue
                    
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 17:
                            try:
                                course = UCICourseDB(
                                    code=int(cols[0].text.strip()) if cols[0].text.strip() else None,
                                    type=cols[1].text.strip(),
                                    section=cols[2].text.strip(),
                                    units=cols[3].text.strip(),
                                    instructor_name=cols[4].text.strip(),
                                    modality=cols[5].text.strip(),
                                    time=cols[6].text.strip(),
                                    place=cols[7].text.strip(),
                                    final=cols[8].text.strip(),
                                    max_capacity=cols[9].text.strip(),
                                    enrolled=cols[10].text.strip(),
                                    waitlist=cols[11].text.strip(),
                                    requests=cols[12].text.strip(),
                                    restrictions=cols[13].text.strip(),
                                    textbooks=cols[14].text.strip(),
                                    web=cols[15].text.strip(),
                                    status=cols[16].text.strip(),
                                    source_url=url,
                                    payload=str(payload)
                                )
                                courses.append(course)
                            except Exception as parse_error:
                                print(f"Error parsing course in {department}: {str(parse_error)}")
                                continue
                
                return courses
                
        except httpx.TimeoutException as e:
            print(f"Timeout for department {department} (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt == max_retries - 1:
                return []
            await asyncio.sleep(1 * (attempt + 1))
            
        except httpx.HTTPError as e:
            print(f"HTTP error for department {department} (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt == max_retries - 1:
                return []
            await asyncio.sleep(1 * (attempt + 1))
            
        except Exception as e:
            print(f"Error fetching courses for department {department} (attempt {attempt + 1}/{max_retries}):")
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception details: {str(e)}")
            if attempt == max_retries - 1:
                return []
            await asyncio.sleep(1 * (attempt + 1))

async def get_all_courses() -> List[UCICourseDB]:
    """Get all courses for all departments and terms."""
    print(f"Getting courses for UCI")
    all_courses = []
    
    # 减少并发请求数量，增加间隔时间
    semaphore = asyncio.Semaphore(2)  # 降到2个并发
    
    async def fetch_department(dept):
        async with semaphore:
            courses = await get_courses_by_department(dept)
            # print(f"Retrieved {len(courses)} courses from {dept}")
            return courses
    
    # 分批处理departments，减小批次大小
    batch_size = 5  # 减小到5个
    for i in range(0, len(departments), batch_size):
        batch = departments[i:i+batch_size]
        tasks = [fetch_department(dept) for dept in batch]
        results = await asyncio.gather(*tasks)
        
        for courses in results:
            all_courses.extend(courses)
        
        # 增加批次间隔时间
        if i + batch_size < len(departments):
            await asyncio.sleep(3)  # 增加到3秒
    
    print(f"Total courses found: {len(all_courses)}")
    return all_courses

async def main() -> List[BaseDB]:
    all_courses = await get_all_courses()
    return all_courses

if __name__ == "__main__":
    asyncio.run(main())

