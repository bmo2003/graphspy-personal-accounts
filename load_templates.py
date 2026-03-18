"""
Load custom request templates into a running GraphSpy instance.

Usage:
    1. Start GraphSpy: graphspy
    2. Run this script: python load_templates.py
"""
import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("[!] 'requests' library required: pip install requests")
    sys.exit(1)

def main():
    templates_file = Path(__file__).parent / "templates.json"
    if not templates_file.exists():
        print("[!] templates.json not found.")
        sys.exit(1)

    try:
        resp = requests.get("http://127.0.0.1:5000/", timeout=3)
    except Exception:
        print("[!] GraphSpy is not running. Start it first: graphspy")
        sys.exit(1)

    templates = json.loads(templates_file.read_text())
    loaded = 0
    for t in templates:
        try:
            resp = requests.post(
                "http://127.0.0.1:5000/api/save_request_template",
                json=t, timeout=5
            )
            if resp.status_code == 200:
                print(f"  [+] {t['template_name']}")
                loaded += 1
            else:
                print(f"  [!] Failed: {t['template_name']}")
        except Exception as e:
            print(f"  [!] Error: {t['template_name']} - {e}")

    print(f"\n[+] Loaded {loaded}/{len(templates)} templates.")

if __name__ == "__main__":
    main()
