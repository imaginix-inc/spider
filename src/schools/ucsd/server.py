from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
from bs4 import BeautifulSoup
from src.models import UCSDCourseDB
from typing import List
import asyncio
from src.models import BaseDB
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

url = "https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudentResult.htm"


def extract_page_content(page_source) -> List[UCSDCourseDB]:
    soup = BeautifulSoup(page_source, 'html.parser')
    tables = soup.find_all('table', class_='tbrdr')
    courses = []  # 改为存储课程列表

    # Initialize course header variables with default values
    current_course_number = None
    current_course_title = None
    current_units = None
    current_restriction_codes = []

    for table in tables:
        items = table.find_all('tr')
        for item in items:
            try:
                tds = item.find_all('td')
                if len(tds) >= 3 and 'class' in tds[0].attrs and tds[0]['class'] == ['crsheader']:
                    # Parse course header
                    header_link = tds[2].find('a')
                    spans = tds[0].find_all('span')
                    current_restriction_codes = [span.text.strip() for span in spans if span.text.strip()]
                    current_course_number = tds[1].text.strip()
                    if header_link:
                        current_course_title = header_link.find('span', class_='boldtxt').text.strip()
                        current_units = header_link.next_sibling
                    else:
                        # print(f"Warning: Skipping malformed header - missing link")
                        continue

                elif len(tds) >= 12 and 'class' in item.attrs and 'sectxt' in item['class']:
                    if not all([current_course_number, current_course_title, current_units]):
                        print(f"Warning: Skipping section - missing course header information")
                        continue

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
                        source_url=source_url
                    )
                    courses.append(course)  # 添加到列表中

                elif len(tds) >= 10 and 'colspan' in tds[5].attrs and tds[5]['colspan'] == '4':
                    if not all([current_course_number, current_course_title, current_units]):
                        print(f"Warning: Skipping TBA section - missing course header information")
                        continue

                    section_id = tds[2].text.strip()
                    meeting_type = tds[3].text.strip()
                    section = tds[4].text.strip()
                    days = tds[5].text.strip()
                    time = "TBA"
                    building = "TBA"
                    room = "TBA"
                    instructor_name = tds[6].text.strip() if len(tds) > 6 else None
                    seats_available = tds[7].text.strip() if len(tds) > 7 else None
                    seats_limit = tds[8].text.strip() if len(tds) > 8 else None
                    source_url = url
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
                        source_url=source_url
                    )
                    courses.append(course)  # 添加到列表中

            except Exception as e:
                print(f"Warning: Error processing row: {str(e)}")
                continue

    # print(f"Extracted {len(courses)} courses from current page")
    return courses  # 返回课程列表


def scrape_department_courses() -> List[UCSDCourseDB]:
    """
    Scrape all courses for all available departments
    Returns:
        list: List of UCSDCourseDB objects
    """
    start_time = time.time()
    all_courses = []  # 存储所有课程

    # 创建 Chrome 选项并启用无头模式
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # 启用无头模式
    chrome_options.add_argument('--disable-gpu')  # 某些系统需要此参数
    
    # 使用配置好的选项创建初始 driver
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        # 等待科目选择下拉框出现
        select_element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "selectedSubjects"))
        )
        select = Select(select_element)
        departments = [option.get_attribute('value') for option in select.options if option.get_attribute('value')]
    finally:
        driver.quit()

    # Process each department with a fresh driver
    for department in departments:
        dept_start_time = time.time()
        # print(f"Processing department: {department}")

        driver = webdriver.Chrome(options=chrome_options)
        try:
            driver.get(url)
            
            # 等待并选择科目
            select_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.ID, "selectedSubjects"))
            )
            select = Select(select_element)
            select.select_by_value(department)

            # 等待并点击搜索按钮
            search_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.ID, "socFacSubmit"))
            )
            search_button.click()

            try:
                # 首先检查是否有结果
                WebDriverWait(driver, 2).until(
                    lambda x: len(x.find_elements(By.CLASS_NAME, "tbrdr")) > 0 or 
                            "No classes were found that meet your search criteria" in x.page_source
                )
                
                # 如果页面包含"没有找到课程"的消息，跳过这个部门
                if "No classes were found that meet your search criteria" in driver.page_source:
                    print(f"No courses found for department {department}")
                    continue

                page_number = 1
                while True:
                    # 等待页面加载完成（等待某个必定会出现的元素）
                    WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "tbrdr"))
                    )
                    
                    page_content = driver.page_source
                    page_courses = extract_page_content(page_content)
                    all_courses.extend(page_courses)  # 将当前页面的课程添加到总列表中
                    # print(f"Page {page_number}: {len(page_courses)} courses processed")

                    try:
                        # 等待并检查分页信息
                        pagination_td = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "td[align='right']"))
                        )
                        current_page = int(pagination_td.text.strip().split()[1].strip('()'))
                        next_page_link = WebDriverWait(driver, 2).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href*='page={current_page + 1}']"))
                        )
                        next_page_link.click()
                        page_number += 1
                    except TimeoutException:
                        # print(f"Reached last page for department {department}")
                        break

            except TimeoutException:
                # print(f"Timeout or no results for department {department}")
                continue

        except Exception as e:
            print(f"Error processing department {department}: {str(e)}")
            continue
        finally:
            driver.quit()

        dept_end_time = time.time()
        dept_duration = dept_end_time - dept_start_time
        # print(f"Department {department} completed in {dept_duration:.2f} seconds")
        # print(f"Courses found in {department}: {len(all_courses)}")
        # print("-" * 100)

    # total_duration = time.time() - start_time
    # print(f"Total courses scraped: {len(all_courses)}")
    # print(f"Total scraping time: {total_duration:.2f} seconds")
    # print(f"Average time per course: {total_duration / len(all_courses):.2f} seconds")

    return all_courses

async def main() -> List[BaseDB]:
    """Main entry point for UCSD course scraping."""
    print("Getting UCSD courses...")
    start_time = time.time()
    courses = scrape_department_courses()
    
    # total_duration = time.time() - start_time
    # print(f"Total courses scraped: {len(courses)}")
    # print(f"Total scraping time: {total_duration:.2f} seconds")
    # print(f"Average time per course: {total_duration/len(courses):.2f} seconds")
    print(f"Scraping {len(courses)} UCSD courses")
    return courses

if __name__ == "__main__":
    asyncio.run(main())
