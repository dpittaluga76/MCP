# HubSpot MCP example (read-only)

A small Python MCP server (stdio) that reads CRM records from HubSpot.

## Tools

| Tool | Description |
|---|---|
| `list_contacts` / `list_companies` / `list_deals` | List records (`limit` up to 100, page with `after` = previous `next_after`) |
| `get_contact` | Fetch one contact by ID |
| `search_contacts` | Full-text search over contacts |

## 1. Get a HubSpot token

HubSpot > Settings > Integrations > Private Apps > Create. Scopes:
`crm.objects.contacts.read`, `crm.objects.companies.read`, `crm.objects.deals.read`.
A free developer test account comes with sample contacts/companies, or use the CRM's built-in sample data.

## 2. Install

```powershell
cd claude\hubspot-mcp
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env   # then paste your token into .env
```

## 3. Try it

```powershell
npx @modelcontextprotocol/inspector .venv\Scripts\python.exe server.py
```

Call `list_contacts` in the Inspector to see your sample records.

## 4. Use it from Claude Code

```powershell
claude mcp add hubspot -- C:\Users\Usuario\mcp\claude\hubspot-mcp\.venv\Scripts\python.exe C:\Users\Usuario\mcp\claude\hubspot-mcp\server.py
```

Or copy `.mcp.json.example` to a `.mcp.json` where your client expects it. Then ask:
"List my HubSpot contacts".

The token is read from `.env` next to `server.py`, so no secrets go in client config.
