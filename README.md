# T.A.R.A

T.A.R.A. — Personal AI Assistant

> *"Your personal AI assistant, serving Devansh Raghuvanshi"*

A personal AI assistant split into two cooperating pieces:

| Component | What it is |
|-----------|-----------|
| **MCP Server** (`uv run tara`) | A [FastMCP](https://github.com/jlowin/fastmcp) server that exposes tools (news, web search, system info, …) over SSE. The backend that does the actual work. |
| **Voice Agent** (`uv run tara_voice`) | A [LiveKit Agents](https://github.com/livekit/agents) voice pipeline that listens to your microphone, reasons with an LLM (Gemini 2.5 Flash), and speaks back with Sarvam TTS — all while pulling tools from the MCP server in real time. |

## How it works

Microphone ──► STT (Sarvam Saaras v3)
│
▼
LLM (Gemini 2.5 Flash)  ◄──────► MCP Server (FastMCP / SSE)
│                              ├─ get_world_news
▼                              ├─ open_world_monitor
TTS (Sarvam Bulbul v3)                     ├─ search_web
│                              └─ …more tools
▼
Speaker / LiveKit room

The voice agent connects to the MCP server via SSE at `http://127.0.0.1:8000/sse`.

---

## Project structure

Tara/
├── server.py           # uv run tara  → starts the MCP server (SSE on :8000)
├── agent_tara.py       # uv run tara_voice → starts the LiveKit voice agent
├── clap_wake.py        # clap-to-wake feature — clap to start a TARA session
├── pyproject.toml
├── .env.example        # copy → .env and fill in your keys
│
└── tara/               # MCP server package
├── config.py       # env-var loading & app-wide settings
├── tools/          # MCP tools (callable by the LLM)
│   ├── web.py      # search_web, fetch_url, get_world_news, open_world_monitor
│   ├── system.py   # get_current_time, get_system_info
│   └── utils.py    # format_json, word_count
├── prompts/        # MCP prompt templates
└── resources/      # MCP resources exposed to clients (tara://info)

---

## Quick start

### 1. Prerequisites

- Python ≥ 3.11
- [`uv`](https://github.com/astral-sh/uv) — `pip install uv`
- A [LiveKit Cloud](https://cloud.livekit.io) project (free tier works)

### 2. Set up environment

```bash
cp .env.example .env
# Open .env and fill in your API keys (see the section below)
```

### 3. Run — two terminals

**Terminal 1 — MCP server** (must start first)

```bash
uv run tara
```

Starts the FastMCP server on `http://127.0.0.1:8000/sse`.

**Terminal 2 — Voice agent**

```bash
uv run tara_voice
```

Starts the LiveKit voice agent in **dev mode**. Open the [LiveKit Agents Playground](https://agents-playground.livekit.io) and connect to your room to talk to TARA.

**Optional — Clap to Wake**

```bash
uv run python clap_wake.py
```

Clap loudly to wake up T.A.R.A. and start a voice session automatically!


## `uv run tara` vs `uv run tara_voice`

| Command | Entry point | What it does |
|---------|------------|--------------|
| `uv run tara` | `server.py → main()` | Launches the **FastMCP server** over SSE on port 8000. Registers all tools, prompts, and resources. |
| `uv run tara_voice` | `agent_tara.py → dev()` | Launches the **LiveKit voice agent**. Builds the STT / LLM / TTS pipeline and wires up the MCP server as a tool source. |

> Both processes must run **simultaneously**.


## Environment variables

Copy `.env.example` → `.env` and fill in the values below.

| Variable | Required | Where to get it |
|----------|----------|----------------|
| `LIVEKIT_URL` | ✅ | [LiveKit Cloud dashboard](https://cloud.livekit.io) |
| `LIVEKIT_API_KEY` | ✅ | LiveKit Cloud → API Keys |
| `LIVEKIT_API_SECRET` | ✅ | LiveKit Cloud → API Keys |
| `SARVAM_API_KEY` | ✅ | [dashboard.sarvam.ai](https://dashboard.sarvam.ai) |
| `GOOGLE_API_KEY` | ✅ | [aistudio.google.com](https://aistudio.google.com/projects) |
| `GROQ_API_KEY` | optional | [console.groq.com](https://console.groq.com) |
| `DEEPGRAM_API_KEY` | optional | [console.deepgram.com](https://console.deepgram.com) |


## Switching providers

Open `agent_tara.py` and change the provider constants at the top:

```python
STT_PROVIDER = "sarvam"   # "sarvam" | "whisper"
LLM_PROVIDER = "gemini"   # "gemini" | "openai"
TTS_PROVIDER = "sarvam"   # "sarvam"
```

## Adding a new tool

1. Create or open a file in `tara/tools/`
2. Define a `register(mcp)` function and decorate tools with `@mcp.tool()`
3. Import and call `register(mcp)` inside `tara/tools/__init__.py`

---

## Tech stack

- **[FastMCP](https://github.com/jlowin/fastmcp)** — MCP server framework
- **[LiveKit Agents](https://github.com/livekit/agents)** — real-time voice pipeline
- **Sarvam Saaras v3** — STT
- **Google Gemini 2.5 Flash** — LLM
- **Sarvam Bulbul v3** — TTS
- **[uv](https://github.com/astral-sh/uv)** — fast Python package manager



