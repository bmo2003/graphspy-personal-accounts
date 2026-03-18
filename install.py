"""
GraphSpy Personal Account Patch Installer

Automatically patches your GraphSpy 1.6.1 installation to support
personal Microsoft account token capture via device code phishing.

Usage:
    python install.py
"""
import shutil
import sys
import json
import time
import subprocess
from pathlib import Path

def find_graphspy_install():
    """Locate the GraphSpy package directory."""
    try:
        import graphspy
        if graphspy.__file__:
            return Path(graphspy.__file__).parent
    except (ImportError, TypeError):
        pass
    # Fallback: search common pipx/pip install locations
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "-f", "graphspy"],
            capture_output=True, text=True, timeout=10
        )
        location = None
        for line in result.stdout.splitlines():
            if line.startswith("Location:"):
                location = Path(line.split(":", 1)[1].strip())
                break
        if location and (location / "graphspy" / "cli.py").exists():
            return location / "graphspy"
    except Exception:
        pass
    # Fallback: try pipx venvs
    for base in [Path.home() / "pipx" / "venvs", Path.home() / ".local" / "pipx" / "venvs"]:
        candidate = base / "graphspy" / "Lib" / "site-packages" / "graphspy"
        if not candidate.exists():
            candidate = base / "graphspy" / "lib" / "python3" / "site-packages" / "graphspy"
        # Try any python version
        lib_dir = base / "graphspy" / "Lib" / "site-packages" / "graphspy"
        if lib_dir.exists():
            return lib_dir
        lib_dir2 = base / "graphspy" / "lib"
        if lib_dir2.exists():
            for pydir in lib_dir2.iterdir():
                sp = pydir / "site-packages" / "graphspy"
                if sp.exists():
                    return sp
    return None

def backup_file(filepath):
    """Create a .bak backup of a file."""
    backup = filepath.with_suffix(filepath.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(filepath, backup)
        print(f"  Backed up: {filepath.name} -> {backup.name}")

def load_templates():
    """Load custom request templates into GraphSpy's database."""
    templates_file = Path(__file__).parent / "templates.json"
    if not templates_file.exists():
        print("  [!] templates.json not found, skipping template import.")
        return

    try:
        import requests
    except ImportError:
        print("  [!] 'requests' library not available, skipping template import.")
        print("  [*] You can load templates manually after starting GraphSpy:")
        print("      python load_templates.py")
        return

    # Check if GraphSpy is running
    try:
        resp = requests.get("http://127.0.0.1:5000/", timeout=3)
        if resp.status_code != 200:
            raise Exception()
    except Exception:
        print("  [!] GraphSpy is not running on localhost:5000.")
        print("  [*] Start GraphSpy first, then run: python load_templates.py")
        return

    templates = json.loads(templates_file.read_text())
    loaded = 0
    for t in templates:
        try:
            resp = requests.post(
                "http://127.0.0.1:5000/api/save_request_template",
                json=t, timeout=5
            )
            if resp.status_code == 200:
                loaded += 1
        except Exception:
            pass
    print(f"  Loaded {loaded}/{len(templates)} templates.")

def install():
    print("GraphSpy Personal Account Patch Installer")
    print("=" * 50)

    gspy_dir = find_graphspy_install()
    if not gspy_dir:
        print("[!] GraphSpy is not installed. Install it first:")
        print("    pipx install graphspy")
        sys.exit(1)

    print(f"[*] Found GraphSpy at: {gspy_dir}")

    patch_dir = Path(__file__).parent / "graphspy"
    if not patch_dir.exists():
        print("[!] Patch files not found. Make sure the 'graphspy' folder is next to this script.")
        sys.exit(1)

    files_to_patch = [
        ("cli.py", gspy_dir / "cli.py"),
        ("templates/access_tokens.html", gspy_dir / "templates" / "access_tokens.html"),
        ("templates/device_codes.html", gspy_dir / "templates" / "device_codes.html"),
        ("templates/layout.html", gspy_dir / "templates" / "layout.html"),
    ]

    print("\n[*] Backing up original files...")
    for _, dest in files_to_patch:
        if dest.exists():
            backup_file(dest)

    print("\n[*] Applying patches...")
    for src_rel, dest in files_to_patch:
        src = patch_dir / src_rel
        if not src.exists():
            print(f"  [!] Missing patch file: {src_rel}")
            continue
        shutil.copy2(src, dest)
        print(f"  Patched: {src_rel}")

    print("\n[*] Loading custom request templates...")
    load_templates()

    print("\n[+] Done! Restart GraphSpy to apply changes.")
    print("[*] If templates didn't load, start GraphSpy and run: python load_templates.py")
    print("[*] To revert patches, rename the .bak files back to their original names.")

if __name__ == "__main__":
    install()
