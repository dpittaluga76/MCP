"""Launch the MCP server, discover its tools, and read a page of contacts."""

import argparse
import asyncio
import os
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main(demo: bool, limit: int) -> int:
    server_script = Path(__file__).resolve().with_name("server.py")
    args = [str(server_script)] + (["--demo"] if demo else [])
    # The MCP SDK only inherits a small allowlist; pass this variable explicitly.
    env = {"HUBSPOT_ACCESS_TOKEN": os.environ["HUBSPOT_ACCESS_TOKEN"]} if "HUBSPOT_ACCESS_TOKEN" in os.environ else {}
    params = StdioServerParameters(command=sys.executable, args=args, env=env)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("Available tools:", ", ".join(tool.name for tool in tools.tools))
            result = await session.call_tool("list_contacts", {"limit": limit})
            for item in result.content:
                if item.type == "text":
                    print(item.text)
            return 1 if result.isError else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example MCP client for HubSpot contacts")
    parser.add_argument("--demo", action="store_true", help="Read fictional local contacts")
    parser.add_argument("--limit", type=int, default=5, help="Maximum contacts to retrieve (1-100)")
    options = parser.parse_args()
    sys.exit(asyncio.run(main(options.demo, options.limit)))
