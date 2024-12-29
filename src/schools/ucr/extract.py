from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Optional


class Course(BaseModel):
    """Information about a course."""

    section: Optional[str] = Field(
        default=None, description="The section of the course"
    )
    units: Optional[str] = Field(
        default=None, description="The number of units of the course"
    )
    offering_title: Optional[str] = Field(
        default=None, description="The title of the course"
    )
    instructor: Optional[str] = Field(
        default=None, description="The name of the instructor"
    )
    days: Optional[str] = Field(
        default=None, description="The days the course is offered"
    )
    time: Optional[str] = Field(
        default=None, description="The time the course is offered"
    )
    location: Optional[str] = Field(
        default=None, description="The location of the course"
    )
    grade_scheme: Optional[str] = Field(
        default=None, description="The grading scheme of the course"
    )
    registered: Optional[str] = Field(
        default=None, description="The number of students registered"
    )
    total_seats: Optional[str] = Field(
        default=None, description="The total number of seats")


class Data(BaseModel):
    """Extracted data about courses."""

    # Creates a model so that we can extract multiple entities.
    courses: Optional[List[Course]] = Field(
        default=[], description="The courses extracted from the text"
    )


prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert extraction algorithm. "
            "Only extract relevant information from the text. "
            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value.",
        ),
        # Please see the how-to about improving performance with
        # reference examples.
        # MessagesPlaceholder('examples'),
        ("human", "{text}"),
    ]
)


async def extract(segs: List[str]) -> List[Dict[str, Any]]:
    segs = list(filter(lambda x: len(x) > 0, segs))
    # Split segments longer than 1000 characters
    new_segs = []
    for seg in segs:
        if len(seg) > 500:
            # Split into chunks of 1000 characters
            chunks = [seg[i:i+500] for i in range(0, len(seg), 500)]
            new_segs.extend(chunks)
        else:
            new_segs.append(seg)
    segs = new_segs
    llm = ChatOpenAI(
        model="gpt-4o", max_retries=5, timeout=30)
    structured_llm = llm.with_structured_output(schema=Data)

    prompt: List[Dict[str, Any]] = await prompt_template.abatch([{"text": text} for text in segs])
    data_list: List[Data] = await structured_llm.abatch(prompt, {
        'max_concurrency': 15,

    })

    # Flatten course data

    all_courses: List[Dict[str, Any]] = [course
                                         for data in data_list
                                         for course in (data.courses or [])]

    return all_courses


if __name__ == "__main__":
    import asyncio

    asyncio.run(extract([open('tmp.txt', 'r').read()]))
