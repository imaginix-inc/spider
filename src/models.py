from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime, func, SmallInteger, BigInteger, Float
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.declarative import DeferredReflection
from typing import Optional


class BaseDB(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source_url: Mapped[str] = mapped_column(String, nullable=True)
    remark: Mapped[str] = mapped_column(String, nullable=True)
    creator: Mapped[str] = mapped_column(String, default='')
    create_time: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, default=func.now())
    updater: Mapped[str] = mapped_column(String, default='')
    update_time: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, default=func.now())
    deleted: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0)
    tenant_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)
    name_vector: Mapped[Vector] = mapped_column(Vector, nullable=True)
    search_vector: Mapped[TSVECTOR] = mapped_column(TSVECTOR, nullable=True)
    instructor_name: Mapped[str] = mapped_column(String, nullable=True)


class UCRCourseDB(BaseDB):
    __abstract__ = False
    __tablename__ = 'ucr_courses'
    section: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    units: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    offering_title: Mapped[Optional[str]
                           ] = mapped_column(String, nullable=True)
    days: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    time: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    grade_scheme: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    registered: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    total_seats: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class USFCourseDB(BaseDB):
    __tablename__ = 'usf_courses'
    term: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, doc="The term of the course")
    time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    days: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    classroom: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date_range: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True)
    schedule_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, doc="The schedule type of the course")
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    course_type: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True)
    course_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, doc="The course code")
    section: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True, doc="The section of the course")
    campus: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, doc="The campus where the course is offered")
    instructional_method: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, doc="The instructional method used in the course")
    credits: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The number of credits for the course")
    capacity: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The capacity of the course")
    actual: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The actual number of enrolled students")
    remaining: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The remaining seats available")
    waitlist_capacity: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The capacity of the waitlist")
    waitlist_actual: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The actual number of students on the waitlist")
    waitlist_remaining: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The remaining spots on the waitlist")
    field_of_study: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, doc="The field of study of the course")
    prerequisite_course: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, doc="The prerequisite course code")
    minimum_grade: Mapped[Optional[str]] = mapped_column(
        String(2), nullable=True, doc="The minimum grade required")


class UCICourseDB(BaseDB):
    __tablename__ = 'uci_courses'
    
    code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    section: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    units: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    modality: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    place: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    final: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    max_capacity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    enrolled: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    waitlist: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    requests: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    restrictions: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    textbooks: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    web: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    payload: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)


class UCSDCourseDB(BaseDB):
    __tablename__ = 'ucsd_courses'
    
    course_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    course_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    units: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    restriction_codes: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    section_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    meeting_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    section: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    days: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    building: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    room: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    seats_available: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    seats_limit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    payload: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
class UCSCCourseDB(BaseDB):
    __tablename__ = 'ucsc_courses'
    subject = mapped_column(String)
    number = mapped_column(String)
    display_name = mapped_column(String)
    instruction_mode = mapped_column(String)
    academic_group = mapped_column(String)
    start_date = mapped_column(String)
    end_date = mapped_column(String)
    status = mapped_column(String)
    enrolled_count = mapped_column(Integer)
    max_enroll = mapped_column(Integer)
    waitlist_count = mapped_column(Integer)
    max_waitlist = mapped_column(Integer)
    course_name = mapped_column(String)
    term = mapped_column(String)
    days = mapped_column(String)
    start_time = mapped_column(String)
    end_time = mapped_column(String)
    units = mapped_column(Integer)

