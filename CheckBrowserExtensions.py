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
            "Firefox": os.path.expanduser(f"C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
        }

        if os.name != 'nt':
            print("This script is designed to run on Windows systems only.")
            return

        extensions_found = False

        # Iterate through each browser
        for browser, path in browser_paths.items():
            try:
                if not os.path.exists(path):
                    print(f"{browser} extensions directory not found at: {path}")
                    continue

                if browser == "Firefox":
                    # Firefox stores extensions differently, in profile subdirectories
                    for profile in os.listdir(path):
                        profile_path = os.path.join(path, profile)
                        if os.path.isdir(profile_path):
                            addon_path = os.path.join(profile_path, "extensions")
                            if os.path.exists(addon_path):
                                for addon in os.listdir(addon_path):
                                    if addon.endswith('.xpi'):
                                        # Try to read the manifest.json from the XPI (simplified approach)
                                        print(
                                            f"Firefox Extension: {addon} (XPI file, detailed parsing not implemented)")
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
                                            print(f"{browser} Extension: {ext_name}")
                                            extensions_found = True
                                    except json.JSONDecodeError:
                                        print(f"{browser} Extension: {ext_id} (Failed to parse manifest)")
                                        extensions_found = True

            except Exception as e:
                print(f"Error checking {browser} extensions: {e}")

        if not extensions_found:
            print("No browser extensions found for Chrome, Edge, or Firefox.")

    except Exception as e:
        print(f"General error checking browser extensions: {e}")
        if not os.name == 'nt':
            print("This script is designed to run on Windows systems only.")


if __name__ == "__main__":
    print("Checking for installed browser extensions...")
    check_browser_extensions()