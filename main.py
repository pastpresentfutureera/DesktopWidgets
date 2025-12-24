"""
Desktop Widgets for Windows 11
Beautiful, colorful, draggable, resizable widgets that stick to desktop
Includes: Calendar, To-Do List, Day Planner, Week Planner, Monthly Planner
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font
import calendar
from datetime import datetime, timedelta
import json
import os
import ctypes
from ctypes import wintypes
import sys

# ============== WINDOWS API SETUP ==============
try:
    user32 = ctypes.windll.user32
    GWL_EXSTYLE = -20
    WS_EX_TOOLWINDOW = 0x00000080
    WS_EX_APPWINDOW = 0x00040000
    HWND_BOTTOM = 1
    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOACTIVATE = 0x0010
except:
    pass

# ============== COLOR THEMES ==============
THEMES = {
    "🌸 Pastel Pink": {
        "bg": "#FFF0F5",
        "header": "#FFB6C1",
        "accent": "#FF69B4",
        "text": "#4A4A4A",
        "button": "#FFC0CB",
        "entry": "#FFFFFF",
        "border": "#FFB6C1"
    },
    "🌊 Pastel Blue": {
        "bg": "#F0F8FF",
        "header": "#87CEEB",
        "accent": "#4169E1",
        "text": "#2F4F4F",
        "button": "#B0E0E6",
        "entry": "#FFFFFF",
        "border": "#87CEEB"
    },
    "🌿 Pastel Green": {
        "bg": "#F0FFF0",
        "header": "#90EE90",
        "accent": "#32CD32",
        "text": "#2F4F4F",
        "button": "#98FB98",
        "entry": "#FFFFFF",
        "border": "#90EE90"
    },
    "🍇 Pastel Purple": {
        "bg": "#F8F0FF",
        "header": "#DDA0DD",
        "accent": "#9370DB",
        "text": "#4A4A4A",
        "button": "#E6E6FA",
        "entry": "#FFFFFF",
        "border": "#DDA0DD"
    },
    "🌻 Pastel Yellow": {
        "bg": "#FFFEF0",
        "header": "#F0E68C",
        "accent": "#DAA520",
        "text": "#4A4A4A",
        "button": "#FAFAD2",
        "entry": "#FFFFFF",
        "border": "#F0E68C"
    },
    "🍑 Pastel Orange": {
        "bg": "#FFF5EE",
        "header": "#FFDAB9",
        "accent": "#FF8C00",
        "text": "#4A4A4A",
        "button": "#FFE4B5",
        "entry": "#FFFFFF",
        "border": "#FFDAB9"
    },
    "🌺 Pastel Coral": {
        "bg": "#FFF0EE",
        "header": "#F08080",
        "accent": "#CD5C5C",
        "text": "#4A4A4A",
        "button": "#FFA07A",
        "entry": "#FFFFFF",
        "border": "#F08080"
    },
    "🐬 Pastel Cyan": {
        "bg": "#F0FFFF",
        "header": "#AFEEEE",
        "accent": "#20B2AA",
        "text": "#2F4F4F",
        "button": "#E0FFFF",
        "entry": "#FFFFFF",
        "border": "#AFEEEE"
    }
}

# ============== DATA FILE PATH ==============
DATA_FILE = os.path.join(os.path.expanduser("~"), "desktop_widgets_data.json")

# ============== BASE WIDGET CLASS ==============
class BaseWidget:
    """Base class for all widgets with common functionality"""
    
    def __init__(self, master, title, widget_id, app):
        self.app = app
        self.widget_id = widget_id
        self.master = master
        
        # Create window
        self.window = tk.Toplevel(master)
        self.window.title(title)
        self.window.overrideredirect(True)  # Remove title bar
        
        # Get saved position and size
        pos = app.data.get("widget_positions", {}).get(widget_id, {"x": 100, "y": 100})
        size = app.data.get("widget_sizes", {}).get(widget_id, {"w": 300, "h": 400})
        
        self.window.geometry(f"{size['w']}x{size['h']}+{pos['x']}+{pos['y']}")
        
        # Variables for dragging and resizing
        self.drag_data = {"x": 0, "y": 0, "dragging": False}
        self.resize_data = {"active": False, "edge": None}
        
        # Make window stay on desktop
        self.window.attributes('-topmost', False)
        self.window.attributes('-alpha', 0.95)
        
        # Create main container
        self.container = tk.Frame(self.window, bg=app.theme["bg"], bd=2, relief="solid")
        self.container.pack(fill="both", expand=True)
        
        # Configure border color
        self.container.config(highlightbackground=app.theme["border"], highlightthickness=2)
        
        # Create header
        self.create_header(title)
        
        # Create content area
        self.content = tk.Frame(self.container, bg=app.theme["bg"])
        self.content.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create resize grip
        self.create_resize_grip()
        
        # Bind events
        self.bind_events()
        
        # Try to send to desktop level
        self.window.after(100, self.send_to_desktop)
    
    def create_header(self, title):
        """Create the header with title and controls"""
        self.header = tk.Frame(self.container, bg=self.app.theme["header"], height=35)
        self.header.pack(fill="x", padx=2, pady=2)
        self.header.pack_propagate(False)
        
        # Title label
        self.title_label = tk.Label(
            self.header, 
            text=f" {title}", 
            bg=self.app.theme["header"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 11, "bold"),
            anchor="w"
        )
        self.title_label.pack(side="left", fill="x", expand=True, padx=5)
        
        # Control buttons frame
        controls = tk.Frame(self.header, bg=self.app.theme["header"])
        controls.pack(side="right", padx=2)
        
        # Theme button
        self.theme_btn = tk.Label(
            controls, 
            text="🎨", 
            bg=self.app.theme["header"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 12),
            cursor="hand2"
        )
        self.theme_btn.pack(side="left", padx=2)
        self.theme_btn.bind("<Button-1>", lambda e: self.app.show_theme_selector())
        
        # Minimize button
        self.min_btn = tk.Label(
            controls, 
            text="─", 
            bg=self.app.theme["header"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 12, "bold"),
            cursor="hand2"
        )
        self.min_btn.pack(side="left", padx=2)
        self.min_btn.bind("<Button-1>", self.minimize)
        
        # Close button
        self.close_btn = tk.Label(
            controls, 
            text="✕", 
            bg=self.app.theme["header"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 12),
            cursor="hand2"
        )
        self.close_btn.pack(side="left", padx=2)
        self.close_btn.bind("<Button-1>", self.hide_widget)
        
        # Bind drag events to header
        self.header.bind("<Button-1>", self.start_drag)
        self.header.bind("<B1-Motion>", self.do_drag)
        self.header.bind("<ButtonRelease-1>", self.stop_drag)
        self.title_label.bind("<Button-1>", self.start_drag)
        self.title_label.bind("<B1-Motion>", self.do_drag)
        self.title_label.bind("<ButtonRelease-1>", self.stop_drag)
    
    def create_resize_grip(self):
        """Create resize grip at bottom-right corner"""
        self.resize_grip = tk.Label(
            self.container,
            text="⋱",
            bg=self.app.theme["bg"],
            fg=self.app.theme["accent"],
            font=("Segoe UI", 14),
            cursor="size_nw_se"
        )
        self.resize_grip.place(relx=1.0, rely=1.0, anchor="se")
        
        self.resize_grip.bind("<Button-1>", self.start_resize)
        self.resize_grip.bind("<B1-Motion>", self.do_resize)
        self.resize_grip.bind("<ButtonRelease-1>", self.stop_resize)
    
    def bind_events(self):
        """Bind common events"""
        self.window.bind("<FocusIn>", lambda e: self.window.after(10, self.send_to_desktop))
    
    def start_drag(self, event):
        """Start dragging the widget"""
        self.drag_data["x"] = event.x_root - self.window.winfo_x()
        self.drag_data["y"] = event.y_root - self.window.winfo_y()
        self.drag_data["dragging"] = True
    
    def do_drag(self, event):
        """Handle drag motion"""
        if self.drag_data["dragging"]:
            x = event.x_root - self.drag_data["x"]
            y = event.y_root - self.drag_data["y"]
            self.window.geometry(f"+{x}+{y}")
    
    def stop_drag(self, event):
        """Stop dragging and save position"""
        self.drag_data["dragging"] = False
        self.save_position()
    
    def start_resize(self, event):
        """Start resizing the widget"""
        self.resize_data["active"] = True
        self.resize_data["x"] = event.x_root
        self.resize_data["y"] = event.y_root
        self.resize_data["width"] = self.window.winfo_width()
        self.resize_data["height"] = self.window.winfo_height()
    
    def do_resize(self, event):
        """Handle resize motion"""
        if self.resize_data["active"]:
            dx = event.x_root - self.resize_data["x"]
            dy = event.y_root - self.resize_data["y"]
            new_width = max(200, self.resize_data["width"] + dx)
            new_height = max(150, self.resize_data["height"] + dy)
            self.window.geometry(f"{new_width}x{new_height}")
    
    def stop_resize(self, event):
        """Stop resizing and save size"""
        self.resize_data["active"] = False
        self.save_size()
    
    def save_position(self):
        """Save widget position to data"""
        if "widget_positions" not in self.app.data:
            self.app.data["widget_positions"] = {}
        self.app.data["widget_positions"][self.widget_id] = {
            "x": self.window.winfo_x(),
            "y": self.window.winfo_y()
        }
        self.app.save_data()
    
    def save_size(self):
        """Save widget size to data"""
        if "widget_sizes" not in self.app.data:
            self.app.data["widget_sizes"] = {}
        self.app.data["widget_sizes"][self.widget_id] = {
            "w": self.window.winfo_width(),
            "h": self.window.winfo_height()
        }
        self.app.save_data()
    
    def send_to_desktop(self):
        """Send window to desktop level (behind other windows)"""
        try:
            hwnd = ctypes.windll.user32.GetParent(self.window.winfo_id())
            ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            )
        except:
            pass
    
    def minimize(self, event=None):
        """Minimize the widget"""
        self.window.withdraw()
        self.window.after(100, self.window.deiconify)
    
    def hide_widget(self, event=None):
        """Hide the widget"""
        self.window.withdraw()
        if "hidden_widgets" not in self.app.data:
            self.app.data["hidden_widgets"] = []
        if self.widget_id not in self.app.data["hidden_widgets"]:
            self.app.data["hidden_widgets"].append(self.widget_id)
        self.app.save_data()
    
    def show_widget(self):
        """Show the widget"""
        self.window.deiconify()
        if "hidden_widgets" in self.app.data and self.widget_id in self.app.data["hidden_widgets"]:
            self.app.data["hidden_widgets"].remove(self.widget_id)
        self.app.save_data()
    
    def update_theme(self):
        """Update widget colors based on current theme"""
        theme = self.app.theme
        self.container.config(bg=theme["bg"], highlightbackground=theme["border"])
        self.header.config(bg=theme["header"])
        self.title_label.config(bg=theme["header"], fg=theme["text"])
        self.theme_btn.config(bg=theme["header"], fg=theme["text"])
        self.min_btn.config(bg=theme["header"], fg=theme["text"])
        self.close_btn.config(bg=theme["header"], fg=theme["text"])
        self.content.config(bg=theme["bg"])
        self.resize_grip.config(bg=theme["bg"], fg=theme["accent"])


# ============== CALENDAR WIDGET ==============
class CalendarWidget(BaseWidget):
    """Calendar widget with event notes"""
    
    def __init__(self, master, app):
        super().__init__(master, "📅 Calendar", "calendar", app)
        
        self.current_date = datetime.now()
        self.selected_date = None
        
        self.create_content()
    
    def create_content(self):
        """Create calendar content"""
        # Navigation frame
        nav_frame = tk.Frame(self.content, bg=self.app.theme["bg"])
        nav_frame.pack(fill="x", pady=5)
        
        self.prev_btn = tk.Button(
            nav_frame, 
            text="◀", 
            command=self.prev_month,
            bg=self.app.theme["button"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 12),
            bd=0,
            cursor="hand2"
        )
        self.prev_btn.pack(side="left", padx=5)
        
        self.month_label = tk.Label(
            nav_frame,
            text="",
            bg=self.app.theme["bg"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 12, "bold")
        )
        self.month_label.pack(side="left", fill="x", expand=True)
        
        self.next_btn = tk.Button(
            nav_frame, 
            text="▶", 
            command=self.next_month,
            bg=self.app.theme["button"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 12),
            bd=0,
            cursor="hand2"
        )
        self.next_btn.pack(side="right", padx=5)
        
        # Days header
        days_frame = tk.Frame(self.content, bg=self.app.theme["bg"])
        days_frame.pack(fill="x", pady=2)
        
        self.day_labels = []
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            lbl = tk.Label(
                days_frame,
                text=day,
                bg=self.app.theme["header"],
                fg=self.app.theme["text"],
                font=("Segoe UI", 9, "bold"),
                width=4
            )
            lbl.pack(side="left", expand=True, fill="x", padx=1)
            self.day_labels.append(lbl)
        
        # Calendar grid
        self.cal_frame = tk.Frame(self.content, bg=self.app.theme["bg"])
        self.cal_frame.pack(fill="both", expand=True, pady=2)
        
        self.date_buttons = []
        for row in range(6):
            row_buttons = []
            for col in range(7):
                btn = tk.Button(
                    self.cal_frame,
                    text="",
                    width=4,
                    height=1,
                    bg=self.app.theme["entry"],
                    fg=self.app.theme["text"],
                    font=("Segoe UI", 9),
                    bd=1,
                    relief="flat",
                    cursor="hand2"
                )
                btn.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
                btn.bind("<Button-1>", lambda e, r=row, c=col: self.select_date(r, c))
                row_buttons.append(btn)
            self.date_buttons.append(row_buttons)
        
        # Configure grid weights
        for i in range(7):
            self.cal_frame.columnconfigure(i, weight=1)
        for i in range(6):
            self.cal_frame.rowconfigure(i, weight=1)
        
        # Event section
        event_frame = tk.Frame(self.content, bg=self.app.theme["bg"])
        event_frame.pack(fill="x", pady=5)
        
        self.event_label = tk.Label(
            event_frame,
            text="📝 Events:",
            bg=self.app.theme["bg"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 10, "bold")
        )
        self.event_label.pack(anchor="w")
        
        # Event text area
        self.event_text = tk.Text(
            event_frame,
            height=3,
            bg=self.app.theme["entry"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 10),
            bd=1,
            relief="solid",
            wrap="word"
        )
        self.event_text.pack(fill="x", pady=2)
        self.event_text.bind("<KeyRelease>", self.save_event)
        
        self.update_calendar()
    
    def update_calendar(self):
        """Update calendar display"""
        year = self.current_date.year
        month = self.current_date.month
        
        self.month_label.config(text=f"{calendar.month_name[month]} {year}")
        
        # Get calendar data
        cal = calendar.monthcalendar(year, month)
        
        today = datetime.now()
        
        for row in range(6):
            for col in range(7):
                btn = self.date_buttons[row][col]
                if row < len(cal) and cal[row][col] != 0:
                    day = cal[row][col]
                    btn.config(text=str(day))
                    
                    date_key = f"{year}-{month:02d}-{day:02d}"
                    
                    # Check if it's today
                    if year == today.year and month == today.month and day == today.day:
                        btn.config(bg=self.app.theme["accent"], fg="white")
                    # Check if has event
                    elif date_key in self.app.data.get("calendar_events", {}):
                        btn.config(bg=self.app.theme["header"], fg=self.app.theme["text"])
                    else:
                        btn.config(bg=self.app.theme["entry"], fg=self.app.theme["text"])
                    
                    btn.config(state="normal")
                else:
                    btn.config(text="", bg=self.app.theme["bg"], state="disabled")
    
    def select_date(self, row, col):
        """Handle date selection"""
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        if row < len(cal) and cal[row][col] != 0:
            day = cal[row][col]
            self.selected_date = f"{self.current_date.year}-{self.current_date.month:02d}-{day:02d}"
            
            # Load event for selected date
            events = self.app.data.get("calendar_events", {})
            event_text = events.get(self.selected_date, "")
            
            self.event_text.delete("1.0", "end")
            self.event_text.insert("1.0", event_text)
            self.event_label.config(text=f"📝 Events for {self.selected_date}:")
    
    def save_event(self, event=None):
        """Save event for selected date"""
        if self.selected_date:
            if "calendar_events" not in self.app.data:
                self.app.data["calendar_events"] = {}
            
            event_text = self.event_text.get("1.0", "end-1c")
            if event_text.strip():
                self.app.data["calendar_events"][self.selected_date] = event_text
            elif self.selected_date in self.app.data["calendar_events"]:
                del self.app.data["calendar_events"][self.selected_date]
            
            self.app.save_data()
            self.update_calendar()
    
    def prev_month(self):
        """Go to previous month"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
    
    def next_month(self):
        """Go to next month"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()
    
    def update_theme(self):
        """Update calendar theme"""
        super().update_theme()
        theme = self.app.theme
        
        self.prev_btn.config(bg=theme["button"], fg=theme["text"])
        self.next_btn.config(bg=theme["button"], fg=theme["text"])
        self.month_label.config(bg=theme["bg"], fg=theme["text"])
        
        for lbl in self.day_labels:
            lbl.config(bg=theme["header"], fg=theme["text"])
        
        self.cal_frame.config(bg=theme["bg"])
        self.event_label.config(bg=theme["bg"], fg=theme["text"])
        self.event_text.config(bg=theme["entry"], fg=theme["text"])
        
        self.update_calendar()


# ============== TODO LIST WIDGET ==============
class TodoWidget(BaseWidget):
    """To-Do List widget"""
    
    def __init__(self, master, app):
        super().__init__(master, "✅ To-Do List", "todo", app)
        self.create_content()
    
    def create_content(self):
        """Create todo list content"""
        # Add task frame
        add_frame = tk.Frame(self.content, bg=self.app.theme["bg"])
        add_frame.pack(fill="x", pady=5)
        
        self.task_entry = tk.Entry(
            add_frame,
            bg=self.app.theme["entry"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 11),
            bd=1,
            relief="solid"
        )
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.task_entry.bind("<Return>", self.add_task)
        
        self.add_btn = tk.Button(
            add_frame,
            text="➕ Add",
            command=self.add_task,
            bg=self.app.theme["button"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 10),
            bd=0,
            cursor="hand2"
        )
        self.add_btn.pack(side="right")
        
        # Task list with scrollbar
        list_frame = tk.Frame(self.content, bg=self.app.theme["bg"])
        list_frame.pack(fill="both", expand=True, pady=5)
        
        self.scrollbar = tk.Scrollbar(list_frame)
        self.scrollbar.pack(side="right", fill="y")
        
        self.task_canvas = tk.Canvas(
            list_frame,
            bg=self.app.theme["bg"],
            highlightthickness=0,
            yscrollcommand=self.scrollbar.set
        )
        self.task_canvas.pack(side="left", fill="both", expand=True)
        
        self.scrollbar.config(command=self.task_canvas.yview)
        
        self.task_container = tk.Frame(self.task_canvas, bg=self.app.theme["bg"])
        self.task_canvas.create_window((0, 0), window=self.task_container, anchor="nw")
        
        self.task_container.bind("<Configure>", 
            lambda e: self.task_canvas.configure(scrollregion=self.task_canvas.bbox("all")))
        
        # Load existing tasks
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from data"""
        # Clear existing
        for widget in self.task_container.winfo_children():
            widget.destroy()
        
        tasks = self.app.data.get("todos", [])
        
        for i, task in enumerate(tasks):
            self.create_task_row(i, task)
    
    def create_task_row(self, index, task):
        """Create a task row"""
        row = tk.Frame(self.task_container, bg=self.app.theme["entry"], pady=2)
        row.pack(fill="x", pady=2, padx=2)
        
        # Checkbox
        var = tk.BooleanVar(value=task.get("done", False))
        cb = tk.Checkbutton(
            row,
            variable=var,
            bg=self.app.theme["entry"],
            activebackground=self.app.theme["entry"],
            command=lambda: self.toggle_task(index, var.get())
        )
        cb.pack(side="left")
        
        # Task text
        text = task.get("text", "")
        lbl = tk.Label(
            row,
            text=text,
            bg=self.app.theme["entry"],
            fg=self.app.theme["text"] if not task.get("done") else "#999999",
            font=("Segoe UI", 10, "overstrike" if task.get("done") else "normal"),
            anchor="w"
        )
        lbl.pack(side="left", fill="x", expand=True, padx=5)
        
        # Delete button
        del_btn = tk.Label(
            row,
            text="🗑",
            bg=self.app.theme["entry"],
            fg="#FF6B6B",
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        del_btn.pack(side="right", padx=5)
        del_btn.bind("<Button-1>", lambda e, idx=index: self.delete_task(idx))
    
    def add_task(self, event=None):
        """Add a new task"""
        text = self.task_entry.get().strip()
        if text:
            if "todos" not in self.app.data:
                self.app.data["todos"] = []
            
            self.app.data["todos"].append({"text": text, "done": False})
            self.app.save_data()
            
            self.task_entry.delete(0, "end")
            self.load_tasks()
    
    def toggle_task(self, index, done):
        """Toggle task completion"""
        if "todos" in self.app.data and index < len(self.app.data["todos"]):
            self.app.data["todos"][index]["done"] = done
            self.app.save_data()
            self.load_tasks()
    
    def delete_task(self, index):
        """Delete a task"""
        if "todos" in self.app.data and index < len(self.app.data["todos"]):
            del self.app.data["todos"][index]
            self.app.save_data()
            self.load_tasks()
    
    def update_theme(self):
        """Update todo theme"""
        super().update_theme()
        theme = self.app.theme
        
        self.task_entry.config(bg=theme["entry"], fg=theme["text"])
        self.add_btn.config(bg=theme["button"], fg=theme["text"])
        self.task_canvas.config(bg=theme["bg"])
        self.task_container.config(bg=theme["bg"])
        
        self.load_tasks()


# ============== DAY PLANNER WIDGET ==============
class DayPlannerWidget(BaseWidget):
    """Day Planner widget with hourly slots"""
    
    def __init__(self, master, app):
        super().__init__(master, "📆 Day Planner", "day_planner", app)
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.create_content()
    
    def create_content(self):
        """Create day planner content"""
        # Date navigation
        nav_frame = tk.Frame(self.content, bg=self.app.theme["bg"])
        nav_frame.pack(fill="x", pady=5)
        
        self.prev_btn = tk.Button(
            nav_frame,
            text="◀",
            command=self.prev_day,
            bg=self.app.theme["button"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 10),
            bd=0,
            cursor="hand2"
        )
        self.prev_btn.pack(side="left")
        
        self.date_label = tk.Label(
            nav_frame,
            text=self.current_date,
            bg=self.app.theme["bg"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 11, "bold")
        )
        self.date_label.pack(side="left", fill="x", expand=True)
        
        self.next_btn = tk.Button(
            nav_frame,
            text="▶",
            command=self.next_day,
            bg=self.app.theme["button"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 10),
            bd=0,
            cursor="hand2"
        )
        self.next_btn.pack(side="right")
        
        # Scrollable time slots
        scroll_frame = tk.Frame(self.content, bg=self.app.theme["bg"])
        scroll_frame.pack(fill="both", expand=True)
        
        self.scrollbar = tk.Scrollbar(scroll_frame)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas = tk.Canvas(
            scroll_frame,
            bg=self.app.theme["bg"],
            highlightthickness=0,
            yscrollcommand=self.scrollbar.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.scrollbar.config(command=self.canvas.yview)
        
        self.slots_frame = tk.Frame(self.canvas, bg=self.app.theme["bg"])
        self.canvas.create_window((0, 0), window=self.slots_frame, anchor="nw")
        
        self.time_entries = {}
        
        # Create time slots (6 AM to 11 PM)
        for hour in range(6, 24):
            self.create_time_slot(hour)
        
        self.slots_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.load_day_data()
    
    def create_time_slot(self, hour):
        """Create a time slot row"""
        row = tk.Frame(self.slots_frame, bg=self.app.theme["bg"])
        row.pack(fill="x", pady=1)
        
        # Time label
        time_str = f"{hour:02d}:00"
        time_lbl = tk.Label(
            row,
            text=time_str,
            bg=self.app.theme["header"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 9),
            width=6
        )
        time_lbl.pack(side="left", padx=2)
        
        # Entry for task
        entry = tk.Entry(
            row,
            bg=self.app.theme["entry"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 10),
            bd=1,
            relief="solid"
        )
        entry.pack(side="left", fill="x", expand=True, padx=2)
        entry.bind("<KeyRelease>", lambda e, h=hour: self.save_slot(h))
        
        self.time_entries[hour] = entry
    
    def load_day_data(self):
        """Load data for current day"""
        day_data = self.app.data.get("day_planner", {}).get(self.current_date, {})
        
        for hour, entry in self.time_entries.items():
            entry.delete(0, "end")
            if str(hour) in day_data:
                entry.insert(0, day_data[str(hour)])
        
        self.date_label.config(text=self.current_date)
    
    def save_slot(self, hour):
        """Save a time slot"""
        if "day_planner" not in self.app.data:
            self.app.data["day_planner"] = {}
        
        if self.current_date not in self.app.data["day_planner"]:
            self.app.data["day_planner"][self.current_date] = {}
        
        text = self.time_entries[hour].get()
        if text:
            self.app.data["day_planner"][self.current_date][str(hour)] = text
        elif str(hour) in self.app.data["day_planner"][self.current_date]:
            del self.app.data["day_planner"][self.current_date][str(hour)]
        
        self.app.save_data()
    
    def prev_day(self):
        """Go to previous day"""
        date = datetime.strptime(self.current_date, "%Y-%m-%d")
        date -= timedelta(days=1)
        self.current_date = date.strftime("%Y-%m-%d")
        self.load_day_data()
    
    def next_day(self):
        """Go to next day"""
        date = datetime.strptime(self.current_date, "%Y-%m-%d")
        date += timedelta(days=1)
        self.current_date = date.strftime("%Y-%m-%d")
        self.load_day_data()
    
    def update_theme(self):
        """Update day planner theme"""
        super().update_theme()
        theme = self.app.theme
        
        self.prev_btn.config(bg=theme["button"], fg=theme["text"])
        self.next_btn.config(bg=theme["button"], fg=theme["text"])
        self.date_label.config(bg=theme["bg"], fg=theme["text"])
        self.canvas.config(bg=theme["bg"])
        self.slots_frame.config(bg=theme["bg"])
        
        for widget in self.slots_frame.winfo_children():
            widget.config(bg=theme["bg"])
            for child in widget.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(bg=theme["header"], fg=theme["text"])
                elif isinstance(child, tk.Entry):
                    child.config(bg=theme["entry"], fg=theme["text"])


# ============== WEEK PLANNER WIDGET ==============
class WeekPlannerWidget(BaseWidget):
    """Week Planner widget"""
    
    def __init__(self, master, app):
        super().__init__(master, "📋 Week Planner", "week_planner", app)
        self.current_week_start = self.get_week_start(datetime.now())
        self.create_content()
    
    def get_week_start(self, date):
        """Get Monday of the week"""
        return date - timedelta(days=date.weekday())
    
    def create_content(self):
        """Create week planner content"""
        # Navigation
        nav_frame = tk.Frame(self.content, bg=self.app.theme["bg"])
        nav_frame.pack(fill="x", pady=5)
        
        self.prev_btn = tk.Button(
            nav_frame,
            text="◀ Prev Week",
            command=self.prev_week,
            bg=self.app.theme["button"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 9),
            bd=0,
            cursor="hand2"
        )
        self.prev_btn.pack(side="left")
        
        self.week_label = tk.Label(
            nav_frame,
            text="",
            bg=self.app.theme["bg"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 10, "bold")
        )
        self.week_label.pack(side="left", fill="x", expand=True)
        
        self.next_btn = tk.Button(
            nav_frame,
            text="Next Week ▶",
            command=self.next_week,
            bg=self.app.theme["button"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 9),
            bd=0,
            cursor="hand2"
        )
        self.next_btn.pack(side="right")
        
        # Days container with scroll
        scroll_frame = tk.Frame(self.content, bg=self.app.theme["bg"])
        scroll_frame.pack(fill="both", expand=True)
        
        self.scrollbar = tk.Scrollbar(scroll_frame)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas = tk.Canvas(
            scroll_frame,
            bg=self.app.theme["bg"],
            highlightthickness=0,
            yscrollcommand=self.scrollbar.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.scrollbar.config(command=self.canvas.yview)
        
        self.days_frame = tk.Frame(self.canvas, bg=self.app.theme["bg"])
        self.canvas.create_window((0, 0), window=self.days_frame, anchor="nw")
        
        self.day_entries = {}
        
        # Create day sections
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i, day in enumerate(days):
            self.create_day_section(i, day)
        
        self.days_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.load_week_data()
    
    def create_day_section(self, index, day_name):
        """Create a day section"""
        frame = tk.Frame(self.days_frame, bg=self.app.theme["entry"], pady=3)
        frame.pack(fill="x", pady=2, padx=2)
        
        # Day header
        header = tk.Label(
            frame,
            text=day_name,
            bg=self.app.theme["header"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 10, "bold"),
            anchor="w"
        )
        header.pack(fill="x", padx=2, pady=2)
        
        # Text area for tasks
        text = tk.Text(
            frame,
            height=3,
            bg=self.app.theme["entry"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 10),
            bd=0,
            wrap="word"
        )
        text.pack(fill="x", padx=5, pady=2)
        text.bind("<KeyRelease>", lambda e, idx=index: self.save_day(idx))
        
        self.day_entries[index] = text
    
    def load_week_data(self):
        """Load data for current week"""
        week_key = self.current_week_start.strftime("%Y-%m-%d")
        week_data = self.app.data.get("week_planner", {}).get(week_key, {})
        
        week_end = self.current_week_start + timedelta(days=6)
        self.week_label.config(
            text=f"{self.current_week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
        )
        
        for i, text_widget in self.day_entries.items():
            text_widget.delete("1.0", "end")
            if str(i) in week_data:
                text_widget.insert("1.0", week_data[str(i)])
    
    def save_day(self, day_index):
        """Save day data"""
        if "week_planner" not in self.app.data:
            self.app.data["week_planner"] = {}
        
        week_key = self.current_week_start.strftime("%Y-%m-%d")
        
        if week_key not in self.app.data["week_planner"]:
            self.app.data["week_planner"][week_key] = {}
        
        text = self.day_entries[day_index].get("1.0", "end-1c")
        if text.strip():
            self.app.data["week_planner"][week_key][str(day_index)] = text
        elif str(day_index) in self.app.data["week_planner"][week_key]:
            del self.app.data["week_planner"][week_key][str(day_index)]
        
        self.app.save_data()
    
    def prev_week(self):
        """Go to previous week"""
        self.current_week_start -= timedelta(days=7)
        self.load_week_data()
    
    def next_week(self):
        """Go to next week"""
        self.current_week_start += timedelta(days=7)
        self.load_week_data()
    
    def update_theme(self):
        """Update week planner theme"""
        super().update_theme()
        theme = self.app.theme
        
        self.prev_btn.config(bg=theme["button"], fg=theme["text"])
        self.next_btn.config(bg=theme["button"], fg=theme["text"])
        self.week_label.config(bg=theme["bg"], fg=theme["text"])
        self.canvas.config(bg=theme["bg"])
        self.days_frame.config(bg=theme["bg"])


# ============== MONTHLY PLANNER WIDGET ==============
class MonthlyPlannerWidget(BaseWidget):
    """Monthly Planner/Goals widget"""
    
    def __init__(self, master, app):
        super().__init__(master, "🎯 Monthly Planner", "monthly_planner", app)
        self.current_date = datetime.now()
        self.create_content()
    
    def create_content(self):
        """Create monthly planner content"""
        # Navigation
        nav_frame = tk.Frame(self.content, bg=self.app.theme["bg"])
        nav_frame.pack(fill="x", pady=5)
        
        self.prev_btn = tk.Button(
            nav_frame,
            text="◀",
            command=self.prev_month,
            bg=self.app.theme["button"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 10),
            bd=0,
            cursor="hand2"
        )
        self.prev_btn.pack(side="left")
        
        self.month_label = tk.Label(
            nav_frame,
            text="",
            bg=self.app.theme["bg"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 12, "bold")
        )
        self.month_label.pack(side="left", fill="x", expand=True)
        
        self.next_btn = tk.Button(
            nav_frame,
            text="▶",
            command=self.next_month,
            bg=self.app.theme["button"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 10),
            bd=0,
            cursor="hand2"
        )
        self.next_btn.pack(side="right")
        
        # Sections
        scroll_frame = tk.Frame(self.content, bg=self.app.theme["bg"])
        scroll_frame.pack(fill="both", expand=True)
        
        self.scrollbar = tk.Scrollbar(scroll_frame)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas = tk.Canvas(
            scroll_frame,
            bg=self.app.theme["bg"],
            highlightthickness=0,
            yscrollcommand=self.scrollbar.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.scrollbar.config(command=self.canvas.yview)
        
        self.sections_frame = tk.Frame(self.canvas, bg=self.app.theme["bg"])
        self.canvas.create_window((0, 0), window=self.sections_frame, anchor="nw")
        
        self.section_texts = {}
        
        # Create sections
        sections = [
            ("🎯 Goals", "goals"),
            ("📝 Key Tasks", "tasks"),
            ("💡 Ideas", "ideas"),
            ("📊 Review", "review"),
            ("✨ Notes", "notes")
        ]
        
        for title, key in sections:
            self.create_section(title, key)
        
        self.sections_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.load_month_data()
    
    def create_section(self, title, key):
        """Create a section"""
        frame = tk.Frame(self.sections_frame, bg=self.app.theme["entry"])
        frame.pack(fill="x", pady=3, padx=2)
        
        # Section header
        header = tk.Label(
            frame,
            text=title,
            bg=self.app.theme["header"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 10, "bold"),
            anchor="w"
        )
        header.pack(fill="x", padx=2, pady=2)
        
        # Text area
        text = tk.Text(
            frame,
            height=4,
            bg=self.app.theme["entry"],
            fg=self.app.theme["text"],
            font=("Segoe UI", 10),
            bd=0,
            wrap="word"
        )
        text.pack(fill="x", padx=5, pady=2)
        text.bind("<KeyRelease>", lambda e, k=key: self.save_section(k))
        
        self.section_texts[key] = text
    
    def load_month_data(self):
        """Load data for current month"""
        month_key = self.current_date.strftime("%Y-%m")
        month_data = self.app.data.get("monthly_planner", {}).get(month_key, {})
        
        self.month_label.config(
            text=f"{calendar.month_name[self.current_date.month]} {self.current_date.year}"
        )
        
        for key, text_widget in self.section_texts.items():
            text_widget.delete("1.0", "end")
            if key in month_data:
                text_widget.insert("1.0", month_data[key])
    
    def save_section(self, section_key):
        """Save section data"""
        if "monthly_planner" not in self.app.data:
            self.app.data["monthly_planner"] = {}
        
        month_key = self.current_date.strftime("%Y-%m")
        
        if month_key not in self.app.data["monthly_planner"]:
            self.app.data["monthly_planner"][month_key] = {}
        
        text = self.section_texts[section_key].get("1.0", "end-1c")
        if text.strip():
            self.app.data["monthly_planner"][month_key][section_key] = text
        elif section_key in self.app.data["monthly_planner"][month_key]:
            del self.app.data["monthly_planner"][month_key][section_key]
        
        self.app.save_data()
    
    def prev_month(self):
        """Go to previous month"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.load_month_data()
    
    def next_month(self):
        """Go to next month"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.load_month_data()
    
    def update_theme(self):
        """Update monthly planner theme"""
        super().update_theme()
        theme = self.app.theme
        
        self.prev_btn.config(bg=theme["button"], fg=theme["text"])
        self.next_btn.config(bg=theme["button"], fg=theme["text"])
        self.month_label.config(bg=theme["bg"], fg=theme["text"])
        self.canvas.config(bg=theme["bg"])
        self.sections_frame.config(bg=theme["bg"])


# ============== MAIN APPLICATION ==============
class DesktopWidgetsApp:
    """Main application managing all widgets"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window
        
        # Load data
        self.load_data()
        
        # Set theme
        theme_name = self.data.get("theme", "🌊 Pastel Blue")
        self.theme = THEMES.get(theme_name, THEMES["🌊 Pastel Blue"])
        
        # Create widgets
        self.widgets = {}
        self.create_widgets()
        
        # Create system tray menu
        self.create_tray_menu()
        
        # Setup auto-start
        self.setup_autostart()
    
    def load_data(self):
        """Load saved data"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except:
                self.data = self.get_default_data()
        else:
            self.data = self.get_default_data()
    
    def get_default_data(self):
        """Get default data structure"""
        return {
            "theme": "🌊 Pastel Blue",
            "calendar_events": {},
            "todos": [],
            "day_planner": {},
            "week_planner": {},
            "monthly_planner": {},
            "widget_positions": {
                "calendar": {"x": 50, "y": 50},
                "todo": {"x": 400, "y": 50},
                "day_planner": {"x": 750, "y": 50},
                "week_planner": {"x": 50, "y": 500},
                "monthly_planner": {"x": 400, "y": 500}
            },
            "widget_sizes": {
                "calendar": {"w": 320, "h": 400},
                "todo": {"w": 300, "h": 400},
                "day_planner": {"w": 300, "h": 400},
                "week_planner": {"w": 320, "h": 350},
                "monthly_planner": {"w": 320, "h": 400}
            },
            "hidden_widgets": []
        }
    
    def save_data(self):
        """Save data to file"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def create_widgets(self):
        """Create all widgets"""
        hidden = self.data.get("hidden_widgets", [])
        
        # Calendar Widget
        self.widgets["calendar"] = CalendarWidget(self.root, self)
        if "calendar" in hidden:
            self.widgets["calendar"].window.withdraw()
        
        # Todo Widget
        self.widgets["todo"] = TodoWidget(self.root, self)
        if "todo" in hidden:
            self.widgets["todo"].window.withdraw()
        
        # Day Planner Widget
        self.widgets["day_planner"] = DayPlannerWidget(self.root, self)
        if "day_planner" in hidden:
            self.widgets["day_planner"].window.withdraw()
        
        # Week Planner Widget
        self.widgets["week_planner"] = WeekPlannerWidget(self.root, self)
        if "week_planner" in hidden:
            self.widgets["week_planner"].window.withdraw()
        
        # Monthly Planner Widget
        self.widgets["monthly_planner"] = MonthlyPlannerWidget(self.root, self)
        if "monthly_planner" in hidden:
            self.widgets["monthly_planner"].window.withdraw()
    
    def create_tray_menu(self):
        """Create a control panel window"""
        self.control_panel = tk.Toplevel(self.root)
        self.control_panel.title("🎮 Widget Control Panel")
        self.control_panel.geometry("280x400")
        self.control_panel.resizable(False, False)
        
        # Make it stay on top
        self.control_panel.attributes('-topmost', True)
        
        # Style
        self.control_panel.configure(bg=self.theme["bg"])
        
        # Title
        title = tk.Label(
            self.control_panel,
            text="🖥️ Desktop Widgets",
            bg=self.theme["header"],
            fg=self.theme["text"],
            font=("Segoe UI", 14, "bold"),
            pady=10
        )
        title.pack(fill="x")
        
        # Widgets toggle section
        toggle_frame = tk.LabelFrame(
            self.control_panel,
            text="Show/Hide Widgets",
            bg=self.theme["bg"],
            fg=self.theme["text"],
            font=("Segoe UI", 10, "bold")
        )
        toggle_frame.pack(fill="x", padx=10, pady=10)
        
        widget_names = {
            "calendar": "📅 Calendar",
            "todo": "✅ To-Do List",
            "day_planner": "📆 Day Planner",
            "week_planner": "📋 Week Planner",
            "monthly_planner": "🎯 Monthly Planner"
        }
        
        self.widget_vars = {}
        for widget_id, widget_name in widget_names.items():
            var = tk.BooleanVar(value=widget_id not in self.data.get("hidden_widgets", []))
            self.widget_vars[widget_id] = var
            
            cb = tk.Checkbutton(
                toggle_frame,
                text=widget_name,
                variable=var,
                bg=self.theme["bg"],
                fg=self.theme["text"],
                font=("Segoe UI", 10),
                activebackground=self.theme["bg"],
                selectcolor=self.theme["entry"],
                command=lambda wid=widget_id: self.toggle_widget(wid)
            )
            cb.pack(anchor="w", padx=10, pady=2)
        
        # Theme section
        theme_frame = tk.LabelFrame(
            self.control_panel,
            text="🎨 Color Theme",
            bg=self.theme["bg"],
            fg=self.theme["text"],
            font=("Segoe UI", 10, "bold")
        )
        theme_frame.pack(fill="x", padx=10, pady=10)
        
        self.theme_var = tk.StringVar(value=self.data.get("theme", "🌊 Pastel Blue"))
        
        for theme_name in THEMES.keys():
            rb = tk.Radiobutton(
                theme_frame,
                text=theme_name,
                variable=self.theme_var,
                value=theme_name,
                bg=self.theme["bg"],
                fg=self.theme["text"],
                font=("Segoe UI", 9),
                activebackground=self.theme["bg"],
                selectcolor=self.theme["entry"],
                command=self.change_theme
            )
            rb.pack(anchor="w", padx=10)
        
        # Buttons
        btn_frame = tk.Frame(self.control_panel, bg=self.theme["bg"])
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        show_all_btn = tk.Button(
            btn_frame,
            text="👁️ Show All",
            command=self.show_all_widgets,
            bg=self.theme["button"],
            fg=self.theme["text"],
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        show_all_btn.pack(side="left", padx=5)
        
        hide_all_btn = tk.Button(
            btn_frame,
            text="🙈 Hide All",
            command=self.hide_all_widgets,
            bg=self.theme["button"],
            fg=self.theme["text"],
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        hide_all_btn.pack(side="left", padx=5)
        
        exit_btn = tk.Button(
            btn_frame,
            text="❌ Exit",
            command=self.exit_app,
            bg="#FF6B6B",
            fg="white",
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        exit_btn.pack(side="right", padx=5)
        
        # Handle close button - minimize instead of close
        self.control_panel.protocol("WM_DELETE_WINDOW", self.minimize_control_panel)
    
    def minimize_control_panel(self):
        """Minimize control panel to taskbar"""
        self.control_panel.iconify()
    
    def toggle_widget(self, widget_id):
        """Toggle widget visibility"""
        if self.widget_vars[widget_id].get():
            self.widgets[widget_id].show_widget()
        else:
            self.widgets[widget_id].hide_widget()
    
    def show_all_widgets(self):
        """Show all widgets"""
        for widget_id, widget in self.widgets.items():
            widget.show_widget()
            self.widget_vars[widget_id].set(True)
    
    def hide_all_widgets(self):
        """Hide all widgets"""
        for widget_id, widget in self.widgets.items():
            widget.hide_widget()
            self.widget_vars[widget_id].set(False)
    
    def show_theme_selector(self):
        """Bring control panel to front for theme selection"""
        self.control_panel.deiconify()
        self.control_panel.lift()
        self.control_panel.attributes('-topmost', True)
    
    def change_theme(self):
        """Change the color theme"""
        theme_name = self.theme_var.get()
        self.theme = THEMES[theme_name]
        self.data["theme"] = theme_name
        self.save_data()
        
        # Update all widgets
        for widget in self.widgets.values():
            widget.update_theme()
        
        # Update control panel
        self.control_panel.configure(bg=self.theme["bg"])
    
    def setup_autostart(self):
        """Setup auto-start on Windows startup"""
        try:
            import winreg
            
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "DesktopWidgets"
            
            # Get the executable path
            if getattr(sys, 'frozen', False):
                # Running as compiled exe
                exe_path = sys.executable
            else:
                # Running as script
                exe_path = f'pythonw "{os.path.abspath(__file__)}"'
            
            # Add to registry
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
                winreg.CloseKey(key)
            except:
                pass
        except:
            pass
    
    def exit_app(self):
        """Exit the application"""
        self.save_data()
        self.root.quit()
        self.root.destroy()
        sys.exit()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


# ============== ENTRY POINT ==============
if __name__ == "__main__":
    app = DesktopWidgetsApp()
    app.run()
