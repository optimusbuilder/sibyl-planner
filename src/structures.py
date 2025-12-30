from pydantic import BaseModel, Field
from typing import List, Optional

class Strategy(BaseModel):
    action: str = Field(description="Action to take, e.g. 'Start Studying'")
    start_date: str = Field(description="ISO date YYYY-MM-DD")
    reasoning: str = Field(description="Why this date?")

class Event(BaseModel):
    title: str
    type: str
    due_date: str
    priority: str
    strategy: Optional[Strategy] = None

class SyllabusData(BaseModel):
    course_name: str
    events: List[Event]

class CourseSyllabus(BaseModel):
    course_name: str
    events: List[Event]

# 4. THE NEW MASTER CONTAINER
class SemesterPlan(BaseModel):
    courses: List[CourseSyllabus]