import tkinter as tk
from tkinter import ttk, messagebox, font
import os
import sys
from PIL import Image, ImageTk

# WoW color scheme
WOW_COLORS = {
    "bg_dark": "#161616",            # Darker background
    "bg_medium": "#202020",          # Medium background
    "bg_light": "#2a2a2a",           # Light background
    "accent_gold": "#ffb100",        # WoW gold accent - more orange/yellow
    "accent_blue": "#0070dd",        # WoW blue accent - proper WoW blue
    "text_normal": "#ffffff",        # Normal text
    "text_highlight": "#ffb100",     # Highlighted text
    "border": "#393939",             # Border color
    "button_bg": "#2a2a2a",          # Button background
    "button_hover": "#3a3a3a",       # Button hover
    "button_pressed": "#1a1a1a",     # Button pressed
    "input_bg": "#202020",           # Input background
    "input_fg": "#ffffff",           # Input text
    "tree_bg": "#202020",            # Treeview background
    "tree_highlight": "#004a93",     # Treeview highlight - more blue
    "selected_item_bg": "#004a93",   # Selected item background - more blue
    "header_bg": "#262626",          # Header background
}

class WoWThemedFrame(ttk.Frame):
    """A WoW-styled frame with themed background and border"""
    def __init__(self, parent, title=None, padding=10, **kwargs):
        super().__init__(parent, padding=padding, style="WoW.TFrame", **kwargs)
        
        if title:
            self.label_frame = ttk.LabelFrame(
                self, 
                text=title, 
                padding=padding,
                style="WoW.TLabelframe"
            )
            self.label_frame.pack(fill=tk.BOTH, expand=True)
            self.content_frame = self.label_frame
        else:
            self.content_frame = self
            
    def get_content_frame(self):
        """Returns the content frame where widgets should be placed"""
        return self.content_frame

class WoWAboutDialog:
    """WoW-styled about dialog showing application information"""
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
        frame = ttk.Frame(self.dialog, style="WoW.TFrame", padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # App title with WoW font and color
        title = ttk.Label(
            frame, 
            text=app_name, 
            font=(title_font, 16, "bold"),
            foreground=WOW_COLORS["accent_gold"],
            background=WOW_COLORS["bg_medium"]
        )
        title.pack(pady=(0, 15))
        
        # Add a separator
        separator = ttk.Separator(frame, orient="horizontal")
        separator.pack(fill="x", pady=5)
        
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
        copyright_label.pack(pady=(15, 10))
        
        # WoW-styled close button
        close_button = ttk.Button(
            frame, 
            text="Close", 
            style="Gold.TButton",
            command=self.dialog.destroy
        )
        close_button.pack(pady=10)

class WoWStatusBar(ttk.Frame):
    """WoW-styled status bar to display application status"""
    def __init__(self, parent):
        super().__init__(parent, style="WoW.TFrame")
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        # Create a canvas for the WoW-style status bar
        self.canvas = tk.Canvas(
            self, 
            height=24, 
            bg=WOW_COLORS["bg_dark"], 
            bd=0,
            highlightthickness=0
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Draw the gold border at the top
        self.canvas.create_line(
            0, 0, self.winfo_width(), 0, 
            fill=WOW_COLORS["accent_gold"], 
            width=1
        )
        
        # Create text on the canvas
        self.text_id = self.canvas.create_text(
            10, 12,
            text=self.status_var.get(),
            fill=WOW_COLORS["accent_gold"],
            anchor=tk.W,
            font=("Palatino Linotype", 9, "bold")
        )
        
        # Bind to resize events
        self.canvas.bind("<Configure>", self.on_resize)
        
        # Track variable changes
        self.status_var.trace_add("write", self.update_text)
        
    def on_resize(self, event):
        """Handle resize events"""
        # Redraw the gold border
        self.canvas.delete("border")
        self.canvas.create_line(
            0, 0, event.width, 0, 
            fill=WOW_COLORS["accent_gold"], 
            width=1,
            tags="border"
        )
        
    def update_text(self, *args):
        """Update the text on the canvas when variable changes"""
        self.canvas.itemconfigure(self.text_id, text=self.status_var.get())
        
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
    """A WoW-styled confirmation dialog with Yes/No options"""
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
        frame = ttk.Frame(dialog, style="WoW.TFrame", padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dialog title with WoW font and color
        title_label = ttk.Label(
            frame, 
            text=title, 
            font=(title_font, 14, "bold"),
            foreground=WOW_COLORS["accent_gold"],
            background=WOW_COLORS["bg_medium"]
        )
        title_label.pack(pady=(0, 10))
        
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
    """Load WoW-like fonts if available, otherwise use similar system fonts"""
    # Check for WoW-like fonts on the system
    available_fonts = font.families()
    
    title_font = "Arial"
    normal_font = "Arial"
    
    # Priority list for title fonts
    title_fonts = [
        "Morpheus", 
        "Morris Roman", 
        "Palatino Linotype", 
        "Georgia", 
        "Times New Roman"
    ]
    
    # Priority list for normal fonts
    normal_fonts = [
        "Friz Quadrata", 
        "Expressway", 
        "Calibri", 
        "Verdana"
    ]
    
    # Find the best available fonts
    for f in title_fonts:
        if f in available_fonts:
            title_font = f
            break
            
    for f in normal_fonts:
        if f in available_fonts:
            normal_font = f
            break
    
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
    
    # Create WoW-like images
    images = create_wow_images()
    
    # Configure main styles
    style.configure(
        "TFrame", 
        background=WOW_COLORS["bg_medium"],
        borderwidth=1,
        relief="raised"
    )
    
    style.configure(
        "WoW.TFrame", 
        background=WOW_COLORS["bg_medium"],
        borderwidth=1,
        relief="raised"
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
        foreground=WOW_COLORS["accent_gold"],
        font=(title_font, 16, "bold")
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
            ("active", "#ffc530"),  # Lighter gold on hover
            ("pressed", "#d99b00")  # Darker gold when pressed
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
        padding=3
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
        foreground=WOW_COLORS["accent_gold"],
        font=(normal_font, 10, "bold"),
        relief="raised",
        borderwidth=1
    )
    
    style.map(
        "Treeview",
        background=[
            ("selected", WOW_COLORS["selected_item_bg"])
        ],
        foreground=[
            ("selected", WOW_COLORS["text_highlight"])
        ]
    )
    
    # Labelframe style (for grouped sections)
    style.configure(
        "TLabelframe", 
        background=WOW_COLORS["bg_medium"],
        foreground=WOW_COLORS["text_normal"],
        borderwidth=2,
        relief="groove"
    )
    
    style.configure(
        "WoW.TLabelframe", 
        background=WOW_COLORS["bg_medium"],
        foreground=WOW_COLORS["text_normal"],
        borderwidth=2,
        relief="groove"
    )
    
    style.configure(
        "TLabelframe.Label", 
        background=WOW_COLORS["bg_medium"],
        foreground=WOW_COLORS["accent_gold"],
        font=(title_font, 12, "bold")
    )
    
    style.configure(
        "WoW.TLabelframe.Label", 
        background=WOW_COLORS["bg_medium"],
        foreground=WOW_COLORS["accent_gold"],
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
            ("selected", WOW_COLORS["accent_gold"]),
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

def apply_global_styling():
    """Apply consistent styling throughout the application"""
    # Apply WoW styling by default
    apply_wow_styling()