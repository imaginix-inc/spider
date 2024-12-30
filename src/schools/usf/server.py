from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import httpx
from bs4 import BeautifulSoup
import bs4
import asyncio
from typing import List, Optional, Dict, Any
from src.models import USFCourseDB, BaseDB
from src.process import post_process
from pydantic import BaseModel, Field
from settings import settings


class CourseModel(BaseModel):
    term: Optional[str] = Field(
        default=None, description="The term of the course", max_length=50
    )
    course_code: Optional[str] = Field(
        default=None, description="The course code", max_length=20
    )
    section: Optional[str] = Field(
        default=None, description="The section of the course", max_length=10
    )
    campus: Optional[str] = Field(
        default=None, description="The campus where the course is offered", max_length=100
    )
    schedule_type: Optional[str] = Field(
        default=None, description="The schedule type of the course", max_length=50
    )
    instructional_method: Optional[str] = Field(
        default=None, description="The instructional method used in the course", max_length=50
    )
    credits: Optional[str] = Field(
        default=None, description="The number of credits for the course"
    )
    capacity: Optional[str] = Field(
        default=None, description="The capacity of the course"
    )
    actual: Optional[str] = Field(
        default=None, description="The actual number of enrolled students"
    )
    remaining: Optional[str] = Field(
        default=None, description="The remaining seats available"
    )
    waitlist_capacity: Optional[str] = Field(
        default=None, description="The capacity of the waitlist"
    )
    waitlist_actual: Optional[str] = Field(
        default=None, description="The actual number of students on the waitlist"
    )
    waitlist_remaining: Optional[str] = Field(
        default=None, description="The remaining spots on the waitlist"
    )
    field_of_study: Optional[str] = Field(
        default=None, description="The field of study of the course", max_length=100
    )
    prerequisite_course: Optional[str] = Field(
        default=None, description="The prerequisite course code", max_length=20
    )
    minimum_grade: Optional[str] = Field(
        default=None, description="The minimum grade required", max_length=2
    )


async def get_course_links() -> List[BaseDB]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://ssb-prod.ec.usfca.edu/PROD/bwckschd.p_get_crse_unsec",
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "zh-CN,zh;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"macOS\"",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1"
            },
            timeout=20,
            data="term_in=202520&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_subj=%25&sel_crse=&sel_title=%25&sel_insm=%25&sel_camp=%25&sel_levl=%25&sel_instr=%25&sel_attr=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a&begin_ap=x&end_ap=y"
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        global_table = soup.find('table', class_='datadisplaytable',
                                 summary='This layout table is used to present the sections found')

        table = list(filter(lambda x: x.name == 'tr', global_table.children))

        paired_rows = [(table[i], table[i + 1])
                       for i in range(0, len(table) - 1, 2)]
        # print(paired_rows[0][0])

        final_courses: List[BaseDB] = []
        for course in paired_rows:
            links = course[0].find_all('a', href=True)
            link = list(filter(lambda x: x['href'].startswith(
                '/PROD/bwckschd.p_disp_detail_sched'), links))[0]
            link = link['href']
            course_title_block: bs4.element.Tag = course[0]
            course_title_a: bs4.element.Tag = course_title_block.find('a')
            course_title = ' '.join(
                course_title_a.text.replace('\n', '').split())
            course_info_block: bs4.element.Tag = course[1]
            schedule_table = course_info_block.find(
                'table', class_='datadisplaytable')
            times = schedule_table.find_all('tr')[1:]  # skip header
            courses: List[USFCourseDB] = []
            for time in times:
                infos = list(map(lambda x: x.text, list(
                    time.find_all("td"))))
                course = USFCourseDB(
                    course_type=infos[0],
                    time=infos[1],
                    days=infos[2],
                    classroom=infos[3],
                    date_range=infos[4],
                    schedule_type=infos[5],
                    instructor_name=infos[6],
                    title=course_title,
                    source_url=link
                )
                courses.append(course)
            course_detect = await load_class(f"https://ssb-prod.ec.usfca.edu{link}")
            data = course_detect.model_dump()
            for course in courses:
                # assign values according to data
                for field in data.keys():
                    if hasattr(course, field):
                        setattr(course, field, data[field])
            courses = await post_process(courses, [course.title for course in courses], [course.title for course in courses])
            final_courses.extend(courses)
        return final_courses

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert extraction algorithm. "
            "Only extract relevant information from the text. "
            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value.",
        ),
        ("human", "{text}"),
    ]
)


async def load_class(link: str) -> CourseModel:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(link, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f'Error when fetch {link}: {e}')
    llm = ChatOpenAI(
        model="gpt-4o-mini", max_retries=5, timeout=30, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(schema=CourseModel)

    prompt: List[Dict[str, Any]] = await prompt_template.ainvoke({"text": soup.get_text()})
    data: CourseModel = await structured_llm.ainvoke(prompt)
    return data


async def main() -> List[BaseDB]:
    links = await get_course_links()
    return links
if __name__ == '__main__':
    print(asyncio.run(load_class(
        'https://ssb-prod.ec.usfca.edu/PROD/bwckschd.p_disp_detail_sched?term_in=202520&crn_in=21278')))
