from mcp.server import FastMCP
from typing import Dict, List, Optional
from system_prompt import SYSTEM_PROMPT, json_formatting_instruction
from pydantic import BaseModel, Field
from langchain_core.documents import Document
mcp=FastMCP()
from langchain_openai import ChatOpenAI


full_system_prompt = SYSTEM_PROMPT + json_formatting_instruction
import os
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY


import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
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

# --- THE MCP TOOL ---

@mcp.tool()
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
        
        # Structure the event body for Google
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'date': start_date, # YYYY-MM-DD
                'timeZone': 'America/New_York', # Hardcoded for Howard/DC area
            },
            'end': {
                'date': start_date, # Google requires end date (same day for all-day)
                'timeZone': 'America/New_York',
            },
            'colorId': color_id 
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Success: Event created! Link: {event.get('htmlLink')}"

    except Exception as e:
        return f"Error creating event: {str(e)}"

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
# 3. The Single Course (Renamed for clarity)
class CourseSyllabus(BaseModel):
    course_name: str
    events: List[Event]

# 4. THE NEW MASTER CONTAINER
class SemesterPlan(BaseModel):
    courses: List[CourseSyllabus]

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from system_prompt import SYSTEM_PROMPT
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
@mcp.tool()
def file_reader(directory_path: str):
    """Reads all PDF files in a directory."""
    
    # ... (Your loading logic) ...
    loader = DirectoryLoader(directory_path, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    
    # --- THE FIX: Convert Objects to Dictionaries ---
    clean_data = []
    for doc in documents:
        clean_data.append({
            "page_content": doc.page_content,
        })
    return clean_data

@mcp.tool()
def content_structurer(file_content: List[Dict]):
    prompt = ChatPromptTemplate.from_messages([
        ("system", full_system_prompt),
        ("user", "Here is the syllabus text: {raw_text}")
        ])
    structured_llm = llm.with_structured_output(SemesterPlan, method="json_mode")
    chain=  prompt | structured_llm
    result = chain.invoke({"raw_text": file_content})
    return result.model_dump_json()
def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()