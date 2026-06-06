"""
MCP Prompts — reusable prompt templates exposed to the client.
"""

# pyrefly: ignore [missing-import]
import tara.prompts


def register_all_prompts(mcp):
    tara.prompts.templates.register(mcp)