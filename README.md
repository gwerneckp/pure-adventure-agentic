# Pure Adventure — Agentic

An AI agent that plays through the **Pure Adventure** text-based mystery game,
built with the [OpenHands SDK](https://docs.openhands.dev/).

## Background

This project is a **Python rewrite** of a university coursework project
originally written in Haskell at the **University of Bath** for a functional
programming course.

### The Original

The [`original-haskell/`](original-haskell/) directory contains the Haskell
source as submitted for coursework. It included a BFS solver that could play
through the game autonomously — the functional programming counterpart to
this LLM agent.

### The Python Rewrite

The Python version (`src/`) was built from scratch to:

- Replace the hand-written BFS solver with an **LLM agent** (any model
  supported by OpenHands SDK) that reads the game output, thinks
  strategically, and chooses its own actions.
- Collapse the Haskell module structure into a **single‑file engine**
  (`engine.py`) that handles all game logic: world model, dialogue system,
  state transitions, and BFS pathfinding (kept as a utility).
- Provide a **tool interface** (`tool.py`) that exposes game actions
  (`choice`, `status`, `reset`, `quit`) to the agent as OpenHands tools.
- Wrap everything in an **entry point** (`run.py`) that configures the
  LLM, launches the agent, and feeds it the system prompt.

## Project Structure

```
├── src/                        # Python: game engine + agent
│   ├── engine.py               # Game state, world model, dialogue system
│   ├── tool.py                 # OpenHands SDK tool definitions
│   └── run.py                  # Agent entry point (LLM config, prompt)
├── original-haskell/           # Original Haskell coursework
│   ├── src/                    #   Haskell source (Types, GameWorld,
│   │                           #   Dialogue, GameLoop, Solver, …)
│   └── test/                   #   Haskell test suite (Hspec)
├── tests/                      # Python test suite
├── scripts/                    # Helper scripts
├── pyproject.toml              # Project metadata & dependencies
├── requirements.txt            # Pip dependencies
└── .env                        # LLM API key (LLM_API_KEY)
```

## Setup

```bash
# Create a .env file with your LLM provider:
echo "LLM_API_KEY=sk-…" > .env
echo "LLM_MODEL=deepseek/deepseek-chat" >> .env    # or any OpenHands-compatible model

# Install dependencies
pip install -r requirements.txt
# or: uv sync

# Run the agent
python src/run.py
```

The agent will play through the game autonomously, choosing where to
travel, who to talk to, and figuring out the win condition.


## Game

Pure Adventure is a mystery set in the town of **Error**. The player
explores locations — Home, Brewpub, Hotel, Temple, Takeaway, and more —
talks to characters, recruits party members, and uncovers a plot that
requires assembling a team of logicians. The game is driven entirely by
a dialogue tree written in a custom DSL embedded in `engine.py`.

## License

AGPL-3.0 — see [`LICENSE`](LICENSE). The original Haskell coursework
retains whatever license it was submitted under.
