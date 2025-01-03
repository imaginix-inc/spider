from bs4 import BeautifulSoup
import requests
from src.models import UCSFCourseDB


base_url = "https://catalog.ucsf.edu/course-catalog"
subjects = {
    "aicompdrug": "Artificial Intelligence and Computational Drug Discovery and Development",
    "anatomy": "Anatomy",
}


def fetch_course_info(url, subject):
    resp = requests.get(url).text
    soup = BeautifulSoup(resp, 'html.parser')

    # Find all courseblock elements
    courseblocks = soup.find_all('div', class_='courseblock')

    courses = []

    # Extract details from each courseblock
    for block in courseblocks:
        course_code = block.find('span', class_="detail-code").get_text(strip=True)
        splitted_course_code = course_code.split(" ")
        course_prefix = splitted_course_code[0]
        course_number = splitted_course_code[-1]

        course_title = block.find('span', class_="detail-title").get_text(strip=True)
        course_unit = block.find('span', class_="detail-hours_html").get_text(strip=True).split(" ")[0][1:]

        course_term = block.find('span', class_="detail-offering").get_text(strip=True)

        course_instructor = block.select('div > p > span.skip-makebubbles > span > a')[0].get_text(strip=True)

        activity_tag = block.find('p', class_="detail-activities")
        course_activities = ''.join(str(item).strip() for item in activity_tag.contents if not hasattr(item, 'contents')).strip()

        course_description = activity_tag.find_parent('div').next_sibling.find('p').get_text(strip=True)

        course = UCSFCourseDB(remark=course_description, term=course_term, units=course_unit,
                              activity=course_activities, prefix=course_prefix, number=course_number,
                              instructor_name=course_instructor, course_name=course_title, source_url=url,
                              subject=subject)
        courses.append((course, course_title))

    return courses



async def main() -> List[BaseDB]:
    course_titles = []
    courses_db = []
    for key in subjects:
        l = fetch_course_info(f"{base_url}/{key}", subjects[key])
        for db, title in l:
            course_titles.append(title)
            courses_db.append(db)
    courses_db = await post_process(courses_db, course_titles, course_titles)
    return courses_db




