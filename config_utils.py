import os
import json
import tkinter as tk
from tkinter import messagebox, filedialog

class ConfigManager:
    """Handles configuration file operations for the application"""
    
    def __init__(self):
        # Main configuration files
        self.servers_config_file = "servers_config.json"
        self.global_config_file = "app_config.json"
        
        # Default configurations
        self.default_server_data = {
            "StormForge": {
                "expansions": {
                    "MoP 5.4.8": {
                        "path": r"F:\stormforge mop\mop_minimal_new\Wow-64_patched.exe",
                        "accounts_file": "accounts_stormforge_mop.json",
                        "coords_file": "login_coords_stormforge_mop.json"
                    },
                    "TBC 2.4.3": {
                        "path": r"F:\stormforge tbc\2.4.3 bot testing client\Wow.exe",
                        "accounts_file": "accounts_stormforge_tbc.json",
                        "coords_file": "login_coords_stormforge_tbc.json"
                    }
                }
            }
        }
        
        # Global app settings
        self.global_config = {
            "theme": "default",
            "auto_update_check": True,
            "last_server": "",
            "last_expansion": ""
        }
        
        # Initialize configs if they don't exist
        self.init_configs()
    
    def init_configs(self):
        """Initialize configuration files if they don't exist"""
        # Initialize global config
        if not os.path.exists(self.global_config_file):
            self.save_global_config()
        
        # Check for existing account files first
        account_files_exist = False
        
        # Look for account files with standard naming patterns
        account_files = [f for f in os.listdir('.') if f.startswith('accounts_') and f.endswith('.json')]
        sfaccounts_files = [f for f in os.listdir('.') if f.startswith('sfaccounts_') and f.endswith('.json')]
        
        if account_files or sfaccounts_files:
            account_files_exist = True
        
        # Initialize servers config only if it doesn't exist
        if not os.path.exists(self.servers_config_file):
            if account_files_exist:
                # If account files exist, start with an empty configuration
                # The detect_existing_accounts method will populate it
                self.save_servers({})
            else:
                # No account files, use default servers
                self.save_servers(self.default_server_data)
    
    def load_servers(self):
        """Load server configuration from file"""
        if os.path.exists(self.servers_config_file):
            try:
                with open(self.servers_config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load server configuration: {e}")
                return self.default_server_data
        else:
            return self.default_server_data
    
    def save_servers(self, servers_data):
        """Save server configuration to file"""
        try:
            with open(self.servers_config_file, 'w') as f:
                json.dump(servers_data, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save server configuration: {e}")
            return False
    
    def load_global_config(self):
        """Load global application configuration"""
        if os.path.exists(self.global_config_file):
            try:
                with open(self.global_config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Update our default config with loaded values
                    self.global_config.update(loaded_config)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load application configuration: {e}")
        return self.global_config
    
    def save_global_config(self):
        """Save global application configuration"""
        try:
            with open(self.global_config_file, 'w') as f:
                json.dump(self.global_config, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save application configuration: {e}")
            return False
    
    def update_last_used(self, server, expansion):
        """Update the last used server and expansion"""
        self.global_config["last_server"] = server
        self.global_config["last_expansion"] = expansion
        self.save_global_config()
    
    def load_accounts(self, accounts_file):
        """Load accounts from the specified file"""
        if os.path.exists(accounts_file):
            try:
                with open(accounts_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load accounts: {e}")
                return {"accounts": []}
        else:
            return {"accounts": []}
    
    def save_accounts(self, accounts_data, accounts_file):
        """Save accounts to the specified file"""
        try:
            with open(accounts_file, 'w') as f:
                json.dump(accounts_data, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save accounts: {e}")
            return False
    
    def load_coordinates(self, coords_file):
        """Load login screen coordinates from the specified file"""
        default_coords = {
            "username_x": 1692,
            "username_y": 737,
            "password_x": 1734, 
            "password_y": 854
        }
        
        if os.path.exists(coords_file):
            try:
                with open(coords_file, 'r') as f:
                    loaded_coords = json.load(f)
                    # Update our default coordinates with loaded values
                    default_coords.update(loaded_coords)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load login coordinates: {e}")
        
        return default_coords
    
    def save_coordinates(self, coords_data, coords_file):
        """Save login screen coordinates to the specified file"""
        try:
            with open(coords_file, 'w') as f:
                json.dump(coords_data, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save login coordinates: {e}")
            return False
    
    def detect_existing_accounts(self):
        """
        Scan the current directory for account files and try to associate them with 
        servers and expansions based on naming patterns
        """
        account_files = [f for f in os.listdir('.') if f.startswith('accounts_') and f.endswith('.json')]
        sfaccounts_files = [f for f in os.listdir('.') if f.startswith('sfaccounts_') and f.endswith('.json')]
        
        # Combine both lists
        all_account_files = account_files + sfaccounts_files
        
        # Start with existing configuration, don't create a new one
        servers_data = self.load_servers()
        updated = False
        
        # Keep track of detected servers and expansions to avoid duplicates
        detected_servers = set()
        detected_expansions = {}
        
        for file in all_account_files:
            # Try to determine server and expansion from filename
            # Pattern: accounts_server_expansion.json or sfaccounts_expansion.json
            parts = file.replace('.json', '').split('_')
            
            if file.startswith('sfaccounts_'):
                # StormForge accounts with old naming convention
                server = "StormForge"
                # Try to determine the expansion from the remaining parts
                if len(parts) > 1:
                    expansion_part = parts[1]
                    if expansion_part.lower() == "mop":
                        expansion = "MoP 5.4.8"
                    elif expansion_part.lower() == "tbc":
                        expansion = "TBC 2.4.3"
                    else:
                        # Unknown expansion, skip
                        continue
                else:
                    # Can't determine expansion, skip
                    continue
            else:
                # New naming convention: accounts_server_expansion.json
                if len(parts) < 3:
                    # Not enough parts to determine server and expansion, skip
                    continue
                    
                server = parts[1].capitalize()
                expansion_part = parts[2]
                
                # Map common abbreviations to expansion names
                if expansion_part.lower() == "mop":
                    expansion = "MoP 5.4.8"
                elif expansion_part.lower() == "tbc":
                    expansion = "TBC 2.4.3"
                elif expansion_part.lower() in ["wotlk", "wrath"]:
                    expansion = "WotLK 3.3.5"
                elif expansion_part.lower() == "cata":
                    expansion = "Cataclysm 4.3.4"
                elif expansion_part.lower() == "legion":
                    expansion = "Legion 7.3.5"
                elif expansion_part.lower() == "classic":
                    expansion = "Classic 1.12"
                else:
                    # Unknown expansion, skip
                    continue
            
            # Track detected servers and expansions to avoid duplicates
            if server not in detected_servers:
                detected_servers.add(server)
            
            if server not in detected_expansions:
                detected_expansions[server] = set()
            
            if expansion in detected_expansions[server]:
                # Skip duplicate expansions for the same server
                continue
            
            detected_expansions[server].add(expansion)
            
            # Check if server exists
            if server not in servers_data:
                servers_data[server] = {"expansions": {}}
                updated = True
            
            # Check if expansion exists
            if expansion not in servers_data[server]["expansions"]:
                # Add expansion with the account file
                servers_data[server]["expansions"][expansion] = {
                    "path": "",  # Path needs to be filled in manually
                    "accounts_file": file,
                    "coords_file": f"login_coords_{server.lower()}_{expansion_part.lower()}.json"
                }
                updated = True
            elif servers_data[server]["expansions"][expansion]["accounts_file"] != file:
                # Found a different account file for existing expansion
                response = messagebox.askyesno(
                    "Account File Found",
                    f"Found account file {file} for {server} - {expansion}.\n"
                    f"Current account file is {servers_data[server]['expansions'][expansion]['accounts_file']}.\n\n"
                    f"Do you want to use {file} instead?"
                )
                if response:
                    servers_data[server]["expansions"][expansion]["accounts_file"] = file
                    updated = True
        
        # Save if changes were made
        if updated:
            self.save_servers(servers_data)
            messagebox.showinfo(
                "Accounts Detected",
                "Found and configured account files for some servers.\n"
                "You may need to fill in missing game paths."
            )
        
        return servers_data
    