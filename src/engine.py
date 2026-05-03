"""Pure Python reimplementation of the Pure Adventure Haskell game.

Model: Game(map, location, party, npcs_at_nodes)  — maps to Haskell's:
  Game Map Node Party [Party]
where Map = list of undirected edges (n1, n2), Party = sorted list of character names.

Win condition: Game state becomes None (Over).
"""
from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass, field
from functools import cache
from typing import Callable

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

Map = list[tuple[int, int]]
Party = list[str]
Event = Callable[["Game"], "Game | None"]


@dataclass(frozen=True)
class Game:
    m: Map = field(default_factory=list)
    loc: int = 0
    party: Party = field(default_factory=list)
    npcs: list[Party] = field(default_factory=list)

    def copy(self, **kwargs) -> Game:
        d = {"m": list(self.m), "loc": self.loc, "party": list(self.party), "npcs": [list(p) for p in self.npcs]}
        d.update(kwargs)
        return Game(**d)


# ---------------------------------------------------------------------------
# World helpers
# ---------------------------------------------------------------------------

def connected(m: Map, node: int) -> list[int]:
    return sorted({b if a == node else a for a, b in m if node in (a, b)})


def connect(n1: int, n2: int, m: Map) -> Map:
    if n1 == n2:
        return m
    pair = (min(n1, n2), max(n1, n2))
    if pair in m:
        return m
    return sorted(m + [pair])


def disconnect(n1: int, n2: int, m: Map) -> Map:
    pair = (min(n1, n2), max(n1, n2))
    return [p for p in m if p != pair]


def msort(xs: list) -> list:
    return sorted(xs)


def merge(xs: list, ys: list) -> list:
    i = j = 0
    result = []
    while i < len(xs) and j < len(ys):
        if xs[i] < ys[j]:
            result.append(xs[i])
            i += 1
        elif xs[i] == ys[j]:
            result.append(xs[i])
            i += 1
            j += 1
        else:
            result.append(ys[j])
            j += 1
    result.extend(xs[i:])
    result.extend(ys[j:])
    return result


# ---------------------------------------------------------------------------
# Events (state transitions)
# ---------------------------------------------------------------------------

def add(p: Party) -> Event:
    def _add(g: Game) -> Game | None:
        if g is None:
            return None
        return g.copy(party=msort(g.party + p))
    return _add


def add_at(n: int, p: Party) -> Event:
    def _add_at(g: Game) -> Game | None:
        if g is None:
            return None
        npcs = [list(pp) for pp in g.npcs]
        npcs[n] = msort(npcs[n] + p)
        return g.copy(npcs=npcs)
    return _add_at


def add_here(p: Party) -> Event:
    def _add_here(g: Game) -> Game | None:
        return add_at(g.loc, p)(g) if g else None
    return _add_here


def remove(p: Party) -> Event:
    def _remove(g: Game) -> Game | None:
        if g is None:
            return None
        return g.copy(party=[c for c in g.party if c not in p])
    return _remove


def remove_at(n: int, p: Party) -> Event:
    def _remove_at(g: Game) -> Game | None:
        if g is None:
            return None
        npcs = [list(pp) for pp in g.npcs]
        npcs[n] = [c for c in npcs[n] if c not in p]
        return g.copy(npcs=npcs)
    return _remove_at


def remove_here(p: Party) -> Event:
    def _remove_here(g: Game) -> Game | None:
        return remove_at(g.loc, p)(g) if g else None
    return _remove_here


def update_map(f: Callable[[Map], Map]) -> Event:
    def _update_map(g: Game) -> Game | None:
        if g is None:
            return None
        return g.copy(m=f(g.m))
    return _update_map


def compose(*events: Event) -> Event:
    """Compose events right-to-left (like Haskell's .).
    
    compose(f, g, h)(x) = f(g(h(x)))
    """
    def _composed(g: Game) -> Game | None:
        if g is None:
            return None
        result = g
        for ev in reversed(events):
            result = ev(result)
            if result is None:
                return None
        return result
    return _composed


# ---------------------------------------------------------------------------
# Locations & descriptions & characters
# ---------------------------------------------------------------------------

LOCATIONS = [
    "Home",                       # 0
    "Brewpub",                    # 1
    "Hotel",                      # 2
    "Hotel room n+1",            # 3
    "Temple",                     # 4
    "Back of temple",            # 5
    "Takeaway",                   # 6
    "The I-50",                   # 7
]

DESCRIPTIONS = [
    "your own home. It is very cosy.",
    "the `Non Tertium Non Datur' Brewpub & Barber's.",
    "the famous Logicester Hilbert Hotel & Resort.",
    "front of Room n+1 in the Hilbert Hotel & Resort. You knock.",
    "the Temple of Linearity, Logicester's most famous landmark, designed by Le Computier.",
    "the back yard of the temple. You see nothing but a giant pile of waste paper.",
    "Curry's Indian Takeaway, on the outskirts of Logicester.",
    "a car on the I-50 between Logicester and Computerborough. The road is blocked by a large, threatening mob.",
]

NPC_AT = [
    ["Bertrand Russell"],                  # 0 Home
    ["Arend Heyting", "Luitzen Brouwer"],  # 1 Brewpub
    ["David Hilbert"],                      # 2 Hotel
    ["William Howard"],                     # 3 Hotel room n+1
    ["Jean-Yves Girard"],                   # 4 Temple
    [],                                     # 5 Back of temple
    ["Haskell Curry", "Jean-Louis Krivine"],# 6 Takeaway
    ["Gottlob Frege"],                      # 7 I-50
]


def make_start() -> Game:
    return Game(m=[(1, 2), (1, 6), (2, 4)], loc=0, party=[], npcs=[list(p) for p in NPC_AT])


# ---------------------------------------------------------------------------
# Dialogue system
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Dialogue:
    pass


@dataclass(frozen=True)
class ActionD(Dialogue):
    msg: str
    event: Event


@dataclass(frozen=True)
class BranchD(Dialogue):
    cond: Callable[[Game], bool]
    then: Dialogue
    els: Dialogue


@dataclass(frozen=True)
class ChoiceD(Dialogue):
    msg: str
    options: list[tuple[str, Dialogue]]


# ---------------------------------------------------------------------------
# Dialogue helper / state queries
# ---------------------------------------------------------------------------

def always(g: Game = None) -> bool:
    return True


def here(g: Game) -> int:
    return g.loc if g else 0


def is_at(n: int, c: str, g: Game) -> bool:
    return g is not None and c in g.npcs[n]


def in_party(c: str, g: Game) -> bool:
    return g is not None and c in g.party


def is_connected(i: int, j: int, g: Game) -> bool:
    return g is not None and (min(i, j), max(i, j)) in g.m


def end(msg: str) -> ChoiceD:
    return ChoiceD(msg, [])


# ---------------------------------------------------------------------------
# Build the full dialogue tree for a given party (mirrors theDialogues)
# ---------------------------------------------------------------------------

def build_dialogues():
    """Return a list of (party, dialogue) pairs matching the Haskell GameData."""
    dialogues: list[tuple[Party, Dialogue]] = []

    # --- Russell (home, first meeting) ---
    dialogues.append((
        ["Russell"],
        ChoiceD(
            "Russell: Let's go on an adventure!",
            [
                ("Sure.", end("You pack your bags and go with Russell.")),
                ("Maybe later.", end("Russell looks disappointed.")),
            ],
        ),
    ))

    # --- Heyting + Russell at brewpub ---
    dialogues.append((
        ["Heyting", "Russell"],
        end("Heyting: Hi Russell, what are you drinking?\nRussell: The strong stuff, as usual."),
    ))

    # --- Bertrand Russell (main recruiter) ---
    def make_russell():
        intro = (
            "A tall, slender, robed character approaches your home. When he gets closer, you recognise him as "
            "Bertrand Russell, an old friend you haven't seen in ages. You invite him in.\n\n"
            "Russell: I am here with an important message. The future of Excluded-Middle Earth hangs in the balance. "
            "The dark forces of the Imperator are stirring, and this time, they might not be contained.\n\n"
            "Do you recall the artefact you recovered in your quest in the forsaken land of Error? The Loop, the "
            "One Loop, the Loop of Power? It must be destroyed. I need you to bring together a team of our finest "
            "Logicians, to travel deep into Error and cast the Loop into lake Bottom. It is the only way to terminate it."
        )

        re2_action: Event = compose(add(["Bertrand Russell"]), remove_here(["Bertrand Russell"]), update_map(lambda m: connect(1, 0, m)))
        re2 = ("Let's go!", ActionD("Let's put our team together and head for Error.", re2_action))

        re1_inner = (
            "What is the power of the Loop?",
            ChoiceD(
                "Russell: for you, if you put it on, you become referentially transparent. "
                "For the Imperator, there is no end to its power. If he gets it in his possession, he will vanquish us all.",
                [re2],
            ),
        )

        return BranchD(
            lambda g: is_at(0, "Bertrand Russell", g),
            ChoiceD(intro, [re1_inner, re2]),
            BranchD(
                lambda g: here(g) == 7,
                end("Russell: Let me speak to him and Brouwer."),
                end("Russell: We should put our team together and head for Error."),
            ),
        )

    dialogues.append((["Bertrand Russell"], make_russell()))

    # --- Arend Heyting ---
    dialogues.append((
        ["Arend Heyting"],
        ChoiceD(
            "Heyting: What can I get you?",
            [
                ("A pint of Ex Falso Quodbibet, please.", end("There you go.")),
                ("The Hop Erat Demonstrandum, please.", end("Excellent choice.")),
                ("Could I get a Maltus Ponens?", end("Mind, that's a strong one.")),
            ],
        ),
    ))

    # --- Luitzen Brouwer ---
    def make_brouwer():
        help_action: Event = compose(add(["Luitzen Brouwer"]), remove_here(["Luitzen Brouwer"]))
        return BranchD(
            lambda g: is_at(1, "Luitzen Brouwer", g),
            ChoiceD(
                "Brouwer: Haircut?",
                [
                    (
                        "Please.",
                        ChoiceD(
                            "Brouwer is done and holds up the mirror. You notice that one hair is standing up straight.",
                            [
                                (
                                    "There's just this one hair sticking up. Could you comb it flat, please?",
                                    ChoiceD(
                                        "Brouwer is done and holds up the mirror. You notice that one hair is standing up straight.",
                                        [("Thanks, it looks great.", end("Brouwer: You're welcome."))],
                                    ),
                                ),
                                ("Thanks, it looks great.", end("Brouwer: You're welcome.")),
                            ],
                        ),
                    ),
                    (
                        "Actually, could you do a close shave?",
                        end("Of course. I shave everyone who doesn't shave themselves."),
                    ),
                    (
                        "I'm really looking for help.",
                        ChoiceD(
                            "Brouwer: Hmmm. What with? Is it mysterious?",
                            [
                                (
                                    "Ooh yes, very. And dangerous.",
                                    ActionD("Brouwer: I'm in!", help_action),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
            end("Nothing"),
        )

    dialogues.append((["Luitzen Brouwer"], make_brouwer()))

    # --- David Hilbert ---
    def make_hilbert():
        return BranchD(
            lambda g: not is_connected(2, 3, g),
            ChoiceD(
                "You wait your turn in the queue. The host, David Hilbert, puts up the first guest in Room 1, "
                "and points the way to the stairs.\n\nYou seem to hear that the next couple are also put up in "
                "Room 1. You decide you must have misheard. It is your turn next.\n\nHilbert: Lodging and breakfast? "
                "Room 1 is free.",
                [
                    (
                        "Didn't you put up the previous guests in Room 1, too?",
                        ChoiceD(
                            "Hilbert: I did. But everyone will move up one room to make room for you if necessary. "
                            "There is always room at the Hilbert Hotel & Resort.",
                            [
                                (
                                    "But what about the last room? Where do the guests in the last room go?",
                                    ChoiceD(
                                        "Hilbert: There is no last room. There are always more rooms.",
                                        [
                                            (
                                                "How can there be infinite rooms? Is the hotel infinitely long?",
                                                ChoiceD(
                                                    "Hilbert: No, of course not! It was designed by the famous architect "
                                                    "Zeno Hadid. Every next room is half the size of the previous.",
                                                    [
                                                        (
                                                            "Actually, I am looking for someone.",
                                                            ActionD(
                                                                "Hilbert: Yes, someone is staying here. You'll find them "
                                                                "in Room n+1. Through the doors over there, up the stairs, "
                                                                "then left.",
                                                                update_map(lambda m: connect(2, 3, m)),
                                                            ),
                                                        ),
                                                    ],
                                                ),
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ),
                    (
                        "Actually, I am looking for someone.",
                        ActionD(
                            "Hilbert: Yes, someone is staying here. You'll find them in Room n+1. Through the doors "
                            "over there, up the stairs, then left.",
                            update_map(lambda m: connect(2, 3, m)),
                        ),
                    ),
                ],
            ),
            end("Hilbert seems busy. You hear him muttering to himself: Problems, problems, nothing but problems. "
                "You decide he has enough on his plate and leave."),
        )

    dialogues.append((["David Hilbert"], make_hilbert()))

    # --- William Howard ---
    def make_howard():
        return BranchD(
            lambda g: is_at(3, "William Howard", g),
            ChoiceD(
                "Howard: Yes? Are we moving up again?",
                [
                    (
                        "Quick, we need your help. We need to travel to Error.",
                        ActionD(
                            "Howard: Fine. My bags are packed anyway, and this room is tiny. Let's go!",
                            compose(add(["William Howard"]), remove_at(3, ["William Howard"])),
                        ),
                    ),
                ],
            ),
            BranchD(
                lambda g: is_at(6, "William Howard", g),
                ChoiceD(
                    "Howard: What can I get you?",
                    [
                        ("The Lambda Rogan Josh with the Raita Monad for starter, please.", end("Coming right up.")),
                        (
                            "The Vindaloop with NaN bread on the side.",
                            ChoiceD("Howard: It's quite spicy.", [("I can handle it.", end("Excellent."))]),
                        ),
                        ("The Chicken Booleani with a stack of poppadums, please.", end("Good choice.")),
                    ],
                ),
                end("Howard: We need to find Curry. He'll know the way."),
            ),
        )

    dialogues.append((["William Howard"], make_howard()))

    # --- Jean-Yves Girard ---
    dialogues.append((
        ["Jean-Yves Girard"],
        BranchD(
            lambda g: is_connected(4, 5, g),
            end("You have seen enough here."),
            ActionD(
                "Raised on a large platform in the centre of the temple, Girard is preaching the Linearity Gospel. "
                "He seems in some sort of trance, so it is hard to make sense of, but you do pick up some interesting "
                "snippets. `Never Throw Anything Away' - you gather they must be environmentalists - `We Will Solve "
                "Church's Problems', `Only This Place Matters'... Perhaps, while he is speaking, now is a good time "
                "to take a peek behind the temple...",
                update_map(lambda m: connect(4, 5, m)),
            ),
        ),
    ))

    # --- Vending machine ---
    dialogues.append((
        ["Vending machine"],
        ChoiceD(
            "The walls of the Temple of Linearity are lined with vending machines. Your curiosity gets the better "
            "of you, and you inspect one up close. It sells the following items:",
            [
                ("Broccoli", end("You don't like broccoli.")),
                ("Mustard", end("It might go with the broccoli.")),
                ("Watches", end("They seem to have a waterproof storage compartment. Strange.")),
                ("Camels", end("You don't smoke, but if you did...")),
                ("Gauloises", end("You don't smoke, but if you did...")),
            ],
        ),
    ))

    # --- Jean-Louis Krivine ---
    dialogues.append((
        ["Jean-Louis Krivine"],
        end("Looking through the open kitchen door, you see the chef doing the dishes. He is rinsing and stacking "
            "plates, but it's not a very quick job because he only has one stack. You also notice he never passes any "
            "plates to the front. On second thought, that makes sense - it's a takeaway, after all, and everything is "
            "packed in cardboard boxes. He seems very busy, so you decide to leave him alone."),
    ))

    # --- Haskell Curry ---
    def make_curry():
        return BranchD(
            lambda g: is_at(6, "Haskell Curry", g),
            ChoiceD(
                "Curry: What can I get you?",
                [
                    ("The Lambda Rogan Josh with the Raita Monad for starter, please.", end("Coming right up.")),
                    (
                        "The Vindaloop with NaN bread on the side.",
                        ChoiceD("Curry: It's quite spicy.", [("I can handle it.", end("Excellent."))]),
                    ),
                    ("The Chicken Booleani with a stack of poppadums, please.", end("Good choice.")),
                    (
                        "Actually, I am looking for help getting to Error.",
                        end("Curry: Hmm. I may be able to help, but I'll need to speak to William Howard."),
                    ),
                ],
            ),
            end("Nothing"),
        )

    dialogues.append((["Haskell Curry"], make_curry()))

    # --- Haskell Curry + William Howard ---
    def make_curry_howard():
        def action(g: Game) -> Game | None:
            g = add(["Haskell Curry"])(g)
            g = remove_at(6, ["Haskell Curry"])(g)
            g = add_at(6, ["William Howard"])(g)
            g = remove(["William Howard"])(g)
            g = update_map(lambda m: connect(6, 7, m))(g)
            return g

        return BranchD(
            lambda g: not is_connected(6, 7, g),
            ActionD(
                "Curry:  You know the way to Error, right?\nHoward: I thought you did?\n"
                "Curry:  Not really. Do we go via Computerborough?\n"
                "Howard: Yes, I think so. Is that along the I-50?\n"
                "Curry:  Yes, third exit. Shall I go with them?\n"
                "Howard: Sure. I can watch the shop while you're away.",
                action,
            ),
            end("It's easy, just take the third exit on I-50."),
        )

    dialogues.append((["Haskell Curry", "William Howard"], make_curry_howard()))

    # --- Gottlob Frege ---
    dialogues.append((
        ["Gottlob Frege"],
        end("A person who appears to be the leader of the mob approaches your vehicle. When he gets closer, you "
            "recognise him as Gottlob Frege. You start backing away, and he starts yelling at you.\n\n"
            "Frege: Give us the Loop! We can control it! We can wield its power!\n\n"
            "You don't see a way forward. Perhaps Russell has a plan."),
    ))

    # --- Bertrand Russell + Gottlob Frege + Luitzen Brouwer (WIN CONDITION) ---
    def make_russell_frege_brouwer():
        r1_text = "You cannot control its power! Even the very wise cannot see all ends!"
        r2_text = "Brouwer, whom do you shave?"
        r3_text = "Frege, answer me this: DOES BROUWER SHAVE HIMSELF?"

        def win_action(g: Game) -> None:
            return None  # Game Over

        re3 = (
            r3_text,
            ActionD(
                "Frege opens his mouth to shout a reply. But no sound passes his lips. His eyes open wide in a look "
                "of bewilderment. Then he looks at the ground, and starts walking in circles, muttering to himself "
                "and looking anxiously at Russell. The mob is temporarily distracted by the display, uncertain what "
                "is happening to their leader, but slowly enclosing both Frege and Russell. Out of the chaos, "
                "Russell shouts:\n\nDRIVE, YOU FOOLS!\n\nYou floor it, and with screeching tires you manage to "
                "circle around the mob. You have made it across.\n\nEND OF ACT 1. To be continued...",
                win_action,
            ),
        )

        re2 = (
            r2_text,
            ChoiceD(
                "Brouwer: Those who do not shave themselves. Obviously. Why?\n\nRussell:",
                [re3],
            ),
        )

        re1 = (
            r1_text,
            ChoiceD(
                "Frege: I can and I will! The power is mine!\n\nRussell:",
                [re2, re3],
            ),
        )

        return ChoiceD(
            "Frege is getting closer, yelling at you to hand over the Loop, with the mob on his heels, slowly "
            "surrounding you. The tension in the car is mounting. But Russell calmly steps out to confront Frege.\n\nRussell:",
            [re1, re2, re3],
        )

    dialogues.append((["Bertrand Russell", "Gottlob Frege", "Luitzen Brouwer"], make_russell_frege_brouwer()))

    # --- Road trip (Russell + Curry + Brouwer at I-50) ---
    dialogues.append((
        ["Bertrand Russell", "Haskell Curry", "Luitzen Brouwer"],
        BranchD(
            lambda g: here(g) == 7,
            end("Road trip! Road trip! Road trip!"),
            end("Let's head for Error!"),
        ),
    ))

    return dialogues


DIALOGUES = build_dialogues()


# ---------------------------------------------------------------------------
# Dialogue engine
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DialogueStep:
    pass


@dataclass(frozen=True)
class DoAction(DialogueStep):
    msg: str
    event: Event


@dataclass(frozen=True)
class DeadEnd(DialogueStep):
    msg: str


@dataclass(frozen=True)
class ExitD(DialogueStep):
    pass


@dataclass(frozen=True)
class NeedChoice(DialogueStep):
    is_invalid: bool
    msg: str
    options: list[tuple[str, int]]  # (text, option_index)
    next_dlg: Dialogue | None = None  # dialogue context for next step_dialogue call


def dialogue_pure(g: Game, dlg: Dialogue, choice: int | None) -> tuple[DialogueStep, Game | None]:
    """Process dialogue without side effects.
    
    choice=None means first time / no input yet.
    choice=0 means exit dialogue.
    choice>0 means pick that option (1-based).
    Returns (step, new_game) where new_game may be updated (for ActionD).
    """
    if isinstance(dlg, ActionD):
        return DoAction(msg=dlg.msg, event=dlg.event), g

    if isinstance(dlg, BranchD):
        target = dlg.then if dlg.cond(g) else dlg.els
        result, g2 = dialogue_pure(g, target, choice)
        if isinstance(result, NeedChoice) and choice is None:
            # Only wrap when first entering (no choice yet) - re-evaluate BranchD on next call
            result = NeedChoice(is_invalid=result.is_invalid, msg=result.msg, options=result.options, next_dlg=dlg)
        return result, g2

    if isinstance(dlg, ChoiceD):
        if not dlg.options:
            return DeadEnd(msg=dlg.msg), g
        if choice is None:
            return NeedChoice(is_invalid=False, msg=dlg.msg, options=[(t, i + 1) for i, (t, _) in enumerate(dlg.options)], next_dlg=dlg), g
        if choice == 0:
            return ExitD(), g
        if 1 <= choice <= len(dlg.options):
            _, next_dlg = dlg.options[choice - 1]
            return dialogue_pure(g, next_dlg, None)
        return NeedChoice(is_invalid=True, msg=dlg.msg, options=[(t, i + 1) for i, (t, _) in enumerate(dlg.options)], next_dlg=dlg), g

    return DeadEnd(msg="Unknown dialogue type."), g


def find_dialogue(party: Party) -> Dialogue:
    for p, dlg in DIALOGUES:
        if sorted(p) == sorted(party):
            return dlg
    import sys as _sys
    print(f"DEBUG: No dialogue found for party={party}", file=_sys.stderr)
    return ActionD("There is nothing we can do.", lambda g: g)


# ---------------------------------------------------------------------------
# Game step (travel / talk logic)
# ---------------------------------------------------------------------------

def describe_location(g: Game) -> str:
    if g is None:
        return "Game Over."
    loc_name = LOCATIONS[g.loc]
    desc = DESCRIPTIONS[g.loc]
    lines = [f"You are in {loc_name}, {desc}"]

    conn = connected(g.m, g.loc)
    if conn:
        lines.append("You can travel to:")
        for i, n in enumerate(conn, 1):
            lines.append(f"  {i} {LOCATIONS[n]}")

    if g.party:
        lines.append("With you are:")
        for i, c in enumerate(g.party, len(conn) + 1):
            lines.append(f"  {i} {c}")

    npcs_here = g.npcs[g.loc]
    if npcs_here:
        lines.append("You can see:")
        start = len(conn) + len(g.party) + 1
        for i, c in enumerate(npcs_here, start):
            lines.append(f"  {i} {c}")

    lines.append("What will you do?")
    return "\n".join(lines)


def step(g: Game, choices: list[int]) -> tuple[Game | None, str | None, Dialogue | None, list[tuple[str, int]] | None]:
    """Process a game step.
    
    Returns: (new_game, message, dialogue_context, dialogue_options)
    - If travel: new_game is updated, message has result
    - If talk: returns dialogue to enter
    - If invalid: returns same game with error message
    """
    if g is None:
        return None, "Game Over.", None, None

    if not choices:
        return g, "No input.", None, None

    if choices == [0]:
        return None, "You quit the game.", None, None

    conn = connected(g.m, g.loc)
    total_opts = len(conn) + len(g.party) + len(g.npcs[g.loc])

    if any(n < 1 or n > total_opts for n in choices):
        return g, "[Unrecognized input]", None, None

    # Determine which options are travel, party, npcs
    conn_count = len(conn)
    party_count = len(g.party)

    moves = [c for c in choices if 1 <= c <= conn_count]
    party_choices = [c for c in choices if conn_count + 1 <= c <= conn_count + party_count]
    npc_choices = [c for c in choices if conn_count + party_count + 1 <= c <= total_opts]

    if len(moves) == 1 and not party_choices and not npc_choices:
        # Travel
        idx = moves[0] - 1
        target = conn[idx]
        new_g = g.copy(loc=target)
        loc_name = LOCATIONS[target]
        return new_g, f"You travel to {loc_name}.", None, None

    if not moves and (party_choices or npc_choices):
        # Talk
        party_names = [g.party[i - conn_count - 1] for i in party_choices]
        npc_names = [g.npcs[g.loc][i - conn_count - len(g.party) - 1] for i in npc_choices]
        all_names = msort(party_names + npc_names)
        dlg = find_dialogue(all_names)
        return g, None, dlg, None

    return g, "[Unrecognized input]", None, None


def step_dialogue(g: Game, dlg: Dialogue, choice: int | None) -> tuple[Game | None, str | None, Dialogue | None, list[tuple[str, int]] | None]:
    """Process a dialogue step.
    
    Returns: (new_game, message, next_dialogue, dialogue_options)
    """
    step_result, new_g = dialogue_pure(g, dlg, choice)

    if isinstance(step_result, DoAction):
        result_g = step_result.event(new_g)
        return result_g, step_result.msg, None, None

    if isinstance(step_result, DeadEnd):
        return g, step_result.msg, None, None

    if isinstance(step_result, ExitD):
        return g, None, None, None

    if isinstance(step_result, NeedChoice):
        return g, step_result.msg if not step_result.is_invalid else None, step_result.next_dlg, step_result.options

    return g, None, None, None


# ---------------------------------------------------------------------------
# BFS travel planner (mirrors Solver.hs)
# ---------------------------------------------------------------------------

def travel_bfs(g: Game, target_loc: int) -> list[int] | None:
    """BFS to find a path from current location to target_loc.
    Returns list of 1-based travel indices to follow, or None if unreachable.
    """
    if g is None:
        return None

    m = g.m
    start = g.loc
    if start == target_loc:
        return []

    queue: list[tuple[int, list[int]]] = [(start, [])]
    visited = {start}

    while queue:
        cur, path = queue.pop(0)
        nbrs = connected(m, cur)
        for i, nb in enumerate(nbrs, 1):
            if nb == target_loc:
                return path + [i]
            if nb not in visited:
                visited.add(nb)
                queue.append((nb, path + [i]))
    return None
