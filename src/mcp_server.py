from mcp.server import FastMCP
from typing import Dict, List, Optional
from src.prompts import SYSTEM_PROMPT
from src.structures import SemesterPlan, CourseSyllabus, Event, Strategy
from langchain_core.documents import Document
mcp=FastMCP()
from langchain_openai import ChatOpenAI
from src.functions import get_calendar_service, file_reader, content_structurer, add_calendar_event, is_iso_date


@mcp.tool()
def file_reader_and_analyzer(directory_path: str) -> str:
    """Main tool to read syllabus PDF and extract events"""
    # Step 1: Read files
    file_content = file_reader(directory_path)
    
    # Step 2: Structure content
    structured_data_json = content_structurer(file_content)
    
    # Step 3: Parse structured data
    semester_plan = SemesterPlan.model_validate_json(structured_data_json)

    return semester_plan.model_dump_json(indent=2)

@mcp.tool()
def add_events_to_calendar(events: List[Dict]):
    """
    Adds a list of events to Google Calendar.

    Args:
        events: List of events. Each event is a dict with:
            {
                "title": str,
                "course_name": str,
                "priority": str,  # 'high' or other
                "strategy": {
                    "start_date": str,  # YYYY-MM-DD
                    "reasoning": str
                }
            }
    """
    results = []
    for event in events:
        strategy = event.get("strategy")
        if strategy:
            color_id = "11" if event.get("priority") == "high" else "1"
            result = add_calendar_event(
                summary=f"{event['title']} - {event['course_name']}",
                start_date=strategy.get("start_date"),
                description=strategy.get("reasoning", ""),
                color_id=color_id
            )
            results.append(result)
    return "\n".join(results)



def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()