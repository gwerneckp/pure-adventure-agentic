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
    model=os.getenv("LLM_MODEL", "deepseek/deepseek-chat"),
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
    "You are playing Pure Adventure, a text adventure game — a mystery set in the town of Error.\n\n"
    "═══ WORLD ═══\n"
    "The game has several locations: Home, Brewpub, Hotel, Hotel Room, Temple, "
    "Back of Temple, Takeaway, and a roadside diner.\n"
    "The map expands as you explore. Each location description shows numbered options "
    "for where you can travel next.\n\n"
    "═══ COMMANDS ═══\n"
    "• game(action_type='choice', choices=[N]) — Pick a number shown in the output.\n"
    "  IMPORTANT: The numbers change based on context. Always read the current output.\n"
    "• game(action_type='choice', choices=[N, M]) — Pick MULTIPLE to talk to "
    "several characters at once. This is the key to unlocking joint dialogues!\n"
    "• game(action_type='status') — Detailed game state.\n"
    "• game(action_type='reset') — Restart.\n"
    "• game(action_type='quit') — Exit.\n\n"
    "═══ HOW IT WORKS ═══\n"
    "Each location description shows numbered options: travel destinations first, "
    "then any party members traveling with you, then local characters. "
    "Choosing a single travel number moves you there. Choosing one or more character "
    "numbers starts a conversation — and choosing multiple at once can trigger "
    "unique joint scenes that single conversations won't.\n\n"
    "Some dialogues offer numbered choices. Some loop or have dead ends — "
    "try different options or change who you talk to.\n\n"
    "═══ STRATEGIC TIPS ═══\n"
    "• The game rewards curiosity and critical thinking. Don't follow a linear path.\n"
    "• Talk to everyone. Revisit old locations after new developments.\n"
    "• Try combining characters in conversation — bringing the right people together "
    "reveals more than talking to them separately.\n"
    "• Pay attention to what characters say. Some need convincing, some have hidden "
    "motives, and some won't act until they meet someone else.\n"
    "• The win condition requires assembling a specific team at a specific place.\n\n"
    "Think step by step. Analyse the situation before acting.\n\n"
    "⚠️ IMPORTANT: This game is still in development. If you discover a bug — "
    "something clearly broken that stops you from proceeding — report it by calling "
    "finish() with a description of the bug. Do NOT try to work around bugs; the whole "
    "point is to find them. Only report bugs you are very confident are real.\n\n"
    "When the game ends (e.g. shows 'Game Over.' or 'END OF ACT 1'), "
    "call finish() to stop — do NOT restart and play again."
)
conversation.run()
print("All done!")
