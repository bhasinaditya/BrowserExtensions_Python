"""
Python script to return a list of installed browser extensions.

TODO: Script needs to filter out extensions
"""

import os
import json
import getpass

def check_browser_extensions():
    try:
        # Get the current user's username
        username = getpass.getuser()
        # Define browser extension directories for Windows
        browser_paths = {
            "Chrome": os.path.expanduser(
                f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions"),
            "Edge": os.path.expanduser(
                f"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Extensions"),
            "Firefox": os.path.expanduser(
                f"C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
        }
        if os.name != 'nt':
            return
        extensions_found = False
        # Iterate through each browser
        for browser, path in browser_paths.items():
            try:
                if not os.path.exists(path):
                    continue
                extension_list = []
                if browser == "Firefox":
                    # Firefox stores extensions in profile subdirectories
                    for profile in os.listdir(path):
                        profile_path = os.path.join(path, profile)
                        if os.path.isdir(profile_path):
                            addon_path = os.path.join(profile_path, "extensions")
                            if os.path.exists(addon_path):
                                for addon in os.listdir(addon_path):
                                    if addon.endswith('.xpi'):
                                        extension_list.append(f"{addon} (XPI file)")
                                        extensions_found = True
                else:
                    # Chrome and Edge store extensions in subdirectories with manifest.json
                    for ext_id in os.listdir(path):
                        ext_path = os.path.join(path, ext_id)
                        if os.path.isdir(ext_path):
                            # Look for manifest.json in versioned subdirectories
                            for version in os.listdir(ext_path):
                                manifest_path = os.path.join(ext_path, version, "manifest.json")
                                if os.path.exists(manifest_path):
                                    try:
                                        with open(manifest_path, 'r', encoding='utf-8') as f:
                                            manifest = json.load(f)
                                            ext_name = manifest.get('name', 'Unknown Extension')
                                            # Silently skip extensions with __MSG in name
                                            if '__MSG' not in ext_name:
                                                extension_list.append(ext_name)
                                                extensions_found = True
                                    except json.JSONDecodeError:
                                        extension_list.append(f"{ext_id} (Failed to parse manifest)")
                                        extensions_found = True
                # Print extensions under a single browser heading
                if extension_list:
                    print(f"\n{browser} Extensions:")
                    for ext_name in extension_list:
                        print(f" - {ext_name}")
            except Exception:
                continue
        if not extensions_found:
            pass  # Silently continue if no extensions are found
    except Exception:
        if os.name != 'nt':
            pass  # Silently continue for non-Windows systems

if __name__ == "__main__":
    check_browser_extensions()