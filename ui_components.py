import tkinter as tk
from tkinter import ttk, messagebox, font
import os
import sys
from PIL import Image, ImageTk

# WoW color scheme
WOW_COLORS = {
    "bg_dark": "#121212",            # Very dark background
    "bg_medium": "#1e1e1e",          # Medium background
    "bg_light": "#252525",           # Light background
    "accent_gold": "#ffb100",        # Classic WoW gold
    "accent_gold_light": "#ffd100",  # Lighter gold for hover states
    "accent_gold_dark": "#c68e00",   # Darker gold for pressed states
    "accent_blue": "#004a93",        # WoW blue accent
    "accent_blue_light": "#0062bd",  # Lighter blue for hover states
    "text_normal": "#ffffff",        # Normal text
    "text_title": "#ffd100",         # Title text (golden)
    "text_header": "#ffd100",        # Section header text
    "text_highlight": "#ffffff",     # Highlighted text
    "border": "#444444",             # Standard border
    "border_gold": "#9d7400",        # Gold-colored border
    "border_highlight": "#666666",   # Lighter border for highlights
    "button_bg": "#292929",          # Button background
    "button_hover": "#3a3a3a",       # Button hover
    "button_pressed": "#1a1a1a",     # Button pressed
    "input_bg": "#181818",           # Input background
    "input_fg": "#ffffff",           # Input text
    "tree_bg": "#1a1a1a",            # Treeview background
    "tree_alternate": "#232323",     # Alternate row in treeview
    "tree_selected": "#004a93",      # Selected item background
    "header_bg": "#282828",          # Header background
}

class WoWThemedFrame(ttk.Frame):
    """A WoW-styled frame with enhanced styling"""
    def __init__(self, parent, title=None, padding=10, **kwargs):
        super().__init__(parent, padding=padding, style="WoW.TFrame", **kwargs)
        
        if title:
            # Create the content area
            self.header_frame = ttk.Frame(self, style="WoW.TFrame", padding=0)
            self.header_frame.pack(fill=tk.X, expand=False, pady=(0, 5))
            
            # Add a separator line above the title
            separator_top = ttk.Separator(self.header_frame, orient="horizontal")
            separator_top.pack(fill=tk.X, pady=2)
            
            # Create title with WoW styling
            title_font = load_wow_fonts()[0]  # Get the title font
            self.title_label = ttk.Label(
                self.header_frame, 
                text=title, 
                font=(title_font, 14, "bold"),
                foreground=WOW_COLORS["text_header"],
                background=WOW_COLORS["bg_medium"],
                anchor="center"
            )
            self.title_label.pack(fill=tk.X, pady=3)
            
            # Add a separator line below the title
            separator_bottom = ttk.Separator(self.header_frame, orient="horizontal")
            separator_bottom.pack(fill=tk.X, pady=2)
            
            # Content area with slight indentation
            self.content_frame = ttk.Frame(self, style="WoW.TFrame", padding=(5, 5, 5, 5))
            self.content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            # Create a border around the content frame
            self.content_frame.configure(borderwidth=1, relief="solid")
        else:
            # No title, just use this frame directly
            self.content_frame = self
            
    def get_content_frame(self):
        """Returns the content frame where widgets should be placed"""
        return self.content_frame

class WoWAboutDialog:
    """WoW-styled about dialog with enhanced styling"""
    def __init__(self, parent, app_name, version, description):
        # Get the best available fonts
        title_font, normal_font = load_wow_fonts()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"About {app_name}")
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Set the background color
        self.dialog.configure(bg=WOW_COLORS["bg_dark"])
        
        # Create a custom frame with WoW-style border
        frame = ttk.Frame(self.dialog, style="WoW.TFrame", padding=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # App title with WoW font and color
        title = ttk.Label(
            frame, 
            text=app_name, 
            font=(title_font, 18, "bold"),
            foreground=WOW_COLORS["text_title"],
            background=WOW_COLORS["bg_medium"]
        )
        title.pack(pady=(0, 10))
        
        # Add top separator
        separator1 = ttk.Separator(frame, orient="horizontal")
        separator1.pack(fill="x", pady=5)
        
        # Version info
        version_label = ttk.Label(
            frame, 
            text=f"Version {version}",
            font=(normal_font, 10),
            foreground=WOW_COLORS["text_normal"],
            background=WOW_COLORS["bg_medium"]
        )
        version_label.pack(pady=5)
        
        # Description
        desc_label = ttk.Label(
            frame, 
            text=description, 
            wraplength=350, 
            justify="center",
            font=(normal_font, 10),
            foreground=WOW_COLORS["text_normal"],
            background=WOW_COLORS["bg_medium"]
        )
        desc_label.pack(pady=10)
        
        # Add another separator
        separator2 = ttk.Separator(frame, orient="horizontal")
        separator2.pack(fill="x", pady=5)
        
        # Copyright
        copyright_label = ttk.Label(
            frame, 
            text="© 2025",
            font=(normal_font, 9),
            foreground=WOW_COLORS["text_normal"],
            background=WOW_COLORS["bg_medium"]
        )
        copyright_label.pack(pady=10)
        
        # WoW-styled close button
        close_button = ttk.Button(
            frame, 
            text="Close", 
            style="Gold.TButton",
            command=self.dialog.destroy
        )
        close_button.pack(pady=10)



class WoWStatusBar(ttk.Frame):
    """WoW-styled status bar with enhanced appearance"""
    def __init__(self, parent):
        super().__init__(parent, style="WoW.TFrame")
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        # Create background frame with border
        self.configure(height=24, borderwidth=1, relief="sunken")
        
        # Get the title font
        title_font, normal_font = load_wow_fonts()
        
        # Create status label with proper styling
        self.status_label = ttk.Label(
            self, 
            textvariable=self.status_var,
            background=WOW_COLORS["bg_dark"],
            foreground=WOW_COLORS["accent_gold"],
            font=(normal_font, 9, "bold"),
            anchor=tk.W,
            padding=(10, 0)
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def set_status(self, text):
        """Set the status text"""
        self.status_var.set(text)
        
    def clear_status(self):
        """Clear the status text"""
        self.status_var.set("Ready")

class LoadingOverlay:
    """Creates an overlay with a loading message"""
    def __init__(self, parent, message="Please wait..."):
        self.parent = parent
        
        # Create overlay frame
        self.overlay = tk.Toplevel(parent)
        self.overlay.withdraw()  # Hide initially
        
        # Make it cover the parent
        w = parent.winfo_width()
        h = parent.winfo_height()
        x = parent.winfo_rootx()
        y = parent.winfo_rooty()
        self.overlay.geometry(f"{w}x{h}+{x}+{y}")
        
        # Configure as a floating panel without decorations
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        
        # Semi-transparent with a dark background
        self.overlay.configure(bg='black')
        self.overlay.attributes("-alpha", 0.7)
        
        # Add the message
        self.message_var = tk.StringVar(value=message)
        self.message_label = tk.Label(
            self.overlay, 
            textvariable=self.message_var,
            bg='black', 
            fg='white',
            font=("Arial", 12)
        )
        self.message_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
    def show(self, message=None):
        """Show the loading overlay"""
        if message:
            self.message_var.set(message)
            
        # Update position in case parent moved
        w = self.parent.winfo_width()
        h = self.parent.winfo_height()
        x = self.parent.winfo_rootx()
        y = self.parent.winfo_rooty()
        self.overlay.geometry(f"{w}x{h}+{x}+{y}")
        
        self.overlay.deiconify()
        self.overlay.update()
        
    def hide(self):
        """Hide the loading overlay"""
        self.overlay.withdraw()
        
    def update_message(self, message):
        """Update the loading message"""
        self.message_var.set(message)
        self.overlay.update()
        
    def destroy(self):
        """Destroy the overlay"""
        self.overlay.destroy()

class WoWConfirmDialog:
    """A WoW-styled confirmation dialog with enhanced styling"""
    def __init__(self, parent, title, message):
        # Get the best available fonts
        title_font, normal_font = load_wow_fonts()
        
        self.result = False
        
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        
        # Set the background color
        dialog.configure(bg=WOW_COLORS["bg_dark"])
        
        # Create a custom frame with WoW-style border
        frame = ttk.Frame(dialog, style="WoW.TFrame", padding=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dialog title with WoW font and color
        title_label = ttk.Label(
            frame, 
            text=title, 
            font=(title_font, 14, "bold"),
            foreground=WOW_COLORS["text_title"],
            background=WOW_COLORS["bg_medium"]
        )
        title_label.pack(pady=(0, 5))
        
        # Add a separator
        separator = ttk.Separator(frame, orient="horizontal")
        separator.pack(fill="x", pady=5)
        
        # Message
        message_label = ttk.Label(
            frame, 
            text=message, 
            wraplength=350, 
            justify="center",
            font=(normal_font, 10),
            foreground=WOW_COLORS["text_normal"],
            background=WOW_COLORS["bg_medium"]
        )
        message_label.pack(pady=15)
        
        # Buttons frame with WoW styling
        button_frame = ttk.Frame(frame, style="WoW.TFrame")
        button_frame.pack(pady=10)
        
        # WoW-styled Yes button (gold style)
        yes_button = ttk.Button(
            button_frame, 
            text="Yes", 
            style="Gold.TButton",
            command=lambda: self.set_result(dialog, True)
        )
        yes_button.pack(side=tk.LEFT, padx=10)
        
        # WoW-styled No button (normal style)
        no_button = ttk.Button(
            button_frame, 
            text="No", 
            command=lambda: self.set_result(dialog, False)
        )
        no_button.pack(side=tk.LEFT, padx=10)
        
        # Make dialog modal
        dialog.focus_set()
        parent.wait_window(dialog)
        
    def set_result(self, dialog, value):
        """Set the result and close the dialog"""
        self.result = value
        dialog.destroy()

def load_wow_fonts():
    """Load WoW fonts if available, otherwise use similar system fonts"""
    # Default fonts in case custom fonts are not available
    title_font = "Arial"
    normal_font = "Arial"
    
    # Try to load custom WoW fonts
    custom_font_dir = "fonts"
    if os.path.exists(custom_font_dir):
        try:
            # Load Morpheus font for titles if available
            morpheus_path = os.path.join(custom_font_dir, "morpheus.ttf")
            if os.path.exists(morpheus_path):
                # Register the font with Tkinter
                font_id = font.Font(font=("Morpheus", 10)).actual()["family"]
                # If font wasn't already registered, register it now
                if font_id != "Morpheus":
                    # Add the font using tkfont.Font
                    custom_font = font.Font(family="Morpheus", size=10, file=morpheus_path)
                title_font = "Morpheus"
        except Exception as e:
            print(f"Error loading Morpheus font: {e}")
    
    # Get available fonts
    available_fonts = font.families()
    
    # If Morpheus failed to load, try these alternatives for titles
    if title_font == "Arial":
        title_fonts = [
            "Morpheus", 
            "Palatino Linotype", 
            "Georgia", 
            "Times New Roman"
        ]
        for f in title_fonts:
            if f in available_fonts:
                title_font = f
                break
    
    # Normal fonts
    normal_fonts = [
        "Friz Quadrata", 
        "Expressway", 
        "Calibri", 
        "Verdana"
    ]
    for f in normal_fonts:
        if f in available_fonts:
            normal_font = f
            break
    
    print(f"Using fonts: Title={title_font}, Normal={normal_font}")
    return title_font, normal_font

def create_wow_images():
    """Create WoW-themed image resources"""
    images = {}
    
    # Try to find images directory
    img_dir = "images"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir, exist_ok=True)
    
    # Check if we can find/create the button images
    button_normal_path = os.path.join(img_dir, "wow_button_normal.png")
    button_hover_path = os.path.join(img_dir, "wow_button_hover.png")
    
    try:
        # We'd normally load existing images, but for simplicity, let's create them
        # In a real implementation, include actual WoW-style button images in the package
        
        # If using PIL, we could create buttons here
        # For now, we'll return empty dict
        pass
        
    except:
        pass
    
    return images

def apply_wow_styling():
    """Apply WoW-styled theme throughout the application"""
    style = ttk.Style()
    
    # Get the best available fonts
    title_font, normal_font = load_wow_fonts()
    
    # Configure main styles
    style.configure(
        "TFrame", 
        background=WOW_COLORS["bg_medium"],
        borderwidth=1,
        relief="solid",
        bordercolor=WOW_COLORS["border"]
    )
    
    style.configure(
        "WoW.TFrame", 
        background=WOW_COLORS["bg_medium"],
        borderwidth=1,
        relief="solid",
        bordercolor=WOW_COLORS["border"]
    )
    
    # Label style
    style.configure(
        "TLabel", 
        background=WOW_COLORS["bg_medium"],
        foreground=WOW_COLORS["text_normal"],
        font=(normal_font, 10)
    )
    
    style.configure(
        "Title.TLabel", 
        background=WOW_COLORS["bg_medium"],
        foreground=WOW_COLORS["text_title"],
        font=(title_font, 16, "bold")
    )
    
    style.configure(
        "Header.TLabel", 
        background=WOW_COLORS["bg_medium"],
        foreground=WOW_COLORS["text_header"],
        font=(title_font, 12, "bold")
    )
    
    # Button style
    style.configure(
        "TButton", 
        background=WOW_COLORS["button_bg"],
        foreground=WOW_COLORS["text_normal"],
        font=(normal_font, 10),
        borderwidth=1,
        relief="raised",
        padding=5
    )
    
    style.map(
        "TButton",
        background=[
            ("active", WOW_COLORS["button_hover"]),
            ("pressed", WOW_COLORS["button_pressed"])
        ],
        foreground=[
            ("active", WOW_COLORS["text_highlight"])
        ],
        relief=[
            ("pressed", "sunken")
        ]
    )
    
    # Gold button for primary actions
    style.configure(
        "Gold.TButton", 
        background=WOW_COLORS["accent_gold"],
        foreground=WOW_COLORS["bg_dark"],
        font=(normal_font, 10, "bold"),
        borderwidth=1,
        relief="raised",
        padding=5
    )
    
    style.map(
        "Gold.TButton",
        background=[
            ("active", WOW_COLORS["accent_gold_light"]),
            ("pressed", WOW_COLORS["accent_gold_dark"])
        ],
        foreground=[
            ("pressed", "#000000")
        ],
        relief=[
            ("pressed", "sunken")
        ]
    )
    
    # Entry style (textboxes)
    style.configure(
        "TEntry", 
        fieldbackground=WOW_COLORS["input_bg"],
        foreground=WOW_COLORS["input_fg"],
        borderwidth=1,
        font=(normal_font, 10),
        padding=3
    )
    
    # Combobox style (dropdowns)
    style.configure(
        "TCombobox", 
        fieldbackground=WOW_COLORS["input_bg"],
        background=WOW_COLORS["button_bg"],
        foreground=WOW_COLORS["input_fg"],
        selectbackground=WOW_COLORS["accent_gold"],
        selectforeground=WOW_COLORS["bg_dark"],
        font=(normal_font, 10),
        padding=3,
        arrowsize=14
    )
    
    style.map(
        "TCombobox",
        fieldbackground=[
            ("readonly", WOW_COLORS["button_bg"])
        ],
        foreground=[
            ("readonly", WOW_COLORS["text_normal"])
        ]
    )
    
    # Treeview style (for server list)
    style.configure(
        "Treeview", 
        background=WOW_COLORS["tree_bg"],
        foreground=WOW_COLORS["text_normal"],
        fieldbackground=WOW_COLORS["tree_bg"],
        font=(normal_font, 10),
        borderwidth=1,
        relief="solid"
    )
    
    style.configure(
        "Treeview.Heading", 
        background=WOW_COLORS["header_bg"],
        foreground=WOW_COLORS["text_header"],
        font=(title_font, 10, "bold"),
        relief="raised",
        borderwidth=1
    )
    
    style.map(
        "Treeview",
        background=[
            ("selected", WOW_COLORS["tree_selected"])
        ],
        foreground=[
            ("selected", WOW_COLORS["text_highlight"])
        ]
    )
    
    # Alternating background colors for rows
    def fixed_map(option):
        return [elm for elm in style.map("Treeview", query_opt=option)
                if elm[:2] != ("!disabled", "!selected")]
    
    style.map("Treeview", 
        background=fixed_map("background"),
        foreground=fixed_map("foreground"))
    
    # Labelframe style (for grouped sections)
    style.configure(
        "TLabelframe", 
        background=WOW_COLORS["bg_medium"],
        foreground=WOW_COLORS["text_normal"],
        borderwidth=2,
        relief="groove",
        bordercolor=WOW_COLORS["border"]
    )
    
    style.configure(
        "WoW.TLabelframe", 
        background=WOW_COLORS["bg_medium"],
        foreground=WOW_COLORS["text_normal"],
        borderwidth=2,
        relief="groove",
        bordercolor=WOW_COLORS["border"]
    )
    
    style.configure(
        "TLabelframe.Label", 
        background=WOW_COLORS["bg_medium"],
        foreground=WOW_COLORS["text_header"],
        font=(title_font, 12, "bold")
    )
    
    style.configure(
        "WoW.TLabelframe.Label", 
        background=WOW_COLORS["bg_medium"],
        foreground=WOW_COLORS["text_header"],
        font=(title_font, 12, "bold")
    )
    
    # Notebook style (for tabs)
    style.configure(
        "TNotebook", 
        background=WOW_COLORS["bg_dark"],
        borderwidth=0
    )
    
    style.configure(
        "TNotebook.Tab", 
        background=WOW_COLORS["bg_medium"],
        foreground=WOW_COLORS["text_normal"],
        font=(normal_font, 10),
        padding=(10, 5),
        borderwidth=1
    )
    
    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", WOW_COLORS["bg_light"]),
            ("active", WOW_COLORS["button_hover"])
        ],
        foreground=[
            ("selected", WOW_COLORS["text_header"]),
            ("active", WOW_COLORS["text_highlight"])
        ]
    )
    
    # Scrollbar style
    style.configure(
        "TScrollbar",
        background=WOW_COLORS["bg_light"],
        troughcolor=WOW_COLORS["bg_dark"],
        borderwidth=1,
        arrowsize=13
    )
    
    # Separator style
    style.configure(
        "TSeparator",
        background=WOW_COLORS["border"]
    )
    
    # Create a custom style for alternating rows in treeview (will need to be applied separately)
    style.configure("Odd.Treeview", background=WOW_COLORS["tree_bg"])
    style.configure("Even.Treeview", background=WOW_COLORS["tree_alternate"])

def apply_global_styling():
    """Apply consistent styling throughout the application"""
    # Apply WoW styling by default
    apply_wow_styling()