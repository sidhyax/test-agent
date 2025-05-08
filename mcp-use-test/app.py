import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient
import sys


async def run_memory_chat():
    """
    Run a chat using MCPAgent with built-in conversation memory
    """

    load_dotenv(".env")
    # os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY NOT FOUND")
        sys.exit(1)

    
    config_file = "browser_mcp.json"
    print(f"Using config file: {config_file}")
    if not os.path.exists(config_file):
        print(f"ERROR: CONFIG FILE NOT FOUND AT: {config_file}")
        sys.exit(1)

    
    print("INITIALIZING CHAT....")

    client = None

    try:
        client = MCPClient.from_config_file(config_file)
        llm = ChatGroq(model="llama3-8b-8192",api_key=os.getenv("GROQ_API_KEY"))


        agent = MCPAgent(
            llm=llm,
            client=client,
            max_steps=5,
            memory_enabled=True,
        )

        print("\n=================MCP-AGENT==============\n")
        print("Type exit or quit to end the conversation")
        print("Type clear to clear the conversation history")
        print("\n=================MCP-AGENT==============\n")


        while True:
            try:
                user_input = input("\nYOU: ")
            except EOFError:
                break

            if user_input.lower() in ["exit","quit"]:
                print("Ending Conversation......")
                break
            
            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("Conversation history cleared....")
                continue

            print("\nASSISTANT: ",end="",flush=True)
            try:
                response = await agent.run(user_input)
                print(response)
            except Exception as e:
                import traceback
                print(f"Error during agent execution: {e}")

    except KeyboardInterrupt:
        print("\n Exiting chat due to Keyboard interrupt....")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("Cleaning Up MCP Client session....")
        if client and client.sessions:
            try:
                await client.close_all_sessions()
                print("MCP session closed..")
            except Exception as e:
                print(f"Error closing MCP session: {e}")
        
        else:
            print("No active MCP session to clean or client not initialized")
        
        print("Cleaning up compelete. Good Bye!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_memory_chat())