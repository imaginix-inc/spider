from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import httpx
from bs4 import BeautifulSoup
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


def map_course_model_to_db(course_model: CourseModel) -> USFCourseDB:
    return USFCourseDB(
        term=course_model.term,
        course_code=course_model.course_code,
        section=course_model.section,
        campus=course_model.campus,
        schedule_type=course_model.schedule_type,
        instructional_method=course_model.instructional_method,
        credits=course_model.credits,
        capacity=course_model.capacity,
        actual=course_model.actual,
        remaining=course_model.remaining,
        waitlist_capacity=course_model.waitlist_capacity,
        waitlist_actual=course_model.waitlist_actual,
        waitlist_remaining=course_model.waitlist_remaining,
        field_of_study=course_model.field_of_study,
        prerequisite_course=course_model.prerequisite_course,
        minimum_grade=course_model.minimum_grade
    )


async def get_course_links() -> List[str]:
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

        links = soup.find_all('a', href=True)
        links = list(filter(lambda x: x['href'].startswith(
            '/PROD/bwckschd.p_disp_detail_sched'), links))
        return links
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


async def load_class(link: str) -> BaseDB:
    async with httpx.AsyncClient() as client:
        response = await client.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
    llm = ChatOpenAI(
        model="gpt-4o-mini", max_retries=5, timeout=30, api_key=settings.openai_api_key)
    structured_llm = llm.with_structured_output(schema=CourseModel)

    prompt: List[Dict[str, Any]] = await prompt_template.ainvoke({"text": soup.get_text()})
    data: CourseModel = await structured_llm.ainvoke(prompt)
    data: USFCourseDB = map_course_model_to_db(data)
    data = (await post_process([data], [data.course_code], [data.course_code]))[0]
    data.source_url = link
    return data


async def main() -> List[BaseDB]:
    links = await get_course_links()
    tasks = [load_class(
        f"https://ssb-prod.ec.usfca.edu{link['href']}") for link in links]
    return await asyncio.gather(*tasks)
if __name__ == '__main__':
    print(asyncio.run(load_class(
        'https://ssb-prod.ec.usfca.edu/PROD/bwckschd.p_disp_detail_sched?term_in=202520&crn_in=21278')))
