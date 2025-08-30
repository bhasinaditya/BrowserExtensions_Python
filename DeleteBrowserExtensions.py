import os
import json
import getpass
import shutil
import tkinter as tk
from tkinter import messagebox, ttk


class ExtensionManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Browser Extensions Manager")
        self.root.geometry("600x400")

        # Dictionary to store extension checkboxes and their paths
        self.extension_checkboxes = {}
        self.extension_paths = {}

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create a canvas with scrollbar
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Configure main frame to expand
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Delete button
        self.delete_button = ttk.Button(self.main_frame, text="Delete Selected", command=self.delete_extensions)
        self.delete_button.grid(row=1, column=0, pady=10)

        # Load extensions
        self.load_extensions()

    def load_extensions(self):
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
                messagebox.showerror("Error", "This script is designed to run on Windows systems only.")
                return

            row = 0
            extensions_found = False

            # Iterate through each browser
            for browser, path in browser_paths.items():
                try:
                    if not os.path.exists(path):
                        ttk.Label(self.scrollable_frame, text=f"{browser} extensions directory not found.").grid(
                            row=row, column=0, sticky=tk.W, pady=2)
                        row += 1
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
                                            extension_list.append(
                                                (f"{addon} (XPI file)", os.path.join(addon_path, addon)))
                                            extensions_found = True
                    else:
                        # Chrome and Edge store extensions in subdirectories
                        for ext_id in os.listdir(path):
                            ext_path = os.path.join(path, ext_id)
                            if os.path.isdir(ext_path):
                                for version in os.listdir(ext_path):
                                    manifest_path = os.path.join(ext_path, version, "manifest.json")
                                    if os.path.exists(manifest_path):
                                        try:
                                            with open(manifest_path, 'r', encoding='utf-8') as f:
                                                manifest = json.load(f)
                                                ext_name = manifest.get('name', 'Unknown Extension')
                                                extension_list.append((ext_name, ext_path))
                                                extensions_found = True
                                        except json.JSONDecodeError:
                                            extension_list.append((f"{ext_id} (Failed to parse manifest)", ext_path))
                                            extensions_found = True

                    # Display extensions under a single browser heading
                    if extension_list:
                        ttk.Label(self.scrollable_frame, text=f"{browser} Extensions:",
                                  font=("Arial", 12, "bold")).grid(row=row, column=0, sticky=tk.W, pady=5)
                        row += 1
                        for ext_name, ext_path in extension_list:
                            var = tk.BooleanVar()
                            ttk.Checkbutton(
                                self.scrollable_frame,
                                text=ext_name,
                                variable=var
                            ).grid(row=row, column=0, sticky=tk.W, padx=20)
                            self.extension_checkboxes[(browser, ext_name)] = var
                            self.extension_paths[(browser, ext_name)] = ext_path
                            row += 1

                except Exception as e:
                    ttk.Label(self.scrollable_frame, text=f"Error checking {browser} extensions: {e}").grid(row=row,
                                                                                                            column=0,
                                                                                                            sticky=tk.W,
                                                                                                            pady=2)
                    row += 1

            if not extensions_found:
                ttk.Label(self.scrollable_frame, text="No browser extensions found for Chrome, Edge, or Firefox.").grid(
                    row=row, column=0, sticky=tk.W, pady=2)

        except Exception as e:
            messagebox.showerror("Error", f"General error checking browser extensions: {e}")
            if not os.name == 'nt':
                messagebox.showerror("Error", "This script is designed to run on Windows systems only.")

    def delete_extensions(self):
        selected_extensions = [
            (browser, ext_name, self.extension_paths[(browser, ext_name)])
            for (browser, ext_name), var in self.extension_checkboxes.items()
            if var.get()
        ]

        if not selected_extensions:
            messagebox.showinfo("Info", "No extensions selected for deletion.")
            return

        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_extensions)} extension(s)?\n\n" +
            "\n".join(f"{browser}: {ext_name}" for browser, ext_name, _ in selected_extensions)
        )

        if not confirm:
            return

        # Delete selected extensions
        for browser, ext_name, ext_path in selected_extensions:
            try:
                if browser == "Firefox":
                    # For Firefox, delete the .xpi file
                    if os.path.isfile(ext_path):
                        os.remove(ext_path)
                else:
                    # For Chrome and Edge, delete the entire extension directory
                    if os.path.isdir(ext_path):
                        shutil.rmtree(ext_path)
                messagebox.showinfo("Success", f"Deleted {browser} extension: {ext_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete {browser} extension {ext_name}: {e}")

        # Refresh the extension list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.extension_checkboxes.clear()
        self.extension_paths.clear()
        self.load_extensions()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExtensionManagerApp(root)
    root.mainloop()