#!/usr/bin/env python3
#====== Log Viewer/LogViewerGUI.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This code is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@gmail.com.
"""
Log Viewer GUI - Graphical interface for the log viewer application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Dict, List, Optional, Any
import threading
import os
from pathlib import Path
import json

from LogViewer import LogViewer, LogEntry, LogCategory


class LogViewerGUI:
    """Main GUI application for log viewer"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Log Viewer")
        self.root.geometry("1200x800")
        
        # Backend log viewer and tab management
        self.log_viewer: Optional[LogViewer] = None
        self.log_text = None  # Current active tab's text widget
        self.current_file_path: Optional[str] = None
        
        # GUI components
        self.setup_styles()
        self.create_menu()
        self.create_main_layout()
        self.create_toolbar()
        self.create_filter_panel()
        self.create_log_display()
        self.create_status_bar()
        
        # Initialize with default config
        self.load_default_config()
    
    def setup_styles(self):
        """Configure GUI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for log levels
        self.log_colors = {
            'ERROR': '#FF4444',
            'WARNING': '#FF8C00',
            'INFO': '#4CAF50',
            'DEBUG': '#2196F3',
            'TRACE': '#9C27B0'
        }
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Log File", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Open Multiple Files", command=self.open_multiple_files)
        file_menu.add_command(label="Merge Open Files", command=self.merge_open_files)
        file_menu.add_command(label="Open Folder", command=self.open_folder)
        file_menu.add_command(label="Merge Open Folder", command=self.merge_open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Load Config", command=self.load_config_file)
        file_menu.add_separator()
        file_menu.add_command(label="Export Filtered Logs", command=self.export_logs, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", command=self.close_current_tab, accelerator="Ctrl+W")
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self.refresh_display, accelerator="F5")
        view_menu.add_command(label="Clear Filters", command=self.clear_filters, accelerator="Ctrl+R")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-e>', lambda e: self.export_logs())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-w>', lambda e: self.close_current_tab())
        self.root.bind('<F5>', lambda e: self.refresh_display())
        self.root.bind('<Control-r>', lambda e: self.clear_filters())
        self.root.bind('<Control-f>', lambda e: self.focus_search())
    
    def create_main_layout(self):
        """Create main window layout"""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create paned window for resizable panels
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for filters and stats
        self.left_panel = ttk.Frame(self.paned_window, width=300)
        self.paned_window.add(self.left_panel, weight=1)
        
        # Right panel for tabbed log display
        self.right_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_panel, weight=3)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Track open tabs and their data
        self.tabs = {}  # tab_id -> {'frame': frame, 'log_viewer': LogViewer, 'log_text': widget}
        self.tab_counter = 0
        self.active_tab = None
    
    def create_toolbar(self):
        """Create toolbar with common actions"""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # File operations
        ttk.Button(toolbar, text="Open File", command=self.open_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Refresh", command=self.refresh_display).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # View options
        self.show_detailed = tk.BooleanVar(value=False)
        ttk.Checkbutton(toolbar, text="Detailed View", variable=self.show_detailed, 
                       command=self.refresh_display).pack(side=tk.LEFT, padx=(0, 5))
        
        # JSON/XML display filter
        ttk.Label(toolbar, text="Display:").pack(side=tk.LEFT, padx=(10, 2))
        self.json_xml_filter_var = tk.StringVar(value="Show All")
        json_xml_combo = ttk.Combobox(toolbar, textvariable=self.json_xml_filter_var,
                                      values=["Show All", "Only JSON/XML", "Hide JSON/XML"],
                                      state="readonly", width=15)
        json_xml_combo.pack(side=tk.LEFT, padx=(0, 5))
        json_xml_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_display())
        
        # Log limit
        ttk.Label(toolbar, text="Limit:").pack(side=tk.LEFT, padx=(10, 2))
        self.limit_var = tk.StringVar(value="100")
        limit_combo = ttk.Combobox(toolbar, textvariable=self.limit_var, width=8,
                                  values=["50", "100", "500", "1000", "All"])
        limit_combo.pack(side=tk.LEFT, padx=(0, 5))
        limit_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_display())
    
    def create_filter_panel(self):
        """Create filtering panel with tabs"""
        # Create notebook for filter tabs
        self.filter_notebook = ttk.Notebook(self.left_panel)
        self.filter_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind to filter notebook tab changes to auto-load config on first access
        self.filter_notebook.bind('<<NotebookTabChanged>>', self.on_filter_tab_changed)
        
        # Tab 1: Filters
        filter_tab = ttk.Frame(self.filter_notebook)
        self.filter_notebook.add(filter_tab, text="Filters")
        
        # Search box
        search_frame = ttk.Frame(filter_tab)
        search_frame.pack(fill=tk.X, pady=(5, 10), padx=5)
        
        ttk.Label(search_frame, text="Search:").pack(anchor=tk.W)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X, pady=(2, 0))
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Dynamic filter area
        self.filter_container = ttk.Frame(filter_tab)
        self.filter_container.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Filter controls
        control_frame = ttk.Frame(filter_tab)
        control_frame.pack(fill=tk.X, pady=(10, 5), padx=5)
        
        ttk.Button(control_frame, text="Apply Filters", command=self.apply_filters).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Clear All", command=self.clear_filters).pack(side=tk.LEFT)
        
        # Tab 2: Config Editor
        config_tab = ttk.Frame(self.filter_notebook)
        self.filter_notebook.add(config_tab, text="Config Editor")
        self.create_config_editor(config_tab)
        
    def create_config_editor(self, parent):
        """Create configuration editor interface"""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # File Filters Section
        filters_frame = ttk.LabelFrame(scrollable_frame, text="Log File Filters", padding=5)
        filters_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filters_frame, text="File extensions (comma-separated):").pack(anchor=tk.W)
        self.file_filters_var = tk.StringVar(value=".txt,.log")
        ttk.Entry(filters_frame, textvariable=self.file_filters_var).pack(fill=tk.X, pady=(2, 0))
        
        # Auto-refresh Section
        refresh_frame = ttk.LabelFrame(scrollable_frame, text="Auto-Refresh Settings", padding=5)
        refresh_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.default_autorefresh_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(refresh_frame, text="Enable auto-refresh by default", 
                       variable=self.default_autorefresh_var).pack(anchor=tk.W)
        
        ttk.Label(refresh_frame, text="Refresh interval (seconds):").pack(anchor=tk.W, pady=(5, 0))
        self.refresh_interval_var = tk.StringVar(value="5")
        ttk.Entry(refresh_frame, textvariable=self.refresh_interval_var, width=10).pack(anchor=tk.W)
        
        # Delimiters Section
        delim_frame = ttk.LabelFrame(scrollable_frame, text="Delimiters", padding=5)
        delim_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Store delimiter data as lists with UI widgets
        self.delimiter_data = {
            "logStartDelimiter": {"label": "Log Start:", "entries": []},
            "logEndDelimiter": {"label": "Log End:", "entries": []},
            "ContainerStartDelimiter": {"label": "Container Start:", "entries": []},
            "ContainerEndDelimiter": {"label": "Container End:", "entries": []},
            "categorySeparator": {"label": "Category Separator:", "entries": []},
            "keyValuePairsSeparator": {"label": "Key-Value Pairs Sep:", "entries": []},
            "keyValueSeparator": {"label": "Key-Value Sep:", "entries": []},
            "arrayElementSeparator": {"label": "Array Element Sep:", "entries": []}
        }
        
        # Default delimiter values
        default_delimiters = {
            "logStartDelimiter": ["("],
            "logEndDelimiter": [")"],
            "ContainerStartDelimiter": ["{", "["],
            "ContainerEndDelimiter": ["}", "]"],
            "categorySeparator": ["|"],
            "keyValuePairsSeparator": [";"],
            "keyValueSeparator": ["="],
            "arrayElementSeparator": [","]
        }
        
        # Create UI for each delimiter type
        self.delimiter_frames = {}
        for key, data in self.delimiter_data.items():
            # Main frame for this delimiter type
            delim_type_frame = ttk.Frame(delim_frame)
            delim_type_frame.pack(fill=tk.X, pady=3)
            
            # Label
            ttk.Label(delim_type_frame, text=data["label"], width=25).pack(side=tk.LEFT)
            
            # Container for delimiter entries
            entries_frame = ttk.Frame(delim_type_frame)
            entries_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Add button for this delimiter type
            add_btn = ttk.Button(delim_type_frame, text="+", width=3,
                                command=lambda k=key: self.add_delimiter_entry(k))
            add_btn.pack(side=tk.RIGHT, padx=(5, 0))
            
            self.delimiter_frames[key] = entries_frame
            
            # Create initial entries for default values
            for value in default_delimiters.get(key, [""]):
                self.create_delimiter_entry(key, value)
        
        # Help text
        help_label = ttk.Label(delim_frame, text="Note: Click + to add multiple delimiter options, - to remove",
                              font=("TkDefaultFont", 8), foreground="gray")
        help_label.pack(pady=(5, 0), anchor=tk.W)
        
        # Categories Section
        cat_frame = ttk.LabelFrame(scrollable_frame, text="Categories", padding=5)
        cat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Category list
        cat_list_frame = ttk.Frame(cat_frame)
        cat_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Category listbox with scrollbar
        cat_scrollbar = ttk.Scrollbar(cat_list_frame)
        cat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.category_listbox = tk.Listbox(cat_list_frame, yscrollcommand=cat_scrollbar.set, height=8)
        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cat_scrollbar.config(command=self.category_listbox.yview)
        self.category_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        
        # Track edited categories properly
        self.edited_categories = {}
        
        # Track if config editor has been initialized with current config
        self.config_editor_initialized = False
        
        # Category buttons
        cat_btn_frame = ttk.Frame(cat_frame)
        cat_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(cat_btn_frame, text="Add", command=self.add_category).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cat_btn_frame, text="Edit", command=self.edit_category).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cat_btn_frame, text="Delete", command=self.delete_category).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cat_btn_frame, text="Move Up", command=self.move_category_up).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cat_btn_frame, text="Move Down", command=self.move_category_down).pack(side=tk.LEFT)
        
        # Save/Load buttons
        action_frame = ttk.Frame(scrollable_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(action_frame, text="Load Config", command=self.load_config_to_editor_explicit).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Save Config", command=self.save_config_from_editor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Apply Changes", command=self.apply_config_changes).pack(side=tk.LEFT)
        
        # Statistics panel
        stats_frame = ttk.LabelFrame(self.left_panel, text="Statistics", padding=5)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.X)
    
    def create_log_display(self):
        """Create initial empty tab display"""
        # Create a welcome tab
        self.create_welcome_tab()
        
        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def create_welcome_tab(self):
        """Create welcome tab"""
        welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(welcome_frame, text="Welcome")
        
        # Welcome message
        welcome_text = tk.Text(welcome_frame, wrap=tk.WORD, font=('Arial', 12))
        welcome_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        welcome_message = """
Welcome to Log Viewer!

Open log files using:
• File > Open File - Open single log file in new tab
• File > Open Multiple Files - Open multiple files in separate tabs
• File > Merge Open - Combine multiple files into one tab
• File > Open Folder - Open all log files from a folder

Use the filters on the left to search and filter log entries.
Each tab maintains its own filters and view settings.
        """
        
        welcome_text.insert('1.0', welcome_message)
        welcome_text.config(state=tk.DISABLED)
    
    def create_log_tab(self, title, log_viewer=None):
        """Create a new log tab"""
        tab_id = f"tab_{self.tab_counter}"
        self.tab_counter += 1
        
        # Create tab frame
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=title)
        
        # Log display frame
        display_frame = ttk.LabelFrame(tab_frame, text="Log Entries", padding=5)
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Auto-refresh checkbox
        refresh_frame = ttk.Frame(display_frame)
        refresh_frame.pack(fill=tk.X, pady=(0, 5))
        
        auto_refresh_var = tk.BooleanVar(value=False)
        auto_refresh_check = ttk.Checkbutton(refresh_frame, text="Auto-refresh", 
                                            variable=auto_refresh_var,
                                            command=lambda: self.toggle_auto_refresh(tab_id))
        auto_refresh_check.pack(side=tk.LEFT)
        
        ttk.Label(refresh_frame, text="Interval (sec):").pack(side=tk.LEFT, padx=(10, 2))
        refresh_interval_var = tk.StringVar(value="5")
        refresh_interval_entry = ttk.Entry(refresh_frame, textvariable=refresh_interval_var, width=5)
        refresh_interval_entry.pack(side=tk.LEFT)
        
        # Create scrolled text widget for this tab
        log_text = scrolledtext.ScrolledText(
            display_frame, 
            wrap=tk.NONE,
            font=('Consolas', 10),
            state=tk.DISABLED
        )
        log_text.pack(fill=tk.BOTH, expand=True)
        
        # Store tab data
        self.tabs[tab_id] = {
            'frame': tab_frame,
            'log_viewer': log_viewer,
            'log_text': log_text,
            'title': title,
            'auto_refresh_var': auto_refresh_var,
            'refresh_interval_var': refresh_interval_var,
            'refresh_timer': None,
            'file_path': None  # Will be set when loading files
        }
        
        # Configure text tags for this tab
        self.setup_text_tags_for_tab(log_text, log_viewer)
        
        # Switch to this tab
        self.notebook.select(tab_frame)
        self.active_tab = tab_id
        
        return tab_id
    
    def setup_text_tags_for_tab(self, log_text, log_viewer):
        """Setup text tags for a specific tab"""
        # Legacy log level colors (fallback)
        for level, color in self.log_colors.items():
            log_text.tag_configure(level.lower(), foreground=color, font=('Consolas', 10, 'bold'))
        
        # Configurable color tags
        self._setup_configurable_color_tags_for_tab(log_text, log_viewer)
        
        # Other standard tags
        log_text.tag_configure('timestamp', foreground='#666666')
        log_text.tag_configure('component', foreground='#0066CC')
        log_text.tag_configure('highlight', background='#FFFF00')
    
    def _setup_configurable_color_tags_for_tab(self, log_text, log_viewer):
        """Setup color tags based on configuration for a specific tab"""
        if not log_viewer or not log_viewer.config_manager:
            return
        
        tag_counter = 0
        for category in log_viewer.config_manager.categories:
            if category.has_color_config():
                # Create tags for each color in the color map
                for rgb_color in category.ColourMap.keys():
                    hex_color = category._rgb_string_to_hex(rgb_color)
                    tag_name = f"color_{tag_counter}"
                    
                    # Determine if we're coloring text or background based on Colouring parameter
                    is_background_coloring = category.Colouring.lower() == "background"
                    
                    if category.ColourType == "WholeLine":
                        # Color the entire line
                        if is_background_coloring:
                            log_text.tag_configure(tag_name, background=hex_color, font=('Consolas', 10, 'bold'))
                        else:
                            log_text.tag_configure(tag_name, foreground=hex_color, font=('Consolas', 10, 'bold'))
                    elif category.ColourType == "LineNumber":
                        # Color just the line number
                        if is_background_coloring:
                            log_text.tag_configure(tag_name, background=hex_color, font=('Consolas', 10, 'bold'))
                        else:
                            log_text.tag_configure(tag_name, foreground=hex_color, font=('Consolas', 10, 'bold'))
                    elif category.ColourType == "SpecificValue":
                        # Color the specific field value
                        if is_background_coloring:
                            log_text.tag_configure(tag_name, background=hex_color, font=('Consolas', 10, 'bold'))
                        else:
                            log_text.tag_configure(tag_name, foreground=hex_color, font=('Consolas', 10, 'bold'))
                    
                    tag_counter += 1
    
    def on_tab_changed(self, event):
        """Handle tab change event"""
        selection = event.widget.select()
        if selection:
            # Find which tab is selected
            for tab_id, tab_data in self.tabs.items():
                if str(tab_data['frame']) == selection:
                    self.active_tab = tab_id
                    self.log_viewer = tab_data['log_viewer']
                    self.log_text = tab_data['log_text']
                    break
            else:
                # Probably the welcome tab
                self.active_tab = None
                self.log_viewer = None
                self.log_text = None
            
            # Update filters for the active tab
            self.create_dynamic_filters()
            self.refresh_display()
    
    def on_filter_tab_changed(self, event):
        """Handle filter notebook tab changes - auto-initialize config editor"""
        if not hasattr(self, 'config_editor_initialized'):
            self.config_editor_initialized = False
            
        # Check if Config Editor tab (tab index 1) is selected
        try:
            selected_tab_widget = self.filter_notebook.select()
            selected_tab = self.filter_notebook.index(selected_tab_widget)
            if selected_tab == 1:  # Config Editor tab
                # Auto-load config into editor on first access only
                if not self.config_editor_initialized and self.log_viewer:
                    self.load_config_to_editor()
                    self.config_editor_initialized = True
        except (tk.TclError, ValueError):
            pass  # Ignore errors if tab selection is in transition
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.status_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=5, pady=2)
    
    # Legacy methods removed - using tab-specific versions
    
    def load_default_config(self):
        """Load configuration from log_config.json file or open config editor if not found"""
        try:
            # Check for log_config.json file
            config_path = Path("log_config.json")
            if not config_path.exists():
                # Show user-friendly message and open config editor
                info_msg = (
                    "Configuration file 'log_config.json' was not found.\n\n"
                    "The Config Editor tab has been opened so you can create a new configuration.\n\n"
                    "Once you've set up your configuration, use 'Save Config' to save it as 'log_config.json'."
                )
                messagebox.showinfo("Config File Not Found", info_msg)
                self.update_status("No config file found - use Config Editor to create one")
                
                # Switch to the config editor tab
                self.filter_notebook.select(1)  # Select the Config Editor tab
                
                # Force focus back to the main window and config editor
                self.root.focus_force()
                self.root.after(100, lambda: self.root.focus_set())
                return
            
            # Create a default log viewer for config
            temp_viewer = LogViewer(config_path="log_config.json")
            # Store config in self for new tabs to use
            self.log_viewer = temp_viewer
            self.update_status("Configuration loaded from log_config.json")
            
            # Create filters for the loaded config
            self.create_dynamic_filters()
            
        except Exception as e:
            error_msg = f"Failed to load log_config.json: {str(e)}\n\nThe Config Editor tab has been opened so you can create a new configuration."
            messagebox.showwarning("Configuration Error", error_msg)
            self.update_status(f"Config loading failed - use Config Editor to create new config")
            # Switch to the config editor tab on error too
            self.filter_notebook.select(1)  # Select the Config Editor tab
            
            # Force focus back to the main window and config editor
            self.root.focus_force()
            self.root.after(100, lambda: self.root.focus_set())
    
    def create_dynamic_filters(self):
        """Create filter widgets based on log categories"""
        # Clear existing filters
        for widget in self.filter_container.winfo_children():
            widget.destroy()
        
        # Get the config manager from either the active tab or the main log_viewer
        config_manager = None
        if self.active_tab and self.active_tab in self.tabs:
            tab_log_viewer = self.tabs[self.active_tab].get('log_viewer')
            if tab_log_viewer and tab_log_viewer.config_manager:
                config_manager = tab_log_viewer.config_manager
        
        # Fall back to main log_viewer config if no active tab
        if not config_manager and self.log_viewer and self.log_viewer.config_manager:
            config_manager = self.log_viewer.config_manager
        
        if not config_manager:
            return
        
        self.filter_widgets = {}
        
        # Create scrollable frame for filters
        canvas = tk.Canvas(self.filter_container, height=200)
        scrollbar = ttk.Scrollbar(self.filter_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for category in config_manager.categories:
            frame = ttk.LabelFrame(scrollable_frame, text=category.name, padding=5)
            frame.pack(fill=tk.X, pady=2, padx=2)
            
            field_type = category.get_field_type().value
            
            # Create operator selection and value inputs
            operator_frame = ttk.Frame(frame)
            operator_frame.pack(fill=tk.X)
            
            # Operator selection
            operator_var = tk.StringVar()
            operators = self._get_operators_for_type(field_type)
            operator_combo = ttk.Combobox(operator_frame, textvariable=operator_var, 
                                        values=operators, width=12, state="readonly")
            operator_combo.set(operators[0])  # Default operator
            operator_combo.pack(side=tk.LEFT, padx=(0, 5))
            
            # Value input(s) based on type
            if field_type == "string":
                # String types - single input
                value_var = tk.StringVar()
                entry = ttk.Entry(operator_frame, textvariable=value_var, width=20)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                if field_type == "string":
                    # Add help text for string filters
                    help_label = ttk.Label(frame, text="Use comma-separated values for 'contains any/all' operators. Containers auto-detected.", 
                                         foreground="gray", font=("TkDefaultFont", 8))
                    help_label.pack(anchor=tk.W)
                
                self.filter_widgets[category.name] = {
                    'type': field_type,
                    'operator_var': operator_var,
                    'value_var': value_var,
                    'operator_combo': operator_combo,
                    'value_entry': entry
                }
                
            elif field_type == "number":
                # Number type - support ranges
                value_frame = ttk.Frame(operator_frame)
                value_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                value1_var = tk.StringVar()
                value2_var = tk.StringVar()
                
                entry1 = ttk.Entry(value_frame, textvariable=value1_var, width=10)
                entry1.pack(side=tk.LEFT)
                
                range_label = ttk.Label(value_frame, text=" to ")
                range_label.pack(side=tk.LEFT)
                
                entry2 = ttk.Entry(value_frame, textvariable=value2_var, width=10)
                entry2.pack(side=tk.LEFT)
                
                # Show/hide range input based on operator
                def on_operator_change(*args):
                    op = operator_var.get()
                    if op in ["between", "not between"]:
                        range_label.pack(side=tk.LEFT)
                        entry2.pack(side=tk.LEFT)
                    else:
                        range_label.pack_forget()
                        entry2.pack_forget()
                
                operator_var.trace('w', on_operator_change)
                on_operator_change()  # Initial state
                
                help_label = ttk.Label(frame, text="Range: 10 to 20, Single: 15", 
                                     foreground="gray", font=("TkDefaultFont", 8))
                help_label.pack(anchor=tk.W)
                
                self.filter_widgets[category.name] = {
                    'type': field_type,
                    'operator_var': operator_var,
                    'value1_var': value1_var,
                    'value2_var': value2_var,
                    'operator_combo': operator_combo,
                    'value1_entry': entry1,
                    'value2_entry': entry2,
                    'range_label': range_label
                }
                
            elif field_type == "datetime":
                # Datetime type - support ranges
                value_frame = ttk.Frame(operator_frame)
                value_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                value1_var = tk.StringVar()
                value2_var = tk.StringVar()
                
                entry1 = ttk.Entry(value_frame, textvariable=value1_var, width=15)
                entry1.pack(side=tk.LEFT)
                
                range_label = ttk.Label(value_frame, text=" to ")
                range_label.pack(side=tk.LEFT)
                
                entry2 = ttk.Entry(value_frame, textvariable=value2_var, width=15)
                entry2.pack(side=tk.LEFT)
                
                # Show/hide range input based on operator
                def on_datetime_operator_change(*args):
                    op = operator_var.get()
                    if op in ["between", "not between"]:
                        range_label.pack(side=tk.LEFT)
                        entry2.pack(side=tk.LEFT)
                    else:
                        range_label.pack_forget()
                        entry2.pack_forget()
                
                operator_var.trace('w', on_datetime_operator_change)
                on_datetime_operator_change()  # Initial state
                
                help_label = ttk.Label(frame, text="Format: 2025-08-08 or 06:50:00 or partial match", 
                                     foreground="gray", font=("TkDefaultFont", 8))
                help_label.pack(anchor=tk.W)
                
                self.filter_widgets[category.name] = {
                    'type': field_type,
                    'operator_var': operator_var,
                    'value1_var': value1_var,
                    'value2_var': value2_var,
                    'operator_combo': operator_combo,
                    'value1_entry': entry1,
                    'value2_entry': entry2,
                    'range_label': range_label
                }
    
    def _get_operators_for_type(self, field_type):
        """Get available operators for a field type"""
        if field_type == "string":
            return ["contains", "equals", "not contains", "not equals", "starts with", "ends with", "contains any", "contains all", "has key", "key equals"]
        elif field_type == "number":
            return ["equals", "not equals", "greater than", "less than", "between", "not between"]
        elif field_type == "datetime":
            return ["contains", "equals", "not contains", "before", "after", "between", "not between"]
        else:
            return ["contains", "equals"]
    
    def open_file(self):
        """Open single log file in new tab"""
        file_path = filedialog.askopenfilename(
            title="Select Log File",
            filetypes=[
                ("Text files", "*.txt"),
                ("Log files", "*.log"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.load_log_file_in_tab(file_path)
    
    def open_multiple_files(self):
        """Open multiple log files in separate tabs"""
        file_paths = filedialog.askopenfilenames(
            title="Select Log Files",
            filetypes=[
                ("Text files", "*.txt"),
                ("Log files", "*.log"),
                ("All files", "*.*")
            ]
        )
        
        for file_path in file_paths:
            self.load_log_file_in_tab(file_path)
    
    def merge_open_files(self):
        """Open multiple log files and merge them into one tab"""
        file_paths = filedialog.askopenfilenames(
            title="Select Log Files to Merge",
            filetypes=[
                ("Text files", "*.txt"),
                ("Log files", "*.log"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            self.merge_files_in_tab(file_paths)
    
    def open_folder(self):
        """Open all log files from a folder in separate tabs"""
        folder_path = filedialog.askdirectory(
            title="Select Folder with Log Files"
        )
        
        if folder_path:
            self.load_folder_files(folder_path, merge=False)
    
    def merge_open_folder(self):
        """Open all log files from a folder and merge them into one tab"""
        folder_path = filedialog.askdirectory(
            title="Select Folder with Log Files to Merge"
        )
        
        if folder_path:
            self.load_folder_files(folder_path, merge=True)
    
    def close_current_tab(self):
        """Close the currently active tab"""
        if self.active_tab and self.active_tab in self.tabs:
            tab_frame = self.tabs[self.active_tab]['frame']
            self.notebook.forget(tab_frame)
            del self.tabs[self.active_tab]
            
            # Reset active tab
            if self.tabs:
                # Select first available tab
                first_tab = next(iter(self.tabs.values()))
                self.notebook.select(first_tab['frame'])
            else:
                self.active_tab = None
                self.log_viewer = None
                self.log_text = None
    
    def load_log_file(self, file_path: str):
        """Legacy method - redirects to tab-based loading"""
        self.load_log_file_in_tab(file_path)
    
    def load_log_file_in_tab(self, file_path: str):
        """Load a log file in a new tab"""
        # Create log viewer for this tab
        try:
            if hasattr(self, 'log_viewer') and self.log_viewer:
                # Use existing config
                tab_log_viewer = LogViewer(config_dict=self.log_viewer.config_manager.config)
            else:
                # Load default config
                tab_log_viewer = LogViewer(config_path="log_config.json")
            
            # Create tab
            file_name = Path(file_path).name
            tab_id = self.create_log_tab(file_name, tab_log_viewer)
            
            # Store file path in tab data
            self.tabs[tab_id]['file_path'] = file_path
            
            # Load file in this tab
            self.progress.start()
            self.update_status(f"Loading log file: {file_path}")
            
            def load_file():
                try:
                    count = tab_log_viewer.load_file(file_path)
                    self.root.after(0, lambda: self.on_file_loaded_in_tab(tab_id, file_path, count))
                except Exception as e:
                    self.root.after(0, lambda: self.on_file_error(str(e)))
            
            import threading
            thread = threading.Thread(target=load_file)
            thread.daemon = True
            thread.start()
            
            return tab_id  # Return tab_id for tracking
            
        except Exception as e:
            self.on_file_error(str(e))
            return None
    
    def _load_file_worker(self, file_path: str):
        """Worker thread for loading log file"""
        try:
            if not self.log_viewer:
                raise Exception("No log viewer configured")
            
            count = self.log_viewer.load_file(file_path)
            
            # Update GUI in main thread
            self.root.after(0, self._on_file_loaded, count, None)
            
        except Exception as e:
            self.root.after(0, self._on_file_loaded, 0, str(e))
    
    def _on_file_loaded(self, count: int, error: Optional[str]):
        """Handle file loading completion (legacy)"""
        self.progress.stop()
        
        if error:
            messagebox.showerror("Load Error", f"Failed to load file: {error}")
            self.update_status("Failed to load file")
        else:
            self.update_status(f"Loaded {count} log entries from {Path(self.current_file_path).name}")
            self.refresh_display()
            self.update_statistics()
    
    def merge_files_in_tab(self, file_paths, folder_path=None):
        """Merge multiple files into one tab"""
        try:
            if hasattr(self, 'log_viewer') and self.log_viewer:
                # Use existing config
                tab_log_viewer = LogViewer(config_dict=self.log_viewer.config_manager.config)
            else:
                # Load default config
                tab_log_viewer = LogViewer(config_path="log_config.json")
            
            # Create tab with merged name
            file_names = [Path(fp).name for fp in file_paths]
            if len(file_names) <= 3:
                title = f"Merged: {', '.join(file_names)}"
            else:
                title = f"Merged: {file_names[0]} + {len(file_names)-1} more"
            
            tab_id = self.create_log_tab(title, tab_log_viewer)
            
            # Store folder path and file list if from a folder
            if folder_path:
                self.tabs[tab_id]['folder_path'] = folder_path
                self.tabs[tab_id]['merged_files'] = file_paths.copy()
                # Get log filters
                log_filters = ['.txt', '.log']  # Default
                if hasattr(self, 'log_viewer') and self.log_viewer:
                    config = self.log_viewer.config_manager.config
                    log_filters = config.get('logViewerConfig', {}).get('LogFileFilters', log_filters)
                self.tabs[tab_id]['log_filters'] = log_filters
            
            # Load and merge files
            self.progress.start()
            self.update_status(f"Merging {len(file_paths)} files...")
            
            def load_and_merge():
                try:
                    all_logs = []
                    for file_path in file_paths:
                        temp_viewer = LogViewer(config_dict=tab_log_viewer.config_manager.config)
                        temp_viewer.load_file(file_path)
                        all_logs.extend(temp_viewer.logs)
                    
                    # Sort merged logs by timestamp if possible
                    try:
                        all_logs.sort(key=lambda log: log.get_field('Timestamp') or '')
                    except:
                        pass  # If sorting fails, keep original order
                    
                    # Set merged logs
                    tab_log_viewer.logs = all_logs
                    tab_log_viewer.filtered_logs = all_logs.copy()
                    
                    total_count = len(all_logs)
                    self.root.after(0, lambda: self.on_file_loaded_in_tab(tab_id, f"{len(file_paths)} files merged", total_count))
                except Exception as e:
                    self.root.after(0, lambda: self.on_file_error(str(e)))
            
            import threading
            thread = threading.Thread(target=load_and_merge)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.on_file_error(str(e))
    
    def load_folder_files(self, folder_path, merge=False):
        """Load all log files from a folder"""
        try:
            # Get log file filters from config
            log_filters = ['.txt', '.log']  # Default
            if hasattr(self, 'log_viewer') and self.log_viewer:
                config = self.log_viewer.config_manager.config
                log_filters = config.get('logViewerConfig', {}).get('LogFileFilters', log_filters)
            
            # Find all log files in folder and subdirectories
            log_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if any(file.lower().endswith(ext.lower()) for ext in log_filters):
                        log_files.append(os.path.join(root, file))
            
            if not log_files:
                self.update_status(f"No log files found in {folder_path}")
                messagebox.showwarning("No Files", f"No log files with extensions {', '.join(log_filters)} found in the selected folder.")
                return
            
            if merge:
                # For merged folder view, track the folder path
                self.merge_files_in_tab(log_files, folder_path=folder_path)
            else:
                # Track folder for individual file tabs
                for log_file in log_files:
                    tab_id = self.load_log_file_in_tab(log_file)
                    if tab_id and tab_id in self.tabs:
                        self.tabs[tab_id]['folder_path'] = folder_path
                        self.tabs[tab_id]['log_filters'] = log_filters
            
        except Exception as e:
            self.on_file_error(str(e))
    
    def on_file_loaded_in_tab(self, tab_id, file_info, count):
        """Handle successful file loading in a tab"""
        self.progress.stop()
        self.update_status(f"Loaded {count} log entries from {file_info}")
        
        # Switch to this tab and refresh display
        if tab_id in self.tabs:
            tab_frame = self.tabs[tab_id]['frame']
            self.notebook.select(tab_frame)
            self.active_tab = tab_id
            self.log_viewer = self.tabs[tab_id]['log_viewer']
            self.log_text = self.tabs[tab_id]['log_text']
            
            # Update filters and display
            self.create_dynamic_filters()
            self.refresh_display()
    
    def on_file_error(self, error_msg):
        """Handle file loading error"""
        self.progress.stop()
        messagebox.showerror("Load Error", f"Failed to load file: {error_msg}")
        self.update_status("Failed to load file")
    
    def refresh_display(self):
        """Refresh log display"""
        if not self.log_viewer or not self.log_viewer.logs or not self.log_text:
            return
        
        # Get display limit
        limit_str = self.limit_var.get()
        limit = None if limit_str == "All" else int(limit_str)
        
        # Get logs to display
        logs_to_show = self.log_viewer.filtered_logs[:limit] if limit else self.log_viewer.filtered_logs
        
        # Clear display
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        
        # Display logs
        detailed = self.show_detailed.get()
        for i, log in enumerate(logs_to_show, 1):
            if detailed:
                self._display_detailed_log(log, i)
            else:
                self._display_compact_log(log, i)
        
        self.log_text.config(state=tk.DISABLED)
        
        # Highlight search terms
        self.highlight_search_terms()
    
    def _display_compact_log(self, log: LogEntry, index: int):
        """Display log in compact format"""
        text = f"[{index}] Line {log.line_number}: {str(log)}\n"
        
        # Insert text with color coding
        start_pos = self.log_text.index(tk.INSERT)
        self.log_text.insert(tk.END, text)
        
        # Apply configurable coloring
        self._apply_configurable_colors(log, start_pos, index)
    
    def _display_detailed_log(self, log: LogEntry, index: int):
        """Display log in detailed format"""
        self.log_text.insert(tk.END, f"\n{'='*60}\n")
        # Include source file for merged logs
        if hasattr(log, 'source_file') and log.source_file:
            from pathlib import Path
            source_name = Path(log.source_file).name
            self.log_text.insert(tk.END, f"Log Entry #{index} (Line {log.line_number}, File: {source_name})\n")
        else:
            self.log_text.insert(tk.END, f"Log Entry #{index} (Line {log.line_number})\n")
        self.log_text.insert(tk.END, f"{'-'*60}\n")
        
        for category in self.log_viewer.config_manager.categories:
            value = log.get_field(category.name)
            if value is not None:
                if isinstance(value, dict):
                    self.log_text.insert(tk.END, f"{category.name}:\n")
                    for k, v in value.items():
                        self.log_text.insert(tk.END, f"  {k}: {v}\n")
                elif isinstance(value, list):
                    self.log_text.insert(tk.END, f"{category.name}: {', '.join(str(v) for v in value)}\n")
                else:
                    self.log_text.insert(tk.END, f"{category.name}: {value}\n")
        
        self.log_text.insert(tk.END, "\n")
    
    def _apply_configurable_colors(self, log: LogEntry, start_pos: str, line_index: int):
        """Apply configurable colors to log entry"""
        if not self.log_viewer or not self.log_viewer.config_manager:
            return
        
        # Get line boundaries
        line_num = start_pos.split('.')[0]
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        
        # Track which colors to apply
        whole_line_color = None
        line_number_color = None
        specific_value_colors = []  # List of (tag_name, color, field_text, is_background_coloring) tuples
        
        # Check each category for color configuration
        for category in self.log_viewer.config_manager.categories:
            if not category.has_color_config():
                continue
                
            field_value = log.get_field(category.name)
            if field_value is None:
                continue
            
            color = category.get_color_for_value(field_value)
            if not color:
                continue
            
            # Create unique tag name for this color and type combination
            tag_name = f"{category.name}_{color.replace('#', '')}"
            
            # Determine if we're coloring text or background based on Colouring parameter
            is_background_coloring = category.Colouring.lower() == "background"
            
            if category.ColourType == "WholeLine":
                # Color entire line
                whole_line_color = (tag_name, color)
                if is_background_coloring:
                    self.log_text.tag_configure(tag_name, background=color, font=('Consolas', 10, 'bold'))
                else:
                    self.log_text.tag_configure(tag_name, foreground=color, font=('Consolas', 10, 'bold'))
                
            elif category.ColourType == "LineNumber":
                # Color line number area only
                line_number_color = (tag_name, color)
                if is_background_coloring:
                    self.log_text.tag_configure(tag_name, background=color, font=('Consolas', 10, 'bold'))
                else:
                    self.log_text.tag_configure(tag_name, foreground=color, font=('Consolas', 10, 'bold'))
                
            elif category.ColourType == "SpecificValue":
                # Store SpecificValue colors to apply after checking for WholeLine conflicts
                field_text = str(field_value)
                specific_value_colors.append((tag_name, color, field_text, is_background_coloring))
        
        # Apply line-level colors FIRST (WholeLine and LineNumber)
        if whole_line_color:
            tag_name, color = whole_line_color
            self.log_text.tag_add(tag_name, line_start, line_end)
        
        if line_number_color:
            # Apply to line number portion only [index] part
            tag_name, color = line_number_color
            bracket_end = self.log_text.search(']', line_start, line_end)
            if bracket_end:
                self.log_text.tag_add(tag_name, line_start, f"{bracket_end}+1c")
        
        # Apply SpecificValue colors AFTER line-level colors (higher priority - overrides line colors)
        for tag_name, color, field_text, is_background_coloring in specific_value_colors:
            # SpecificValue colors use their configured coloring method and override line colors
            if is_background_coloring:
                self.log_text.tag_configure(tag_name, background=color, font=('Consolas', 10, 'bold'))
            else:
                self.log_text.tag_configure(tag_name, foreground=color, font=('Consolas', 10, 'bold'))
            
            # Find and color occurrences of this value in the line
            line_text = self.log_text.get(line_start, line_end)
            start_idx = 0
            while True:
                pos = line_text.find(field_text, start_idx)
                if pos == -1:
                    break
                
                # Calculate absolute position in text widget
                abs_start = f"{line_num}.{pos}"
                abs_end = f"{line_num}.{pos + len(field_text)}"
                self.log_text.tag_add(tag_name, abs_start, abs_end)
                start_idx = pos + len(field_text)
    
    def apply_filters(self):
        """Apply multiple simultaneous filters to logs"""
        if not self.log_viewer:
            return
        
        # Start with all logs
        filtered_logs = self.log_viewer.logs.copy()
        
        # Apply JSON/XML display filters
        if hasattr(self, 'json_xml_filter_var'):
            filter_mode = self.json_xml_filter_var.get()
            if filter_mode != "Show All":
                display_filtered = []
                for log in filtered_logs:
                    # Check if log contains JSON or XML
                    text = log.raw_text
                    is_json = '{' in text or '[' in text  # Simple JSON detection
                    is_xml = '<' in text and '>' in text  # Simple XML detection
                    is_json_or_xml = is_json or is_xml
                    
                    # Apply filter based on mode
                    if filter_mode == "Only JSON/XML":
                        if is_json_or_xml:
                            display_filtered.append(log)
                    elif filter_mode == "Hide JSON/XML":
                        if not is_json_or_xml:
                            display_filtered.append(log)
                
                filtered_logs = display_filtered
        
        # Apply search filter
        search_term = self.search_var.get().strip()
        if search_term:
            search_filtered = []
            for log in filtered_logs:
                if search_term.lower() in log.raw_text.lower():
                    search_filtered.append(log)
            filtered_logs = search_filtered
        
        # Apply field filters
        for category_name, filter_info in self.filter_widgets.items():
            filtered_logs = self._apply_single_filter(filtered_logs, category_name, filter_info)
        
        # Update filtered logs
        self.log_viewer.filtered_logs = filtered_logs
        
        # Refresh display and stats
        self.refresh_display()
        self.update_statistics()
        self.update_status(f"Applied filters - showing {len(filtered_logs)} of {len(self.log_viewer.logs)} entries")
    
    def _apply_single_filter(self, logs, category_name, filter_info):
        """Apply a single filter to the log list"""
        operator = filter_info['operator_var'].get()
        field_type = filter_info['type']
        
        # Get filter values
        if field_type == "string":
            value = filter_info['value_var'].get().strip()
            if not value:
                return logs
            
            return self._filter_string_field(logs, category_name, operator, value)
            
        elif field_type == "number":
            value1 = filter_info['value1_var'].get().strip()
            value2 = filter_info['value2_var'].get().strip()
            
            if not value1:
                return logs
            
            return self._filter_number_field(logs, category_name, operator, value1, value2)
            
        elif field_type == "datetime":
            value1 = filter_info['value1_var'].get().strip()
            value2 = filter_info['value2_var'].get().strip()
            
            if not value1:
                return logs
            
            return self._filter_datetime_field(logs, category_name, operator, value1, value2)
        
        return logs
    
    def _filter_string_field(self, logs, category_name, operator, value):
        """Filter logs by string field"""
        filtered = []
        
        for log in logs:
            field_value = log.get_field(category_name)
            
            if field_value is None:
                continue
                
            # Handle different field value types (parsed by container logic)
            if isinstance(field_value, dict):
                # For structured strings, check keys and values
                if operator == "has key":
                    if value in field_value:
                        filtered.append(log)
                elif operator == "key equals":
                    key, val = value.split('=', 1) if '=' in value else (value, '')
                    if key in field_value and (not val or str(field_value[key]) == val):
                        filtered.append(log)
                elif operator == "contains":
                    field_str = ' '.join(f"{k}={v}" for k, v in field_value.items())
                    if value.lower() in field_str.lower():
                        filtered.append(log)
                elif operator == "not contains":
                    field_str = ' '.join(f"{k}={v}" for k, v in field_value.items())
                    if value.lower() not in field_str.lower():
                        filtered.append(log)
                        
            elif field_type == "array_string" and isinstance(field_value, list):
                # For array strings, check array elements
                if operator == "contains":
                    if any(value.lower() in str(item).lower() for item in field_value):
                        filtered.append(log)
                elif operator == "not contains":
                    if not any(value.lower() in str(item).lower() for item in field_value):
                        filtered.append(log)
                elif operator == "contains all":
                    search_items = [item.strip().lower() for item in value.split(',')]
                    field_items = [str(item).lower() for item in field_value]
                    if all(any(search in field for field in field_items) for search in search_items):
                        filtered.append(log)
                elif operator == "contains any":
                    search_items = [item.strip().lower() for item in value.split(',')]
                    field_items = [str(item).lower() for item in field_value]
                    if any(any(search in field for field in field_items) for search in search_items):
                        filtered.append(log)
                        
            else:
                # Regular string comparison
                field_str = str(field_value).lower()
                value_lower = value.lower()
                
                if operator == "contains":
                    if value_lower in field_str:
                        filtered.append(log)
                elif operator == "equals":
                    if field_str == value_lower:
                        filtered.append(log)
                elif operator == "not contains":
                    if value_lower not in field_str:
                        filtered.append(log)
                elif operator == "not equals":
                    if field_str != value_lower:
                        filtered.append(log)
                elif operator == "starts with":
                    if field_str.startswith(value_lower):
                        filtered.append(log)
                elif operator == "ends with":
                    if field_str.endswith(value_lower):
                        filtered.append(log)
                elif operator == "contains any":
                    # Split comma-separated values and check if any are contained in field
                    search_items = [item.strip().lower() for item in value.split(',')]
                    if any(search in field_str for search in search_items):
                        filtered.append(log)
                elif operator == "contains all":
                    # Split comma-separated values and check if all are contained in field
                    search_items = [item.strip().lower() for item in value.split(',')]
                    if all(search in field_str for search in search_items):
                        filtered.append(log)
        
        return filtered
    
    def _filter_number_field(self, logs, category_name, operator, value1, value2):
        """Filter logs by number field"""
        try:
            num1 = float(value1)
            num2 = float(value2) if value2 else None
        except ValueError:
            return logs
        
        filtered = []
        
        for log in logs:
            field_value = log.get_field(category_name)
            
            if field_value is None:
                continue
                
            try:
                field_num = float(field_value)
                
                if operator == "equals":
                    if field_num == num1:
                        filtered.append(log)
                elif operator == "not equals":
                    if field_num != num1:
                        filtered.append(log)
                elif operator == "greater than":
                    if field_num > num1:
                        filtered.append(log)
                elif operator == "less than":
                    if field_num < num1:
                        filtered.append(log)
                elif operator == "between" and num2 is not None:
                    if min(num1, num2) <= field_num <= max(num1, num2):
                        filtered.append(log)
                elif operator == "not between" and num2 is not None:
                    if not (min(num1, num2) <= field_num <= max(num1, num2)):
                        filtered.append(log)
                        
            except (ValueError, TypeError):
                continue
        
        return filtered
    
    def _filter_datetime_field(self, logs, category_name, operator, value1, value2):
        """Filter logs by datetime field"""
        filtered = []
        
        for log in logs:
            field_value = log.get_field(category_name)
            
            if field_value is None:
                continue
                
            field_str = str(field_value)
            
            if operator == "contains":
                if value1.lower() in field_str.lower():
                    filtered.append(log)
            elif operator == "equals":
                if field_str.lower() == value1.lower():
                    filtered.append(log)
            elif operator == "not contains":
                if value1.lower() not in field_str.lower():
                    filtered.append(log)
            elif operator in ["before", "after", "between", "not between"]:
                # Simple string comparison for datetime ranges
                # In a production system, you'd parse the datetime properly
                if operator == "before":
                    if field_str < value1:
                        filtered.append(log)
                elif operator == "after":
                    if field_str > value1:
                        filtered.append(log)
                elif operator == "between" and value2:
                    if min(value1, value2) <= field_str <= max(value1, value2):
                        filtered.append(log)
                elif operator == "not between" and value2:
                    if not (min(value1, value2) <= field_str <= max(value1, value2)):
                        filtered.append(log)
        
        return filtered
    
    def clear_filters(self):
        """Clear all filters"""
        if not self.log_viewer:
            return
        
        # Clear search
        self.search_var.set("")
        
        # Clear filter widgets
        for filter_info in self.filter_widgets.values():
            # Reset operators to default
            field_type = filter_info['type']
            operators = self._get_operators_for_type(field_type)
            filter_info['operator_var'].set(operators[0])
            
            # Clear values
            if 'value_var' in filter_info:
                filter_info['value_var'].set("")
            if 'value1_var' in filter_info:
                filter_info['value1_var'].set("")
            if 'value2_var' in filter_info:
                filter_info['value2_var'].set("")
        
        # Reset filters to show all logs
        self.log_viewer.reset_filters()
        self.refresh_display()
        self.update_statistics()
        self.update_status("Filters cleared")
    
    def on_search_change(self, event=None):
        """Handle search box changes"""
        # Auto-apply search with slight delay
        self.root.after(300, self.apply_filters)
    
    def highlight_search_terms(self):
        """Highlight search terms in log display"""
        search_term = self.search_var.get().strip()
        if not search_term:
            return
        
        # Remove existing highlights
        self.log_text.tag_remove('highlight', 1.0, tk.END)
        
        # Add new highlights
        start_pos = 1.0
        while True:
            start_pos = self.log_text.search(search_term, start_pos, tk.END, nocase=True)
            if not start_pos:
                break
            
            end_pos = f"{start_pos}+{len(search_term)}c"
            self.log_text.tag_add('highlight', start_pos, end_pos)
            start_pos = end_pos
    
    def update_statistics(self):
        """Update statistics display"""
        if not self.log_viewer:
            return
        
        stats = self.log_viewer.get_stats()
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        # Basic stats
        self.stats_text.insert(tk.END, f"Total Logs: {stats['total_logs']}\n")
        self.stats_text.insert(tk.END, f"Filtered: {stats['filtered_logs']}\n\n")
        
        # Log levels breakdown
        if 'log_levels' in stats:
            self.stats_text.insert(tk.END, "Log Levels:\n")
            for level, count in stats['log_levels'].items():
                self.stats_text.insert(tk.END, f"  {level}: {count}\n")
        
        self.stats_text.config(state=tk.DISABLED)
    
    def export_logs(self):
        """Export filtered logs"""
        if not self.log_viewer or not self.log_viewer.filtered_logs:
            messagebox.showwarning("Export", "No logs to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Logs",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("JSON files", "*.json")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        # Export as JSON
                        log_data = []
                        for log in self.log_viewer.filtered_logs:
                            log_data.append({
                                'line_number': log.line_number,
                                'raw_text': log.raw_text,
                                'fields': log.fields
                            })
                        json.dump(log_data, f, indent=2)
                    elif file_path.endswith('.csv'):
                        # Export as CSV
                        import csv
                        writer = csv.writer(f)
                        
                        # Header
                        headers = ['Line', 'Raw Text'] + [cat.name for cat in self.log_viewer.config_manager.categories]
                        writer.writerow(headers)
                        
                        # Data
                        for log in self.log_viewer.filtered_logs:
                            row = [log.line_number, log.raw_text]
                            for cat in self.log_viewer.config_manager.categories:
                                value = log.get_field(cat.name)
                                if isinstance(value, (dict, list)):
                                    value = str(value)
                                row.append(value)
                            writer.writerow(row)
                    else:
                        # Export as text
                        for log in self.log_viewer.filtered_logs:
                            f.write(f"Line {log.line_number}: {log.raw_text}\n")
                
                messagebox.showinfo("Export", f"Exported {len(self.log_viewer.filtered_logs)} logs to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def load_config_file(self):
        """Load configuration from file"""
        file_path = filedialog.askopenfilename(
            title="Select Configuration File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Load new configuration
                temp_viewer = LogViewer(config_path=file_path)
                # Store config in self for new tabs to use
                self.log_viewer = temp_viewer
                
                # Update all existing tabs with new config if needed
                for tab_id, tab_data in self.tabs.items():
                    # Reload with new config
                    tab_data['log_viewer'].config_manager = temp_viewer.config_manager
                    # Refresh tags for this tab
                    self.setup_text_tags_for_tab(tab_data['log_text'], tab_data['log_viewer'])
                
                # Always create filters based on the new config
                self.create_dynamic_filters()
                
                # Refresh display if there's an active tab
                if self.active_tab and self.active_tab in self.tabs:
                    self.refresh_display()
                
                self.update_status(f"Configuration loaded from {Path(file_path).name}")
                
                # Reload current file if one is loaded
                if self.current_file_path:
                    self.load_log_file(self.current_file_path)
                    
            except Exception as e:
                messagebox.showerror("Configuration Error", f"Failed to load config: {str(e)}")
    
    def focus_search(self):
        """Focus on search entry"""
        self.search_entry.focus_set()
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_var.set(message)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Log Viewer GUI v1.0

A configurable log parser and viewer with filtering capabilities.

Features:
• Configurable log parsing
• Advanced filtering with ContainsAny/ContainsAll
• Search functionality
• Export to multiple formats
• Real-time statistics
• Configurable color coding

Built with Python and Tkinter

© 2025 Andrew Keith Watts. All rights reserved.

This code is the intellectual property of Andrew Keith Watts. Unauthorized
reproduction, distribution, or modification of this code, in whole or in part,
without the express written permission of Andrew Keith Watts is strictly prohibited.

For inquiries, please contact AndrewKWatts@gmail.com.
        """
        messagebox.showinfo("About Log Viewer", about_text.strip())
    
    # Config Editor Methods
    def load_config_to_editor_explicit(self):
        """Load a config file into the editor (called by Load Config button)"""
        file_path = filedialog.askopenfilename(
            title="Select Configuration File to Load",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Load the config file
                temp_viewer = LogViewer(config_path=file_path)
                self.log_viewer = temp_viewer
                
                # Load into editor
                self.load_config_to_editor(force_reload=True)
                
                # Also update all tabs with new config
                for tab_id, tab_data in self.tabs.items():
                    tab_data['log_viewer'].config_manager = temp_viewer.config_manager
                    self.setup_text_tags_for_tab(tab_data['log_text'], tab_data['log_viewer'])
                
                # Always create filters based on the new config
                self.create_dynamic_filters()
                
                # Refresh display if there's an active tab
                if self.active_tab and self.active_tab in self.tabs:
                    self.refresh_display()
                
                self.update_status(f"Configuration loaded from {Path(file_path).name}")
                messagebox.showinfo("Success", f"Configuration loaded from {Path(file_path).name}")
                
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load configuration: {str(e)}")
    
    def load_config_to_editor(self, force_reload=False):
        """Load current config into the editor"""
        if not self.log_viewer or not self.log_viewer.config_manager:
            if force_reload:
                messagebox.showwarning("No Config", "No configuration loaded")
            return
        
        config = self.log_viewer.config_manager.config
        lvc = config.get('logViewerConfig', {})
        
        # Load file filters
        filters = lvc.get('LogFileFilters', ['.txt', '.log'])
        self.file_filters_var.set(','.join(filters))
        
        # Load auto-refresh settings
        self.default_autorefresh_var.set(lvc.get('DefaultAutoRefresh', False))
        self.refresh_interval_var.set(str(lvc.get('RefreshInterval', 5)))
        
        # Load delimiters into the new UI
        delimiters = lvc.get('delimiters', {})
        for key in self.delimiter_data.keys():
            # Clear existing entries
            for entry in self.delimiter_data[key]["entries"][:]:
                entry["frame"].destroy()
            self.delimiter_data[key]["entries"].clear()
            
            # Get delimiter values
            delimiter_values = delimiters.get(key, [])
            if not isinstance(delimiter_values, list):
                delimiter_values = [delimiter_values]  # Convert string to list
            
            # Create entries for each value
            if delimiter_values:
                for value in delimiter_values:
                    self.create_delimiter_entry(key, str(value))
            else:
                # Create at least one empty entry
                self.create_delimiter_entry(key, "")
        
        # Load categories
        self.category_listbox.delete(0, tk.END)
        for cat in lvc.get('categories', []):
            self.category_listbox.insert(tk.END, cat.get('name', 'Unnamed'))
        
        # Reset initialization flag if this was a forced reload
        if force_reload:
            self.config_editor_initialized = True
        
        self.update_status("Configuration loaded into editor")
    
    def save_config_from_editor(self):
        """Save the edited configuration to a file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            config = self.build_config_from_editor()
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=4)
            messagebox.showinfo("Success", f"Configuration saved to {Path(file_path).name}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration: {str(e)}")
    
    def apply_config_changes(self):
        """Apply the edited configuration"""
        try:
            config = self.build_config_from_editor()
            # Create new log viewer with this config
            temp_viewer = LogViewer(config_dict=config)
            self.log_viewer = temp_viewer
            
            # Update all tabs with new config
            for tab_id, tab_data in self.tabs.items():
                tab_data['log_viewer'].config_manager = temp_viewer.config_manager
                self.setup_text_tags_for_tab(tab_data['log_text'], tab_data['log_viewer'])
            
            # Always create filters based on the new config
            self.create_dynamic_filters()
            
            # Refresh display if there's an active tab
            if self.active_tab and self.active_tab in self.tabs:
                self.refresh_display()
            
            self.update_status("Configuration changes applied")
            messagebox.showinfo("Success", "Configuration changes applied successfully")
        except Exception as e:
            messagebox.showerror("Apply Error", f"Failed to apply configuration: {str(e)}")
    
    def build_config_from_editor(self):
        """Build configuration dictionary from editor values"""
        # Get file filters
        filters = [f.strip() for f in self.file_filters_var.get().split(',') if f.strip()]
        
        # Get delimiters from the new UI
        delimiters = {}
        for key in self.delimiter_data.keys():
            values = self.get_delimiter_values(key)
            delimiters[key] = values if values else [""]
        
        # Build categories from listbox order and edited data
        categories = []
        for i in range(self.category_listbox.size()):
            cat_name = self.category_listbox.get(i)
            
            # Use order based on position in listbox (no explicit order field)
            cat_dict = {'name': cat_name, 'type': 'string'}  # Default type
            
            # Check if we have edited data for this category
            if cat_name in self.edited_categories:
                edited_cat = self.edited_categories[cat_name]
                cat_dict.update(edited_cat)
                # Remove 'order' field if present - using array order instead
                cat_dict.pop('order', None)
            else:
                # Try to get from existing config
                if self.log_viewer and self.log_viewer.config_manager:
                    for cat in self.log_viewer.config_manager.categories:
                        if cat.name == cat_name:
                            cat_dict = {
                                'name': cat.name,
                                'type': cat.type
                            }
                            if cat.description:
                                cat_dict['description'] = cat.description
                            if cat.ColourType:
                                cat_dict['ColourType'] = cat.ColourType
                                cat_dict['Colouring'] = cat.Colouring
                                cat_dict['ColourMap'] = cat.ColourMap
                            break
            
            categories.append(cat_dict)
        
        return {
            'logViewerConfig': {
                'LogFileFilters': filters,
                'DefaultAutoRefresh': self.default_autorefresh_var.get(),
                'RefreshInterval': int(self.refresh_interval_var.get() or 5),
                'delimiters': delimiters,
                'categories': categories
            }
        }
    
    # Delimiter Management Methods
    def create_delimiter_entry(self, delim_type, initial_value=""):
        """Create a single delimiter entry with remove button"""
        entry_frame = ttk.Frame(self.delimiter_frames[delim_type])
        entry_frame.pack(side=tk.LEFT, padx=2)
        
        # Entry field
        var = tk.StringVar(value=initial_value)
        entry = ttk.Entry(entry_frame, textvariable=var, width=8)
        entry.pack(side=tk.LEFT)
        
        # Remove button
        remove_btn = ttk.Button(entry_frame, text="-", width=2,
                               command=lambda: self.remove_delimiter_entry(delim_type, entry_frame, var))
        remove_btn.pack(side=tk.LEFT, padx=(2, 0))
        
        # Store the entry data
        self.delimiter_data[delim_type]["entries"].append({
            "frame": entry_frame,
            "var": var
        })
        
        return var
    
    def add_delimiter_entry(self, delim_type):
        """Add a new delimiter entry for the specified type"""
        self.create_delimiter_entry(delim_type, "")
    
    def remove_delimiter_entry(self, delim_type, frame, var):
        """Remove a delimiter entry"""
        # Find and remove from entries list
        entries = self.delimiter_data[delim_type]["entries"]
        for i, entry in enumerate(entries):
            if entry["frame"] == frame:
                entries.pop(i)
                break
        
        # Destroy the frame
        frame.destroy()
        
        # Ensure at least one entry remains
        if not entries:
            self.create_delimiter_entry(delim_type, "")
    
    def get_delimiter_values(self, delim_type):
        """Get all delimiter values for a specific type"""
        values = []
        for entry in self.delimiter_data[delim_type]["entries"]:
            value = entry["var"].get().strip()
            if value:
                values.append(value)
        return values if values else [""]
    
    # Category Management Methods
    def on_category_select(self, event):
        """Handle category selection in listbox"""
        pass  # Placeholder for category selection handling
    
    def add_category(self):
        """Add a new category"""
        # Open dialog to add new category
        dialog = CategoryEditDialog(self.root, "Add Category")
        if dialog.result:
            # Add to listbox and track edited categories
            self.category_listbox.insert(tk.END, dialog.result['name'])
            # Store category data indexed by name
            self.edited_categories[dialog.result['name']] = dialog.result
    
    def edit_category(self):
        """Edit selected category"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a category to edit")
            return
        
        # Get current category data
        index = selection[0]
        current_name = self.category_listbox.get(index)
        
        # Get existing category data from config or edited categories
        existing_data = None
        if current_name in self.edited_categories:
            existing_data = self.edited_categories[current_name]
        elif self.log_viewer and self.log_viewer.config_manager:
            for cat in self.log_viewer.config_manager.categories:
                if cat.name == current_name:
                    existing_data = {
                        'name': cat.name,
                        'type': cat.type,
                        'ColourType': cat.ColourType,
                        'Colouring': cat.Colouring,
                        'ColourMap': cat.ColourMap,
                        'description': getattr(cat, 'description', '')
                    }
                    break
        
        # Open dialog with current values
        dialog = CategoryEditDialog(self.root, "Edit Category", existing_data)
        if dialog.result:
            # If name changed, remove old entry from edited_categories
            if current_name != dialog.result['name'] and current_name in self.edited_categories:
                del self.edited_categories[current_name]
            
            # Update listbox and store edited data
            self.category_listbox.delete(index)
            self.category_listbox.insert(index, dialog.result['name'])
            self.edited_categories[dialog.result['name']] = dialog.result
    
    def delete_category(self):
        """Delete selected category"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a category to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this category?"):
            index = selection[0]
            category_name = self.category_listbox.get(index)
            # Remove from edited categories if present
            if category_name in self.edited_categories:
                del self.edited_categories[category_name]
            self.category_listbox.delete(index)
    
    def move_category_up(self):
        """Move selected category up in order"""
        selection = self.category_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        index = selection[0]
        item = self.category_listbox.get(index)
        self.category_listbox.delete(index)
        self.category_listbox.insert(index - 1, item)
        self.category_listbox.selection_set(index - 1)
    
    def move_category_down(self):
        """Move selected category down in order"""
        selection = self.category_listbox.curselection()
        if not selection or selection[0] == self.category_listbox.size() - 1:
            return
        
        index = selection[0]
        item = self.category_listbox.get(index)
        self.category_listbox.delete(index)
        self.category_listbox.insert(index + 1, item)
        self.category_listbox.selection_set(index + 1)
    
    # Auto-refresh Methods
    def toggle_auto_refresh(self, tab_id):
        """Toggle auto-refresh for a specific tab"""
        if tab_id not in self.tabs:
            return
        
        tab_data = self.tabs[tab_id]
        if tab_data['auto_refresh_var'].get():
            # Start auto-refresh
            self.start_auto_refresh(tab_id)
        else:
            # Stop auto-refresh
            self.stop_auto_refresh(tab_id)
    
    def start_auto_refresh(self, tab_id):
        """Start auto-refresh timer for a tab"""
        if tab_id not in self.tabs:
            return
        
        tab_data = self.tabs[tab_id]
        
        def refresh():
            if tab_id in self.tabs and tab_data['auto_refresh_var'].get():
                try:
                    if tab_data.get('folder_path'):
                        # Folder-based tab - check for new files and reload existing ones
                        self.refresh_folder_tab(tab_id)
                    elif tab_data.get('file_path'):
                        # Single file tab
                        tab_data['log_viewer'].load_file(tab_data['file_path'])
                        if self.active_tab == tab_id:
                            self.refresh_display()
                    elif tab_data.get('merged_files'):
                        # Merged files tab
                        self.refresh_merged_tab(tab_id)
                except:
                    pass  # Silently ignore errors during auto-refresh
                
                # Schedule next refresh
                interval = int(tab_data['refresh_interval_var'].get() or 5) * 1000
                tab_data['refresh_timer'] = self.root.after(interval, refresh)
        
        # Start the refresh cycle
        refresh()
    
    def stop_auto_refresh(self, tab_id):
        """Stop auto-refresh timer for a tab"""
        if tab_id not in self.tabs:
            return
        
        tab_data = self.tabs[tab_id]
        if tab_data['refresh_timer']:
            self.root.after_cancel(tab_data['refresh_timer'])
            tab_data['refresh_timer'] = None
    
    def refresh_folder_tab(self, tab_id):
        """Refresh a folder-based tab, checking for new files"""
        if tab_id not in self.tabs:
            return
        
        tab_data = self.tabs[tab_id]
        folder_path = tab_data.get('folder_path')
        log_filters = tab_data.get('log_filters', ['.txt', '.log'])
        
        if not folder_path:
            return
        
        try:
            # Find current log files in folder
            current_files = set()
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if any(file.lower().endswith(ext.lower()) for ext in log_filters):
                        current_files.add(os.path.join(root, file))
            
            # For single file tabs from folder, just reload the existing file
            if tab_data.get('file_path'):
                # Check if the file still exists
                if tab_data['file_path'] in current_files:
                    tab_data['log_viewer'].load_file(tab_data['file_path'])
                    if self.active_tab == tab_id:
                        self.refresh_display()
                # Note: We don't add new files to individual file tabs
        except Exception as e:
            pass  # Silently handle errors
    
    def refresh_merged_tab(self, tab_id):
        """Refresh a merged files tab, including new files from folder"""
        if tab_id not in self.tabs:
            return
        
        tab_data = self.tabs[tab_id]
        folder_path = tab_data.get('folder_path')
        log_filters = tab_data.get('log_filters', ['.txt', '.log'])
        
        try:
            if folder_path:
                # Folder-based merged tab - scan for all files including new ones
                current_files = []
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        if any(file.lower().endswith(ext.lower()) for ext in log_filters):
                            current_files.append(os.path.join(root, file))
                
                # Check if we have new files
                old_files = set(tab_data.get('merged_files', []))
                new_files = set(current_files)
                
                if new_files != old_files:
                    # Files have changed, reload everything
                    self.reload_merged_files(tab_id, current_files)
                    tab_data['merged_files'] = current_files
            else:
                # Fixed file list - just reload existing files
                merged_files = tab_data.get('merged_files', [])
                if merged_files:
                    self.reload_merged_files(tab_id, merged_files)
        except Exception as e:
            pass  # Silently handle errors
    
    def reload_merged_files(self, tab_id, file_paths):
        """Reload and merge files for a tab"""
        if tab_id not in self.tabs or not file_paths:
            return
        
        tab_data = self.tabs[tab_id]
        tab_log_viewer = tab_data['log_viewer']
        
        try:
            all_logs = []
            for file_path in file_paths:
                if os.path.exists(file_path):  # Only load existing files
                    temp_viewer = LogViewer(config_dict=tab_log_viewer.config_manager.config)
                    temp_viewer.load_file(file_path)
                    all_logs.extend(temp_viewer.logs)
            
            # Sort merged logs by timestamp if possible
            try:
                all_logs.sort(key=lambda log: log.get_field('Timestamp') or '')
            except:
                pass  # If sorting fails, keep original order
            
            # Update the tab's log viewer
            tab_log_viewer.logs = all_logs
            tab_log_viewer.filtered_logs = all_logs.copy()
            
            # Refresh display if this is the active tab
            if self.active_tab == tab_id:
                self.refresh_display()
        except Exception as e:
            pass  # Silently handle errors
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


class CategoryEditDialog:
    """Simple dialog for editing category properties"""
    def __init__(self, parent, title, initial_data=None):
        self.result = None
        
        # Initialize with existing data or defaults
        if isinstance(initial_data, str):
            # Legacy: if string passed, treat as initial name only
            self.initial_data = {'name': initial_data, 'type': 'string'}
        elif isinstance(initial_data, dict):
            self.initial_data = initial_data
        else:
            self.initial_data = {'name': '', 'type': 'string'}
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Name field
        ttk.Label(self.dialog, text="Category Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar(value=self.initial_data.get('name', ''))
        ttk.Entry(self.dialog, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Type field
        ttk.Label(self.dialog, text="Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.type_var = tk.StringVar(value=self.initial_data.get('type', 'string'))
        type_combo = ttk.Combobox(self.dialog, textvariable=self.type_var, 
                                 values=["string", "number", "datetime"], state="readonly")
        type_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Description field
        ttk.Label(self.dialog, text="Description:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.description_var = tk.StringVar(value=self.initial_data.get('description', ''))
        ttk.Entry(self.dialog, textvariable=self.description_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # Color configuration frame
        color_frame = ttk.LabelFrame(self.dialog, text="Color Configuration (Optional)", padding=5)
        color_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        
        # Color type
        ttk.Label(color_frame, text="Color Type:").grid(row=0, column=0, sticky=tk.W)
        self.color_type_var = tk.StringVar(value=self.initial_data.get('ColourType', ''))
        color_type_combo = ttk.Combobox(color_frame, textvariable=self.color_type_var,
                    values=["", "WholeLine", "LineNumber", "SpecificValue"],
                    state="readonly", width=15)
        color_type_combo.grid(row=0, column=1, sticky=tk.W)
        
        # Coloring (Text/Background)
        ttk.Label(color_frame, text="Coloring:").grid(row=1, column=0, sticky=tk.W)
        self.coloring_var = tk.StringVar(value=self.initial_data.get('Colouring', 'Text'))
        ttk.Combobox(color_frame, textvariable=self.coloring_var,
                    values=["Text", "Background"],
                    state="readonly", width=15).grid(row=1, column=1, sticky=tk.W)
        
        # ColourMap section
        ttk.Label(color_frame, text="Color Mappings:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        # Color map list frame
        map_list_frame = ttk.Frame(color_frame)
        map_list_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        # Listbox for color mappings
        self.colormap_listbox = tk.Listbox(map_list_frame, height=4)
        self.colormap_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for listbox
        colormap_scroll = ttk.Scrollbar(map_list_frame, orient=tk.VERTICAL, command=self.colormap_listbox.yview)
        colormap_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.colormap_listbox.config(yscrollcommand=colormap_scroll.set)
        
        # Color map buttons
        colormap_btn_frame = ttk.Frame(color_frame)
        colormap_btn_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        ttk.Button(colormap_btn_frame, text="Add Mapping", command=self.add_color_mapping).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(colormap_btn_frame, text="Edit Mapping", command=self.edit_color_mapping).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(colormap_btn_frame, text="Delete Mapping", command=self.delete_color_mapping).pack(side=tk.LEFT)
        
        # Initialize color mappings
        self.color_mappings = self.initial_data.get('ColourMap', {}).copy()
        self.refresh_colormap_listbox()
        
        # Bind color type change to show/hide color map controls
        color_type_combo.bind('<<ComboboxSelected>>', self.on_color_type_change)
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Wait for dialog
        self.dialog.wait_window()
    
    def ok_clicked(self):
        """Handle OK button click"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Invalid Input", "Category name is required")
            return
        
        self.result = {
            'name': name,
            'type': self.type_var.get()
        }
        
        # Add description if provided
        description = self.description_var.get().strip()
        if description:
            self.result['description'] = description
        
        if self.color_type_var.get():
            self.result['ColourType'] = self.color_type_var.get()
            self.result['Colouring'] = self.coloring_var.get()
            # Only include ColourMap if there are mappings
            if self.color_mappings:
                self.result['ColourMap'] = self.color_mappings
        
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.dialog.destroy()
    
    def refresh_colormap_listbox(self):
        """Refresh the color mappings listbox"""
        self.colormap_listbox.delete(0, tk.END)
        for rgb_color, value in self.color_mappings.items():
            display_text = f"{rgb_color} → {value}"
            self.colormap_listbox.insert(tk.END, display_text)
    
    def on_color_type_change(self, event=None):
        """Handle color type selection change"""
        # Could be used to show/hide different controls based on color type
        pass
    
    def add_color_mapping(self):
        """Add a new color mapping"""
        dialog = ColorMappingDialog(self.dialog, "Add Color Mapping")
        if dialog.result:
            rgb_color, value = dialog.result
            self.color_mappings[rgb_color] = value
            self.refresh_colormap_listbox()
    
    def edit_color_mapping(self):
        """Edit selected color mapping"""
        selection = self.colormap_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a color mapping to edit")
            return
        
        # Get selected mapping
        index = selection[0]
        rgb_colors = list(self.color_mappings.keys())
        if index < len(rgb_colors):
            rgb_color = rgb_colors[index]
            value = self.color_mappings[rgb_color]
            
            dialog = ColorMappingDialog(self.dialog, "Edit Color Mapping", (rgb_color, value))
            if dialog.result:
                new_rgb, new_value = dialog.result
                # Remove old mapping if color changed
                if rgb_color != new_rgb:
                    del self.color_mappings[rgb_color]
                self.color_mappings[new_rgb] = new_value
                self.refresh_colormap_listbox()
    
    def delete_color_mapping(self):
        """Delete selected color mapping"""
        selection = self.colormap_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a color mapping to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this color mapping?"):
            index = selection[0]
            rgb_colors = list(self.color_mappings.keys())
            if index < len(rgb_colors):
                del self.color_mappings[rgb_colors[index]]
                self.refresh_colormap_listbox()


class ColorMappingDialog:
    """Dialog for editing color mappings"""
    def __init__(self, parent, title, initial_data=None):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("350x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Initialize data
        if initial_data:
            rgb_color, value = initial_data
        else:
            rgb_color, value = "255,0,0", ""
        
        # RGB Color field with auto-refresh
        ttk.Label(self.dialog, text="RGB Color (r,g,b):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.rgb_var = tk.StringVar(value=rgb_color)
        rgb_entry = ttk.Entry(self.dialog, textvariable=self.rgb_var, width=15)
        rgb_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Bind auto-refresh to RGB field changes
        self.rgb_var.trace('w', self.on_rgb_change)
        
        # Color preview button
        self.color_button = tk.Button(self.dialog, text="Preview", width=8, command=self.preview_color)
        self.color_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Value field
        ttk.Label(self.dialog, text="Match Value:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.value_var = tk.StringVar(value=value)
        value_entry = ttk.Entry(self.dialog, textvariable=self.value_var, width=25)
        value_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        
        # Help text
        help_text = "Examples:\n" \
                   "• String match: 'ERROR' or 'DatabaseService'\n" \
                   "• Number range: '1000-2000' or single value '0'\n" \
                   "• Array of values: 'ERROR,CRITICAL,FATAL' (comma-separated)"
        help_label = ttk.Label(self.dialog, text=help_text, font=("TkDefaultFont", 8), foreground="gray")
        help_label.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT)
        
        # Set initial color preview
        self.preview_color()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Wait for dialog
        self.dialog.wait_window()
    
    def on_rgb_change(self, *args):
        """Auto-refresh color preview when RGB values change"""
        self.preview_color()
    
    def preview_color(self):
        """Preview the color based on RGB values"""
        try:
            rgb_string = self.rgb_var.get().strip()
            if not rgb_string:
                self.color_button.config(bg="#FFFFFF", text="Preview")
                return
                
            r, g, b = map(int, rgb_string.split(','))
            # Ensure RGB values are in valid range
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self.color_button.config(bg=hex_color, text="")
        except (ValueError, IndexError):
            self.color_button.config(bg="#FFFFFF", text="Invalid")
    
    def ok_clicked(self):
        """Handle OK button click"""
        rgb_color = self.rgb_var.get().strip()
        value = self.value_var.get().strip()
        
        if not rgb_color or not value:
            messagebox.showwarning("Invalid Input", "Both RGB color and match value are required")
            return
        
        # Validate RGB format
        try:
            r, g, b = map(int, rgb_color.split(','))
            if not all(0 <= c <= 255 for c in [r, g, b]):
                raise ValueError("RGB values must be 0-255")
        except (ValueError, IndexError) as e:
            messagebox.showwarning("Invalid RGB", "RGB color must be in format 'r,g,b' with values 0-255")
            return
        
        self.result = (rgb_color, value)
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.dialog.destroy()


def main():
    """Main entry point for GUI application"""
    app = LogViewerGUI()
    app.run()


if __name__ == "__main__":
    main()