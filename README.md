# GraphSpy Personal Account Support

Patches for [GraphSpy v1.6.1](https://github.com/RedByte1337/GraphSpy) that add support for **personal Microsoft account** (consumer/Outlook.com) token capture via device code phishing.

Out of the box, GraphSpy only supports organizational (work/school) accounts. These patches extend device code phishing to work with personal Microsoft accounts — useful for security awareness training where employees use personal email.

## Quick Start

```bash
pip install pipx
pipx install graphspy
git clone https://github.com/bmo2003/graphspy-personal-accounts.git
cd graphspy-personal-accounts
python install.py
graphspy
```

If GraphSpy wasn't running during install, load the demo templates separately:
```bash
python load_templates.py
```

## What This Fixes

### The Problem
Microsoft blocks device code authentication for first-party client IDs (Azure CLI, Auth Broker, etc.) on personal accounts. Personal accounts also return **opaque access tokens** instead of JWTs, which causes GraphSpy to crash in multiple places when trying to decode them.

### The Solution
- Adds `netcorebrowser` (`1d18b3b0-251b-4714-a02a-9956cec86c2d`) as a third-party client ID that works with personal accounts
- Routes personal account requests through `/consumers/oauth2/v2.0/` endpoints with the correct `device_code` parameter (not `code`)
- Handles opaque (non-JWT) access tokens throughout the codebase instead of crashing
- Fixes token metadata storage so access tokens show proper expiry times and scopes instead of "unknown"
- Fixes the Token Options sidebar to display personal account token info correctly
- Fixes the refresh-to-access-token flow for consumer accounts (auto-detects and uses v2 endpoint with scope)
- Adds "MSGraph Full Access (Personal Accounts)" scope option for broader permissions
- Includes 21 pre-built custom request templates for demos

## Modified Files

| File | Changes |
|------|---------|
| `graphspy/cli.py` | Opaque token handling in `save_access_token()`, `poll_device_codes()`, `refresh_to_access_token()`, `api_decode_token()`. Consumer endpoint routing. `save_refresh_token()` accepts "consumers" tenant. |
| `graphspy/templates/access_tokens.html` | Added netcorebrowser to Client ID dropdowns on the Access Tokens page. |
| `graphspy/templates/device_codes.html` | Added netcorebrowser to Client ID dropdown. Added `microsoft.com/link` to Device Login URLs. Added "MSGraph Full Access" scope option. |
| `graphspy/templates/layout.html` | Token Options sidebar handles opaque tokens. "Refresh and activate" auto-detects consumer accounts and uses v2+scope. Added netcorebrowser to Client ID dropdown. |

## Installation

### Automatic
```bash
# Install GraphSpy
pip install pipx
pipx install graphspy

# Clone and install patches
git clone https://github.com/bmo2003/graphspy-personal-accounts.git
cd graphspy-personal-accounts
python install.py
```

The installer will:
1. Find your GraphSpy installation automatically (works with pip and pipx)
2. Back up original files (`.bak` extension)
3. Apply the patched files
4. Load 21 demo request templates (if GraphSpy is running)

### Loading Templates
Templates are loaded into GraphSpy's database via its API, so GraphSpy needs to be running:
```bash
# If templates didn't load during install:
graphspy                    # start GraphSpy in one terminal
python load_templates.py    # run this in another terminal
```

### Manual Installation
Copy the files from the `graphspy/` directory into your GraphSpy installation, replacing the originals:
```
graphspy/cli.py                        -> <site-packages>/graphspy/cli.py
graphspy/templates/access_tokens.html  -> <site-packages>/graphspy/templates/access_tokens.html
graphspy/templates/device_codes.html   -> <site-packages>/graphspy/templates/device_codes.html
graphspy/templates/layout.html         -> <site-packages>/graphspy/templates/layout.html
```

Find your install path:
```bash
python -c "import graphspy; print(graphspy.__file__)"
```

## Usage

1. Start GraphSpy: `graphspy`
2. Go to **Authentication > Device Code**
3. Select **netcorebrowser (Personal Accounts)** from the Client ID dropdown
4. Set API Version to **v2**
5. Set Scope to **MSGraph Full Access (Personal Accounts)** for full demo capabilities, or **MSGraph** for read-only
6. Click **Request login code**
7. Send the target to `https://microsoft.com/link` with the generated code
8. Once they authenticate, the token appears in the Device Code List with status **SUCCESS**

### What Works With Personal Accounts
- **Outlook/Email** — Full inbox access via Outlook Graph page
- **OneDrive/Files** — Browse personal OneDrive files
- **Custom Requests** — Hit any Graph API endpoint (`/me`, `/me/contacts`, `/me/calendar/events`, etc.)
- **Token Refresh** — Refresh button auto-detects consumer account and uses correct endpoint

### What Doesn't Work (Microsoft limitation, not a code issue)
- **MFA Methods** — Uses `mysignins.microsoft.com` API which requires enterprise accounts
- **Entra ID / Users** — Directory enumeration is organizational only
- **SharePoint** — Enterprise-only service
- **Teams** — Requires organizational APIs

## Included Templates

21 pre-built custom request templates are included. Load them via `python load_templates.py` while GraphSpy is running, then access them from **Custom > Custom Requests > Load...**

### Read Templates
| Template | What It Does |
|----------|-------------|
| My Profile | View victim's full profile info |
| Inbox (Top 10) | Read latest inbox emails |
| Search Emails for Keyword | Search all emails for "password" |
| Search Emails for Bank | Search all emails for "bank account" |
| Deleted Emails | Read deleted/trashed emails |
| Junk Email Folder | Read spam-filtered emails |
| Sent Emails | Read victim's sent messages |
| Draft Emails | Read unsent draft emails |
| Contacts | Export contact list |
| Calendar Events | View calendar/meetings |
| OneDrive Files | Browse cloud storage files |
| Search Files for Password | Search OneDrive for sensitive files |
| List Inbox Rules | Check for existing mail rules |
| List Email Attachments | View attachments on a specific email |

### Write Templates (require "Full Access" scope)
| Template | What It Does |
|----------|-------------|
| Send Email as Victim | Send email from victim's account (hidden from Sent folder) |
| Reply to Email | Reply to an existing email thread |
| Create Inbox Forwarding Rule | Silently forward all incoming email to an external address |
| Delete Inbox Rule by ID | Remove a forwarding rule |
| Move Email to Inbox | Move emails between folders (e.g., junk to inbox) |
| Delete Email by ID | Delete specific emails (cover tracks) |
| Upload File to OneDrive | Place a file in victim's cloud storage |

## Demo Tips

- **Scope matters**: Use "MSGraph Full Access (Personal Accounts)" scope to get write permissions. The default "MSGraph" scope only gives read access.
- **Search for sensitive keywords**: Use the search templates to find emails containing "password", "bank account", etc.
- **Show the forwarding rule**: Create a rule, send a test email, show it gets forwarded silently. Then show the victim how to find and delete the rule in Outlook Settings > Mail > Rules.
- **Send as victim**: Send an email from the victim's account with `saveToSentItems: false` — it won't appear in their Sent folder.
- **Password change demo**: After capturing a token, have the "victim" change their password. Show that the access token still works for ~1 hour, but the refresh token is immediately revoked.
- **Check sign-in activity**: Show the victim `account.microsoft.com/security` > Recent Activity — the "netcorebrowser" sign-in will be visible there. This is how to detect the attack.

## Patches

Raw unified diffs are in the `patches/` directory if you prefer to review or apply them manually:
```bash
cd <site-packages>
patch -p1 < patches/cli.patch
patch -p1 < patches/device_codes.patch
patch -p1 < patches/layout.patch
patch -p1 < patches/access_tokens.patch
```

## Disclaimer

This tool is intended for **authorized security testing and awareness training only**. Always obtain proper authorization before conducting any phishing simulations. Unauthorized access to computer systems is illegal.
