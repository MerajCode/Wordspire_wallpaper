import tkinter as tk
from tkinter import ttk, messagebox
import controller as database
import os
import sys
import threading
import win32com.client
import pystray
from PIL import Image, ImageDraw

__version__ = "1.0.0"

# Globle Variables
service_thread = None
stop_event = threading.Event()
root = None

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.getenv("APPDATA"), "Wordspire_by_merajcode")
    else:
        return os.path.dirname(os.path.abspath(__file__))

def hide_window():
    if root: root.withdraw()

def show_window(icon=None, item=None):
    if root:
        root.after(0, root.deiconify)
        root.after(100, root.lift)
        root.after(200, root.focus_force)

def quit_app(icon=None, item=None):
    if stop_event: stop_event.set()
    if icon: icon.stop()
    if root: root.quit(); root.destroy()
    sys.exit()

def create_tray_icon():
    def run_tray():
        base_path = get_base_path()
        try:
            image = Image.open(os.path.join(base_path, "icon.ico"))
        except Exception:
            image = Image.new('RGB', (64, 64), color='white')
            draw = Image.Draw(image)
            draw.text((20, 20), "W", fill="#007acc", font_size=32)
        
        menu = pystray.Menu(pystray.MenuItem("Open Wordspire", show_window, default=True), pystray.MenuItem("Exit", quit_app))
        icon = pystray.Icon("Wordspire", image, "Wordspire Wallpaper", menu)
        icon.run()

    threading.Thread(target=run_tray, daemon=False).start()

def create_startup_shortcut():
    startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    exe_path = sys.executable
    shortcut_path = os.path.join(startup_path, "Wordspire.lnk")
    if os.path.exists(shortcut_path): return
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = exe_path
    shortcut.Arguments = "--background"
    shortcut.WorkingDirectory = os.path.dirname(exe_path)
    shortcut.IconLocation = exe_path
    shortcut.save()

def start_service():
    global service_thread
    if service_thread and service_thread.is_alive():
        messagebox.showinfo("Info", "Service is already running.", parent=root)
        return
    import background_service
    stop_event.clear()
    service_thread = threading.Thread(target=background_service.start_monitoring, args=(None, stop_event), daemon=True)
    service_thread.start()
    create_startup_shortcut()
    if root: root.update_service_status()

def stop_service():
    if service_thread and service_thread.is_alive():
        stop_event.set()
        messagebox.showinfo("Info", "Service has been stopped.", parent=root)
    if root: root.update_service_status()

# Main Style css
class Theme:
    BG_COLOR = "#202020"; FG_COLOR = "#e0e0e0"; FRAME_COLOR = "#2d2d2d"; NAV_COLOR = "#252526"
    BTN_BG = "#007acc"; BTN_FG = "white"; BTN_ACTIVE_BG = "#005f9e"
    BTN_DANGER_BG = "#c43838"
    TREE_BG = "#2a2a2a"; TREE_FG = "#cccccc"; TREE_HEADING_BG = "#3e3e42"
    TREE_HEADING_FG = "#569cd6"; TREE_ROW_SELECTED = "#094771"
    STATUS_RUNNING_FG = "#38c46c"; STATUS_STOPPED_FG = "#f44336"
    NAV_BTN_BG = "#333333"; NAV_BTN_ACTIVE_BG = "#004c8c"
    FONT_LARGE = ("Segoe UI", 16, "bold"); FONT_NORMAL = ("Segoe UI", 10); FONT_BOLD = ("Segoe UI", 10, "bold")

# Dialog window
class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title, fields_with_values={}):
        super().__init__(parent)
        self.title(title); self.configure(bg=Theme.FRAME_COLOR, padx=20, pady=20); self.resizable(False, False)
        self.transient(parent); self.grab_set(); self.result = None; self.entries = {}
        frame = ttk.Frame(self, style="Dark.TFrame"); frame.pack(fill="both", expand=True)
        for i, (field, value) in enumerate(fields_with_values.items()):
            label = ttk.Label(frame, text=f"{field}:", style="Dark.TLabel"); label.grid(row=i, column=0, sticky="w", pady=5, padx=5)
            entry = ttk.Entry(frame, width=50, font=Theme.FONT_NORMAL, style="Dark.TEntry"); entry.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
            entry.insert(0, value); self.entries[field] = entry
        btn_frame = ttk.Frame(frame, style="Dark.TFrame"); btn_frame.grid(row=len(fields_with_values), columnspan=2, pady=(20, 0))
        save_btn = ttk.Button(btn_frame, text="✔ Save", command=self.on_save, style="Accent.TButton"); save_btn.pack(side="left", padx=10)
        cancel_btn = ttk.Button(btn_frame, text="❌ Cancel", command=self.destroy); cancel_btn.pack(side="left", padx=10)
        self._center_window(); self.wait_window(self)

    def _center_window(self):
        self.update_idletasks(); parent = self.master
        self.geometry(f"+{parent.winfo_x()+(parent.winfo_width()//2)-(self.winfo_width()//2)}+{parent.winfo_y()+(parent.winfo_height()//2)-(self.winfo_height()//2)}")

    def on_save(self):
        self.result = {field: entry.get().strip() for field, entry in self.entries.items()}
        if not self.result[list(self.result.keys())[0]]:
            messagebox.showerror("Validation Error", f"'{list(self.result.keys())[0]}' cannot be empty.", parent=self); return
        self.destroy()

# Page template
class BasePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Dark.TFrame")
        self.controller = controller; self.create_widgets(); self.refresh_data()
    def create_widgets(self): raise NotImplementedError
    def on_item_select(self, event=None):
        state = "normal" if self.tree.selection() else "disabled"
        self.edit_btn.config(state=state); self.delete_btn.config(state=state)
    def refresh_data(self): self.on_item_select()

class QuotesPage(BasePage):
    def create_widgets(self):
        tree_frame = ttk.Frame(self, style="Dark.TFrame"); tree_frame.pack(fill="both", expand=True, pady=(0, 10))
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Quote"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=50, stretch=False, anchor="center")
        self.tree.heading("Quote", text="Quote"); self.tree.column("Quote", width=600)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=scrollbar.set); scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self.edit_item() if self.tree.focus() else None); self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        btn_frame = ttk.Frame(self, style="Dark.TFrame"); btn_frame.pack(fill="x")
        self.add_btn = ttk.Button(btn_frame, text="⊕ Add Quote", command=self.add_item, style="Accent.TButton")
        self.edit_btn = ttk.Button(btn_frame, text="✏ Edit", command=self.edit_item)
        self.delete_btn = ttk.Button(btn_frame, text="🗑 Delete", command=self.delete_item)
        self.add_btn.pack(side="left"); self.edit_btn.pack(side="left", padx=5); self.delete_btn.pack(side="left")
    def refresh_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for row in database.get_all_quotes(): self.tree.insert("", "end", values=row)
        super().refresh_data()
    def add_item(self):
        dialog = CustomDialog(self, "Add New Quote", {"Quote": ""}); 
        if dialog.result: database.add_quote(dialog.result["Quote"]); self.refresh_data()
    def edit_item(self):
        if not self.tree.focus(): return
        item = self.tree.item(self.tree.focus(), 'values')
        dialog = CustomDialog(self, "Edit Quote", {"Quote": item[1]})
        if dialog.result: database.update_quote(item[0], dialog.result["Quote"]); self.refresh_data()
    def delete_item(self):
        if not self.tree.focus(): return
        if messagebox.askyesno("Confirm", f"Delete quote ID {self.tree.item(self.tree.focus(),'values')[0]}?"):
            database.delete_quote(self.tree.item(self.tree.focus(),'values')[0]); self.refresh_data()

class VocabPage(BasePage):
    def create_widgets(self):
        tree_frame = ttk.Frame(self, style="Dark.TFrame"); tree_frame.pack(fill="both", expand=True, pady=(0, 10))
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Word", "Meaning", "Example"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=50, stretch=False, anchor="center")
        self.tree.heading("Word", text="Word"); self.tree.column("Word", width=150)
        self.tree.heading("Meaning", text="Meaning"); self.tree.column("Meaning", width=250)
        self.tree.heading("Example", text="Example"); self.tree.column("Example", width=300)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=scrollbar.set); scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self.edit_item() if self.tree.focus() else None); self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        btn_frame = ttk.Frame(self, style="Dark.TFrame"); btn_frame.pack(fill="x")
        self.add_btn = ttk.Button(btn_frame, text="⊕ Add Word", command=self.add_item, style="Accent.TButton")
        self.edit_btn = ttk.Button(btn_frame, text="✏ Edit", command=self.edit_item)
        self.delete_btn = ttk.Button(btn_frame, text="🗑 Delete", command=self.delete_item)
        self.add_btn.pack(side="left"); self.edit_btn.pack(side="left", padx=5); self.delete_btn.pack(side="left")
    def refresh_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for row in database.get_all_vocab(): self.tree.insert("", "end", values=row)
        super().refresh_data()
    def add_item(self):
        dialog = CustomDialog(self, "Add New Word", {"Word": "", "Meaning": "", "Example": ""})
        if dialog.result: database.add_vocab(dialog.result["Word"], dialog.result["Meaning"], dialog.result["Example"]); self.refresh_data()
    def edit_item(self):
        if not self.tree.focus(): return
        item = self.tree.item(self.tree.focus(), 'values')
        dialog = CustomDialog(self, "Edit Word", {"Word": item[1], "Meaning": item[2], "Example": item[3]})
        if dialog.result: database.update_vocab(item[0], dialog.result["Word"], dialog.result["Meaning"], dialog.result["Example"]); self.refresh_data()
    def delete_item(self):
        if not self.tree.focus(): return
        if messagebox.askyesno("Confirm", f"Delete vocab ID {self.tree.item(self.tree.focus(),'values')[0]}?"):
            database.delete_vocab(self.tree.item(self.tree.focus(),'values')[0]); self.refresh_data()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Wordspire Wallpaper"); self.geometry("950x600"); self.configure(bg=Theme.BG_COLOR)
        try:
            self.iconbitmap(default=os.path.join(get_base_path(), "icon.ico"))
        except tk.TclError:
            print("icon.ico not found.")

        self.eval('tk::PlaceWindow . center'); self.setup_styles(); self.protocol("WM_DELETE_WINDOW", hide_window)

        main_frame = ttk.Frame(self, style="Dark.TFrame"); main_frame.pack(fill="both", expand=True)
        nav_pane = ttk.Frame(main_frame, width=200, style="Nav.TFrame")
        nav_pane.pack(side="left", fill="y", padx=(5, 3), pady=5); nav_pane.pack_propagate(False)
        content_pane = ttk.Frame(main_frame, style="Dark.TFrame")
        content_pane.pack(side="right", fill="both", expand=True, pady=5, padx=(3, 5))
        content_pane.grid_rowconfigure(0, weight=1); content_pane.grid_columnconfigure(0, weight=1)

        title_label = ttk.Label(nav_pane, text="Wordspire", style="Header.TLabel", background=Theme.NAV_COLOR)
        title_label.pack(pady=20, padx=20)

        self.nav_buttons = {}
        quotes_btn = ttk.Button(nav_pane, text="📖 Quotes", command=lambda: self.show_frame("QuotesPage"), style="Nav.TButton", compound="left", padding=(0, 6, 0, 6))
        quotes_btn.pack(fill="x", padx=10, pady=2); self.nav_buttons["QuotesPage"] = quotes_btn
        vocab_btn = ttk.Button(nav_pane, text="📚 Vocabulary", command=lambda: self.show_frame("VocabPage"), style="Nav.TButton", compound="left", padding=(0, 6, 0, 6))
        vocab_btn.pack(fill="x", padx=10, pady=2); self.nav_buttons["VocabPage"] = vocab_btn
        
        ttk.Separator(nav_pane, orient="horizontal").pack(fill='x', pady=20, padx=10)
        
        self.service_toggle_btn = ttk.Button(nav_pane, command=self.toggle_service, style="Accent.TButton")
        self.service_toggle_btn.pack(fill="x", padx=10, pady=2, ipady=4)

        #about software https://www.youtube.com/@merajcode
        ttk.Separator(nav_pane, orient="horizontal").pack(fill='x', pady=20, padx=10)
        info_frame = ttk.Frame(nav_pane, style="Nav.TFrame")
        info_frame.pack(fill='x', padx=10, pady=15)

        my_title_label = ttk.Label(
            info_frame,
            text="About Wordspire",
            font=Theme.FONT_BOLD,
            background=Theme.NAV_COLOR,
            foreground="#ffffff" 
        )
        my_title_label.pack(anchor="w", pady=(0, 5))

        my_paragraph_label = ttk.Label(
            info_frame,
            text="This application is build by merajcode this helps you learn new words and get inspired by quotes every day, right on your desktop.\n\n",
            background=Theme.NAV_COLOR,
            wraplength=160, 
            justify="left" 
        )
        my_paragraph_label.pack(anchor="w")
        detail_paragraph_label = ttk.Label(
            info_frame,
            text="Youtube: https://www.youtube.com/@merajcode \n Github: https://github.com/merajcode \n\n App Version : 1.0.0", 
            background=Theme.NAV_COLOR,
            wraplength=160,
            justify="left",  
            font=("Segoe UI", 7)
        )
        detail_paragraph_label.pack(anchor="w")
        
        self.service_status_var = tk.StringVar(value="Service: Stopped")
        status_label = ttk.Label(nav_pane, textvariable=self.service_status_var, background=Theme.NAV_COLOR, font=Theme.FONT_BOLD, anchor="w", padding=(10,0,0,0))
        status_label.pack(side="bottom", fill="x", pady=10); self.status_label = status_label

        self.frames = {}
        for F in (QuotesPage, VocabPage):
            page_name = F.__name__; frame = F(parent=content_pane, controller=self)
            self.frames[page_name] = frame; frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.show_frame("QuotesPage"); self.update_service_status()

    def toggle_service(self):
        if service_thread and service_thread.is_alive(): stop_service()
        else: start_service()
        self.update_service_status()

    def update_service_status(self):
        if service_thread and service_thread.is_alive():
            self.service_status_var.set("● Service: Running")
            self.status_label.config(foreground=Theme.STATUS_RUNNING_FG)
            self.service_toggle_btn.config(text="❌ Disable Service", style="Danger.TButton")
        else:
            self.service_status_var.set("● Service: Stopped")
            self.status_label.config(foreground=Theme.STATUS_STOPPED_FG)
            self.service_toggle_btn.config(text="✔ Enable Service", style="Accent.TButton")
        self.after(2000, self.update_service_status)

    def setup_styles(self):
        style = ttk.Style(); style.theme_use("clam")
        style.configure(".", background=Theme.BG_COLOR, foreground=Theme.FG_COLOR, font=Theme.FONT_NORMAL, borderwidth=0)
        style.configure("Dark.TFrame", background=Theme.FRAME_COLOR); style.configure("Nav.TFrame", background=Theme.NAV_COLOR)
        style.configure("TLabel", background=Theme.BG_COLOR); style.configure("Dark.TLabel", background=Theme.FRAME_COLOR)
        style.configure("Header.TLabel", font=Theme.FONT_LARGE, foreground="#ffffff")
        style.configure("TButton", padding=8, font=Theme.FONT_BOLD, borderwidth=0, relief="flat")
        style.map("TButton", background=[('active', Theme.BTN_ACTIVE_BG), ('disabled', '#555')])
        style.configure("Accent.TButton", background=Theme.BTN_BG)
        style.configure("Danger.TButton", background=Theme.BTN_DANGER_BG)
        style.configure("Nav.TButton", background=Theme.NAV_BTN_BG, font=Theme.FONT_BOLD, padding=(10, 0))
        style.map("Nav.TButton", background=[('active', Theme.BTN_ACTIVE_BG)])
        style.configure("Selected.Nav.TButton", background=Theme.NAV_BTN_ACTIVE_BG, font=Theme.FONT_BOLD, padding=(10, 0))
        style.configure("TEntry", fieldbackground=Theme.BG_COLOR, foreground=Theme.FG_COLOR, insertcolor=Theme.FG_COLOR, borderwidth=2, relief="solid")
        style.map("TEntry", bordercolor=[('focus', Theme.BTN_BG)])
        style.configure("Treeview", background=Theme.TREE_BG, foreground=Theme.TREE_FG, fieldbackground=Theme.TREE_BG, rowheight=28)
        style.map("Treeview", background=[('selected', Theme.TREE_ROW_SELECTED)])
        style.configure("Treeview.Heading", font=Theme.FONT_BOLD, background=Theme.TREE_HEADING_BG, foreground=Theme.TREE_HEADING_FG, padding=10, relief="flat")

    def show_frame(self, page_name):
        for name, button in self.nav_buttons.items():
            button.config(style="Selected.Nav.TButton" if name == page_name else "Nav.TButton")
        frame = self.frames[page_name]; frame.tkraise(); frame.refresh_data()

# main startup function
if __name__ == "__main__":
    database.initialize_db()
    root = App()
    create_tray_icon()
    if "--background" in sys.argv:
        root.withdraw()
        start_service()
    root.mainloop()