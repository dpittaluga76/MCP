import json
import base64
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import httpx
import server


class ContactsTests(unittest.IsolatedAsyncioTestCase):
    async def test_demo_pagination(self):
        with patch.object(server, "DEMO", True):
            first = await server.list_contacts(limit=2)
            second = await server.list_contacts(limit=2, after=first["next_after"])
        self.assertEqual([item["id"] for item in first["results"]], ["demo-1", "demo-2"])
        self.assertEqual([item["id"] for item in second["results"]], ["demo-3"])
        self.assertIsNone(second["next_after"])

    async def test_live_request_and_cursor(self):
        def handler(request):
            self.assertEqual(request.headers["Authorization"], "Bearer example-key")
            self.assertEqual(request.url.path, "/crm/objects/2026-03/contacts")
            self.assertEqual(request.url.params["after"], "opaque-cursor")
            return httpx.Response(200, json={"results": [{"id": "123", "properties": {"firstname": "Example"}}], "paging": {"next": {"after": "next-cursor"}}})

        original_client = httpx.AsyncClient
        with patch.object(server, "DEMO", False), patch.dict(os.environ, {"HUBSPOT_ACCESS_TOKEN": "example-key"}), patch.object(server.httpx, "AsyncClient", side_effect=lambda **kwargs: original_client(transport=httpx.MockTransport(handler), **kwargs)):
            result = await server.list_contacts(limit=2, after="opaque-cursor")
        self.assertEqual(result["source"], "HubSpot")
        self.assertEqual(result["results"][0]["id"], "123")
        self.assertEqual(result["next_after"], "next-cursor")

    async def test_missing_credential(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(server, "ENV_FILE", Path(temp) / ".env"), patch.object(server, "DEMO", False), patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "HUBSPOT_ACCESS_TOKEN"):
                await server.list_contacts()

    async def test_dotenv_key_and_environment_precedence(self):
        with tempfile.TemporaryDirectory() as temp:
            env_file = Path(temp) / ".env"
            env_file.write_text("HUBSPOT_ACCESS_TOKEN_BASE64=" + base64.b64encode(b"test-key").decode() + "\n")
            with patch.object(server, "ENV_FILE", env_file), patch.dict(os.environ, {}, clear=True):
                self.assertEqual(server.get_access_token(), "test-key")
                with patch.dict(os.environ, {"HUBSPOT_ACCESS_TOKEN": "override"}):
                    self.assertEqual(server.get_access_token(), "override")

    async def test_invalid_base64(self):
        with tempfile.TemporaryDirectory() as temp:
            env_file = Path(temp) / ".env"
            env_file.write_text("HUBSPOT_ACCESS_TOKEN_BASE64=not-base64!\n")
            with patch.object(server, "ENV_FILE", env_file), patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(ValueError, "invalid"):
                    server.get_access_token()

    async def test_limit_validation(self):
        with self.assertRaisesRegex(ValueError, "between 1 and 100"):
            await server.list_contacts(limit=101)


class ProtocolTests(unittest.TestCase):
    def test_client_launches_server_and_reads_demo(self):
        result = subprocess.run([sys.executable, "client.py", "--demo", "--limit", "2"], cwd=Path(__file__).parent, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Available tools: list_contacts", result.stdout)
        payload = json.loads(result.stdout.split("\n", 1)[1])
        self.assertEqual(payload["source"], "fictional demo data")
        self.assertEqual(payload["next_after"], "2")


if __name__ == "__main__":
    unittest.main()
