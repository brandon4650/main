import os
import time
import subprocess
import threading
import pyautogui
import tkinter as tk
from tkinter import messagebox, ttk
from ui_components import WOW_COLORS

class LoginAutomation:
    """Handles the automation of logging into WoW private servers"""
    
    def __init__(self, parent, status_callback=None):
        """
        Initialize login automation
        
        Args:
            parent: The parent window/widget
            status_callback: Function to call to update status messages
        """
        self.parent = parent
        self.status_callback = status_callback
        self.process = None
        self.login_thread = None
    
    def update_status(self, message):
        """Update status message via callback if available"""
        if self.status_callback:
            self.status_callback(message)
    
    def launch_game(self, game_path, account_data, login_coords):
        """
        Launch the game and attempt to log in
        
        Args:
            game_path: Path to the game executable
            account_data: Dictionary with username and password
            login_coords: Dictionary with screen coordinates for login fields
        """
        # Check if executable exists
        if not os.path.exists(game_path):
            messagebox.showerror("Error", f"Game executable not found at: {game_path}")
            return False
        
        # Start a new thread for game launching and login
        self.login_thread = threading.Thread(
            target=self._login_thread,
            args=(game_path, account_data, login_coords),
            daemon=True
        )
        self.login_thread.start()
        return True
    
    def _login_thread(self, game_path, account_data, login_coords):
        """Thread function that handles the game launch and login process"""
        try:
            self.update_status("Launching game client...")
            
            # Launch the game
            self.process = subprocess.Popen(game_path)
            
            # Wait for login screen
            self.update_status("Waiting for login screen...")
            time.sleep(8)  # Initial wait for the game to start
            
            # Try to find login fields
            max_attempts = 40
            attempt = 0
            success = False
            
            while attempt < max_attempts and not success:
                try:
                    # Take a short pause
                    time.sleep(0.5)
                    self.update_status(f"Attempting to log in... ({attempt+1}/{max_attempts})")
                    
                    # Enter username - try multiple times with different approaches
                    for _ in range(3):
                        pyautogui.click(x=login_coords["username_x"], y=login_coords["username_y"])
                        time.sleep(0.3)
                        pyautogui.hotkey('ctrl', 'a')  # Select all
                        time.sleep(0.1)
                        pyautogui.press('delete')      # Clear the field
                        time.sleep(0.1)
                        
                    # Type username slowly
                    for char in account_data["username"]:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)
                    
                    time.sleep(0.5)
                    
                    # Enter password - try multiple times with different approaches
                    for _ in range(3):
                        pyautogui.click(x=login_coords["password_x"], y=login_coords["password_y"])
                        time.sleep(0.3)
                        pyautogui.hotkey('ctrl', 'a')  # Select all
                        time.sleep(0.1)
                        pyautogui.press('delete')      # Clear the field
                        time.sleep(0.1)
                    
                    # Type password slowly
                    for char in account_data["password"]:
                        pyautogui.typewrite(char)
                        time.sleep(0.05)
                    
                    time.sleep(0.5)
                    
                    # Press Enter instead of clicking the login button
                    pyautogui.press('enter')
                    
                    self.update_status(f"Logged in as {account_data['username']}")
                    success = True
                    break
                    
                except Exception as e:
                    attempt += 1
                    time.sleep(1)
                    self.update_status(f"Waiting for login screen... {attempt}/{max_attempts}")
            
            if not success:
                self.update_status("Failed to log in automatically.")
                messagebox.showwarning(
                    "Login Failed",
                    "Automated login failed. You may need to configure login screen coordinates."
                )
            
        except Exception as e:
            self.update_status(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during login: {str(e)}")
    
    def terminate(self):
        """Terminate the game process if it's running"""
        if self.process:
            try:
                self.process.terminate()
                self.update_status("Game process terminated")
            except:
                pass

class CoordinatesTool:
    """Tool to help configure login screen coordinates in WoW style"""
    
    def __init__(self, parent, coords_file, save_callback=None):
        """
        Initialize coordinate tool
        
        Args:
            parent: The parent window/widget
            coords_file: The file to save coordinates to
            save_callback: Function to call after saving coordinates
        """
        from tkinter import ttk
        import tkinter as tk
        
        self.parent = parent
        self.coords_file = coords_file
        self.save_callback = save_callback
        
        # Create the dialog window in WoW style
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configure Login Screen Coordinates")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configure with WoW colors
        self.dialog.configure(bg=WOW_COLORS["bg_dark"])
        
        # Create main frame with WoW style
        main_frame = ttk.Frame(self.dialog, style="WoW.TFrame", padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the UI with WoW styling
        title_label = ttk.Label(
            main_frame, 
            text="Configure Login Screen Coordinates", 
            style="Title.TLabel"
        )
        title_label.pack(pady=10)
        
        # Separator under title
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill="x", pady=5)
                
        # Instructions with WoW style
        instructions = ttk.Label(
            main_frame, 
            text="Please launch the game manually and position the login screen.\n" +
                 "Then click each button below and click on the corresponding\n" +
                 "position on the login screen.", 
            justify="center",
            foreground=WOW_COLORS["text_normal"],
            background=WOW_COLORS["bg_medium"]
        )
        instructions.pack(pady=10)
        
        # Create frame for coordinate info with WoW styling
        coord_frame = ttk.Frame(main_frame, style="WoW.TFrame", padding=10)
        coord_frame.pack(fill=tk.BOTH, expand=True)
        
        # Current coordinates
        self.coordinates = {
            "username": {"x": 1692, "y": 737, "desc": "Username Field"},
            "password": {"x": 1734, "y": 854, "desc": "Password Field"}
        }
        
        # Try to load existing coordinates
        try:
            if os.path.exists(coords_file):
                with open(coords_file, 'r') as f:
                    import json
                    custom_coords = json.load(f)
                    for key in self.coordinates:
                        field_x = f"{key}_x"
                        field_y = f"{key}_y"
                        if field_x in custom_coords and field_y in custom_coords:
                            self.coordinates[key]["x"] = custom_coords[field_x]
                            self.coordinates[key]["y"] = custom_coords[field_y]
        except Exception as e:
            print(f"Error loading coordinates: {str(e)}")
        
        # Create entry widgets and buttons for each coordinate
        self.coord_vars = {}
        row = 0
        for key, values in self.coordinates.items():
            ttk.Label(coord_frame, text=f"{values['desc']}:").grid(row=row, column=0, sticky=tk.W, pady=5)
            
            coord_text = tk.StringVar(value=f"X: {values['x']}, Y: {values['y']}")
            self.coord_vars[key] = coord_text
            entry = ttk.Entry(coord_frame, textvariable=coord_text, state="readonly")
            entry.grid(row=row, column=1, padx=5, pady=5, sticky=tk.EW)
            
            capture_btn = ttk.Button(coord_frame, text="Set Position", 
                                  command=lambda k=key: self.capture_position(k))
            capture_btn.grid(row=row, column=2, padx=5, pady=5)
            
            row += 1
        
        # Note about Enter key
        ttk.Label(coord_frame, text="Note: The app will press Enter to login after entering credentials", 
               font=("Arial", 9, "italic")).grid(row=row, column=0, columnspan=3, pady=(15,5), sticky=tk.W)
            
        # Add button to test the coordinates
        test_btn = ttk.Button(coord_frame, text="Test Coordinates", 
                           command=self.test_coordinates)
        test_btn.grid(row=row+1, column=0, columnspan=3, pady=10)
        
        # Add button to save the coordinates
        save_btn = ttk.Button(
            coord_frame, 
            text="Save Coordinates", 
            style="Gold.TButton",
            command=self.save_coordinates
        )
        save_btn.grid(row=row+2, column=0, columnspan=3, pady=10)
        
        # Make the grid expandable
        coord_frame.columnconfigure(1, weight=1)
    
    def capture_position(self, field_key):
        """Capture mouse position after a delay"""
        messagebox.showinfo("Capture Position", 
                         f"Click OK and then click on the {self.coordinates[field_key]['desc']} on the login screen.\n" +
                         "You have 3 seconds to position your mouse.")
        
        self.dialog.withdraw()  # Hide the dialog temporarily
        self.parent.withdraw()  # Hide the parent window temporarily
        time.sleep(3)  # Give the user time to position the mouse
        x, y = pyautogui.position()
        self.dialog.deiconify()  # Show the dialog again
        self.parent.deiconify()  # Show the parent window again
        
        # Update the coordinate variable
        self.coord_vars[field_key].set(f"X: {x}, Y: {y}")
        
        # Update the coordinates dictionary
        self.coordinates[field_key]["x"] = x
        self.coordinates[field_key]["y"] = y
    
    def test_coordinates(self):
        """Test the current coordinates by moving the mouse to each position"""
        try:
            # Hide windows temporarily
            self.dialog.withdraw()
            self.parent.withdraw()
            
            # Move mouse to each position with a delay
            for key, values in self.coordinates.items():
                x = values["x"]
                y = values["y"]
                pyautogui.moveTo(x, y, duration=0.5)
                time.sleep(1)
            
            # Show windows again
            self.dialog.deiconify()
            self.parent.deiconify()
            
            # Show message about Enter key
            messagebox.showinfo("Test Completed", 
                             "Mouse movement test completed.\n" +
                             "The app will press Enter to login after filling credentials.\n\n" +
                             "Did the cursor move to the correct positions?")
        except Exception as e:
            self.dialog.deiconify()
            self.parent.deiconify()
            messagebox.showerror("Test Failed", f"Error during test: {str(e)}")
    
    def save_coordinates(self):
        """Save the coordinates to file and close the dialog"""
        try:
            # Convert to the format expected by the login function
            login_coords = {}
            for key, values in self.coordinates.items():
                x = values["x"]
                y = values["y"]
                
                login_coords[f"{key}_x"] = x
                login_coords[f"{key}_y"] = y
            
            # We no longer need the login button coordinates since we use Enter
            # But we'll keep them in the file for backwards compatibility
            if "login_button_x" not in login_coords:
                login_coords["login_button_x"] = login_coords.get("password_x", 0) + 100
                login_coords["login_button_y"] = login_coords.get("password_y", 0) + 100
            
            # Save to file
            with open(self.coords_file, 'w') as f:
                import json
                json.dump(login_coords, f, indent=4)
            
            messagebox.showinfo("Coordinates Saved", 
                             f"Login screen coordinates have been saved.\nThe automated login should work next time.")
            
            # Call the save callback if provided
            if self.save_callback:
                self.save_callback(login_coords)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Save Failed", f"Error saving coordinates: {str(e)}")