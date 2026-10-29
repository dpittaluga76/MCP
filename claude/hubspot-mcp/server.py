"""MCP server that exposes read-only HubSpot CRM tools.

Auth: a HubSpot Private App access token in HUBSPOT_ACCESS_TOKEN
(HubSpot > Settings > Integrations > Private Apps, scopes: crm.objects.contacts.read,
crm.objects.companies.read, crm.objects.deals.read).
"""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path(__file__).parent / ".env")

BASE_URL = "https://api.hubapi.com"

DEFAULT_PROPERTIES = {
    "contacts": ["firstname", "lastname", "email", "phone", "company", "lifecyclestage"],
    "companies": ["name", "domain", "industry", "city", "country", "numberofemployees"],
    "deals": ["dealname", "amount", "dealstage", "pipeline", "closedate"],
}

mcp = FastMCP("hubspot")


def _client() -> httpx.Client:
    token = os.environ.get("HUBSPOT_ACCESS_TOKEN")
    if not token:
        raise RuntimeError(
            "HUBSPOT_ACCESS_TOKEN is not set. Copy .env.example to .env and add your token."
        )
    return httpx.Client(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )


def _slim(record: dict) -> dict:
    """Flatten a HubSpot record to {id, ...properties}."""
    return {"id": record["id"], **record.get("properties", {})}


def _list(object_type: str, limit: int, after: str | None) -> dict:
    params = {
        "limit": max(1, min(limit, 100)),
        "properties": ",".join(DEFAULT_PROPERTIES[object_type]),
    }
    if after:
        params["after"] = after
    with _client() as client:
        resp = client.get(f"/crm/v3/objects/{object_type}", params=params)
        resp.raise_for_status()
        data = resp.json()
    return {
        "results": [_slim(r) for r in data.get("results", [])],
        "next_after": data.get("paging", {}).get("next", {}).get("after"),
    }


@mcp.tool()
def list_contacts(limit: int = 10, after: str | None = None) -> dict:
    """List HubSpot contacts. Pass `next_after` from a previous call as `after` to page."""
    return _list("contacts", limit, after)


@mcp.tool()
def list_companies(limit: int = 10, after: str | None = None) -> dict:
    """List HubSpot companies. Pass `next_after` from a previous call as `after` to page."""
    return _list("companies", limit, after)


@mcp.tool()
def list_deals(limit: int = 10, after: str | None = None) -> dict:
    """List HubSpot deals. Pass `next_after` from a previous call as `after` to page."""
    return _list("deals", limit, after)


@mcp.tool()
def get_contact(contact_id: str) -> dict:
    """Get a single HubSpot contact by its record ID."""
    with _client() as client:
        resp = client.get(
            f"/crm/v3/objects/contacts/{contact_id}",
            params={"properties": ",".join(DEFAULT_PROPERTIES["contacts"])},
        )
        resp.raise_for_status()
        return _slim(resp.json())


@mcp.tool()
def search_contacts(query: str, limit: int = 10) -> dict:
    """Full-text search HubSpot contacts (name, email, phone, company...)."""
    body = {
        "query": query,
        "limit": max(1, min(limit, 100)),
        "properties": DEFAULT_PROPERTIES["contacts"],
    }
    with _client() as client:
        resp = client.post("/crm/v3/objects/contacts/search", json=body)
        resp.raise_for_status()
        data = resp.json()
    return {"total": data.get("total", 0), "results": [_slim(r) for r in data.get("results", [])]}


if __name__ == "__main__":
    mcp.run()  # stdio transport
