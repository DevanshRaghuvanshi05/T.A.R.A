"""
Data resources — expose static content or dynamic data via MCP resources.
"""


def register(mcp):

    @mcp.resource("tara://info")
    def server_info() -> str:
        """Returns basic info about this MCP server."""
        return (
            "TARA MCP Server\n"
            "A personal AI voice assistant.\n"
            "Built with FastMCP."
        )