import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

from config_utils import ConfigManager
from ui_components import (
    WoWThemedFrame, WoWStatusBar, WoWAboutDialog, 
    apply_global_styling, WOW_COLORS, WoWConfirmDialog
)
from account_manager import AccountManagerScreen

class ServerManagerScreen:
    """Main screen for managing different WoW private servers"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("WoW Private Server Manager")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        # Set minimum size
        self.root.minsize(650, 500)
        
        # Configure root window with WoW colors
        self.root.configure(bg=WOW_COLORS["bg_dark"])
        
        # Try to set icon
        try:
            self.root.iconbitmap("wow_icon.ico")
        except:
            pass
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        
        # Auto-detect account files
        self.servers = self.config_manager.detect_existing_accounts()
        
        # Apply global styling
        apply_global_styling()
        
        # Create main layout
        self.create_layout()
        
        # Create menu
        self.create_menu()
        
        # Status bar
        self.status_bar = WoWStatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_layout(self):
        """Create the main application layout"""
        # Main container
        main_container = ttk.Frame(self.root, style="WoW.TFrame", padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure for resizing
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_container, 
            text="WoW Private Server Manager", 
            style="Title.TLabel"
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)
        
        # Server browser section
        self.server_frame = WoWThemedFrame(main_container, title="Available Servers")
        self.server_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        server_content = self.server_frame.get_content_frame()
        
        # Create and configure the server tree
        self.create_server_tree(server_content)
        
        # Buttons frame
        button_frame = ttk.Frame(main_container, style="WoW.TFrame")
        button_frame.grid(row=2, column=0, sticky=tk.EW, pady=15)
        
        # Configure columns for button layout
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)
        
        # Add buttons
        self.connect_button = ttk.Button(
            button_frame, 
            text="Connect", 
            style="Gold.TButton",
            command=self.connect_to_server
        )
        self.connect_button.grid(row=0, column=0, padx=5, sticky=tk.EW)
        
        self.add_server_button = ttk.Button(
            button_frame, 
            text="Add Server", 
            command=self.add_server
        )
        self.add_server_button.grid(row=0, column=1, padx=5, sticky=tk.EW)
        
        self.edit_server_button = ttk.Button(
            button_frame, 
            text="Edit", 
            command=self.edit_server
        )
        self.edit_server_button.grid(row=0, column=2, padx=5, sticky=tk.EW)
        
        self.remove_server_button = ttk.Button(
            button_frame, 
            text="Remove", 
            command=self.remove_server
        )
        self.remove_server_button.grid(row=0, column=3, padx=5, sticky=tk.EW)
    
    def create_server_tree(self, parent):
        """Create the treeview widget for displaying servers and expansions"""
        # Create a frame to hold the treeview and scrollbar
        tree_frame = ttk.Frame(parent, style="WoW.TFrame")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview with scrollbar
        self.server_tree = ttk.Treeview(tree_frame, columns=("path",), show="tree headings")
        self.server_tree.heading("#0", text="Servers and Expansions")
        self.server_tree.heading("path", text="Path")
        self.server_tree.column("#0", width=250, stretch=True)
        self.server_tree.column("path", width=350, stretch=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.server_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.server_tree.xview)
        self.server_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.server_tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        
        # Configure expansion
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # Double-click binding
        self.server_tree.bind("<Double-1>", lambda e: self.connect_to_server())
        
        # Populate server tree with data
        self.populate_server_tree()
    
    def populate_server_tree(self):
        """Fill the server tree with server and expansion data"""
        # Clear existing items
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)
        
        # Add servers as top-level items
        for server_name, server_data in self.servers.items():
            server_id = self.server_tree.insert("", "end", text=server_name, values=("",), open=True)
            
            # Add expansions as children
            if "expansions" in server_data:
                for expansion_name, expansion_data in server_data["expansions"].items():
                    path = expansion_data.get("path", "")
                    self.server_tree.insert(
                        server_id, 
                        "end", 
                        text=expansion_name,
                        values=(path,),
                        tags=("expansion",)
                    )
    
    def create_menu(self):
        """Create the application menu"""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # Configure menu with WoW colors
        menu_bar.configure(bg=WOW_COLORS["bg_dark"], fg=WOW_COLORS["text_normal"], activebackground=WOW_COLORS["bg_light"], activeforeground=WOW_COLORS["accent_gold"])
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.configure(bg=WOW_COLORS["bg_dark"], fg=WOW_COLORS["text_normal"], activebackground=WOW_COLORS["bg_light"], activeforeground=WOW_COLORS["accent_gold"])
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh Server List", command=self.refresh_servers)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.configure(bg=WOW_COLORS["bg_dark"], fg=WOW_COLORS["text_normal"], activebackground=WOW_COLORS["bg_light"], activeforeground=WOW_COLORS["accent_gold"])
        menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Scan for Account Files", 
                              command=lambda: self.config_manager.detect_existing_accounts())
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.configure(bg=WOW_COLORS["bg_dark"], fg=WOW_COLORS["text_normal"], activebackground=WOW_COLORS["bg_light"], activeforeground=WOW_COLORS["accent_gold"])
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def connect_to_server(self):
        """Connect to the selected server/expansion"""
        selection = self.server_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a server or expansion to connect to.")
            return
        
        item = selection[0]
        parent_id = self.server_tree.parent(item)
        
        # Determine if a server or expansion is selected
        if parent_id:  # Expansion selected
            server_name = self.server_tree.item(parent_id, "text")
            expansion_name = self.server_tree.item(item, "text")
            
            # Check if expansion exists
            if (server_name in self.servers and 
                "expansions" in self.servers[server_name] and 
                expansion_name in self.servers[server_name]["expansions"]):
                
                expansion_data = self.servers[server_name]["expansions"][expansion_name]
                
                # Check if executable exists
                if not expansion_data.get("path") or not os.path.exists(expansion_data["path"]):
                    messagebox.showerror(
                        "Error", 
                        f"Game executable not found: {expansion_data.get('path')}\n"
                        "Please edit the server configuration."
                    )
                    return
                
                # Update last used
                self.config_manager.update_last_used(server_name, expansion_name)
                
                # Hide current window
                self.root.withdraw()
                
                # Launch account manager
                account_manager_root = tk.Toplevel(self.root)
                account_manager_root.configure(bg=WOW_COLORS["bg_dark"])
                account_manager = AccountManagerScreen(
                    account_manager_root, 
                    server_name, 
                    expansion_name, 
                    expansion_data, 
                    self.config_manager,
                    self.on_account_manager_close
                )
            else:
                messagebox.showerror("Error", "Selected expansion not found in configuration.")
        else:  # Server selected
            # Check if the server has any expansions
            server_name = self.server_tree.item(item, "text")
            if server_name in self.servers and "expansions" in self.servers[server_name]:
                expansions = self.servers[server_name]["expansions"]
                if expansions:
                    # If there's only one expansion, connect directly
                    if len(expansions) == 1:
                        expansion_name = next(iter(expansions))
                        expansion_data = expansions[expansion_name]
                        
                        # Check if executable exists
                        if not expansion_data.get("path") or not os.path.exists(expansion_data["path"]):
                            messagebox.showerror(
                                "Error", 
                                f"Game executable not found: {expansion_data.get('path')}\n"
                                "Please edit the server configuration."
                            )
                            return
                        
                        # Update last used
                        self.config_manager.update_last_used(server_name, expansion_name)
                        
                        # Hide current window
                        self.root.withdraw()
                        
                        # Launch account manager
                        account_manager_root = tk.Toplevel(self.root)
                        account_manager_root.configure(bg=WOW_COLORS["bg_dark"])
                        account_manager = AccountManagerScreen(
                            account_manager_root, 
                            server_name, 
                            expansion_name, 
                            expansion_data, 
                            self.config_manager,
                            self.on_account_manager_close
                        )
                    else:
                        # If multiple expansions, ask user to select one
                        messagebox.showinfo(
                            "Select Expansion", 
                            f"Please select a specific expansion for {server_name}."
                        )
                else:
                    messagebox.showinfo(
                        "No Expansions", 
                        f"Server {server_name} has no configured expansions. Please add one."
                    )
            else:
                messagebox.showerror("Error", "Selected server not found in configuration.")
    
    def on_account_manager_close(self, account_manager_root):
        """Handle closing of the account manager window"""
        account_manager_root.destroy()
        self.root.deiconify()
    
    def add_server(self):
        """Add a new server"""
        self.open_server_dialog("Add New Server")
    
    def edit_server(self):
        """Edit the selected server or expansion"""
        selection = self.server_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a server or expansion to edit.")
            return
        
        item = selection[0]
        parent_id = self.server_tree.parent(item)
        
        if parent_id:  # Expansion selected
            server_name = self.server_tree.item(parent_id, "text")
            expansion_name = self.server_tree.item(item, "text")
            self.open_expansion_dialog("Edit Expansion", server_name, expansion_name)
        else:  # Server selected
            server_name = self.server_tree.item(item, "text")
            self.open_server_dialog("Edit Server", server_name)
    
    def remove_server(self):
        """Remove the selected server or expansion"""
        selection = self.server_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a server or expansion to remove.")
            return
        
        item = selection[0]
        parent_id = self.server_tree.parent(item)
        
        if parent_id:  # Expansion selected
            server_name = self.server_tree.item(parent_id, "text")
            expansion_name = self.server_tree.item(item, "text")
            
            confirm = WoWConfirmDialog(
                self.root,
                "Confirm Remove", 
                f"Are you sure you want to remove the expansion '{expansion_name}' from server '{server_name}'?"
            ).result
            
            if confirm:
                # Remove the expansion
                if (server_name in self.servers and 
                    "expansions" in self.servers[server_name] and 
                    expansion_name in self.servers[server_name]["expansions"]):
                    
                    del self.servers[server_name]["expansions"][expansion_name]
                    
                    # If no more expansions left, ask if server should be removed too
                    if not self.servers[server_name]["expansions"]:
                        confirm_server = WoWConfirmDialog(
                            self.root,
                            "No Expansions Left", 
                            f"Server '{server_name}' now has no expansions. Do you want to remove the server too?"
                        ).result
                        if confirm_server:
                            del self.servers[server_name]
                    
                    # Save and update
                    self.config_manager.save_servers(self.servers)
                    self.populate_server_tree()
                    self.status_bar.set_status(f"Removed expansion '{expansion_name}' from server '{server_name}'")
        else:  # Server selected
            server_name = self.server_tree.item(item, "text")
            
            confirm = WoWConfirmDialog(
                self.root,
                "Confirm Remove", 
                f"Are you sure you want to remove the server '{server_name}' and all its expansions?"
            ).result
            
            if confirm:
                # Remove the server
                if server_name in self.servers:
                    del self.servers[server_name]
                    
                    # Save and update
                    self.config_manager.save_servers(self.servers)
                    self.populate_server_tree()
                    self.status_bar.set_status(f"Removed server '{server_name}'")
    
    def open_server_dialog(self, title, existing_server=None):
        """Open dialog to add or edit a server"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("450x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=WOW_COLORS["bg_dark"])
        
        # Make dialog modal
        dialog.focus_set()
        
        # Main frame with WoW styling
        frame = ttk.Frame(dialog, style="WoW.TFrame", padding="20")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dialog title
        title_label = ttk.Label(
            frame, 
            text=title, 
            style="Title.TLabel"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=tk.W)
        
        # Separator
        separator = ttk.Separator(frame, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        # Server details
        ttk.Label(frame, text="Server Name:").grid(row=2, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(frame, textvariable=name_var)
        name_entry.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=5)
        
        # Set values if editing
        if existing_server:
            name_var.set(existing_server)
            # Make name non-editable for existing servers
            name_entry.configure(state="disabled")
        
        # Buttons with WoW styling
        button_frame = ttk.Frame(frame, style="WoW.TFrame")
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        save_button = ttk.Button(
            button_frame, 
            text="Save", 
            style="Gold.TButton",
            command=lambda: self.save_server(dialog, name_var.get(), existing_server)
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=dialog.destroy
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Make grid expandable
        frame.columnconfigure(1, weight=1)
    
    def open_expansion_dialog(self, title, server_name, existing_expansion=None):
        """Open dialog to add or edit an expansion"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x350")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=WOW_COLORS["bg_dark"])
        
        # Make dialog modal
        dialog.focus_set()
        
        # Main frame with WoW styling
        frame = ttk.Frame(dialog, style="WoW.TFrame", padding="20")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dialog title
        title_label = ttk.Label(
            frame, 
            text=title, 
            style="Title.TLabel"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky=tk.W)
        
        # Separator
        separator = ttk.Separator(frame, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        # Server name (display only)
        ttk.Label(frame, text="Server:").grid(row=2, column=0, sticky=tk.W, pady=5)
        server_label = ttk.Label(
            frame, 
            text=server_name, 
            foreground=WOW_COLORS["accent_gold"],
            background=WOW_COLORS["bg_medium"]
        )
        server_label.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Expansion details
        ttk.Label(frame, text="Expansion:").grid(row=3, column=0, sticky=tk.W, pady=5)
        expansion_var = tk.StringVar()
        expansion_entry = ttk.Entry(frame, textvariable=expansion_var)
        expansion_entry.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=5)
        
        ttk.Label(frame, text="Executable Path:").grid(row=4, column=0, sticky=tk.W, pady=5)
        path_var = tk.StringVar()
        path_frame = ttk.Frame(frame, style="WoW.TFrame")
        path_frame.grid(row=4, column=1, sticky=tk.EW, pady=5, padx=5)
        path_entry = ttk.Entry(path_frame, textvariable=path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        browse_button = ttk.Button(
            path_frame, 
            text="Browse", 
            command=lambda: self.browse_executable(path_var)
        )
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(frame, text="Accounts File:").grid(row=5, column=0, sticky=tk.W, pady=5)
        accounts_var = tk.StringVar()
        accounts_entry = ttk.Entry(frame, textvariable=accounts_var)
        accounts_entry.grid(row=5, column=1, sticky=tk.EW, pady=5, padx=5)
        
        ttk.Label(frame, text="Coordinates File:").grid(row=6, column=0, sticky=tk.W, pady=5)
        coords_var = tk.StringVar()
        coords_entry = ttk.Entry(frame, textvariable=coords_var)
        coords_entry.grid(row=6, column=1, sticky=tk.EW, pady=5, padx=5)
        
        # Set values if editing
        if existing_expansion and server_name in self.servers and "expansions" in self.servers[server_name]:
            expansions = self.servers[server_name]["expansions"]
            if existing_expansion in expansions:
                expansion_data = expansions[existing_expansion]
                
                expansion_var.set(existing_expansion)
                path_var.set(expansion_data.get("path", ""))
                accounts_var.set(expansion_data.get("accounts_file", ""))
                coords_var.set(expansion_data.get("coords_file", ""))
                
                # Make expansion name non-editable for existing expansions
                expansion_entry.configure(state="disabled")
        else:
            # Default values for new expansion
            expansion_var.set("")
            path_var.set("")
            
            # Generate default account and coords files based on server and expansion
            def sanitize_filename(s):
                return s.lower().replace(" ", "_")
            
            server_part = sanitize_filename(server_name)
            accounts_var.set(f"accounts_{server_part}_new.json")
            coords_var.set(f"login_coords_{server_part}_new.json")
        
        # Buttons with WoW styling
        button_frame = ttk.Frame(frame, style="WoW.TFrame")
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        save_button = ttk.Button(
            button_frame, 
            text="Save", 
            style="Gold.TButton",
            command=lambda: self.save_expansion(
                dialog, 
                server_name, 
                expansion_var.get(), 
                path_var.get(),
                accounts_var.get(),
                coords_var.get(),
                existing_expansion
            )
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=dialog.destroy
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Make grid expandable
        frame.columnconfigure(1, weight=1)
    
    def browse_executable(self, path_var):
        """Open file dialog to browse for executable"""
        file_path = filedialog.askopenfilename(
            title="Select WoW Executable",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if file_path:
            path_var.set(file_path)
    
    def save_server(self, dialog, name, existing_server=None):
        """Save the server to configuration"""
        # Validation
        if not name:
            messagebox.showerror("Error", "Server name is required.")
            return
        
        if not existing_server and name in self.servers:
            messagebox.showerror("Error", f"A server with name '{name}' already exists.")
            return
        
        # Create new server if it doesn't exist
        if existing_server:
            # Rename the server if name changed
            if existing_server != name:
                self.servers[name] = self.servers[existing_server]
                del self.servers[existing_server]
        else:
            # Create new server
            self.servers[name] = {"expansions": {}}
        
        # Save configuration
        self.config_manager.save_servers(self.servers)
        
        # Update UI
        self.populate_server_tree()
        self.status_bar.set_status(f"Server '{name}' saved")
        
        # Close dialog
        dialog.destroy()
        
        # If this is a new server, open dialog to add an expansion
        if not existing_server:
            self.open_expansion_dialog("Add Expansion for " + name, name)
    
    def save_expansion(self, dialog, server_name, expansion_name, path, accounts_file, coords_file, existing_expansion=None):
        """Save the expansion to configuration"""
        # Validation
        if not expansion_name:
            messagebox.showerror("Error", "Expansion name is required.")
            return
        
        if not server_name in self.servers:
            messagebox.showerror("Error", f"Server '{server_name}' not found.")
            return
        
        if not "expansions" in self.servers[server_name]:
            self.servers[server_name]["expansions"] = {}
        
        if not existing_expansion and expansion_name in self.servers[server_name]["expansions"]:
            messagebox.showerror("Error", f"An expansion with name '{expansion_name}' already exists for this server.")
            return
        
        # Validate path
        if path and not os.path.exists(path):
            messagebox.showwarning(
                "Warning", 
                f"The executable path does not exist: {path}\nYou will need to update it later."
            )
        
        # Prepare expansion data
        expansion_data = {
            "path": path,
            "accounts_file": accounts_file,
            "coords_file": coords_file
        }
        
        # Add/update expansion
        if existing_expansion:
            # Rename the expansion if name changed
            if existing_expansion != expansion_name:
                self.servers[server_name]["expansions"][expansion_name] = expansion_data
                del self.servers[server_name]["expansions"][existing_expansion]
            else:
                # Update existing
                self.servers[server_name]["expansions"][expansion_name] = expansion_data
        else:
            # Add new
            self.servers[server_name]["expansions"][expansion_name] = expansion_data
        
        # Save configuration
        self.config_manager.save_servers(self.servers)
        
        # Update UI
        self.populate_server_tree()
        self.status_bar.set_status(f"Expansion '{expansion_name}' saved for server '{server_name}'")
        
        # Close dialog
        dialog.destroy()
    
    def refresh_servers(self):
        """Refresh the server list from configuration"""
        self.servers = self.config_manager.load_servers()
        self.populate_server_tree()
        self.status_bar.set_status("Server list refreshed")
    
    def show_about(self):
        """Show about dialog"""
        WoWAboutDialog(
            self.root,
            "WoW Private Server Manager",
            "1.0",
            "A tool for managing multiple WoW private servers and accounts."
        )