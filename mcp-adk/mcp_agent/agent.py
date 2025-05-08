import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

load_dotenv()

async def create_agent():
  """Gets tools from MCP Server."""
  tools, exit_stack = await MCPToolset.from_server(
      connection_params=StdioServerParameters(
          command='C://Program Files//nodejs//npx.cmd',
          args=["-y",    # Arguments for the command
            "@modelcontextprotocol/server-filesystem",
            # TODO: IMPORTANT! Change the path below to an ABSOLUTE path on your system.
            "C://Users//SIDHYA//Development//PROJECTS",
          ],
      )
  )

  agent = LlmAgent(
      model='gemini-2.0-flash',
      name='mcp_agent',
      description="explore the folder and give information",
      instruction=(
          'Help user accessing their file systems'
      ),
      tools=tools,
      api_key=os.getenv("GOOGLE_API_KEY")
  )
  return agent, exit_stack


root_agent = create_agent()