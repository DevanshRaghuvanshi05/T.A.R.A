"""
MCP Prompts — reusable prompt templates exposed to the client.
"""

# pyrefly: ignore [missing-import]
from tara.prompts import templates


def register_all_prompts(mcp):
    templates.register(mcp)
