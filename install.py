"""
GraphSpy Personal Account Patch Installer

Automatically patches your GraphSpy 1.6.1 installation to support
personal Microsoft account token capture via device code phishing.

Usage:
    python install.py
"""
import shutil
import sys
import os
from pathlib import Path

def find_graphspy_install():
    """Locate the GraphSpy package directory."""
    try:
        import graphspy
        return Path(graphspy.__file__).parent
    except ImportError:
        return None

def backup_file(filepath):
    """Create a .bak backup of a file."""
    backup = filepath.with_suffix(filepath.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(filepath, backup)
        print(f"  Backed up: {filepath.name} -> {backup.name}")

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

    print("\n[+] Done! Restart GraphSpy to apply changes.")
    print("[*] To revert, rename the .bak files back to their original names.")

if __name__ == "__main__":
    install()
