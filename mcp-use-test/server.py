import os
import sys
import asyncio
import traceback
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from langchain_google_genai import ChatGoogleGenerativeAI

class MemoryChatApp:
    """
    Enhanced chat application using MCPAgent with conversation memory
    """
    
    def __init__(self, config_file="browser_mcp.json"):
        self.config_file = config_file
        self.console = Console()
        self.client = None
        self.agent = None
        
    async def initialize(self):
        """Initialize the chat components"""
        try:
            # Load environment variables
            load_dotenv(".env")
            
            # Check for API key
            if not os.getenv("GROQ_API_KEY"):
                self.console.print("[bold red]ERROR: GROQ_API_KEY NOT FOUND[/bold red]")
                return False
            if not os.getenv("GOOGLE_API_KEY"):
                self.console.print("[bold red]ERROR: GOOGLE_API_KEY NOT FOUND[/bold red]")
                return False
                
            # Check for config file
            self.console.print(f"Using config file: {self.config_file}")
            if not os.path.exists(self.config_file):
                self.console.print(f"[bold red]ERROR: CONFIG FILE NOT FOUND AT: {self.config_file}[/bold red]")
                return False
                
            # Initialize client
            self.client = MCPClient.from_config_file(self.config_file)
            
            # Initialize LLM
            # llm = ChatGroq(
            #     model="llama3-8b-8192", 
            #     api_key=os.getenv("GROQ_API_KEY"),
            #     temperature=0.7,
            #     max_tokens=1024
            # )

            llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
            
            # Initialize agent
            self.agent = MCPAgent(
                llm=llm,
                client=self.client,
                max_steps=7,  # Increased from 5 to allow for more complex tasks
                memory_enabled=True,
                verbose=True,  # Enable verbose mode for better debugging
            )
            
            return True
            
        except Exception as e:
            self.console.print(f"[bold red]Initialization Error: {e}[/bold red]")
            traceback.print_exc()
            return False
    
    def print_welcome(self):
        """Display welcome message and instructions"""
        welcome_text = """
# MCP-AGENT Chat Interface

- Type [bold blue]exit[/bold blue] or [bold blue]quit[/bold blue] to end the conversation
- Type [bold blue]clear[/bold blue] to clear the conversation history
- Type [bold blue]help[/bold blue] to display this message again
- Type [bold blue]debug on/off[/bold blue] to toggle debug mode
        """
        self.console.print(Panel(Markdown(welcome_text), title="Welcome", border_style="green"))
    
    async def process_command(self, command):
        """Process special commands"""
        cmd = command.lower().strip()
        
        if cmd in ["exit", "quit"]:
            return False
            
        if cmd == "clear":
            if self.agent:
                self.agent.clear_conversation_history()
                self.console.print("[green]Conversation history cleared...[/green]")
            return True
            
        if cmd == "help":
            self.print_welcome()
            return True
            
        if cmd == "debug on":
            if self.agent:
                self.agent.verbose = True
                self.console.print("[green]Debug mode enabled[/green]")
            return True
            
        if cmd == "debug off":
            if self.agent:
                self.agent.verbose = False
                self.console.print("[green]Debug mode disabled[/green]")
            return True
            
        return None  # Not a command
    
    async def get_response(self, user_input):
        """Get response from the agent with error handling"""
        try:
            with self.console.status("[bold green]Processing...[/bold green]"):
                response = await self.agent.run(user_input)
            return response
        except Exception as e:
            self.console.print(f"[bold red]Error during agent execution: {e}[/bold red]")
            traceback.print_exc()
            return f"I encountered an error processing your request: {str(e)}"
    
    async def cleanup(self):
        """Clean up resources"""
        self.console.print("\n[yellow]Cleaning up MCP Client session...[/yellow]")
        if self.client and self.client.sessions:
            try:
                await self.client.close_all_sessions()
                self.console.print("[green]MCP sessions closed successfully[/green]")
            except Exception as e:
                self.console.print(f"[bold red]Error closing MCP session: {e}[/bold red]")
        else:
            self.console.print("[yellow]No active MCP session to clean or client not initialized[/yellow]")
    
    async def run(self):
        """Run the chat application"""
        self.console.print("[bold]INITIALIZING CHAT....[/bold]")
        
        if not await self.initialize():
            self.console.print("[bold red]Failed to initialize. Exiting...[/bold red]")
            return
            
        self.print_welcome()
        
        try:
            while True:
                user_input = Prompt.ask("\n[bold cyan]YOU[/bold cyan]")
                
                # Process commands
                cmd_result = await self.process_command(user_input)
                if cmd_result is False:  # Exit command
                    self.console.print("[yellow]Ending conversation...[/yellow]")
                    break
                elif cmd_result is True:  # Other command processed
                    continue
                
                # Get response from agent
                self.console.print("\n[bold green]ASSISTANT[/bold green]: ", end="")
                response = await self.get_response(user_input)
                
                # Format and display response
                self.console.print(Markdown(response))
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Exiting chat due to keyboard interrupt...[/yellow]")
        except Exception as e:
            self.console.print(f"[bold red]ERROR: {e}[/bold red]")
            traceback.print_exc()
        finally:
            await self.cleanup()
            self.console.print("[green]Cleanup complete. Goodbye![/green]")


async def main():
    """Main entry point"""
    app = MemoryChatApp()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())