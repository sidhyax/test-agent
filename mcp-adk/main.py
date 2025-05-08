import os
import asyncio
from dotenv import load_dotenv
from google.genai import types
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

async def get_agent():
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@openbnb/mcp-server-airbnb",
                "--ignore-robots-txt"
            ]
        )
    )

    agent = LlmAgent(
        name="travel_assistant",
        model="gemini-2.0-flash",
        tools=tools,
        instruction="""
        You are a travel assistant. You can help the user find information about their travel plans.
        """
    )

    return agent, exit_stack

async def main():
    agent, exit_stack = await get_agent()
    session_service = InMemorySessionService()
    session = session_service.create_session(
        state={},
        user_id="user_123",
        app_name="travel_assistant_app"
    )

    query = "What are the best places to visit in Paris for 2 people on August 1st to 4th, 2025?"

    content = types.Content(
        role="user",
        parts=[
            types.Part(text=query)
        ]
    )

    runner = Runner(
        app_name="travel_assistant_app",
        agent=agent,
        session_service=session_service
    )

    try:
        async for message in runner.run_async(
            session_id=session.id,
            user_id=session.user_id,
            new_message=content
        ):
            print(message.content.parts[0].text)
    finally:
        await exit_stack.aclose()

if __name__ == "__main__":
    asyncio.run(main())
