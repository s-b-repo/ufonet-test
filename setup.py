#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file is part of the UFONet project: https://ufonet.03c8.net

Copyright (c) 2013/2024 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc.,
51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
"""

import sys
import os
import time
import subprocess

# List of required Python libraries
LIBRARIES = [
    "GeoIP", "python-geoip", "pygeoip", "requests", "whois",
    "scapy", "pycryptodomex", "duckduckgo-search"
]

# Ensure script is run with Python 3
if sys.version_info.major < 3:
    sys.exit("Sorry, UFONet requires Python >= 3")


def speech():
    print("[MASTER] Connecting UFONET [AI] system, remotely...\n")
    time.sleep(2)
    print("[AI] Hello Master!... ;-)\n")
    print("[AI] Launching self-deployment protocols...\n")
    time.sleep(1)
    print(r"""
      _______
    |.-----.|
    ||x . x||
    ||_.-._||
    `--)-(--`
   __[=== o]___
  |:::::::::::|
    """)


def check_euid():
    try:
        return os.geteuid()
    except AttributeError:
        return None  # Not available on Windows; assume non-root


def install_system_dependencies():
    print("\n[UFONET] Installing system packages...\n")
    apt_packages = [
        "libpython3.11-dev", "python3-pycurl", "python3-geoip",
        "python3-whois", "python3-requests",
        "libgeoip-dev", "libgeoip1t64"  # <-- Notice: libgeoip1t64 not libgeoip1
    ]
    subprocess.run(
        ["sudo", "apt-get", "update"], check=True
    )
    subprocess.run(
        ["sudo", "apt-get", "install", "-y", "--no-install-recommends"] + apt_packages,
        check=True
    )


def install_python_packages():
    print("\n[UFONET] Installing Python libraries...\n")

    base_cmd = [
        "python3", "-m", "pip", "install",
        "--no-warn-script-location",
        "--root-user-action=ignore",
        "--break-system-packages"
    ]

    # Attempt upgrading pip, but ignore error if uninstall fails
    try:
        subprocess.run(
            base_cmd + ["--upgrade", "pip"],
            check=True
        )
    except subprocess.CalledProcessError:
        print("[WARNING] Could not upgrade pip. Skipping... (Debian system pip is protected)")

    # Upgrade pycurl
    subprocess.run(
        base_cmd + ["pycurl", "--upgrade"],
        check=True
    )

    # Install all other libraries
    for lib in LIBRARIES:
        subprocess.run(
            base_cmd + [lib, "--ignore-installed"],
            check=False  # Continue even if some optional libraries fail
        )


def setup_web_folder():
    target_dir = "/var/www/ufonet/"
    print(f"\n[UFONET] Setting up web folder at {target_dir}...\n")
    
    try:
        # Step 1: Create folder if it doesn't exist
        if not os.path.exists(target_dir):
            subprocess.run(["sudo", "mkdir", "-p", target_dir], check=True)
            print(f"[UFONET] Created folder: {target_dir}")
        else:
            print(f"[UFONET] Folder already exists: {target_dir}")

        # Step 2: Check ownership
        stat_info = os.stat(target_dir)
        uid = stat_info.st_uid
        user_name = os.getenv('USER')
        import pwd
        current_owner = pwd.getpwuid(uid).pw_name

        if current_owner != user_name:
            subprocess.run(["sudo", "chown", f"{user_name}:{user_name}", target_dir], check=True)
            print(f"[UFONET] Ownership corrected to {user_name}:{user_name}")
        else:
            print(f"[UFONET] Ownership already correct: {current_owner}")

        # Step 3: Check permissions
        permissions = oct(stat_info.st_mode)[-3:]
        if permissions != "755":
            subprocess.run(["sudo", "chmod", "755", target_dir], check=True)
            print(f"[UFONET] Permissions corrected to 755")
        else:
            print(f"[UFONET] Permissions already 755")

        print("[UFONET] Web folder setup complete!")

    except Exception as e:
        print(f"[ERROR] Failed to setup {target_dir}: {e}")
        sys.exit(1)



def rerun_as_root():
    try:
        print("[UFONET] Root permissions are required. Trying sudo...\n")
        args = ["sudo", sys.executable] + sys.argv
        os.execvp("sudo", args)
    except Exception as e:
        sys.exit(f"[ERROR] Failed to rerun as root: {e}")


def main():
    if check_euid() not in (0, None):
        rerun_as_root()

    speech()
    install_system_dependencies()
    install_python_packages()
    setup_web_folder()

    print("\n[UFONET] Setup completed successfully! You can now run: ./ufonet\n")


if __name__ == '__main__':
    main()
