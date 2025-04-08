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
        
        # Empty default configurations (no pre-defined servers)
        self.default_server_data = {}
        
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
        
        # Initialize servers config only if it doesn't exist
        if not os.path.exists(self.servers_config_file):
            # Create an empty server configuration
            self.save_servers({})
            
            # Inform the user about how to add servers
            messagebox.showinfo(
                "No Servers Found", 
                "No server configurations were found.\n\n" +
                "You can:\n" +
                "- Use 'Add Server' to manually configure a new server\n" +
                "- Use 'Tools > Scan for Account Files' to detect servers from existing account files"
            )
    
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
        # Start with existing configuration, don't create a new one
        servers_data = self.load_servers()
        
        # Print current working directory for debugging
        print(f"Scanning for account files in: {os.getcwd()}")
        
        # Check if we have any account files first
        account_files = [f for f in os.listdir('.') if (f.startswith('accounts_') or f.startswith('sfaccounts_')) and f.endswith('.json')]
        
        if not account_files:
            print("No account files found, returning existing configuration")
            return servers_data
        
        # List found files for debugging
        print(f"Found account files: {account_files}")
        
        # Process account files
        updated = False
        detected_servers = set()
        detected_expansions = {}
        
        for file in account_files:
            print(f"Processing file: {file}")
            
            # Skip files that don't exist or are empty
            if not os.path.exists(file) or os.path.getsize(file) == 0:
                print(f"Skipping non-existent or empty file: {file}")
                continue
                
            # Check if the file contains account data
            try:
                with open(file, 'r') as f:
                    file_content = json.load(f)
                    if "accounts" not in file_content or not file_content["accounts"]:
                        print(f"Skipping file with no accounts: {file}")
                        continue
            except:
                print(f"Failed to read file: {file}")
                continue
            
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
                        print(f"Unknown expansion in file: {file}")
                        continue
                else:
                    # Can't determine expansion, skip
                    print(f"Can't determine expansion from file: {file}")
                    continue
            else:
                # New naming convention: accounts_server_expansion.json
                if len(parts) < 3:
                    # Not enough parts to determine server and expansion, skip
                    print(f"Not enough parts in filename: {file}")
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
                    print(f"Unknown expansion in file: {file}")
                    continue
            
            print(f"Detected server: {server}, expansion: {expansion}")
            
            # Track detected servers and expansions to avoid duplicates
            if server not in detected_servers:
                detected_servers.add(server)
            
            if server not in detected_expansions:
                detected_expansions[server] = set()
            
            if expansion in detected_expansions[server]:
                # Skip duplicate expansions for the same server
                print(f"Skipping duplicate expansion: {expansion} for server: {server}")
                continue
            
            detected_expansions[server].add(expansion)
            
            # Check if server exists
            if server not in servers_data:
                servers_data[server] = {"expansions": {}}
                updated = True
                print(f"Added new server: {server}")
            
            # Check if expansion exists
            if expansion not in servers_data[server]["expansions"]:
                # Add expansion with the account file
                servers_data[server]["expansions"][expansion] = {
                    "path": "",  # Path needs to be filled in manually
                    "accounts_file": file,
                    "coords_file": f"login_coords_{server.lower()}_{expansion_part.lower()}.json"
                }
                updated = True
                print(f"Added new expansion: {expansion} to server: {server}")
        
        # Save if changes were made
        if updated:
            print("Saving updated server configuration")
            self.save_servers(servers_data)
            messagebox.showinfo(
                "Accounts Detected",
                "Found and configured account files for some servers.\n"
                "You may need to fill in missing game paths."
            )
        
        return servers_data
    