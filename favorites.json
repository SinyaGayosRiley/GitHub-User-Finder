import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class GitHubUserFinder:
    def init(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # Favorites file
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()

        # GUI Elements
        self.create_widgets()

    def create_widgets(self):
        # Search label and entry
        ttk.Label(self.root, text="GitHub Username:", font=("Arial", 12)).pack(pady=(10, 0))
        self.search_entry = ttk.Entry(self.root, width=50, font=("Arial", 10))
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<Return>", lambda e: self.search_user())

        # Search button
        self.search_btn = ttk.Button(self.root, text="Search", command=self.search_user)
        self.search_btn.pack(pady=5)

        # Results Treeview
        columns = ("Avatar", "Username", "Profile URL", "Type")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)
        self.tree.heading("Avatar", text="Avatar URL")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Profile URL", text="Profile URL")
        self.tree.heading("Type", text="Type")
        self.tree.column("Avatar", width=200)
        self.tree.column("Username", width=150)
        self.tree.column("Profile URL", width=200)
        self.tree.column("Type", width=100)

        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Buttons frame
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=5)

        self.add_fav_btn = ttk.Button(btn_frame, text="Add to Favorites", command=self.add_to_favorites)
        self.add_fav_btn.pack(side=tk.LEFT, padx=5)

        self.show_fav_btn = ttk.Button(btn_frame, text="Show Favorites", command=self.show_favorites_window)
        self.show_fav_btn.pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def search_user(self):
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showwarning("Input Error", "Search field cannot be empty!")
            return

        self.status_var.set(f"Searching for '{username}'...")
        self.root.update_idletasks()

        # Clear previous results
        for row in self.tree.get_children():
            self.tree.delete(row)

        # GitHub API call
        try:
            url = f"https://api.github.com/users/{username}"
            response = requests.get(url)
            if response.status_code == 200:
                user_data = response.json()
                self.tree.insert("", tk.END, values=(
                    user_data.get("avatar_url", "N/A"),
                    user_data.get("login", "N/A"),
                    user_data.get("html_url", "N/A"),
                    user_data.get("type", "N/A")
                ))
                self.status_var.set(f"User '{username}' found.")
            elif response.status_code == 404:
                self.status_var.set(f"User '{username}' not found.")
                messagebox.showinfo("Not Found", f"GitHub user '{username}' does not exist.")
            else:
                self.status_var.set("API error. Try again later.")
        except Exception as e:
            self.status_var.set("Network error")
            messagebox.showerror("Error", f"Failed to connect to GitHub API.\n{e}")

    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            with open(self.favorites_file, "r") as f:
                try:
                    return json.load(f)
                except:
                    return []
        return []
def save_favorites(self):
        with open(self.favorites_file, "w") as f:
            json.dump(self.favorites, f, indent=4)

    def add_to_favorites(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please search and select a user first.")
            return

        item = self.tree.item(selected[0])
        values = item["values"]
        user_data = {
            "username": values[1],
            "avatar_url": values[0],
            "profile_url": values[2],
            "type": values[3],
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Check if already in favorites
        if any(fav["username"] == user_data["username"] for fav in self.favorites):
            messagebox.showinfo("Already exists", f"{user_data['username']} is already in favorites.")
            return

        self.favorites.append(user_data)
        self.save_favorites()
        self.status_var.set(f"Added {user_data['username']} to favorites.")

    def show_favorites_window(self):
        fav_win = tk.Toplevel(self.root)
        fav_win.title("Favorite GitHub Users")
        fav_win.geometry("600x400")

        columns = ("Username", "Profile URL", "Type", "Added At")
        tree_fav = ttk.Treeview(fav_win, columns=columns, show="headings")
        for col in columns:
            tree_fav.heading(col, text=col)
            tree_fav.column(col, width=130)
        tree_fav.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for fav in self.favorites:
            tree_fav.insert("", tk.END, values=(
                fav["username"],
                fav["profile_url"],
                fav["type"],
                fav["added_at"]
            ))

        def remove_selected():
            selected = tree_fav.selection()
            if not selected:
                return
            for sel in selected:
                values = tree_fav.item(sel)["values"]
                username = values[0]
                self.favorites = [fav for fav in self.favorites if fav["username"] != username]
                self.save_favorites()
                tree_fav.delete(sel)
            messagebox.showinfo("Removed", "Selected user(s) removed from favorites.")

        ttk.Button(fav_win, text="Remove Selected", command=remove_selected).pack(pady=5)

if name == "main":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()