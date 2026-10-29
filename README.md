# mcp

Two small, read-only Python [MCP](https://modelcontextprotocol.io) servers that read CRM data from HubSpot. Each one was written by a different AI assistant. Both talk to the HubSpot REST API over stdio and never create or change records.

| | [`chatgpt/`](chatgpt/README.md) | [`claude/hubspot-mcp/`](claude/hubspot-mcp/README.md) |
|---|---|---|
| Written with | ChatGPT / Codex | Claude Code |
| Tools | `list_contacts` | `list_contacts`, `list_companies`, `list_deals`, `get_contact`, `search_contacts` |
| Includes | MCP server, a minimal MCP client, Windows launcher (`run_hubspot.bat`), offline tests | MCP server only (try it with MCP Inspector or Claude Code) |
| Demo mode | Yes: `--demo` uses three fictional contacts, no HubSpot account needed | No: needs a HubSpot token |
| Credential | `HUBSPOT_ACCESS_TOKEN_BASE64` in `chatgpt/.env`, or `HUBSPOT_ACCESS_TOKEN` env var | `HUBSPOT_ACCESS_TOKEN` in `claude/hubspot-mcp/.env` |
| HubSpot scopes | `crm.objects.contacts.read` | `crm.objects.contacts.read`, `crm.objects.companies.read`, `crm.objects.deals.read` |

## Quick start

Both need Python 3.10 or later. The commands below are for Windows PowerShell, run from the repository root.

### ChatGPT version (demo, no account needed)

```powershell
cd chatgpt
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe client.py --demo
```

See [chatgpt/README.md](chatgpt/README.md) for live mode, the batch launcher, tests and how to connect other MCP clients.

### Claude version

```powershell
cd claude\hubspot-mcp
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env   # then paste your HubSpot token into .env
claude mcp add hubspot -- <repo>\claude\hubspot-mcp\.venv\Scripts\python.exe <repo>\claude\hubspot-mcp\server.py
```

Replace `<repo>` with the absolute path to this repository. See [claude/hubspot-mcp/README.md](claude/hubspot-mcp/README.md) for token setup and testing with MCP Inspector.

## Getting a HubSpot token

In HubSpot, create a service key (**Settings → Integrations → Service Keys**) or a private app (**Settings → Integrations → Private Apps**) and grant the read scopes listed above. A free developer test account comes with sample records.

## Credentials

Tokens live only in each project's `.env` file (or `service_key.txt`), and these files are git-ignored. A root [.gitignore](.gitignore) also ignores `.env`, `service_key.txt`, `.mcp.json`, key files and virtual environments anywhere in the repo. Commit only the `.env.example` templates. Results can contain personal contact data, so use a test account where possible.
