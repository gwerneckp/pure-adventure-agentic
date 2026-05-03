"""Adventure Game Tool - lets the AI play the Pure Adventure game."""
from collections.abc import Sequence
from typing import TYPE_CHECKING, Self

from openhands.sdk.tool.tool import (
    Action,
    Observation,
    ToolAnnotations,
    ToolDefinition,
    ToolExecutor,
)

from engine import (
    Game,
    describe_location,
    step_dialogue,
    step,
    make_start,
    connected,
    LOCATIONS,
)

if TYPE_CHECKING:
    from openhands.sdk.conversation.base import BaseConversation
    from openhands.sdk.conversation.state import ConversationState


class GameAction(Action):
    action_type: str
    choices: list[int] | None = None


class GameObservation(Observation):
    game_over: bool = False


class GameExecutor(ToolExecutor):
    def __init__(self):
        self.game: Game | None = make_start()
        self.current_dialogue = None

    def _show(self) -> GameObservation:
        """Show current view (location description or dialogue options)."""
        if self.current_dialogue is not None:
            g, msg, next_dlg, options = step_dialogue(self.game, self.current_dialogue, None)
            self.game = g
            self.current_dialogue = next_dlg
            parts = []
            if msg:
                parts.append(msg)
            if g is None:
                parts.append("Game Over.")
                return GameObservation.from_text("\n".join(parts), game_over=True)
            if next_dlg is None:
                parts.append(describe_location(g))
            elif options:
                opts_str = "\n".join(f"  {i}. {t}" for t, i in options)
                parts.append(f"Options:\n{opts_str}")
            return GameObservation.from_text("\n".join(parts))
        return GameObservation.from_text(describe_location(self.game))

    def __call__(
        self,
        action: GameAction,
        _conversation: "BaseConversation | None" = None,
    ) -> GameObservation:
        atype = action.action_type

        # Game lifecycle actions
        if atype == "reset":
            self.game = make_start()
            self.current_dialogue = None
            return GameObservation.from_text("Game reset. " + describe_location(self.game))

        if atype == "quit":
            self.game = None
            return GameObservation.from_text("You quit the game.", game_over=True)

        if self.game is None:
            return GameObservation.from_text("Game Over.", game_over=True)

        # View-only actions
        if atype == "look":
            self.current_dialogue = None
            return GameObservation.from_text(describe_location(self.game))

        if atype == "inventory":
            if self.game.party:
                return GameObservation.from_text("Party members:\n- " + "\n- ".join(self.game.party))
            return GameObservation.from_text("Your party is empty.")

        if atype == "status":
            conn = connected(self.game.m, self.game.loc)
            loc_names = ", ".join(LOCATIONS[n] for n in conn)
            party = ", ".join(self.game.party) if self.game.party else "(none)"
            npcs = ", ".join(self.game.npcs[self.game.loc]) if self.game.npcs[self.game.loc] else "(none)"
            return GameObservation.from_text(
                f"Location: {LOCATIONS[self.game.loc]} ({self.game.loc})\n"
                f"Connected to: {loc_names}\n"
                f"Party: {party}\n"
                f"NPCs here: {npcs}\n"
                f"Total map edges: {len(self.game.m)}"
            )

        # Unified choice action — handles travel, talk, AND dialogue
        # Just pick the number shown in the output and it does the right thing
        if atype in ("choice", "travel", "talk", "dialogue"):
            choices = action.choices or []

            if self.current_dialogue is not None and choices:
                # Active dialogue — pick an option
                g, msg, next_dlg, options = step_dialogue(self.game, self.current_dialogue, choices[0])
                self.game = g
                self.current_dialogue = next_dlg
                parts = []
                if msg:
                    parts.append(msg)
                if g is None:
                    parts.append("Game Over.")
                    return GameObservation.from_text("\n".join(parts), game_over=True)
                if next_dlg is None:
                    parts.append(describe_location(g))
                elif options:
                    opts_str = "\n".join(f"  {i}. {t}" for t, i in options)
                    parts.append(f"Options:\n{opts_str}")
                return GameObservation.from_text("\n".join(parts))

            # No active dialogue — use engine's unified step()
            g, msg, dlg, options = step(self.game, choices)
            self.game = g
            parts = []
            if msg:
                parts.append(msg)
            if g is None:
                parts.append("Game Over.")
                return GameObservation.from_text("\n".join(parts), game_over=True)
            if dlg is not None:
                # Entering dialogue — step into it
                self.current_dialogue = dlg
                g, msg, next_dlg, options = step_dialogue(self.game, dlg, None)
                self.game = g
                self.current_dialogue = next_dlg
                if msg:
                    parts.append(msg)
                if next_dlg is None:
                    parts.append(describe_location(g))
                elif options:
                    opts_str = "\n".join(f"  {i}. {t}" for t, i in options)
                    parts.append(f"Options:\n{opts_str}")
            else:
                self.current_dialogue = None
                parts.append(describe_location(g))
            return GameObservation.from_text("\n".join(parts))

        return GameObservation.from_text(f"Unknown action: {atype}")


class GameTool(ToolDefinition[GameAction, GameObservation]):
    @classmethod
    def create(
        cls,
        conv_state: "ConversationState | None" = None,
        **params,
    ) -> Sequence[Self]:
        return [
            cls(
                description=(
                    "Play the Pure Adventure text game. "
                    "Just use action_type='choice' with choices=[N] where N is any number shown in the game output. "
                    "The game automatically handles travel, talking to NPCs, or dialogue responses based on what you pick. "
                    "Also available: 'status' (detailed state), 'reset' (restart), 'quit' (exit)."
                ),
                action_type=GameAction,
                observation_type=GameObservation,
                executor=GameExecutor(),
                annotations=ToolAnnotations(
                    title="game",
                    readOnlyHint=False,
                ),
            )
        ]
