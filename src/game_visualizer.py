"""Custom game visualizer with a high-tech terminal UI for Pure Adventure."""
import re

from rich.box import HEAVY, HEAVY_EDGE, MINIMAL, ROUNDED
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from openhands.sdk.conversation.visualizer.base import (
    ConversationVisualizerBase,
)
from openhands.sdk.event import (
    ActionEvent,
    MessageEvent,
    ObservationEvent,
)
from openhands.sdk.event.base import Event


def _create_console() -> Console:
    return Console(
        force_terminal=True,
        color_system="truecolor",
    )


# ── Colour palette ──────────────────────────────────────────────────────
C = {
    "accent": "cyan",
    "accent2": "bright_cyan",
    "heading": "bold bright_white",
    "dim": "bright_black",
    "thought": "bright_magenta",
    "reasoning": "italic bright_blue",
    "travel": "green",
    "party": "cyan",
    "npc": "yellow",
    "dialogue": "magenta",
    "action_call": "bold yellow",
    "result_prefix": "bold green",
    "error": "bold red",
    "game_over": "bold red",
}

# ── Parse helpers ───────────────────────────────────────────────────────

_SECTION_HEADERS = [
    "You can travel to:",
    "With you are:",
    "You can see:",
]

_LOC_OPT_RE = re.compile(r"^  (\d+) (.+)$")
_DLG_OPT_RE = re.compile(r"^  (\d+)\. (.+)$")
_OPTIONS_HEADER_RE = re.compile(r"^Options:$")


def _parse_game_text(
    text: str,
) -> tuple[
    Text | None,
    list[tuple[str, str]] | None,
    list[tuple[str, str]] | None,
    list[tuple[str, str]] | None,
    list[tuple[str, str]] | None,
    str | None,
]:
    """Parse game observation text into structured sections.

    Returns:
        (description, travel_options, party_options, npc_options,
         dialogue_options, dialogue_msg)
    """
    lines = text.split("\n")

    desc_lines: list[str] = []
    travel_opts: list[tuple[str, str]] = []
    party_opts: list[tuple[str, str]] = []
    npc_opts: list[tuple[str, str]] = []
    dialogue_opts: list[tuple[str, str]] = []
    dialogue_msg: str | None = None

    current_section: str | None = None
    in_dialogue_options = False

    for line in lines:
        stripped = line.strip()

        if _OPTIONS_HEADER_RE.match(stripped):
            in_dialogue_options = True
            continue

        if stripped in _SECTION_HEADERS:
            current_section = stripped
            desc_lines.append(stripped)
            continue

        m = _DLG_OPT_RE.match(line)
        if m and in_dialogue_options:
            dialogue_opts.append((m.group(1), m.group(2)))
            continue

        m = _LOC_OPT_RE.match(line)
        if m:
            label = m.group(2)
            if stripped == "What will you do?":
                continue
            if current_section == "You can travel to:":
                travel_opts.append((m.group(1), label))
            elif current_section == "With you are:":
                party_opts.append((m.group(1), label))
            elif current_section == "You can see:":
                npc_opts.append((m.group(1), label))
            else:
                travel_opts.append((m.group(1), label))
            continue

        if in_dialogue_options:
            dialogue_msg = (dialogue_msg or "") + line + "\n"
        else:
            desc_lines.append(line)

    desc_text = Text("\n".join(desc_lines).strip()) if desc_lines else None

    if desc_text:
        desc_text.highlight_regex(r"(You are in .+)", f"bold {C['accent']}")
        desc_text.highlight_regex(r"(Game Over\.)", C["game_over"])
        desc_text.highlight_regex(r"(END OF ACT 1)", "bold yellow")
        for hdr in _SECTION_HEADERS:
            desc_text.highlight_regex(re.escape(hdr), f"bold {C['dim']}")

    if dialogue_msg:
        dialogue_msg = dialogue_msg.strip()

    return (
        desc_text,
        travel_opts or None,
        party_opts or None,
        npc_opts or None,
        dialogue_opts or None,
        dialogue_msg,
    )


def _make_option_table(
    options: list[tuple[str, str]],
    num_color: str,
    label_color: str,
) -> Table:
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 1),
        collapse_padding=True,
    )
    table.add_column("Num", style=f"bold {num_color}", justify="right", width=3)
    table.add_column("Label", style=f"bold {label_color}")
    for num, label in options:
        table.add_row(num, label)
    return table


# ── Action display ─────────────────────────────────────────────────────

def _format_action_detail(event: ActionEvent) -> Table | Text:
    """Format the action as a clean key-value table instead of raw dump."""
    action = event.action
    data = action.model_dump()

    # Remove internal/irrelevant fields
    data.pop("kind", None)

    table = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
        collapse_padding=True,
    )
    table.add_column("Key", style=f"bold {C['accent2']}", width=14, no_wrap=True)
    table.add_column("Value", style="bold white")

    for key, value in data.items():
        if value is None or value == [] or value == {}:
            continue
        label = key.replace("_", " ").title()
        if isinstance(value, list):
            display = ", ".join(str(v) for v in value)
        elif isinstance(value, dict):
            display = ", ".join(f"{k}={v}" for k, v in value.items())
        else:
            display = str(value)
        table.add_row(label, display)

    return table


# ── Panel builders ──────────────────────────────────────────────────────

def _build_thought_panel(event: ActionEvent) -> Panel:
    """Build the agent reasoning + action panel."""
    parts: list[Text | Panel | Rule] = []

    # Thought/reasoning section
    thought_text = " ".join(t.text for t in event.thought) if event.thought else ""
    if thought_text:
        parts.append(Text(thought_text, style=C["thought"]))

    # Reasoning content (from reasoning models)
    if event.reasoning_content:
        parts.append(Text())
        parts.append(Rule(style=C["dim"]))
        parts.append(Text(event.reasoning_content, style=C["reasoning"]))

    # Action call details — custom clean formatting
    if event.action:
        parts.append(Text())
        parts.append(Rule(style=C["dim"]))
        # Action type header
        action_name = event.action.__class__.__name__
        parts.append(Text(f"⚡ {action_name}", style=f"bold {C['accent2']}"))
        parts.append(Text())
        parts.append(_format_action_detail(event))

    inner = Group(*parts) if parts else Text("(no reasoning logged)")

    return Panel(
        inner,
        title="[bold bright_magenta]🔍 Agent Reasoning",
        border_style="bright_magenta",
        box=ROUNDED,
        padding=(1, 2),
    )


def _build_observation_panel(text: str) -> Panel:
    """Build the game world panel from an observation."""
    (
        desc_text,
        travel_opts,
        party_opts,
        npc_opts,
        dialogue_opts,
        dialogue_msg,
    ) = _parse_game_text(text)

    inner_parts: list[Text | Panel | Table] = []

    # ── Description ──────────────────────────────────────────────────────
    if desc_text:
        inner_parts.append(desc_text)

    # ── Dialogue message ─────────────────────────────────────────────────
    if dialogue_msg:
        inner_parts.append(Text())
        inner_parts.append(
            Panel(
                Text(dialogue_msg, style="italic bright_white"),
                title="[bold magenta]💬 Dialogue",
                border_style="magenta",
                box=ROUNDED,
                padding=(1, 2),
            )
        )

    # ── Section: Travel destinations ─────────────────────────────────────
    if travel_opts:
        inner_parts.append(Text())
        inner_parts.append(
            Panel(
                _make_option_table(travel_opts, C["travel"], "bold white"),
                title=f"[bold green]🗺 Travel",
                border_style=C["travel"],
                box=HEAVY_EDGE,
                padding=(0, 1),
                expand=False,
            )
        )

    # ── Section: Party members ───────────────────────────────────────────
    if party_opts:
        inner_parts.append(Text())
        inner_parts.append(
            Panel(
                _make_option_table(party_opts, C["party"], "bold white"),
                title=f"[bold cyan]👥 Party",
                border_style=C["party"],
                box=HEAVY_EDGE,
                padding=(0, 1),
                expand=False,
            )
        )

    # ── Section: NPCs at location ────────────────────────────────────────
    if npc_opts:
        inner_parts.append(Text())
        inner_parts.append(
            Panel(
                _make_option_table(npc_opts, C["npc"], "bold white"),
                title=f"[bold yellow]👤 Characters",
                border_style=C["npc"],
                box=HEAVY_EDGE,
                padding=(0, 1),
                expand=False,
            )
        )

    # ── Section: Dialogue options ────────────────────────────────────────
    if dialogue_opts:
        inner_parts.append(Text())
        inner_parts.append(
            Panel(
                _make_option_table(
                    dialogue_opts, C["dialogue"], "bold white"
                ),
                title=f"[bold magenta]💬 Choose Response",
                border_style=C["dialogue"],
                box=HEAVY_EDGE,
                padding=(0, 1),
                expand=False,
            )
        )

    # Nothing parsed? Show raw text as fallback
    if not inner_parts and text.strip():
        inner_parts.append(Text(text.strip()))

    inner = Group(*inner_parts) if inner_parts else Text("(empty)")

    # Check for game over
    subtitle = None
    if "Game Over." in text:
        subtitle = f"[{C['game_over']}]💀 GAME OVER[/{C['game_over']}]"

    return Panel(
        inner,
        title=f"[bold {C['accent']}]🎮 Game State[/bold {C['accent']}]",
        subtitle=subtitle,
        border_style=C["accent"],
        box=HEAVY,
        padding=(1, 2),
    )


class GameVisualizer(ConversationVisualizerBase):
    """Custom visualizer that renders the game with a high-tech terminal UI.

    Event flow per turn:
      1. ActionEvent → Agent Reasoning panel (shows thought + tool call)
      2. ObservationEvent → Game State panel (shows world + options)
    """

    _console: Console

    def __init__(self):
        super().__init__()
        self._console = _create_console()

    def on_event(self, event: Event) -> None:
        if isinstance(event, ObservationEvent):
            if event.tool_name == "game":
                self._console.print(
                    _build_observation_panel(event.observation.text)
                )
                self._console.print()
            else:
                self._console.print(
                    Panel(
                        Text(event.observation.text),
                        title=f"[bold yellow]Tool: {event.tool_name}",
                        border_style="yellow",
                        box=ROUNDED,
                        padding=(1, 2),
                    )
                )
                self._console.print()

        elif isinstance(event, ActionEvent):
            # Always render a clean action → result pair.
            # The action panel shows what the AI was thinking + what it chose.
            self._print_turn_separator()
            self._console.print(_build_thought_panel(event))
            self._console.print()

        elif isinstance(event, MessageEvent):
            if event.source == "user":
                self._console.print(
                    Panel(
                        Text(
                            event.llm_message.content[0].text
                            if event.llm_message.content
                            else "",
                            style="gold3",
                        ),
                        title="[bold gold3]📩 User Message",
                        border_style="gold3",
                        box=ROUNDED,
                        padding=(1, 2),
                    )
                )
                self._console.print()

    def _print_turn_separator(self) -> None:
        """Print a subtle divider between game turns."""
        self._console.print(
            Panel(
                Text("", style=C["dim"]),
                box=MINIMAL,
                padding=(0, 0),
                border_style=C["dim"],
                height=1,
            )
        )
