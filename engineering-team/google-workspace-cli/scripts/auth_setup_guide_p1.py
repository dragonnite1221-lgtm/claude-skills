# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from auth_setup_guide_base import *  # noqa: F403,E402


SERVICE_SCOPES: Dict[str, List[str]] = {
    "gmail": [
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.labels",
        "https://www.googleapis.com/auth/gmail.settings.basic",
    ],
    "drive": [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive.metadata.readonly",
    ],
    "sheets": [
        "https://www.googleapis.com/auth/spreadsheets",
    ],
    "calendar": [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events",
    ],
    "tasks": [
        "https://www.googleapis.com/auth/tasks",
    ],
    "chat": [
        "https://www.googleapis.com/auth/chat.spaces.readonly",
        "https://www.googleapis.com/auth/chat.messages",
    ],
    "docs": [
        "https://www.googleapis.com/auth/documents",
    ],
    "admin": [
        "https://www.googleapis.com/auth/admin.directory.user.readonly",
        "https://www.googleapis.com/auth/admin.directory.group",
        "https://www.googleapis.com/auth/admin.directory.orgunit.readonly",
    ],
    "meet": [
        "https://www.googleapis.com/auth/meetings.space.created",
    ],
}
OAUTH_GUIDE = """
=== Google Workspace CLI: OAuth Setup Guide ===

Step 1: Create a Google Cloud Project
  1. Go to https://console.cloud.google.com/
  2. Click "Select a project" -> "New Project"
  3. Name it (e.g., "gws-cli-access") and click Create
  4. Note the Project ID

Step 2: Enable Required APIs
  1. Go to APIs & Services -> Library
  2. Search and enable each API you need:
     - Gmail API
     - Google Drive API
     - Google Sheets API
     - Google Calendar API
     - Tasks API
     - Admin SDK API (for admin operations)

Step 3: Configure OAuth Consent Screen
  1. Go to APIs & Services -> OAuth consent screen
  2. Select "Internal" (for Workspace) or "External" (for personal)
  3. Fill in app name, support email
  4. Add scopes for the services you need
  5. Save and continue

Step 4: Create OAuth Credentials
  1. Go to APIs & Services -> Credentials
  2. Click "Create Credentials" -> "OAuth client ID"
  3. Application type: "Desktop app"
  4. Name it "gws-cli"
  5. Download the JSON file

Step 5: Configure gws CLI
  1. Set environment variables:
     export GWS_CLIENT_ID=<your-client-id>
     export GWS_CLIENT_SECRET=<your-client-secret>

  2. Or place the credentials JSON:
     mv client_secret_*.json ~/.config/gws/credentials.json

Step 6: Authenticate
  gws auth setup
  # Opens browser for consent, stores token in system keyring

Step 7: Verify
  gws auth status
  gws gmail users getProfile me
"""
SERVICE_ACCOUNT_GUIDE = """
=== Google Workspace CLI: Service Account Setup Guide ===

Step 1: Create a Google Cloud Project
  (Same as OAuth Step 1)

Step 2: Create a Service Account
  1. Go to IAM & Admin -> Service Accounts
  2. Click "Create Service Account"
  3. Name: "gws-cli-service"
  4. Grant roles as needed (no role needed for Workspace API access)
  5. Click "Done"

Step 3: Create Key
  1. Click on the service account
  2. Go to "Keys" tab
  3. Add Key -> Create new key -> JSON
  4. Download and store securely

Step 4: Enable Domain-Wide Delegation
  1. On the service account page, click "Edit"
  2. Check "Enable Google Workspace domain-wide delegation"
  3. Save
  4. Note the Client ID (numeric)

Step 5: Authorize in Google Admin
  1. Go to admin.google.com
  2. Security -> API Controls -> Domain-wide Delegation
  3. Add new:
     - Client ID: <numeric client ID from Step 4>
     - Scopes: (paste required scopes)
  4. Authorize

Step 6: Configure gws CLI
  export GWS_SERVICE_ACCOUNT_KEY=/path/to/service-account-key.json
  export GWS_DELEGATED_USER=admin@yourdomain.com

Step 7: Verify
  gws auth status
  gws gmail users getProfile me
"""
