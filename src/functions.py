# Function to authenticate and get Google Calendar service
import json
import os.path
import datetime
from typing import Dict, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
SCOPES = ['https://www.googleapis.com/auth/calendar']
def get_calendar_service():
    """Authenticates and returns the Google Calendar Service"""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def add_calendar_event(
    summary: str, 
    start_date: str, 
    description: str = "",
    color_id: str = "1"
) -> str:
    """
    Creates an ALL-DAY event on the user's primary Google Calendar.
    
    Args:
        summary: The title of the event (e.g., "Study for Chem Midterm").
        start_date: The date in YYYY-MM-DD format.
        description: Details about the event (reasoning, priority).
        color_id: Optional. "11" is Red (High Priority), "1" is Blue (Normal).
    """
    try:
        service = get_calendar_service()
        
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'date': start_date, # YYYY-MM-DD
                'timeZone': 'America/New_York', 
            },
            'end': {
                'date': start_date,
                'timeZone': 'America/New_York',
            },
            'colorId': color_id 
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Success: Event created! Link: {event.get('htmlLink')}"

    except Exception as e:
        return f"Error creating event: {str(e)}"
def is_iso_date(s: str) -> bool:
    try:
        datetime.date.fromisoformat(s)
        return True
    except ValueError:
        return False

# Functions for reading files and structuring content
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from src.content_structurer_llm_prompt import SYSTEM_PROMPT

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from src.structures import SemesterPlan, CourseSyllabus, Event, Strategy
import os
from dotenv import load_dotenv
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY

llm = ChatAnthropic(
    model="claude-sonnet-4-5",
    temperature=0,
    timeout=None,
    max_retries=2,
)

def file_reader(directory_path: str) -> List[Dict]:
    """Reads all PDF files in a directory."""
    
    loader = DirectoryLoader(directory_path, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    clean_data = []
    for doc in documents:
        clean_data.append({
            "page_content": doc.page_content,
        })
    return clean_data


def content_structurer(file_content: List[Dict]):
    """Extracts and structures calendar events from syllabus text."""
    combined_text = "\n".join([page['page_content'] for page in file_content])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "Here is the syllabus text: {raw_text}")
    ])
    
    # That's it. No json_mode, no schema escaping, just works.
    structured_llm = llm.with_structured_output(SemesterPlan)
    chain = prompt | structured_llm
    result = chain.invoke({"raw_text": combined_text})
    
    return result.model_dump_json()