"""A minimal read-only HubSpot MCP server using the stdio transport."""

import argparse
import base64
import binascii
import os
from pathlib import Path

import httpx
from dotenv import dotenv_values
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

mcp = FastMCP("HubSpot contacts example")
DEMO = False
CONTACTS_URL = "https://api.hubapi.com/crm/objects/2026-03/contacts"
PROPERTIES = "firstname,lastname,email"
ENV_FILE = Path(__file__).resolve().with_name(".env")
DEMO_CONTACTS = [
    {"id": "demo-1", "properties": {"firstname": "Alex", "lastname": "Example", "email": "alex@example.com"}},
    {"id": "demo-2", "properties": {"firstname": "Sam", "lastname": "Sample", "email": "sam@example.com"}},
    {"id": "demo-3", "properties": {"firstname": "Taylor", "lastname": "Demo", "email": "taylor@example.com"}},
]


def get_access_token() -> str:
    """Prefer the process environment, then decode the local .env value."""
    token = os.environ.get("HUBSPOT_ACCESS_TOKEN", "").strip()
    if token:
        return token
    encoded = (dotenv_values(ENV_FILE, interpolate=False).get("HUBSPOT_ACCESS_TOKEN_BASE64") or "").strip()
    if not encoded:
        raise ValueError("Set HUBSPOT_ACCESS_TOKEN or add HUBSPOT_ACCESS_TOKEN_BASE64 to chatgpt/.env.")
    try:
        token = base64.b64decode(encoded, validate=True).decode("utf-8").strip()
    except (binascii.Error, ValueError, UnicodeDecodeError):
        raise ValueError("HUBSPOT_ACCESS_TOKEN_BASE64 in chatgpt/.env is invalid.") from None
    if not token:
        raise ValueError("The HubSpot service key in chatgpt/.env is empty.")
    return token


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True))
async def list_contacts(limit: int = 5, after: str | None = None) -> dict:
    """Read one page of HubSpot contacts. Pass next_after to get another page.

    Returns up to 100 contacts with id, first name, last name, and email.
    In demo mode the records are fictional and never come from HubSpot.
    """
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")

    if DEMO:
        if after is not None and (not after.isascii() or not after.isdecimal() or len(after) > 9):
            raise ValueError("Invalid demo pagination cursor")
        start = int(after) if after is not None else 0
        end = start + limit
        return {"source": "fictional demo data", "results": DEMO_CONTACTS[start:end],
                "next_after": str(end) if end < len(DEMO_CONTACTS) else None}

    token = get_access_token()
    params = {"limit": str(limit), "properties": PROPERTIES}
    if after is not None:
        params["after"] = after
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(CONTACTS_URL, params=params, headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status in (401, 403):
            raise ValueError(f"HubSpot returned HTTP {status}. Check the service key and contacts read scope.") from None
        raise ValueError(f"HubSpot returned HTTP {status}. Try again or check HubSpot's API status.") from None
    except httpx.RequestError:
        raise ValueError("Could not reach the HubSpot API. Check your network connection.") from None

    return {"source": "HubSpot", "results": data.get("results", []),
            "next_after": data.get("paging", {}).get("next", {}).get("after")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read-only HubSpot MCP server")
    parser.add_argument("--demo", action="store_true", help="Use fictional local contacts without a HubSpot credential")
    DEMO = parser.parse_args().demo
    mcp.run(transport="stdio")
