import tkinter as tk
import os
from server_manager import ServerManagerScreen
from ui_components import WOW_COLORS, apply_global_styling

def setup_wow_theme():
    """Set up the WoW theme for the application"""
    # Create images directory if it doesn't exist
    os.makedirs("images", exist_ok=True)
    
    # You could create or download WoW-themed icon here
    # For now we'll just use a default icon if available
    return os.path.exists("wow_icon.ico")

def main():
    """Main entry point for the WoW Private Server Manager application"""
    # Create the root window
    root = tk.Tk()
    
    # Window title
    root.title("WoW Private Server Manager")
    
    # Set up the WoW theme
    has_icon = setup_wow_theme()
    
    # Configure root window with WoW colors
    root.configure(bg=WOW_COLORS["bg_dark"])
    
    # Set icon if available
    if has_icon:
        try:
            root.iconbitmap("wow_icon.ico")
        except:
            pass
    
    # Apply global styling
    apply_global_styling()
    
    # Create the application
    app = ServerManagerScreen(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()