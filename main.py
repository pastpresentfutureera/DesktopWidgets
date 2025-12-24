"""
Enhanced Desktop Widgets for Windows 11
Version 2.0 - Better fonts, individual colors, horizontal week planner,
calendar with events below dates, and many new features!
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import calendar
from datetime import datetime, timedelta
import json
import os
import ctypes
import sys
import threading
import time

# ============== WINDOWS API ==============
try:
    user32 = ctypes.windll.user32
    HWND_BOTTOM = 1
    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOACTIVATE = 0x0010
except:
    pass

# ============== BEAUTIFUL COLOR THEMES ==============
THEMES = {
    "🌸 Rose Pink": {
        "bg": "#FFF5F5", "header": "#FEC8D8", "accent": "#FF6B9D",
        "text": "#5D4E60", "button": "#FFD1DC", "entry": "#FFFFFF",
        "border": "#FEC8D8", "highlight": "#FF85A2"
    },
    "🌊 Ocean Blue": {
        "bg": "#F0F8FF", "header": "#87CEEB", "accent": "#4A90D9",
        "text": "#2C3E50", "button": "#B8D4E8", "entry": "#FFFFFF",
        "border": "#87CEEB", "highlight": "#5DADE2"
    },
    "🌿 Mint Green": {
        "bg": "#F0FFF4", "header": "#98FB98", "accent": "#3CB371",
        "text": "#2D4A3E", "button": "#B2F2BB", "entry": "#FFFFFF",
        "border": "#98FB98", "highlight": "#66CDAA"
    },
    "🍇 Lavender": {
        "bg": "#F8F0FF", "header": "#D8BFD8", "accent": "#9370DB",
        "text": "#4A4063", "button": "#E6D5E8", "entry": "#FFFFFF",
        "border": "#D8BFD8", "highlight": "#BA55D3"
    },
    "🌻 Sunny Yellow": {
        "bg": "#FFFEF5", "header": "#FFE66D", "accent": "#F4B400",
        "text": "#5D4E37", "button": "#FFF3B0", "entry": "#FFFFFF",
        "border": "#FFE66D", "highlight": "#FFD93D"
    },
    "🍑 Peach": {
        "bg": "#FFF8F0", "header": "#FFDAB9", "accent": "#FF8C69",
        "text": "#5D4037", "button": "#FFE4C4", "entry": "#FFFFFF",
        "border": "#FFDAB9", "highlight": "#FFA07A"
    },
    "🐬 Aqua Cyan": {
        "bg": "#F0FFFF", "header": "#AFEEEE", "accent": "#20B2AA",
        "text": "#2F4F4F", "button": "#B0E0E6", "entry": "#FFFFFF",
        "border": "#AFEEEE", "highlight": "#48D1CC"
    },
    "🌺 Coral": {
        "bg": "#FFF5EE", "header": "#FFB4A2", "accent": "#E07A5F",
        "text": "#5D4037", "button": "#FFCDB2", "entry": "#FFFFFF",
        "border": "#FFB4A2", "highlight": "#FF8A80"
    },
    "❄️ Ice Silver": {
        "bg": "#F8F9FA", "header": "#DEE2E6", "accent": "#6C757D",
        "text": "#343A40", "button": "#E9ECEF", "entry": "#FFFFFF",
        "border": "#CED4DA", "highlight": "#ADB5BD"
    },
    "🌙 Soft Purple": {
        "bg": "#FAF5FF", "header": "#E9D5FF", "accent": "#A855F7",
        "text": "#4C1D95", "button": "#F3E8FF", "entry": "#FFFFFF",
        "border": "#E9D5FF", "highlight": "#C084FC"
    }
}

# ============== FONTS CONFIGURATION ==============
FONTS = {
    "title": ("Segoe UI Semibold", 12),
    "header": ("Segoe UI Semibold", 11),
    "normal": ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
    "tiny": ("Segoe UI", 8),
    "button": ("Segoe UI Semibold", 10),
    "calendar_day": ("Segoe UI Semibold", 9),
    "calendar_event": ("Segoe UI", 7),
    "time": ("Consolas", 10),
    "clock": ("Segoe UI Light", 24),
}

# ============== DATA FILE ==============
DATA_FILE = os.path.join(os.path.expanduser("~"), "desktop_widgets_data_v2.json")

# ============== BASE WIDGET CLASS ==============
class BaseWidget:
    """Enhanced base widget with individual theming"""
    
    def __init__(self, master, title, widget_id, app, default_size=(320, 420)):
        self.app = app
        self.widget_id = widget_id
        self.master = master
        self.title_text = title
        
        # Get individual theme for this widget
        widget_themes = app.data.get("widget_themes", {})
        theme_name = widget_themes.get(widget_id, app.data.get("default_theme", "🌊 Ocean Blue"))
        self.theme = THEMES.get(theme_name, THEMES["🌊 Ocean Blue"])
        self.current_theme_name = theme_name
        
        # Create window
        self.window = tk.Toplevel(master)
        self.window.title(title)
        self.window.overrideredirect(True)
        
        # Get saved position and size
        pos = app.data.get("widget_positions", {}).get(widget_id, {"x": 100, "y": 100})
        size = app.data.get("widget_sizes", {}).get(widget_id, {"w": default_size[0], "h": default_size[1]})
        
        self.window.geometry(f"{size['w']}x{size['h']}+{pos['x']}+{pos['y']}")
        
        # Dragging variables
        self.drag_data = {"x": 0, "y": 0, "dragging": False}
        self.resize_data = {"active": False}
        
        # Window attributes
        self.window.attributes('-topmost', False)
        self.window.attributes('-alpha', 0.97)
        
        # Main container with rounded appearance
        self.container = tk.Frame(self.window, bg=self.theme["border"], bd=0)
        self.container.pack(fill="both", expand=True, padx=1, pady=1)
        
        self.inner_container = tk.Frame(self.container, bg=self.theme["bg"])
        self.inner_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Create header
        self.create_header(title)
        
        # Create content area
        self.content = tk.Frame(self.inner_container, bg=self.theme["bg"])
        self.content.pack(fill="both", expand=True, padx=8, pady=(5, 8))
        
        # Create resize grip
        self.create_resize_grip()
        
        # Bind events
        self.window.bind("<FocusIn>", lambda e: self.window.after(50, self.send_to_desktop))
        
        # Send to desktop
        self.window.after(100, self.send_to_desktop)
    
    def create_header(self, title):
        """Create beautiful header"""
        self.header = tk.Frame(self.inner_container, bg=self.theme["header"], height=38)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        
        # Left side - Title
        self.title_label = tk.Label(
            self.header,
            text=f"  {title}",
            bg=self.theme["header"],
            fg=self.theme["text"],
            font=FONTS["title"],
            anchor="w"
        )
        self.title_label.pack(side="left", fill="x", expand=True)
        
        # Right side - Control buttons
        controls = tk.Frame(self.header, bg=self.theme["header"])
        controls.pack(side="right", padx=5)
        
        # Theme button
        self.theme_btn = tk.Label(
            controls,
            text=" 🎨 ",
            bg=self.theme["header"],
            fg=self.theme["text"],
            font=("Segoe UI", 11),
            cursor="hand2"
        )
        self.theme_btn.pack(side="left", padx=2)
        self.theme_btn.bind("<Button-1>", self.show_theme_menu)
        self.theme_btn.bind("<Enter>", lambda e: self.theme_btn.config(bg=self.theme["highlight"]))
        self.theme_btn.bind("<Leave>", lambda e: self.theme_btn.config(bg=self.theme["header"]))
        
        # Minimize button
        self.min_btn = tk.Label(
            controls,
            text=" ─ ",
            bg=self.theme["header"],
            fg=self.theme["text"],
            font=("Segoe UI", 11),
            cursor="hand2"
        )
        self.min_btn.pack(side="left", padx=2)
        self.min_btn.bind("<Button-1>", lambda e: self.window.iconify())
        self.min_btn.bind("<Enter>", lambda e: self.min_btn.config(bg=self.theme["highlight"]))
        self.min_btn.bind("<Leave>", lambda e: self.min_btn.config(bg=self.theme["header"]))
        
        # Close button
        self.close_btn = tk.Label(
            controls,
            text=" ✕ ",
            bg=self.theme["header"],
            fg=self.theme["text"],
            font=("Segoe UI", 11),
            cursor="hand2"
        )
        self.close_btn.pack(side="left", padx=2)
        self.close_btn.bind("<Button-1>", self.hide_widget)
        self.close_btn.bind("<Enter>", lambda e: self.close_btn.config(bg="#FF6B6B", fg="white"))
        self.close_btn.bind("<Leave>", lambda e: self.close_btn.config(bg=self.theme["header"], fg=self.theme["text"]))
        
        # Bind drag events
        for widget in [self.header, self.title_label]:
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.do_drag)
            widget.bind("<ButtonRelease-1>", self.stop_drag)
    
    def create_resize_grip(self):
        """Create resize grip"""
        self.resize_grip = tk.Label(
            self.inner_container,
            text="⋮⋮",
            bg=self.theme["bg"],
            fg=self.theme["border"],
            font=("Segoe UI", 10),
            cursor="size_nw_se"
        )
        self.resize_grip.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5)
        
        self.resize_grip.bind("<Button-1>", self.start_resize)
        self.resize_grip.bind("<B1-Motion>", self.do_resize)
        self.resize_grip.bind("<ButtonRelease-1>", self.stop_resize)
    
    def show_theme_menu(self, event):
        """Show theme selection dropdown"""
        menu = tk.Menu(self.window, tearoff=0, font=FONTS["normal"])
        menu.config(bg=self.theme["bg"], fg=self.theme["text"])
        
        for theme_name in THEMES.keys():
            menu.add_command(
                label=theme_name,
                command=lambda tn=theme_name: self.change_individual_theme(tn)
            )
        
        menu.tk_popup(event.x_root, event.y_root)
    
    def change_individual_theme(self, theme_name):
        """Change theme for this widget only"""
        self.theme = THEMES[theme_name]
        self.current_theme_name = theme_name
        
        # Save to data
        if "widget_themes" not in self.app.data:
            self.app.data["widget_themes"] = {}
        self.app.data["widget_themes"][self.widget_id] = theme_name
        self.app.save_data()
        
        # Update appearance
        self.update_theme()
    
    def start_drag(self, event):
        self.drag_data["x"] = event.x_root - self.window.winfo_x()
        self.drag_data["y"] = event.y_root - self.window.winfo_y()
        self.drag_data["dragging"] = True
    
    def do_drag(self, event):
        if self.drag_data["dragging"]:
            x = event.x_root - self.drag_data["x"]
            y = event.y_root - self.drag_data["y"]
            self.window.geometry(f"+{x}+{y}")
    
    def stop_drag(self, event):
        self.drag_data["dragging"] = False
        self.save_position()
    
    def start_resize(self, event):
        self.resize_data["active"] = True
        self.resize_data["x"] = event.x_root
        self.resize_data["y"] = event.y_root
        self.resize_data["width"] = self.window.winfo_width()
        self.resize_data["height"] = self.window.winfo_height()
    
    def do_resize(self, event):
        if self.resize_data["active"]:
            dx = event.x_root - self.resize_data["x"]
            dy = event.y_root - self.resize_data["y"]
            new_w = max(250, self.resize_data["width"] + dx)
            new_h = max(200, self.resize_data["height"] + dy)
            self.window.geometry(f"{new_w}x{new_h}")
    
    def stop_resize(self, event):
        self.resize_data["active"] = False
        self.save_size()
        self.on_resize()
    
    def on_resize(self):
        """Override in subclasses for resize handling"""
        pass
    
    def save_position(self):
        if "widget_positions" not in self.app.data:
            self.app.data["widget_positions"] = {}
        self.app.data["widget_positions"][self.widget_id] = {
            "x": self.window.winfo_x(),
            "y": self.window.winfo_y()
        }
        self.app.save_data()
    
    def save_size(self):
        if "widget_sizes" not in self.app.data:
            self.app.data["widget_sizes"] = {}
        self.app.data["widget_sizes"][self.widget_id] = {
            "w": self.window.winfo_width(),
            "h": self.window.winfo_height()
        }
        self.app.save_data()
    
    def send_to_desktop(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.window.winfo_id())
            ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            )
        except:
            pass
    
    def hide_widget(self, event=None):
        self.window.withdraw()
        if "hidden_widgets" not in self.app.data:
            self.app.data["hidden_widgets"] = []
        if self.widget_id not in self.app.data["hidden_widgets"]:
            self.app.data["hidden_widgets"].append(self.widget_id)
        self.app.save_data()
        self.app.update_control_panel()
    
    def show_widget(self):
        self.window.deiconify()
        if "hidden_widgets" in self.app.data and self.widget_id in self.app.data["hidden_widgets"]:
            self.app.data["hidden_widgets"].remove(self.widget_id)
        self.app.save_data()
    
    def update_theme(self):
        """Update widget colors - override in subclasses"""
        self.container.config(bg=self.theme["border"])
        self.inner_container.config(bg=self.theme["bg"])
        self.header.config(bg=self.theme["header"])
        self.title_label.config(bg=self.theme["header"], fg=self.theme["text"])
        self.theme_btn.config(bg=self.theme["header"], fg=self.theme["text"])
        self.min_btn.config(bg=self.theme["header"], fg=self.theme["text"])
        self.close_btn.config(bg=self.theme["header"], fg=self.theme["text"])
        self.content.config(bg=self.theme["bg"])
        self.resize_grip.config(bg=self.theme["bg"], fg=self.theme["border"])


# ============== ENHANCED CALENDAR WIDGET ==============
class CalendarWidget(BaseWidget):
    """Calendar with visible events below each date"""
    
    def __init__(self, master, app):
        super().__init__(master, "📅 Calendar", "calendar", app, (380, 480))
        self.current_date = datetime.now()
        self.selected_date = None
        self.create_content()
    
    def create_content(self):
        # Navigation
        nav = tk.Frame(self.content, bg=self.theme["bg"])
        nav.pack(fill="x", pady=(0, 8))
        
        self.prev_btn = tk.Button(
            nav, text="◀ Prev", command=self.prev_month,
            bg=self.theme["button"], fg=self.theme["text"],
            font=FONTS["button"], bd=0, padx=10, cursor="hand2",
            activebackground=self.theme["highlight"]
        )
        self.prev_btn.pack(side="left")
        
        self.month_label = tk.Label(
            nav, text="", bg=self.theme["bg"], fg=self.theme["text"],
            font=FONTS["header"]
        )
        self.month_label.pack(side="left", fill="x", expand=True)
        
        self.next_btn = tk.Button(
            nav, text="Next ▶", command=self.next_month,
            bg=self.theme["button"], fg=self.theme["text"],
            font=FONTS["button"], bd=0, padx=10, cursor="hand2",
            activebackground=self.theme["highlight"]
        )
        self.next_btn.pack(side="right")
        
        # Day headers
        days_frame = tk.Frame(self.content, bg=self.theme["bg"])
        days_frame.pack(fill="x", pady=(0, 3))
        
        self.day_headers = []
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            lbl = tk.Label(
                days_frame, text=day, bg=self.theme["header"],
                fg=self.theme["text"], font=FONTS["calendar_day"],
                width=5, pady=3
            )
            lbl.pack(side="left", expand=True, fill="x", padx=1)
            self.day_headers.append(lbl)
        
        # Calendar grid with scrollable frame
        self.cal_container = tk.Frame(self.content, bg=self.theme["bg"])
        self.cal_container.pack(fill="both", expand=True)
        
        self.cal_canvas = tk.Canvas(self.cal_container, bg=self.theme["bg"], highlightthickness=0)
        self.cal_scrollbar = tk.Scrollbar(self.cal_container, orient="vertical", command=self.cal_canvas.yview)
        
        self.cal_frame = tk.Frame(self.cal_canvas, bg=self.theme["bg"])
        
        self.cal_canvas.pack(side="left", fill="both", expand=True)
        self.cal_scrollbar.pack(side="right", fill="y")
        self.cal_canvas.configure(yscrollcommand=self.cal_scrollbar.set)
        
        self.cal_window = self.cal_canvas.create_window((0, 0), window=self.cal_frame, anchor="nw")
        
        self.cal_frame.bind("<Configure>", self.on_frame_configure)
        self.cal_canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Create date cells
        self.date_cells = []
        for row in range(6):
            row_cells = []
            for col in range(7):
                cell = self.create_date_cell(row, col)
                row_cells.append(cell)
            self.date_cells.append(row_cells)
        
        # Event editing section
        self.edit_frame = tk.Frame(self.content, bg=self.theme["bg"])
        self.edit_frame.pack(fill="x", pady=(8, 0))
        
        self.selected_label = tk.Label(
            self.edit_frame, text="📝 Select a date to add events",
            bg=self.theme["bg"], fg=self.theme["text"],
            font=FONTS["small"], anchor="w"
        )
        self.selected_label.pack(fill="x")
        
        self.event_entry = tk.Entry(
            self.edit_frame, bg=self.theme["entry"], fg=self.theme["text"],
            font=FONTS["normal"], bd=1, relief="solid"
        )
        self.event_entry.pack(fill="x", pady=(3, 0))
        self.event_entry.bind("<Return>", self.save_event)
        self.event_entry.bind("<KeyRelease>", self.save_event)
        
        self.update_calendar()
    
    def create_date_cell(self, row, col):
        """Create a date cell with space for events"""
        cell_frame = tk.Frame(self.cal_frame, bg=self.theme["entry"], bd=1, relief="solid")
        cell_frame.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
        
        # Configure grid weights
        self.cal_frame.columnconfigure(col, weight=1)
        self.cal_frame.rowconfigure(row, weight=1)
        
        # Date number
        date_label = tk.Label(
            cell_frame, text="", bg=self.theme["entry"],
            fg=self.theme["text"], font=FONTS["calendar_day"],
            anchor="nw", padx=3, pady=1
        )
        date_label.pack(fill="x", anchor="nw")
        
        # Event text (below date)
        event_label = tk.Label(
            cell_frame, text="", bg=self.theme["entry"],
            fg=self.theme["accent"], font=FONTS["calendar_event"],
            anchor="nw", padx=3, pady=0, justify="left",
            wraplength=45
        )
        event_label.pack(fill="both", expand=True, anchor="nw")
        
        # Bind click events
        for widget in [cell_frame, date_label, event_label]:
            widget.bind("<Button-1>", lambda e, r=row, c=col: self.select_date(r, c))
            widget.bind("<Enter>", lambda e, f=cell_frame: f.config(bg=self.theme["highlight"]))
            widget.bind("<Leave>", lambda e, f=cell_frame, d=date_label, ev=event_label: self.reset_cell_bg(f, d, ev))
        
        return {
            "frame": cell_frame,
            "date_label": date_label,
            "event_label": event_label,
            "date_value": None
        }
    
    def reset_cell_bg(self, frame, date_lbl, event_lbl):
        """Reset cell background on mouse leave"""
        bg = self.theme["entry"]
        if hasattr(frame, 'is_today') and frame.is_today:
            bg = self.theme["accent"]
        elif hasattr(frame, 'is_selected') and frame.is_selected:
            bg = self.theme["header"]
        frame.config(bg=bg)
        date_lbl.config(bg=bg)
        event_lbl.config(bg=bg)
    
    def on_frame_configure(self, event):
        self.cal_canvas.configure(scrollregion=self.cal_canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        self.cal_canvas.itemconfig(self.cal_window, width=event.width)
    
    def update_calendar(self):
        """Update calendar display with events"""
        year = self.current_date.year
        month = self.current_date.month
        
        self.month_label.config(text=f"{calendar.month_name[month]} {year}")
        
        cal = calendar.monthcalendar(year, month)
        today = datetime.now()
        events = self.app.data.get("calendar_events", {})
        
        for row in range(6):
            for col in range(7):
                cell = self.date_cells[row][col]
                frame = cell["frame"]
                date_lbl = cell["date_label"]
                event_lbl = cell["event_label"]
                
                if row < len(cal) and cal[row][col] != 0:
                    day = cal[row][col]
                    date_key = f"{year}-{month:02d}-{day:02d}"
                    
                    cell["date_value"] = date_key
                    date_lbl.config(text=str(day))
                    
                    # Get event for this date
                    event_text = events.get(date_key, "")
                    # Truncate for display
                    display_text = event_text[:25] + "..." if len(event_text) > 25 else event_text
                    event_lbl.config(text=display_text)
                    
                    # Styling
                    frame.is_today = False
                    frame.is_selected = False
                    
                    if year == today.year and month == today.month and day == today.day:
                        bg = self.theme["accent"]
                        fg = "white"
                        frame.is_today = True
                    elif date_key == self.selected_date:
                        bg = self.theme["header"]
                        fg = self.theme["text"]
                        frame.is_selected = True
                    elif event_text:
                        bg = self.theme["button"]
                        fg = self.theme["text"]
                    else:
                        bg = self.theme["entry"]
                        fg = self.theme["text"]
                    
                    frame.config(bg=bg)
                    date_lbl.config(bg=bg, fg=fg)
                    event_lbl.config(bg=bg, fg=self.theme["accent"] if not frame.is_today else "white")
                    
                    frame.grid()
                else:
                    cell["date_value"] = None
                    date_lbl.config(text="")
                    event_lbl.config(text="")
                    frame.config(bg=self.theme["bg"])
                    date_lbl.config(bg=self.theme["bg"])
                    event_lbl.config(bg=self.theme["bg"])
    
    def select_date(self, row, col):
        """Select a date for editing"""
        cell = self.date_cells[row][col]
        if cell["date_value"]:
            self.selected_date = cell["date_value"]
            events = self.app.data.get("calendar_events", {})
            event_text = events.get(self.selected_date, "")
            
            self.event_entry.delete(0, "end")
            self.event_entry.insert(0, event_text)
            self.selected_label.config(text=f"📝 Event for {self.selected_date}:")
            
            self.update_calendar()
    
    def save_event(self, event=None):
        """Save event for selected date"""
        if self.selected_date:
            if "calendar_events" not in self.app.data:
                self.app.data["calendar_events"] = {}
            
            text = self.event_entry.get()
            if text.strip():
                self.app.data["calendar_events"][self.selected_date] = text
            elif self.selected_date in self.app.data["calendar_events"]:
                del self.app.data["calendar_events"][self.selected_date]
            
            self.app.save_data()
            self.update_calendar()
    
    def prev_month(self):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
    
    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()
    
    def update_theme(self):
        super().update_theme()
        theme = self.theme
        
        self.prev_btn.config(bg=theme["button"], fg=theme["text"], activebackground=theme["highlight"])
        self.next_btn.config(bg=theme["button"], fg=theme["text"], activebackground=theme["highlight"])
        self.month_label.config(bg=theme["bg"], fg=theme["text"])
        
        for lbl in self.day_headers:
            lbl.config(bg=theme["header"], fg=theme["text"])
        
        self.cal_container.config(bg=theme["bg"])
        self.cal_canvas.config(bg=theme["bg"])
        self.cal_frame.config(bg=theme["bg"])
        
        self.edit_frame.config(bg=theme["bg"])
        self.selected_label.config(bg=theme["bg"], fg=theme["text"])
        self.event_entry.config(bg=theme["entry"], fg=theme["text"])
        
        self.update_calendar()


# ============== TODO LIST WIDGET ==============
class TodoWidget(BaseWidget):
    """Enhanced To-Do List with priorities"""
    
    def __init__(self, master, app):
        super().__init__(master, "✅ To-Do List", "todo", app, (320, 450))
        self.create_content()
    
    def create_content(self):
        # Add task section
        add_frame = tk.Frame(self.content, bg=self.theme["bg"])
        add_frame.pack(fill="x", pady=(0, 8))
        
        self.task_entry = tk.Entry(
            add_frame, bg=self.theme["entry"], fg=self.theme["text"],
            font=FONTS["normal"], bd=1, relief="solid"
        )
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.task_entry.insert(0, "Enter new task...")
        self.task_entry.bind("<FocusIn>", lambda e: self.task_entry.delete(0, "end") if self.task_entry.get() == "Enter new task..." else None)
        self.task_entry.bind("<Return>", self.add_task)
        
        # Priority dropdown
        self.priority_var = tk.StringVar(value="●")
        priorities = ["🔴 High", "🟡 Medium", "🟢 Low"]
        self.priority_menu = ttk.Combobox(
            add_frame, textvariable=self.priority_var,
            values=priorities, width=10, state="readonly"
        )
        self.priority_menu.pack(side="left", padx=(0, 5))
        self.priority_menu.current(1)
        
        self.add_btn = tk.Button(
            add_frame, text="➕", command=self.add_task,
            bg=self.theme["accent"], fg="white",
            font=FONTS["button"], bd=0, padx=10, cursor="hand2"
        )
        self.add_btn.pack(side="right")
        
        # Filter buttons
        filter_frame = tk.Frame(self.content, bg=self.theme["bg"])
        filter_frame.pack(fill="x", pady=(0, 5))
        
        self.filter_var = tk.StringVar(value="all")
        
        for text, val in [("All", "all"), ("Active", "active"), ("Done", "done")]:
            rb = tk.Radiobutton(
                filter_frame, text=text, variable=self.filter_var,
                value=val, bg=self.theme["bg"], fg=self.theme["text"],
                font=FONTS["small"], selectcolor=self.theme["entry"],
                activebackground=self.theme["bg"], command=self.load_tasks
            )
            rb.pack(side="left", padx=5)
        
        # Task list
        list_frame = tk.Frame(self.content, bg=self.theme["bg"])
        list_frame.pack(fill="both", expand=True)
        
        self.scrollbar = tk.Scrollbar(list_frame)
        self.scrollbar.pack(side="right", fill="y")
        
        self.task_canvas = tk.Canvas(
            list_frame, bg=self.theme["bg"], highlightthickness=0,
            yscrollcommand=self.scrollbar.set
        )
        self.task_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.task_canvas.yview)
        
        self.task_container = tk.Frame(self.task_canvas, bg=self.theme["bg"])
        self.task_canvas.create_window((0, 0), window=self.task_container, anchor="nw")
        
        self.task_container.bind("<Configure>",
            lambda e: self.task_canvas.configure(scrollregion=self.task_canvas.bbox("all")))
        
        # Stats
        self.stats_label = tk.Label(
            self.content, text="", bg=self.theme["bg"],
            fg=self.theme["text"], font=FONTS["small"]
        )
        self.stats_label.pack(fill="x", pady=(5, 0))
        
        self.load_tasks()
    
    def load_tasks(self):
        """Load and display tasks"""
        for widget in self.task_container.winfo_children():
            widget.destroy()
        
        tasks = self.app.data.get("todos", [])
        filter_val = self.filter_var.get()
        
        # Sort by priority
        priority_order = {"🔴 High": 0, "🟡 Medium": 1, "🟢 Low": 2}
        sorted_tasks = sorted(enumerate(tasks), 
            key=lambda x: (x[1].get("done", False), priority_order.get(x[1].get("priority", "🟡 Medium"), 1)))
        
        displayed = 0
        total = len(tasks)
        done = sum(1 for t in tasks if t.get("done"))
        
        for orig_idx, task in sorted_tasks:
            if filter_val == "active" and task.get("done"):
                continue
            if filter_val == "done" and not task.get("done"):
                continue
            
            self.create_task_row(orig_idx, task)
            displayed += 1
        
        self.stats_label.config(text=f"📊 {done}/{total} completed")
    
    def create_task_row(self, index, task):
        """Create a task row"""
        priority = task.get("priority", "🟡 Medium")
        priority_colors = {
            "🔴 High": "#FFE5E5",
            "🟡 Medium": "#FFF9E5",
            "🟢 Low": "#E5FFE5"
        }
        row_bg = priority_colors.get(priority, self.theme["entry"])
        
        row = tk.Frame(self.task_container, bg=row_bg, pady=4, padx=5)
        row.pack(fill="x", pady=2)
        
        # Priority indicator
        priority_icon = priority.split()[0] if priority else "●"
        tk.Label(row, text=priority_icon, bg=row_bg, font=FONTS["small"]).pack(side="left")
        
        # Checkbox
        var = tk.BooleanVar(value=task.get("done", False))
        cb = tk.Checkbutton(
            row, variable=var, bg=row_bg, activebackground=row_bg,
            command=lambda: self.toggle_task(index, var.get())
        )
        cb.pack(side="left")
        
        # Task text
        text_style = "overstrike" if task.get("done") else "normal"
        text_color = "#999999" if task.get("done") else self.theme["text"]
        
        lbl = tk.Label(
            row, text=task.get("text", ""), bg=row_bg, fg=text_color,
            font=("Segoe UI", 10, text_style), anchor="w"
        )
        lbl.pack(side="left", fill="x", expand=True, padx=5)
        
        # Delete button
        del_btn = tk.Label(
            row, text="🗑️", bg=row_bg, fg="#FF6B6B",
            font=FONTS["normal"], cursor="hand2"
        )
        del_btn.pack(side="right", padx=3)
        del_btn.bind("<Button-1>", lambda e: self.delete_task(index))
    
    def add_task(self, event=None):
        text = self.task_entry.get().strip()
        if text and text != "Enter new task...":
            if "todos" not in self.app.data:
                self.app.data["todos"] = []
            
            self.app.data["todos"].append({
                "text": text,
                "done": False,
                "priority": self.priority_var.get(),
                "created": datetime.now().isoformat()
            })
            self.app.save_data()
            
            self.task_entry.delete(0, "end")
            self.load_tasks()
    
    def toggle_task(self, index, done):
        if "todos" in self.app.data and index < len(self.app.data["todos"]):
            self.app.data["todos"][index]["done"] = done
            self.app.save_data()
            self.load_tasks()
    
    def delete_task(self, index):
        if "todos" in self.app.data and index < len(self.app.data["todos"]):
            del self.app.data["todos"][index]
            self.app.save_data()
            self.load_tasks()
    
    def update_theme(self):
        super().update_theme()
        theme = self.theme
        
        self.task_entry.config(bg=theme["entry"], fg=theme["text"])
        self.add_btn.config(bg=theme["accent"])
        self.task_canvas.config(bg=theme["bg"])
        self.task_container.config(bg=theme["bg"])
        self.stats_label.config(bg=theme["bg"], fg=theme["text"])
        
        self.load_tasks()


# ============== DAY PLANNER WIDGET ==============
class DayPlannerWidget(BaseWidget):
    """Day planner with time slots"""
    
    def __init__(self, master, app):
        super().__init__(master, "📆 Day Planner", "day_planner", app, (320, 480))
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.create_content()
    
    def create_content(self):
        # Date navigation
        nav = tk.Frame(self.content, bg=self.theme["bg"])
        nav.pack(fill="x", pady=(0, 8))
        
        self.prev_btn = tk.Button(
            nav, text="◀", command=self.prev_day,
            bg=self.theme["button"], fg=self.theme["text"],
            font=FONTS["button"], bd=0, padx=8, cursor="hand2"
        )
        self.prev_btn.pack(side="left")
        
        self.today_btn = tk.Button(
            nav, text="Today", command=self.go_today,
            bg=self.theme["accent"], fg="white",
            font=FONTS["small"], bd=0, padx=8, cursor="hand2"
        )
        self.today_btn.pack(side="left", padx=5)
        
        self.date_label = tk.Label(
            nav, text="", bg=self.theme["bg"], fg=self.theme["text"],
            font=FONTS["header"]
        )
        self.date_label.pack(side="left", fill="x", expand=True)
        
        self.next_btn = tk.Button(
            nav, text="▶", command=self.next_day,
            bg=self.theme["button"], fg=self.theme["text"],
            font=FONTS["button"], bd=0, padx=8, cursor="hand2"
        )
        self.next_btn.pack(side="right")
        
        # Time slots
        scroll_frame = tk.Frame(self.content, bg=self.theme["bg"])
        scroll_frame.pack(fill="both", expand=True)
        
        self.scrollbar = tk.Scrollbar(scroll_frame)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas = tk.Canvas(
            scroll_frame, bg=self.theme["bg"], highlightthickness=0,
            yscrollcommand=self.scrollbar.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.canvas.yview)
        
        self.slots_frame = tk.Frame(self.canvas, bg=self.theme["bg"])
        self.canvas.create_window((0, 0), window=self.slots_frame, anchor="nw")
        
        self.time_entries = {}
        
        # Create slots from 5 AM to 11 PM
        for hour in range(5, 24):
            self.create_time_slot(hour)
        
        self.slots_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.load_day_data()
    
    def create_time_slot(self, hour):
        row = tk.Frame(self.slots_frame, bg=self.theme["bg"])
        row.pack(fill="x", pady=1)
        
        # Current hour highlighting
        current_hour = datetime.now().hour
        is_current = (hour == current_hour and self.current_date == datetime.now().strftime("%Y-%m-%d"))
        
        time_bg = self.theme["accent"] if is_current else self.theme["header"]
        time_fg = "white" if is_current else self.theme["text"]
        
        # Time label
        time_str = f"{hour:02d}:00"
        time_lbl = tk.Label(
            row, text=time_str, bg=time_bg, fg=time_fg,
            font=FONTS["time"], width=6, pady=4
        )
        time_lbl.pack(side="left", padx=(0, 3))
        
        # Task entry
        entry = tk.Entry(
            row, bg=self.theme["entry"], fg=self.theme["text"],
            font=FONTS["normal"], bd=1, relief="solid"
        )
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<KeyRelease>", lambda e, h=hour: self.save_slot(h))
        
        self.time_entries[hour] = {"entry": entry, "time_label": time_lbl}
    
    def load_day_data(self):
        day_data = self.app.data.get("day_planner", {}).get(self.current_date, {})
        
        # Format date nicely
        date_obj = datetime.strptime(self.current_date, "%Y-%m-%d")
        date_str = date_obj.strftime("%A, %B %d, %Y")
        self.date_label.config(text=date_str)
        
        current_hour = datetime.now().hour
        is_today = self.current_date == datetime.now().strftime("%Y-%m-%d")
        
        for hour, widgets in self.time_entries.items():
            entry = widgets["entry"]
            time_lbl = widgets["time_label"]
            
            entry.delete(0, "end")
            if str(hour) in day_data:
                entry.insert(0, day_data[str(hour)])
            
            # Highlight current hour
            is_current = (hour == current_hour and is_today)
            time_bg = self.theme["accent"] if is_current else self.theme["header"]
            time_fg = "white" if is_current else self.theme["text"]
            time_lbl.config(bg=time_bg, fg=time_fg)
    
    def save_slot(self, hour):
        if "day_planner" not in self.app.data:
            self.app.data["day_planner"] = {}
        
        if self.current_date not in self.app.data["day_planner"]:
            self.app.data["day_planner"][self.current_date] = {}
        
        text = self.time_entries[hour]["entry"].get()
        if text:
            self.app.data["day_planner"][self.current_date][str(hour)] = text
        elif str(hour) in self.app.data["day_planner"][self.current_date]:
            del self.app.data["day_planner"][self.current_date][str(hour)]
        
        self.app.save_data()
    
    def prev_day(self):
        date = datetime.strptime(self.current_date, "%Y-%m-%d")
        date -= timedelta(days=1)
        self.current_date = date.strftime("%Y-%m-%d")
        self.load_day_data()
    
    def next_day(self):
        date = datetime.strptime(self.current_date, "%Y-%m-%d")
        date += timedelta(days=1)
        self.current_date = date.strftime("%Y-%m-%d")
        self.load_day_data()
    
    def go_today(self):
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.load_day_data()
    
    def update_theme(self):
        super().update_theme()
        theme = self.theme
        
        self.prev_btn.config(bg=theme["button"], fg=theme["text"])
        self.next_btn.config(bg=theme["button"], fg=theme["text"])
        self.today_btn.config(bg=theme["accent"])
        self.date_label.config(bg=theme["bg"], fg=theme["text"])
        self.canvas.config(bg=theme["bg"])
        self.slots_frame.config(bg=theme["bg"])
        
        self.load_day_data()


# ============== HORIZONTAL WEEK PLANNER ==============
class WeekPlannerWidget(BaseWidget):
    """Horizontal week planner"""
    
    def __init__(self, master, app):
        super().__init__(master, "📋 Week Planner", "week_planner", app, (700, 380))
        self.current_week_start = self.get_week_start(datetime.now())
        self.create_content()
    
    def get_week_start(self, date):
        return date - timedelta(days=date.weekday())
    
    def create_content(self):
        # Navigation
        nav = tk.Frame(self.content, bg=self.theme["bg"])
        nav.pack(fill="x", pady=(0, 8))
        
        self.prev_btn = tk.Button(
            nav, text="◀ Prev Week", command=self.prev_week,
            bg=self.theme["button"], fg=self.theme["text"],
            font=FONTS["button"], bd=0, padx=10, cursor="hand2"
        )
        self.prev_btn.pack(side="left")
        
        self.week_label = tk.Label(
            nav, text="", bg=self.theme["bg"], fg=self.theme["text"],
            font=FONTS["header"]
        )
        self.week_label.pack(side="left", fill="x", expand=True)
        
        self.today_btn = tk.Button(
            nav, text="This Week", command=self.go_this_week,
            bg=self.theme["accent"], fg="white",
            font=FONTS["small"], bd=0, padx=8, cursor="hand2"
        )
        self.today_btn.pack(side="right", padx=5)
        
        self.next_btn = tk.Button(
            nav, text="Next Week ▶", command=self.next_week,
            bg=self.theme["button"], fg=self.theme["text"],
            font=FONTS["button"], bd=0, padx=10, cursor="hand2"
        )
        self.next_btn.pack(side="right")
        
        # Horizontal days container
        self.days_container = tk.Frame(self.content, bg=self.theme["bg"])
        self.days_container.pack(fill="both", expand=True)
        
        self.day_columns = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for i, day_name in enumerate(days):
            self.create_day_column(i, day_name)
            self.days_container.columnconfigure(i, weight=1)
        
        self.days_container.rowconfigure(0, weight=0)  # Header
        self.days_container.rowconfigure(1, weight=1)  # Content
        
        self.load_week_data()
    
    def create_day_column(self, index, day_name):
        """Create a vertical day column"""
        # Header
        header = tk.Label(
            self.days_container, text=day_name[:3],
            bg=self.theme["header"], fg=self.theme["text"],
            font=FONTS["calendar_day"], pady=5
        )
        header.grid(row=0, column=index, sticky="ew", padx=1, pady=(0, 2))
        
        # Date sub-label
        date_lbl = tk.Label(
            self.days_container, text="",
            bg=self.theme["button"], fg=self.theme["text"],
            font=FONTS["tiny"], pady=2
        )
        date_lbl.grid(row=1, column=index, sticky="ew", padx=1)
        
        # Text area for tasks
        text = tk.Text(
            self.days_container, bg=self.theme["entry"], fg=self.theme["text"],
            font=FONTS["small"], bd=1, relief="solid", wrap="word",
            width=12
        )
        text.grid(row=2, column=index, sticky="nsew", padx=1, pady=2)
        text.bind("<KeyRelease>", lambda e, idx=index: self.save_day(idx))
        
        self.day_columns[index] = {
            "header": header,
            "date_label": date_lbl,
            "text": text
        }
        
        self.days_container.rowconfigure(2, weight=1)
    
    def load_week_data(self):
        week_key = self.current_week_start.strftime("%Y-%m-%d")
        week_data = self.app.data.get("week_planner", {}).get(week_key, {})
        
        week_end = self.current_week_start + timedelta(days=6)
        self.week_label.config(
            text=f"{self.current_week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
        )
        
        today = datetime.now().date()
        
        for i in range(7):
            day_date = self.current_week_start + timedelta(days=i)
            column = self.day_columns[i]
            
            # Update date label
            column["date_label"].config(text=day_date.strftime("%d"))
            
            # Highlight today
            if day_date.date() == today:
                column["header"].config(bg=self.theme["accent"], fg="white")
                column["date_label"].config(bg=self.theme["accent"], fg="white")
            else:
                column["header"].config(bg=self.theme["header"], fg=self.theme["text"])
                column["date_label"].config(bg=self.theme["button"], fg=self.theme["text"])
            
            # Load text
            column["text"].delete("1.0", "end")
            if str(i) in week_data:
                column["text"].insert("1.0", week_data[str(i)])
    
    def save_day(self, day_index):
        if "week_planner" not in self.app.data:
            self.app.data["week_planner"] = {}
        
        week_key = self.current_week_start.strftime("%Y-%m-%d")
        
        if week_key not in self.app.data["week_planner"]:
            self.app.data["week_planner"][week_key] = {}
        
        text = self.day_columns[day_index]["text"].get("1.0", "end-1c")
        if text.strip():
            self.app.data["week_planner"][week_key][str(day_index)] = text
        elif str(day_index) in self.app.data["week_planner"][week_key]:
            del self.app.data["week_planner"][week_key][str(day_index)]
        
        self.app.save_data()
    
    def prev_week(self):
        self.current_week_start -= timedelta(days=7)
        self.load_week_data()
    
    def next_week(self):
        self.current_week_start += timedelta(days=7)
        self.load_week_data()
    
    def go_this_week(self):
        self.current_week_start = self.get_week_start(datetime.now())
        self.load_week_data()
    
    def update_theme(self):
        super().update_theme()
        theme = self.theme
        
        self.prev_btn.config(bg=theme["button"], fg=theme["text"])
        self.next_btn.config(bg=theme["button"], fg=theme["text"])
        self.today_btn.config(bg=theme["accent"])
        self.week_label.config(bg=theme["bg"], fg=theme["text"])
        self.days_container.config(bg=theme["bg"])
        
        for column in self.day_columns.values():
            column["text"].config(bg=theme["entry"], fg=theme["text"])
        
        self.load_week_data()


# ============== MONTHLY PLANNER WIDGET ==============
class MonthlyPlannerWidget(BaseWidget):
    """Monthly goals and planning"""
    
    def __init__(self, master, app):
        super().__init__(master, "🎯 Monthly Planner", "monthly_planner", app, (340, 480))
        self.current_date = datetime.now()
        self.create_content()
    
    def create_content(self):
        # Navigation
        nav = tk.Frame(self.content, bg=self.theme["bg"])
        nav.pack(fill="x", pady=(0, 8))
        
        self.prev_btn = tk.Button(
            nav, text="◀", command=self.prev_month,
            bg=self.theme["button"], fg=self.theme["text"],
            font=FONTS["button"], bd=0, padx=8, cursor="hand2"
        )
        self.prev_btn.pack(side="left")
        
        self.month_label = tk.Label(
            nav, text="", bg=self.theme["bg"], fg=self.theme["text"],
            font=FONTS["header"]
        )
        self.month_label.pack(side="left", fill="x", expand=True)
        
        self.next_btn = tk.Button(
            nav, text="▶", command=self.next_month,
            bg=self.theme["button"], fg=self.theme["text"],
            font=FONTS["button"], bd=0, padx=8, cursor="hand2"
        )
        self.next_btn.pack(side="right")
        
        # Sections with scroll
        scroll_frame = tk.Frame(self.content, bg=self.theme["bg"])
        scroll_frame.pack(fill="both", expand=True)
        
        self.scrollbar = tk.Scrollbar(scroll_frame)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas = tk.Canvas(
            scroll_frame, bg=self.theme["bg"], highlightthickness=0,
            yscrollcommand=self.scrollbar.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.canvas.yview)
        
        self.sections_frame = tk.Frame(self.canvas, bg=self.theme["bg"])
        self.canvas.create_window((0, 0), window=self.sections_frame, anchor="nw")
        
        self.section_texts = {}
        
        sections = [
            ("🎯 Main Goals", "goals", 4),
            ("📋 Key Tasks", "tasks", 4),
            ("💡 Ideas & Projects", "ideas", 3),
            ("📚 Learning", "learning", 2),
            ("💪 Habits to Build", "habits", 2),
            ("📝 Notes", "notes", 3)
        ]
        
        for title, key, height in sections:
            self.create_section(title, key, height)
        
        self.sections_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.load_month_data()
    
    def create_section(self, title, key, height):
        frame = tk.Frame(self.sections_frame, bg=self.theme["bg"])
        frame.pack(fill="x", pady=3)
        
        header = tk.Label(
            frame, text=title, bg=self.theme["header"],
            fg=self.theme["text"], font=FONTS["small"],
            anchor="w", padx=8, pady=4
        )
        header.pack(fill="x")
        
        text = tk.Text(
            frame, height=height, bg=self.theme["entry"],
            fg=self.theme["text"], font=FONTS["normal"],
            bd=1, relief="solid", wrap="word", padx=5, pady=5
        )
        text.pack(fill="x")
        text.bind("<KeyRelease>", lambda e, k=key: self.save_section(k))
        
        self.section_texts[key] = {"text": text, "header": header}
    
    def load_month_data(self):
        month_key = self.current_date.strftime("%Y-%m")
        month_data = self.app.data.get("monthly_planner", {}).get(month_key, {})
        
        self.month_label.config(
            text=f"{calendar.month_name[self.current_date.month]} {self.current_date.year}"
        )
        
        for key, widgets in self.section_texts.items():
            widgets["text"].delete("1.0", "end")
            if key in month_data:
                widgets["text"].insert("1.0", month_data[key])
    
    def save_section(self, section_key):
        if "monthly_planner" not in self.app.data:
            self.app.data["monthly_planner"] = {}
        
        month_key = self.current_date.strftime("%Y-%m")
        
        if month_key not in self.app.data["monthly_planner"]:
            self.app.data["monthly_planner"][month_key] = {}
        
        text = self.section_texts[section_key]["text"].get("1.0", "end-1c")
        if text.strip():
            self.app.data["monthly_planner"][month_key][section_key] = text
        elif section_key in self.app.data["monthly_planner"][month_key]:
            del self.app.data["monthly_planner"][month_key][section_key]
        
        self.app.save_data()
    
    def prev_month(self):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.load_month_data()
    
    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.load_month_data()
    
    def update_theme(self):
        super().update_theme()
        theme = self.theme
        
        self.prev_btn.config(bg=theme["button"], fg=theme["text"])
        self.next_btn.config(bg=theme["button"], fg=theme["text"])
        self.month_label.config(bg=theme["bg"], fg=theme["text"])
        self.canvas.config(bg=theme["bg"])
        self.sections_frame.config(bg=theme["bg"])
        
        for widgets in self.section_texts.values():
            widgets["header"].config(bg=theme["header"], fg=theme["text"])
            widgets["text"].config(bg=theme["entry"], fg=theme["text"])


# ============== CLOCK WIDGET ==============
class ClockWidget(BaseWidget):
    """Digital clock with date"""
    
    def __init__(self, master, app):
        super().__init__(master, "🕐 Clock", "clock", app, (220, 140))
        self.create_content()
        self.update_clock()
    
    def create_content(self):
        # Time display
        self.time_label = tk.Label(
            self.content, text="", bg=self.theme["bg"],
            fg=self.theme["accent"], font=FONTS["clock"]
        )
        self.time_label.pack(expand=True)
        
        # Date display
        self.date_label = tk.Label(
            self.content, text="", bg=self.theme["bg"],
            fg=self.theme["text"], font=FONTS["normal"]
        )
        self.date_label.pack()
    
    def update_clock(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("%H:%M:%S"))
        self.date_label.config(text=now.strftime("%A, %B %d, %Y"))
        self.window.after(1000, self.update_clock)
    
    def update_theme(self):
        super().update_theme()
        self.time_label.config(bg=self.theme["bg"], fg=self.theme["accent"])
        self.date_label.config(bg=self.theme["bg"], fg=self.theme["text"])


# ============== STICKY NOTES WIDGET ==============
class StickyNotesWidget(BaseWidget):
    """Quick sticky notes"""
    
    def __init__(self, master, app):
        super().__init__(master, "📌 Sticky Notes", "sticky_notes", app, (300, 350))
        self.create_content()
    
    def create_content(self):
        # Add note button
        add_frame = tk.Frame(self.content, bg=self.theme["bg"])
        add_frame.pack(fill="x", pady=(0, 5))
        
        self.add_btn = tk.Button(
            add_frame, text="➕ Add New Note", command=self.add_note,
            bg=self.theme["accent"], fg="white",
            font=FONTS["button"], bd=0, padx=15, pady=5, cursor="hand2"
        )
        self.add_btn.pack()
        
        # Notes container
        scroll_frame = tk.Frame(self.content, bg=self.theme["bg"])
        scroll_frame.pack(fill="both", expand=True)
        
        self.scrollbar = tk.Scrollbar(scroll_frame)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas = tk.Canvas(
            scroll_frame, bg=self.theme["bg"], highlightthickness=0,
            yscrollcommand=self.scrollbar.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.canvas.yview)
        
        self.notes_frame = tk.Frame(self.canvas, bg=self.theme["bg"])
        self.canvas.create_window((0, 0), window=self.notes_frame, anchor="nw")
        
        self.notes_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.load_notes()
    
    def load_notes(self):
        for widget in self.notes_frame.winfo_children():
            widget.destroy()
        
        notes = self.app.data.get("sticky_notes", [])
        
        note_colors = ["#FFFACD", "#FFE4E1", "#E0FFFF", "#F0FFF0", "#FFF0F5", "#F5F5DC"]
        
        for i, note in enumerate(notes):
            color = note_colors[i % len(note_colors)]
            self.create_note_card(i, note, color)
    
    def create_note_card(self, index, note, bg_color):
        card = tk.Frame(self.notes_frame, bg=bg_color, pady=5, padx=5)
        card.pack(fill="x", pady=3, padx=2)
        
        # Header with delete button
        header = tk.Frame(card, bg=bg_color)
        header.pack(fill="x")
        
        time_lbl = tk.Label(
            header, text=note.get("time", ""), bg=bg_color,
            fg="#888888", font=FONTS["tiny"]
        )
        time_lbl.pack(side="left")
        
        del_btn = tk.Label(
            header, text="✕", bg=bg_color, fg="#FF6B6B",
            font=FONTS["small"], cursor="hand2"
        )
        del_btn.pack(side="right")
        del_btn.bind("<Button-1>", lambda e: self.delete_note(index))
        
        # Note text
        text = tk.Text(
            card, height=3, bg=bg_color, fg="#333333",
            font=FONTS["normal"], bd=0, wrap="word"
        )
        text.pack(fill="x")
        text.insert("1.0", note.get("text", ""))
        text.bind("<KeyRelease>", lambda e, idx=index: self.save_note(idx, text))
    
    def add_note(self):
        if "sticky_notes" not in self.app.data:
            self.app.data["sticky_notes"] = []
        
        self.app.data["sticky_notes"].insert(0, {
            "text": "",
            "time": datetime.now().strftime("%b %d, %H:%M")
        })
        self.app.save_data()
        self.load_notes()
    
    def save_note(self, index, text_widget):
        if "sticky_notes" in self.app.data and index < len(self.app.data["sticky_notes"]):
            self.app.data["sticky_notes"][index]["text"] = text_widget.get("1.0", "end-1c")
            self.app.save_data()
    
    def delete_note(self, index):
        if "sticky_notes" in self.app.data and index < len(self.app.data["sticky_notes"]):
            del self.app.data["sticky_notes"][index]
            self.app.save_data()
            self.load_notes()
    
    def update_theme(self):
        super().update_theme()
        self.add_btn.config(bg=self.theme["accent"])
        self.canvas.config(bg=self.theme["bg"])
        self.notes_frame.config(bg=self.theme["bg"])
        self.load_notes()


# ============== POMODORO TIMER WIDGET ==============
class PomodoroWidget(BaseWidget):
    """Pomodoro timer for productivity"""
    
    def __init__(self, master, app):
        super().__init__(master, "🍅 Pomodoro Timer", "pomodoro", app, (280, 280))
        self.work_time = 25 * 60
        self.break_time = 5 * 60
        self.time_left = self.work_time
        self.is_running = False
        self.is_work = True
        self.sessions = 0
        self.create_content()
    
    def create_content(self):
        # Mode indicator
        self.mode_label = tk.Label(
            self.content, text="🎯 WORK MODE", bg=self.theme["bg"],
            fg=self.theme["accent"], font=FONTS["header"]
        )
        self.mode_label.pack(pady=(10, 5))
        
        # Timer display
        self.timer_label = tk.Label(
            self.content, text="25:00", bg=self.theme["bg"],
            fg=self.theme["text"], font=("Segoe UI Light", 48)
        )
        self.timer_label.pack(pady=10)
        
        # Control buttons
        btn_frame = tk.Frame(self.content, bg=self.theme["bg"])
        btn_frame.pack(pady=10)
        
        self.start_btn = tk.Button(
            btn_frame, text="▶ Start", command=self.toggle_timer,
            bg=self.theme["accent"], fg="white",
            font=FONTS["button"], bd=0, padx=20, pady=8, cursor="hand2"
        )
        self.start_btn.pack(side="left", padx=5)
        
        self.reset_btn = tk.Button(
            btn_frame, text="↺ Reset", command=self.reset_timer,
            bg=self.theme["button"], fg=self.theme["text"],
            font=FONTS["button"], bd=0, padx=20, pady=8, cursor="hand2"
        )
        self.reset_btn.pack(side="left", padx=5)
        
        # Session counter
        self.session_label = tk.Label(
            self.content, text="Sessions: 0", bg=self.theme["bg"],
            fg=self.theme["text"], font=FONTS["normal"]
        )
        self.session_label.pack(pady=5)
        
        # Settings
        settings_frame = tk.Frame(self.content, bg=self.theme["bg"])
        settings_frame.pack(pady=5)
        
        tk.Label(settings_frame, text="Work:", bg=self.theme["bg"],
            fg=self.theme["text"], font=FONTS["small"]).pack(side="left")
        
        self.work_spin = tk.Spinbox(
            settings_frame, from_=1, to=60, width=3,
            font=FONTS["small"], command=self.update_settings
        )
        self.work_spin.pack(side="left", padx=2)
        self.work_spin.delete(0, "end")
        self.work_spin.insert(0, "25")
        
        tk.Label(settings_frame, text="min  Break:", bg=self.theme["bg"],
            fg=self.theme["text"], font=FONTS["small"]).pack(side="left")
        
        self.break_spin = tk.Spinbox(
            settings_frame, from_=1, to=30, width=3,
            font=FONTS["small"], command=self.update_settings
        )
        self.break_spin.pack(side="left", padx=2)
        self.break_spin.delete(0, "end")
        self.break_spin.insert(0, "5")
        
        tk.Label(settings_frame, text="min", bg=self.theme["bg"],
            fg=self.theme["text"], font=FONTS["small"]).pack(side="left")
    
    def update_settings(self):
        try:
            self.work_time = int(self.work_spin.get()) * 60
            self.break_time = int(self.break_spin.get()) * 60
            if not self.is_running:
                self.time_left = self.work_time if self.is_work else self.break_time
                self.update_display()
        except:
            pass
    
    def toggle_timer(self):
        self.is_running = not self.is_running
        self.start_btn.config(text="⏸ Pause" if self.is_running else "▶ Start")
        if self.is_running:
            self.run_timer()
    
    def run_timer(self):
        if self.is_running and self.time_left > 0:
            self.time_left -= 1
            self.update_display()
            self.window.after(1000, self.run_timer)
        elif self.time_left <= 0:
            self.timer_complete()
    
    def timer_complete(self):
        self.is_running = False
        self.start_btn.config(text="▶ Start")
        
        if self.is_work:
            self.sessions += 1
            self.session_label.config(text=f"Sessions: {self.sessions}")
            self.is_work = False
            self.time_left = self.break_time
            self.mode_label.config(text="☕ BREAK TIME", fg="#4CAF50")
        else:
            self.is_work = True
            self.time_left = self.work_time
            self.mode_label.config(text="🎯 WORK MODE", fg=self.theme["accent"])
        
        self.update_display()
        
        # Flash notification
        self.window.bell()
    
    def reset_timer(self):
        self.is_running = False
        self.is_work = True
        self.time_left = self.work_time
        self.start_btn.config(text="▶ Start")
        self.mode_label.config(text="🎯 WORK MODE", fg=self.theme["accent"])
        self.update_display()
    
    def update_display(self):
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
    
    def update_theme(self):
        super().update_theme()
        self.mode_label.config(bg=self.theme["bg"])
        self.timer_label.config(bg=self.theme["bg"], fg=self.theme["text"])
        self.start_btn.config(bg=self.theme["accent"])
        self.reset_btn.config(bg=self.theme["button"], fg=self.theme["text"])
        self.session_label.config(bg=self.theme["bg"], fg=self.theme["text"])


# ============== HABIT TRACKER WIDGET ==============
class HabitTrackerWidget(BaseWidget):
    """Weekly habit tracker"""
    
    def __init__(self, master, app):
        super().__init__(master, "💪 Habit Tracker", "habit_tracker", app, (400, 350))
        self.create_content()
    
    def create_content(self):
        # Add habit
        add_frame = tk.Frame(self.content, bg=self.theme["bg"])
        add_frame.pack(fill="x", pady=(0, 8))
        
        self.habit_entry = tk.Entry(
            add_frame, bg=self.theme["entry"], fg=self.theme["text"],
            font=FONTS["normal"], bd=1, relief="solid"
        )
        self.habit_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.habit_entry.insert(0, "New habit...")
        self.habit_entry.bind("<FocusIn>", lambda e: self.habit_entry.delete(0, "end") if self.habit_entry.get() == "New habit..." else None)
        self.habit_entry.bind("<Return>", self.add_habit)
        
        self.add_btn = tk.Button(
            add_frame, text="➕", command=self.add_habit,
            bg=self.theme["accent"], fg="white",
            font=FONTS["button"], bd=0, padx=10, cursor="hand2"
        )
        self.add_btn.pack(side="right")
        
        # Days header
        days_frame = tk.Frame(self.content, bg=self.theme["bg"])
        days_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(days_frame, text="Habit", bg=self.theme["bg"],
            fg=self.theme["text"], font=FONTS["small"], width=15, anchor="w").pack(side="left")
        
        self.day_labels = []
        for day in ["M", "T", "W", "T", "F", "S", "S"]:
            lbl = tk.Label(days_frame, text=day, bg=self.theme["header"],
                fg=self.theme["text"], font=FONTS["small"], width=3)
            lbl.pack(side="left", padx=1)
            self.day_labels.append(lbl)
        
        tk.Label(days_frame, text="", width=3, bg=self.theme["bg"]).pack(side="left")
        
        # Habits list
        scroll_frame = tk.Frame(self.content, bg=self.theme["bg"])
        scroll_frame.pack(fill="both", expand=True)
        
        self.scrollbar = tk.Scrollbar(scroll_frame)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas = tk.Canvas(
            scroll_frame, bg=self.theme["bg"], highlightthickness=0,
            yscrollcommand=self.scrollbar.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.canvas.yview)
        
        self.habits_frame = tk.Frame(self.canvas, bg=self.theme["bg"])
        self.canvas.create_window((0, 0), window=self.habits_frame, anchor="nw")
        
        self.habits_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.load_habits()
    
    def get_week_key(self):
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        return week_start.strftime("%Y-%m-%d")
    
    def load_habits(self):
        for widget in self.habits_frame.winfo_children():
            widget.destroy()
        
        habits = self.app.data.get("habits", [])
        week_key = self.get_week_key()
        week_data = self.app.data.get("habit_tracking", {}).get(week_key, {})
        
        for i, habit in enumerate(habits):
            self.create_habit_row(i, habit, week_data.get(str(i), []))
    
    def create_habit_row(self, index, habit_name, completed_days):
        row = tk.Frame(self.habits_frame, bg=self.theme["entry"], pady=3)
        row.pack(fill="x", pady=2)
        
        # Habit name
        lbl = tk.Label(row, text=habit_name, bg=self.theme["entry"],
            fg=self.theme["text"], font=FONTS["small"], width=15, anchor="w")
        lbl.pack(side="left", padx=3)
        
        # Day checkboxes
        vars = []
        for day in range(7):
            var = tk.BooleanVar(value=day in completed_days)
            vars.append(var)
            
            cb = tk.Checkbutton(
                row, variable=var, bg=self.theme["entry"],
                activebackground=self.theme["entry"],
                command=lambda idx=index, d=day, v=var: self.toggle_day(idx, d, v.get())
            )
            cb.pack(side="left", padx=1)
        
        # Delete button
        del_btn = tk.Label(row, text="🗑️", bg=self.theme["entry"],
            fg="#FF6B6B", font=FONTS["small"], cursor="hand2")
        del_btn.pack(side="right", padx=3)
        del_btn.bind("<Button-1>", lambda e: self.delete_habit(index))
    
    def add_habit(self, event=None):
        text = self.habit_entry.get().strip()
        if text and text != "New habit...":
            if "habits" not in self.app.data:
                self.app.data["habits"] = []
            
            self.app.data["habits"].append(text)
            self.app.save_data()
            
            self.habit_entry.delete(0, "end")
            self.load_habits()
    
    def toggle_day(self, habit_index, day, completed):
        if "habit_tracking" not in self.app.data:
            self.app.data["habit_tracking"] = {}
        
        week_key = self.get_week_key()
        if week_key not in self.app.data["habit_tracking"]:
            self.app.data["habit_tracking"][week_key] = {}
        
        habit_key = str(habit_index)
        if habit_key not in self.app.data["habit_tracking"][week_key]:
            self.app.data["habit_tracking"][week_key][habit_key] = []
        
        days = self.app.data["habit_tracking"][week_key][habit_key]
        
        if completed and day not in days:
            days.append(day)
        elif not completed and day in days:
            days.remove(day)
        
        self.app.save_data()
    
    def delete_habit(self, index):
        if "habits" in self.app.data and index < len(self.app.data["habits"]):
            del self.app.data["habits"][index]
            self.app.save_data()
            self.load_habits()
    
    def update_theme(self):
        super().update_theme()
        self.habit_entry.config(bg=self.theme["entry"], fg=self.theme["text"])
        self.add_btn.config(bg=self.theme["accent"])
        self.canvas.config(bg=self.theme["bg"])
        self.habits_frame.config(bg=self.theme["bg"])
        
        for lbl in self.day_labels:
            lbl.config(bg=self.theme["header"], fg=self.theme["text"])
        
        self.load_habits()


# ============== MAIN APPLICATION ==============
class DesktopWidgetsApp:
    """Main application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.load_data()
        
        self.widgets = {}
        self.create_widgets()
        self.create_control_panel()
        self.setup_autostart()
    
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except:
                self.data = self.get_default_data()
        else:
            self.data = self.get_default_data()
    
    def get_default_data(self):
        return {
            "default_theme": "🌊 Ocean Blue",
            "widget_themes": {},
            "calendar_events": {},
            "todos": [],
            "day_planner": {},
            "week_planner": {},
            "monthly_planner": {},
            "sticky_notes": [],
            "habits": [],
            "habit_tracking": {},
            "widget_positions": {},
            "widget_sizes": {},
            "hidden_widgets": []
        }
    
    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Save error: {e}")
    
    def create_widgets(self):
        hidden = self.data.get("hidden_widgets", [])
        
        widget_classes = {
            "calendar": CalendarWidget,
            "todo": TodoWidget,
            "day_planner": DayPlannerWidget,
            "week_planner": WeekPlannerWidget,
            "monthly_planner": MonthlyPlannerWidget,
            "clock": ClockWidget,
            "sticky_notes": StickyNotesWidget,
            "pomodoro": PomodoroWidget,
            "habit_tracker": HabitTrackerWidget
        }
        
        for widget_id, widget_class in widget_classes.items():
            self.widgets[widget_id] = widget_class(self.root, self)
            if widget_id in hidden:
                self.widgets[widget_id].window.withdraw()
    
    def create_control_panel(self):
        self.control_panel = tk.Toplevel(self.root)
        self.control_panel.title("🎮 Widget Control Panel")
        self.control_panel.geometry("320x580")
        self.control_panel.resizable(False, False)
        self.control_panel.attributes('-topmost', True)
        
        theme = THEMES.get(self.data.get("default_theme", "🌊 Ocean Blue"))
        self.control_panel.configure(bg=theme["bg"])
        
        # Title
        title = tk.Label(
            self.control_panel,
            text="🖥️ Desktop Widgets v2.0",
            bg=theme["header"],
            fg=theme["text"],
            font=FONTS["title"],
            pady=12
        )
        title.pack(fill="x")
        
        # Scrollable content
        canvas = tk.Canvas(self.control_panel, bg=theme["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.control_panel, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=theme["bg"])
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Widget toggles
        toggle_frame = tk.LabelFrame(
            scroll_frame, text="📱 Show/Hide Widgets",
            bg=theme["bg"], fg=theme["text"], font=FONTS["header"]
        )
        toggle_frame.pack(fill="x", padx=10, pady=10)
        
        widget_names = {
            "calendar": "📅 Calendar",
            "todo": "✅ To-Do List",
            "day_planner": "📆 Day Planner",
            "week_planner": "📋 Week Planner (Horizontal)",
            "monthly_planner": "🎯 Monthly Planner",
            "clock": "🕐 Clock",
            "sticky_notes": "📌 Sticky Notes",
            "pomodoro": "🍅 Pomodoro Timer",
            "habit_tracker": "💪 Habit Tracker"
        }
        
        self.widget_vars = {}
        for widget_id, widget_name in widget_names.items():
            var = tk.BooleanVar(value=widget_id not in self.data.get("hidden_widgets", []))
            self.widget_vars[widget_id] = var
            
            cb = tk.Checkbutton(
                toggle_frame, text=widget_name, variable=var,
                bg=theme["bg"], fg=theme["text"], font=FONTS["normal"],
                activebackground=theme["bg"], selectcolor=theme["entry"],
                command=lambda wid=widget_id: self.toggle_widget(wid)
            )
            cb.pack(anchor="w", padx=10, pady=2)
        
        # Quick actions
        action_frame = tk.LabelFrame(
            scroll_frame, text="⚡ Quick Actions",
            bg=theme["bg"], fg=theme["text"], font=FONTS["header"]
        )
        action_frame.pack(fill="x", padx=10, pady=10)
        
        btn_row = tk.Frame(action_frame, bg=theme["bg"])
        btn_row.pack(fill="x", pady=5)
        
        tk.Button(
            btn_row, text="👁️ Show All", command=self.show_all_widgets,
            bg=theme["button"], fg=theme["text"], font=FONTS["button"],
            bd=0, padx=12, pady=5, cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_row, text="🙈 Hide All", command=self.hide_all_widgets,
            bg=theme["button"], fg=theme["text"], font=FONTS["button"],
            bd=0, padx=12, pady=5, cursor="hand2"
        ).pack(side="left", padx=5)
        
        # Info
        info_frame = tk.LabelFrame(
            scroll_frame, text="ℹ️ Tips",
            bg=theme["bg"], fg=theme["text"], font=FONTS["header"]
        )
        info_frame.pack(fill="x", padx=10, pady=10)
        
        tips = [
            "🎨 Click color icon on each widget to change its theme",
            "↔️ Drag widgets by their header",
            "📐 Resize using bottom-right corner",
            "💾 All data auto-saves"
        ]
        
        for tip in tips:
            tk.Label(
                info_frame, text=tip, bg=theme["bg"], fg=theme["text"],
                font=FONTS["small"], anchor="w", wraplength=280
            ).pack(fill="x", padx=10, pady=2)
        
        # Exit button
        tk.Button(
            scroll_frame, text="❌ Exit Application", command=self.exit_app,
            bg="#FF6B6B", fg="white", font=FONTS["button"],
            bd=0, padx=20, pady=8, cursor="hand2"
        ).pack(pady=15)
        
        self.control_panel.protocol("WM_DELETE_WINDOW", self.minimize_control_panel)
    
    def update_control_panel(self):
        for widget_id, var in self.widget_vars.items():
            var.set(widget_id not in self.data.get("hidden_widgets", []))
    
    def minimize_control_panel(self):
        self.control_panel.iconify()
    
    def toggle_widget(self, widget_id):
        if self.widget_vars[widget_id].get():
            self.widgets[widget_id].show_widget()
        else:
            self.widgets[widget_id].hide_widget()
    
    def show_all_widgets(self):
        for widget_id, widget in self.widgets.items():
            widget.show_widget()
            self.widget_vars[widget_id].set(True)
    
    def hide_all_widgets(self):
        for widget_id, widget in self.widgets.items():
            widget.hide_widget()
            self.widget_vars[widget_id].set(False)
    
    def setup_autostart(self):
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "DesktopWidgets"
            
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = f'pythonw "{os.path.abspath(__file__)}"'
            
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
                winreg.CloseKey(key)
            except:
                pass
        except:
            pass
    
    def exit_app(self):
        self.save_data()
        self.root.quit()
        self.root.destroy()
        sys.exit()
    
    def run(self):
        self.root.mainloop()


# ============== START APPLICATION ==============
if __name__ == "__main__":
    app = DesktopWidgetsApp()
    app.run()
