"""
Resource registry — imports and registers all resource modules with the MCP server.
"""

# pyrefly: ignore [missing-import]
from tara.resources import data


def register_all_resources(mcp):
    data.register(mcp)