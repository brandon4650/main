import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

from config_utils import ConfigManager
from ui_components import (
    WoWThemedFrame as ThemedFrame,  # Create alias for backward compatibility
    WoWStatusBar as StatusBar,      # Create alias for backward compatibility
    WoWAboutDialog as AboutDialog,  # Create alias for backward compatibility
    WoWConfirmDialog as ConfirmDialog,  # Create alias for backward compatibility
    WOW_COLORS
)
from login_automation import LoginAutomation, CoordinatesTool

class AccountManagerScreen:
    """Screen for managing accounts for a specific server and expansion"""
    
    def __init__(self, root, server_name, expansion_name, expansion_data, config_manager, on_close_callback=None):
        self.root = root
        self.server_name = server_name
        self.expansion_name = expansion_name
        self.expansion_data = expansion_data
        self.config_manager = config_manager
        self.on_close_callback = on_close_callback
        
        # Configure window
        self.root.title(f"{server_name} - {expansion_name} Account Manager")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set minimum size
        self.root.minsize(500, 400)
        
        # Try to set icon
        try:
            self.root.iconbitmap("wow_icon.ico")
        except:
            pass
        
        # Account configuration
        self.accounts_file = expansion_data.get("accounts_file", f"accounts_{server_name.lower()}_{expansion_name.lower().replace(' ', '_')}.json")
        self.wow_path = expansion_data.get("path", "")
        self.coords_file = expansion_data.get("coords_file", f"login_coords_{server_name.lower()}_{expansion_name.lower().replace(' ', '_')}.json")
        
        # Load accounts
        self.accounts_data = self.config_manager.load_accounts(self.accounts_file)
        
        # Create UI elements
        self.create_layout()
        
        # Create menu
        self.create_menu()
        
        # Status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize login automation
        self.login_automation = LoginAutomation(
            self.root,
            lambda msg: self.status_bar.set_status(msg)
        )
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_layout(self):
        """Create the main layout for the account manager"""
        # Main container
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configure for resizing
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_container, 
            text=f"{self.server_name} - {self.expansion_name} Account Manager", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)
        
        # Account selection frame
        account_select_frame = ThemedFrame(main_container, title="Select Account")
        account_select_frame.grid(row=1, column=0, sticky=tk.EW, padx=5, pady=5)
        
        # Get content frame
        account_select_content = account_select_frame.get_content_frame()
        
        # Container for dropdown and button to allow better resizing
        dropdown_container = ttk.Frame(account_select_content)
        dropdown_container.pack(fill=tk.X, padx=5, pady=10)
        dropdown_container.columnconfigure(0, weight=1)
        
        # Account dropdown
        self.account_var = tk.StringVar()
        self.account_dropdown = ttk.Combobox(dropdown_container, textvariable=self.account_var, state="readonly")
        self.account_dropdown.grid(row=0, column=0, padx=(0,5), sticky=tk.EW)
        
        # Launch button
        self.launch_button = ttk.Button(dropdown_container, text="Launch", command=self.launch_game)
        self.launch_button.grid(row=0, column=1)
        
        # Update account dropdown
        self.update_account_dropdown()
        
        # Account management frame
        manage_frame = ThemedFrame(main_container, title="Manage Accounts")
        manage_frame.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=(15, 5))
        
        # Get content frame for account management
        manage_content = manage_frame.get_content_frame()
        
        # Enable grid resizing
        manage_content.columnconfigure(1, weight=1)
        manage_content.rowconfigure(6, weight=1)  # For the account list
        
        # Username field
        ttk.Label(manage_content, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(manage_content, textvariable=self.username_var)
        self.username_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Password field
        ttk.Label(manage_content, text="Password:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(manage_content, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Account alias field
        ttk.Label(manage_content, text="Account Alias:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.alias_var = tk.StringVar()
        self.alias_entry = ttk.Entry(manage_content, textvariable=self.alias_var)
        self.alias_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Account action buttons
        action_frame = ttk.Frame(manage_content)
        action_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.EW)
        
        # Configure columns for button layout
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        action_frame.columnconfigure(2, weight=1)
        
        # Add/Update button
        self.add_button = ttk.Button(action_frame, text="Add/Update Account", command=self.add_update_account)
        self.add_button.grid(row=0, column=0, padx=5, sticky=tk.EW)
        
        # Delete button
        self.delete_button = ttk.Button(action_frame, text="Delete Account", command=self.delete_account)
        self.delete_button.grid(row=0, column=1, padx=5, sticky=tk.EW)
        
        # Clear button
        self.clear_button = ttk.Button(action_frame, text="Clear Fields", command=self.clear_fields)
        self.clear_button.grid(row=0, column=2, padx=5, sticky=tk.EW)
        
        # Separator
        ttk.Separator(manage_content, orient="horizontal").grid(
            row=4, column=0, columnspan=2, sticky=tk.EW, pady=10
        )
        
        # Account list section
        ttk.Label(manage_content, text="All Accounts:", font=("Arial", 10, "bold")).grid(
            row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(5,0)
        )
        
        # Create account list treeview
        account_list_frame = ttk.Frame(manage_content)
        account_list_frame.grid(row=6, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)
        
        # Configure grid for treeview
        account_list_frame.columnconfigure(0, weight=1)
        account_list_frame.rowconfigure(0, weight=1)
        
        # Treeview for displaying accounts
        self.account_tree = ttk.Treeview(
            account_list_frame, 
            columns=("username", "alias"), 
            show="headings", 
            selectmode="browse"
        )
        self.account_tree.heading("username", text="Username")
        self.account_tree.heading("alias", text="Alias")
        self.account_tree.column("username", width=150)
        self.account_tree.column("alias", width=150)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(account_list_frame, orient="vertical", command=self.account_tree.yview)
        self.account_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout for treeview and scrollbar
        self.account_tree.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        # Bind events
        self.account_tree.bind("<<TreeviewSelect>>", self.on_account_selected_from_tree)
        self.account_dropdown.bind("<<ComboboxSelected>>", self.on_account_selected)
        
        # Populate the account list
        self.populate_account_tree()
    
    def create_menu(self):
        """Create menu bar for the account manager"""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Accounts", command=self.import_accounts)
        file_menu.add_command(label="Export Accounts", command=self.export_accounts)
        file_menu.add_separator()
        file_menu.add_command(label="Return to Server Selection", command=self.return_to_server_selection)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Configure Login Screen", command=self.open_coordinate_tool)
        tools_menu.add_command(label="Change Game Path", command=self.change_game_path)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def on_close(self):
        """Handle window close event"""
        # Call the close callback if available
        if self.on_close_callback:
            self.on_close_callback(self.root)
        else:
            self.root.destroy()
    
    def return_to_server_selection(self):
        """Return to the server selection screen"""
        self.on_close()
    
    def update_account_dropdown(self):
        """Update the account dropdown with available accounts"""
        # Get account names from the accounts data
        account_list = []
        for account in self.accounts_data.get("accounts", []):
            display_name = account.get("alias") or account.get("username")
            account_list.append(display_name)
        
        # Update dropdown values
        self.account_dropdown['values'] = account_list
        
        # Select first account if available
        if account_list:
            self.account_dropdown.current(0)
    
    def populate_account_tree(self):
        """Fill the account treeview with account data"""
        # Clear existing items
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)
        
        # Add accounts to the treeview
        for account in self.accounts_data.get("accounts", []):
            username = account.get("username", "")
            alias = account.get("alias", "")
            
            self.account_tree.insert("", "end", values=(username, alias))
    
    def clear_fields(self):
        """Clear all input fields"""
        self.username_var.set("")
        self.password_var.set("")
        self.alias_var.set("")
    
    def find_account_by_display_name(self, display_name):
        """Find account by display name (alias or username)"""
        for account in self.accounts_data.get("accounts", []):
            if (account.get("alias") == display_name or 
                (not account.get("alias") and account.get("username") == display_name)):
                return account
        return None
    
    def on_account_selected(self, event):
        """Handle account selection from dropdown"""
        selected = self.account_var.get()
        account = self.find_account_by_display_name(selected)
        
        if account:
            self.username_var.set(account.get("username", ""))
            self.password_var.set(account.get("password", ""))
            self.alias_var.set(account.get("alias", ""))
            
            # Also select in the treeview
            self.select_account_in_tree(account.get("username", ""))
    
    def on_account_selected_from_tree(self, event):
        """Handle account selection from treeview"""
        selection = self.account_tree.selection()
        if selection:
            item = selection[0]
            values = self.account_tree.item(item, "values")
            if values:
                username = values[0]
                
                # Find the account
                for account in self.accounts_data.get("accounts", []):
                    if account.get("username") == username:
                        self.username_var.set(account.get("username", ""))
                        self.password_var.set(account.get("password", ""))
                        self.alias_var.set(account.get("alias", ""))
                        
                        # Also select in the dropdown
                        display_name = account.get("alias") or account.get("username")
                        self.account_var.set(display_name)
                        break
    
    def select_account_in_tree(self, username):
        """Select the account with the given username in the treeview"""
        for item in self.account_tree.get_children():
            values = self.account_tree.item(item, "values")
            if values and values[0] == username:
                self.account_tree.selection_set(item)
                self.account_tree.see(item)
                break
    
    def add_update_account(self):
        """Add or update an account"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        alias = self.alias_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required!")
            return
        
        # Check if account already exists
        found = False
        for i, account in enumerate(self.accounts_data.get("accounts", [])):
            if account.get("username") == username:
                # Update existing account
                self.accounts_data["accounts"][i] = {
                    "username": username,
                    "password": password,
                    "alias": alias,
                    "server": self.server_name,
                    "expansion": self.expansion_name
                }
                found = True
                break
        
        if not found:
            # Create accounts list if it doesn't exist
            if "accounts" not in self.accounts_data:
                self.accounts_data["accounts"] = []
            
            # Add new account
            self.accounts_data["accounts"].append({
                "username": username,
                "password": password,
                "alias": alias,
                "server": self.server_name,
                "expansion": self.expansion_name
            })
        
        # Save accounts
        self.config_manager.save_accounts(self.accounts_data, self.accounts_file)
        
        # Update UI
        self.update_account_dropdown()
        self.populate_account_tree()
        self.clear_fields()
        
        # Update status
        display_name = alias or username
        self.status_bar.set_status(f"Account '{display_name}' saved")
        messagebox.showinfo("Success", f"Account '{display_name}' has been saved")
    
    def delete_account(self):
        """Delete the selected account"""
        username = self.username_var.get().strip()
        
        if not username:
            messagebox.showerror("Error", "No account selected")
            return
        
        # Find the account
        found = False
        for i, account in enumerate(self.accounts_data.get("accounts", [])):
            if account.get("username") == username:
                # Ask for confirmation
                display_name = account.get("alias") or account.get("username")
                confirm = ConfirmDialog(
                    self.root,
                    "Confirm Delete",
                    f"Are you sure you want to delete account '{display_name}'?"
                ).result
                
                if confirm:
                    # Remove the account
                    self.accounts_data["accounts"].pop(i)
                    
                    # Save accounts
                    self.config_manager.save_accounts(self.accounts_data, self.accounts_file)
                    
                    # Update UI
                    self.update_account_dropdown()
                    self.populate_account_tree()
                    self.clear_fields()
                    
                    # Update status
                    self.status_bar.set_status(f"Account '{display_name}' deleted")
                    messagebox.showinfo("Success", f"Account '{display_name}' has been deleted")
                
                found = True
                break
        
        if not found:
            messagebox.showerror("Error", f"Account with username '{username}' not found")
    
    def launch_game(self):
        """Launch the game with the selected account"""
        selected = self.account_var.get()
        if not selected:
            messagebox.showerror("Error", "No account selected")
            return
        
        account = self.find_account_by_display_name(selected)
        if not account:
            messagebox.showerror("Error", "Selected account not found")
            return
        
        # Check if game path exists
        if not self.wow_path or not os.path.exists(self.wow_path):
            messagebox.showerror(
                "Error", 
                f"Game executable not found at: {self.wow_path}\n"
                "Please set the correct path using Tools > Change Game Path."
            )
            return
        
        # Load login coordinates
        login_coords = self.config_manager.load_coordinates(self.coords_file)
        
        # Launch the game
        success = self.login_automation.launch_game(
            self.wow_path,
            account,
            login_coords
        )
        
        if success:
            self.status_bar.set_status(f"Launching game with account '{selected}'...")
    
    def import_accounts(self):
        """Import accounts from a JSON file"""
        try:
            import_file = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                title="Import Accounts"
            )
            
            if not import_file:
                return
            
            # Load accounts from file
            with open(import_file, 'r') as f:
                imported_data = json.load(f)
            
            imported_accounts = imported_data.get("accounts", [])
            
            if not imported_accounts:
                messagebox.showinfo("Import", "No accounts found in the selected file.")
                return
            
            # Ask whether to merge or replace
            if self.accounts_data.get("accounts"):
                merge = messagebox.askyesno(
                    "Import Accounts",
                    "Do you want to merge with existing accounts?\n"
                    "Click No to replace all existing accounts."
                )
                
                if merge:
                    # Update server and expansion for imported accounts
                    for account in imported_accounts:
                        account["server"] = self.server_name
                        account["expansion"] = self.expansion_name
                    
                    # Add imported accounts to existing accounts
                    self.accounts_data["accounts"].extend(imported_accounts)
                else:
                    # Replace all accounts with imported ones
                    # Update server and expansion for imported accounts
                    for account in imported_accounts:
                        account["server"] = self.server_name
                        account["expansion"] = self.expansion_name
                    
                    self.accounts_data["accounts"] = imported_accounts
            else:
                # No existing accounts, just set the imported ones
                # Update server and expansion for imported accounts
                for account in imported_accounts:
                    account["server"] = self.server_name
                    account["expansion"] = self.expansion_name
                
                self.accounts_data["accounts"] = imported_accounts
            
            # Save accounts
            self.config_manager.save_accounts(self.accounts_data, self.accounts_file)
            
            # Update UI
            self.update_account_dropdown()
            self.populate_account_tree()
            
            # Update status
            self.status_bar.set_status(f"Imported {len(imported_accounts)} accounts")
            messagebox.showinfo("Import Successful", f"Successfully imported {len(imported_accounts)} accounts.")
            
        except Exception as e:
            messagebox.showerror("Import Failed", f"Error importing accounts: {str(e)}")
    
    def export_accounts(self):
        """Export accounts to a JSON file"""
        try:
            if not self.accounts_data.get("accounts"):
                messagebox.showerror("Export Failed", "No accounts to export.")
                return
            
            export_file = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                title="Export Accounts"
            )
            
            if not export_file:
                return
            
            # Write accounts to file
            with open(export_file, 'w') as f:
                json.dump(self.accounts_data, f, indent=4)
            
            # Update status
            count = len(self.accounts_data.get("accounts", []))
            self.status_bar.set_status(f"Exported {count} accounts")
            messagebox.showinfo("Export Successful", f"Successfully exported {count} accounts.")
            
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error exporting accounts: {str(e)}")
    
    def open_coordinate_tool(self):
        """Open the login screen coordinate configuration tool"""
        coord_tool = CoordinatesTool(
            self.root,
            self.coords_file,
            lambda coords: self.status_bar.set_status("Login screen coordinates saved")
        )
    
    def change_game_path(self):
        """Change the path to the game executable"""
        try:
            game_path = filedialog.askopenfilename(
                filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")],
                title="Select Game Executable"
            )
            
            if not game_path:
                return
            
            # Update the path in memory
            self.wow_path = game_path
            self.expansion_data["path"] = game_path
            
            # Update the path in the server configuration
            servers = self.config_manager.load_servers()
            if (self.server_name in servers and 
                "expansions" in servers[self.server_name] and 
                self.expansion_name in servers[self.server_name]["expansions"]):
                
                servers[self.server_name]["expansions"][self.expansion_name]["path"] = game_path
                self.config_manager.save_servers(servers)
                
                # Update status
                self.status_bar.set_status(f"Game path updated")
                messagebox.showinfo("Path Updated", f"Game executable path has been updated.")
            else:
                messagebox.showerror(
                    "Update Failed", 
                    "Could not update the server configuration. The path will only be used for this session."
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change game path: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        AboutDialog(
            self.root,
            f"{self.server_name} Account Manager",
            "1.0",
            f"Account manager for {self.server_name} - {self.expansion_name}."
        )
