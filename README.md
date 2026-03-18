# GraphSpy Personal Account Support

Patches for [GraphSpy v1.6.1](https://github.com/RedByte1337/GraphSpy) that add support for **personal Microsoft account** (consumer/Outlook.com) token capture via device code phishing.

Out of the box, GraphSpy only supports organizational (work/school) accounts. These patches extend device code phishing to work with personal Microsoft accounts — useful for security awareness training where employees use personal email.

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

## Modified Files

| File | Changes |
|------|---------|
| `graphspy/cli.py` | Opaque token handling in `save_access_token()`, `poll_device_codes()`, `refresh_to_access_token()`, `api_decode_token()`. Consumer endpoint routing. `save_refresh_token()` accepts "consumers" tenant. |
| `graphspy/templates/device_codes.html` | Added netcorebrowser to Client ID dropdown. Added `microsoft.com/link` to Device Login URLs. |
| `graphspy/templates/access_tokens.html` | Added netcorebrowser to Client ID dropdowns on the Access Tokens page. |
| `graphspy/templates/layout.html` | Token Options sidebar handles opaque tokens. "Refresh and activate" auto-detects consumer accounts and uses v2+scope. Added netcorebrowser to Client ID dropdown. |

## Installation

### Automatic
```bash
# Make sure GraphSpy 1.6.1 is installed
pipx install graphspy

# Run the installer (backs up originals automatically)
python install.py
```

### Manual
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
4. Set API Version to **v2**, Scope to **MSGraph**
5. Click **Request login code**
6. Send the target to `https://microsoft.com/link` with the generated code
7. Once they authenticate, the token appears in the Device Code List with status **SUCCESS**

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

## Demo Tips

- **Search files for sensitive keywords**: Custom request `GET https://graph.microsoft.com/v1.0/me/drive/root/search(q='password')`
- **Read deleted emails**: Custom request `GET https://graph.microsoft.com/v1.0/me/mailFolders/deletedItems/messages`
- **Password change demo**: After capturing a token, have the "victim" change their password. Show that the access token still works for ~1 hour, but the refresh token is immediately revoked.

## Patches

Raw unified diffs are in the `patches/` directory if you prefer to review or apply them manually:
```bash
cd <site-packages>
patch -p1 < patches/cli.patch
patch -p1 < patches/device_codes.patch
patch -p1 < patches/layout.patch
```

## Disclaimer

This tool is intended for **authorized security testing and awareness training only**. Always obtain proper authorization before conducting any phishing simulations. Unauthorized access to computer systems is illegal.
