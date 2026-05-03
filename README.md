# Adventure Game — Agentic Play

AI agent that plays through the Pure Adventure Haskell text game,
using the OpenHands SDK.

## Structure

```
├── src/                    # Python game engine + agent
│   ├── engine.py           # Game state, dialogue system, world model
│   ├── tool.py             # OpenHands SDK tool wrapper
│   └── run.py              # Entry point — launches the agent
├── original-haskell/       # Original Haskell implementation
│   ├── src/                # Haskell source files
│   └── test/               # Haskell test suite
├── tests/                  # Python tests
├── docs/                   # Documentation
└── scripts/                # Helper scripts
```

## Running

```bash
cd src
python run.py
```
