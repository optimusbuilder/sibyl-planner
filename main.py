import asyncio
from langchain.agents import create_agent
from langchain.agents import AgentState
from langgraph.checkpoint.memory import InMemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import tool, ToolRuntime
from sibyl_prompt import SIBYL_PROMPT
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic 
from dataclasses import dataclass
from langgraph.types import Command
from langchain.messages import ToolMessage
from langchain.messages import HumanMessage
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY


model = ChatAnthropic(
    model="claude-haiku-4-5",
    temperature=0,
    )

client1 = MultiServerMCPClient(
    {
        "local_server": {
            "transport": "stdio",
            "command": "/Users/oluwaferanmioyelude/Documents/Coding Projects/Sibyl/.venv/bin/python",
            "args": [
                "/Users/oluwaferanmioyelude/Documents/Coding Projects/Sibyl/mcp_server.py"
            ],
        }
    }
)


@dataclass
class CustomState(AgentState):
    username: str
    academic_standing: str
    university: str



@tool
def update_username(username: str, runtime: ToolRuntime) -> Command:
    """ Update the username of the user in the state once they've revealed it"""
    return Command[tuple[()]](update={
        "username": username,
        "messages": [ToolMessage("Successfully updated user's username", tool_call_id=runtime.tool_call_id)]
    })
@tool
def update_user_university(university: str, runtime: ToolRuntime) -> Command:
    """ Update the university of the user in the state once they've revealed it"""
    return Command[tuple[()]](update={
        "university": university,
        "messages": [ToolMessage("Successfully updated user's university", tool_call_id=runtime.tool_call_id)]
    })
@tool
def update_user_academic_standing(academic_standing : str, runtime: ToolRuntime) -> Command:
    """ Update the academic standing of the user(like freshman, sophmore) in the state once they've revealed it"""
    return Command[tuple[()]](update={
        "academic_standing": academic_standing,
        "messages": [ToolMessage("Successfully updated user's academic standing", tool_call_id=runtime.tool_call_id)]
    })




async def main():
    # Get MCP tools
    mcp_tools = await client1.get_tools()
    
    agent = create_agent(
        model=model,
        tools=[update_username, update_user_university, update_user_academic_standing, *mcp_tools],
        system_prompt=SIBYL_PROMPT
    )
    question=HumanMessage(content="I want you to scan my syllabi. This is the path to it: /Users/oluwaferanmioyelude/Documents/Syllabus")
    response = await agent.ainvoke({
        "messages": [question]
    })
    
    # Get final response
    final_message = response["messages"][-1]
    print(final_message.content)

asyncio.run(main())
