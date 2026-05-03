from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Add src directory to path so imports work
sys.path.insert(0, str(Path(__file__).parent))

# Load .env from project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.sdk.tool import register_tool

from tool import GameTool

# Register the custom tool
register_tool("GameTool", GameTool)

llm = LLM(
    model="deepseek/deepseek-chat",
    api_key=os.getenv("LLM_API_KEY"),
    reasoning_effort=None,
    extended_thinking_budget=None,
)

agent = Agent(
    llm=llm,
    tools=[Tool(name="GameTool")],
)

cwd = str(Path(__file__).parent.parent)
conversation = Conversation(agent=agent, workspace=cwd)

conversation.send_message(
    "You are playing Pure Adventure, a text adventure game.\n\n"
    "═══ WORLD ═══\n"
    "Locations: Home (0), Brewpub (1), Hotel (2), Hotel Room n+1 (3), "
    "Temple (4), Back of Temple (5), Takeaway (6), I-50 (7).\n"
    "Traveling to any connected location costs nothing — just pick its number.\n\n"
    "═══ YOUR MISSION ═══\n"
    "Something dangerous is stirring in Error. An old friend has a plan "
    "that requires assembling a team of logicians. Talk to everyone — "
    "some characters need convincing, others may need to talk to each other.\n\n"
    "To advance, you'll need to:\n"
    "• Recruit party members into your group\n"
    "• Travel to new locations (the map expands as you make progress)\n"
    "• Talk to multiple characters at the same time to trigger joint dialogues\n"
    "• Find the win condition — it involves three specific characters at one location\n\n"
    "═══ COMMANDS ═══\n"
    "• game(action_type='choice', choices=[N]) — Pick any number shown in the output.\n"
    "  You can pick MULTIPLE numbers to talk to multiple people at once!\n"
    "  Example: choices=[4, 5] talks to both #4 and #5 together.\n"
    "• game(action_type='status') — Detailed game state.\n"
    "• game(action_type='reset') — Restart the game.\n"
    "• game(action_type='quit') — Exit the game.\n\n"
    "Think step by step. Some dialogues loop or have dead ends — try different options.\n\n"
    "⚠️ IMPORTANT: This game is still in development. If you discover a bug — "
    "something clearly broken that stops you from proceeding — report it by calling "
    "finish() with a description of the bug. Do NOT try to work around bugs; the whole "
    "point is to find them. Only report bugs you are very confident are real.\n\n"
    "When the game ends (e.g. shows 'Game Over.' or 'END OF ACT 1'), "
    "call finish() to stop — do NOT restart and play again."
)
conversation.run()
print("All done!")
