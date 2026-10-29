# HubSpot MCP example

This is a small Python **MCP server and client** for reading a page of contacts. The client starts the server over stdio, discovers its tools, and calls `list_contacts`; the server calls HubSpot's REST API. No CRM records are created or changed.

Everything for this example lives in `chatgpt/`. The demo mode uses three fictional contacts and works without a HubSpot account or credential. Live mode reads real records from the account associated with your key; it does not filter for records that HubSpot labels as samples.

## Run the demo on Windows PowerShell

From the repository root:

```powershell
cd chatgpt
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe client.py --demo
```

If Python 3.11 is unavailable, use Python 3.10 or later. You should see `list_contacts` and three fictional contacts. Use `--limit 2` to see a pagination cursor. Demo mode makes no HubSpot requests.

## Read contacts from HubSpot

1. In the HubSpot account you want to query, create a service key under **Settings → Integrations → Service Keys**. Grant `crm.objects.contacts.read`. A Super Admin or user with Developer tools access may be needed. Existing legacy private-app access tokens with the same read scope can also be used.
2. Store the key as Base64 in the Git-ignored `.env` file in this folder. If your key is in `service_key.txt`, create `.env` in PowerShell with:

   ```powershell
   $keyBytes = [Text.Encoding]::UTF8.GetBytes((Get-Content .\service_key.txt -Raw).Trim())
   $encodedKey = [Convert]::ToBase64String($keyBytes)
   Set-Content -LiteralPath .\.env -Value "HUBSPOT_ACCESS_TOKEN_BASE64=$encodedKey" -Encoding ascii
   Remove-Variable keyBytes, encodedKey
   ```

   This command replaces an existing `.env`. Update it after rotating your key. Then run `.\.venv\Scripts\python.exe client.py`.

The server reads `.env` from its own folder, regardless of the current working directory. An explicitly set `HUBSPOT_ACCESS_TOKEN` environment variable takes precedence. Base64 is encoding, not encryption: anyone who can read `.env` can recover the key. Both `.env` and `service_key.txt` are Git-ignored; keep them out of chat. The HubSpot connector in ChatGPT/Codex does not supply credentials to this local example.

The server reads up to five contacts by default. Results can contain personal information; use a test account or test records if appropriate. An empty `results` array means the account has no accessible contacts. A 401 or 403 usually means the key or scope needs attention. The example does not create sample records.

### Run with the Windows batch file

After setting up `chatgpt\.env`, you can launch the live example in PowerShell with:

```powershell
cd C:\Users\Usuario\mcp\chatgpt
.\run_hubspot.bat
```

The batch file runs the client, which starts the server; the server reads `.env` and the batch file exits with the client's status. It displays the returned contacts; it does not save them to a file.

## Connect another MCP-compatible AI client

Configure the host to launch `server.py` with the absolute path to this project's virtual-environment Python. The exact configuration location and format depend on the host. For hosts accepting an `mcpServers` JSON object, the following is an illustrative Windows demo configuration (replace `C:\\path\\to\\mcp` with your actual repository path):

```json
{
  "mcpServers": {
    "hubspot-example": {
      "command": "C:\\path\\to\\mcp\\chatgpt\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\mcp\\chatgpt\\server.py", "--demo"]
    }
  }
}
```

For live mode, remove `--demo` and set up the server's `.env` as described above. Alternatively, supply `HUBSPOT_ACCESS_TOKEN` through your host's secret/environment settings. Restart the host if needed. Ask it to call `list_contacts` with `limit: 5`; pass the returned `next_after` as `after` to read the next page. Cursors are opaque in live mode. Some clients may display or log tool results, so handle contact data accordingly.

## Files and implementation notes

- `server.py`: read-only `list_contacts` MCP tool, fictional demo data, and HubSpot HTTP call.
- `client.py`: minimal stdio MCP client; passes the credential to its server subprocess explicitly.
- `run_hubspot.bat`: Windows launcher that starts the client.
- `.env.example`: template for the Base64-encoded service key in the ignored `.env` file.
- `test_example.py`: offline tests for pagination, authentication and the actual MCP subprocess.
- `requirements.txt`: dependency ranges; MCP is constrained to the v1 SDK because this example uses its `FastMCP` and `ClientSession` APIs.

Run the tests from this directory in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

The official [HubSpot API versioning guide](https://developers.hubspot.com/docs/api/how-to-use-hubspot-api) documents the contacts endpoint, and [HubSpot's service key guide](https://developers.hubspot.com/blog/hubspot-service-keys-the-right-api-credential-for-data-integrations) covers credentials. HubSpot also offers its own [remote MCP server](https://developers.hubspot.com/ai-tools/mcp), which is a separate integration from this example.
