from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime, func, SmallInteger, BigInteger, Float, Text, ARRAY
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.declarative import DeferredReflection
from typing import Optional, List


class Base(DeclarativeBase):
    pass


class BaseDB(Base):
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
    __tablename__ = 'rumi_ucr_class_schedule_2025_spring'
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
    __tablename__ = 'rumi_usf_class_schedule_2025_spring'
    term: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The term of the course")
    time: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    days: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    classroom: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    date_range: Mapped[Optional[str]] = mapped_column(
        String, nullable=True)
    schedule_type: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The schedule type of the course")
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    course_type: Mapped[Optional[str]] = mapped_column(
        String, nullable=True)
    course_code: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The course code")
    section: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The section of the course")
    campus: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The campus where the course is offered")
    instructional_method: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The instructional method used in the course")
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
        String, nullable=True, doc="The field of study of the course")
    prerequisite_course: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The prerequisite course code")
    minimum_grade: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="The minimum grade required")


class UCICourseDB(BaseDB):
    __tablename__ = 'rumi_uci_class_schedule_2025_spring'

    code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    section: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    units: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    modality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    time: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    place: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    final: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    max_capacity: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True)
    enrolled: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    waitlist: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    requests: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    restrictions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    textbooks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    web: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class UCSDCourseDB(BaseDB):
    __tablename__ = 'rumi_ucsd_class_schedule_2025_spring'

    course_number: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True)
    course_title: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True)
    units: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    restriction_codes: Mapped[Optional[List[str]]
                              ] = mapped_column(ARRAY(String), nullable=True)
    section_id: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True)
    meeting_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True)
    section: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    days: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    building: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    room: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    seats_available: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True)
    seats_limit: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True)


class UCSCCourseDB(BaseDB):
    __tablename__ = 'rumi_ucsc_class_schedule_2025_spring'
    subject: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    instruction_mode: Mapped[Optional[str]
                             ] = mapped_column(String, nullable=True)
    academic_group: Mapped[Optional[str]
                           ] = mapped_column(String, nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    enrolled_count: Mapped[Optional[int]
                           ] = mapped_column(String, nullable=True)
    max_enroll: Mapped[Optional[int]] = mapped_column(String, nullable=True)
    waitlist_count: Mapped[Optional[int]
                           ] = mapped_column(String, nullable=True)
    max_waitlist: Mapped[Optional[int]] = mapped_column(String, nullable=True)
    course_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    term: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    days: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    start_time: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    end_time: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    units: Mapped[Optional[int]] = mapped_column(String, nullable=True)


class UCLACourseDB(BaseDB):
    __tablename__ = 'rumi_ucla_class_schedule_2025_spring'
    section: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    waitlist: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    days: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    time: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    units: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    term: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    subject_area_code: Mapped[Optional[str]
                              ] = mapped_column(String, nullable=True)
    catalog_number: Mapped[Optional[str]
                           ] = mapped_column(String, nullable=True)
    class_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sequence_number: Mapped[Optional[str]
                            ] = mapped_column(String, nullable=True)
    path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    token: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class UCSFCourseDB(BaseDB):
    __tablename__ = 'rumi_ucsf_class_schedule_2025_spring'
    subject: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    prefix: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    course_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    units: Mapped[Optional[int]] = mapped_column(String, nullable=True)
    activity: Mapped[Optional[int]] = mapped_column(String, nullable=True)
    term: Mapped[Optional[int]] = mapped_column(String, nullable=True)
