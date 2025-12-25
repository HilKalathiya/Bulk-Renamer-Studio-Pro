import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, simpledialog
import pandas as pd

# --- CONFIGURATION & ASSETS ---
COLORS = {
    "bg": "#121212",  # Very Dark Grey (Main BG)
    "surface": "#1e1e1e",  # Card BG
    "surface_light": "#2c2c2c",  # Hover/Input BG
    "primary": "#03dac6",  # Teal Accent (2025 Trend)
    "primary_hover": "#018786",
    "on_primary": "#000000",
    "error": "#cf6679",
    "text_main": "#ffffff",
    "text_dim": "#b0b0b0",
    "border": "#333333",
}

FONTS = {
    "h1": ("Segoe UI", 20, "bold"),
    "h2": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 10),
    "bold": ("Segoe UI", 10, "bold"),
    "mono": ("Consolas", 9),
}

# --- MODERN WIDGETS ---


class ModernButton(tk.Button):
    def __init__(self, master, text, command, type="primary"):
        bg = COLORS["primary"] if type == "primary" else COLORS["surface_light"]
        fg = COLORS["on_primary"] if type == "primary" else COLORS["text_main"]
        hover = COLORS["primary_hover"] if type == "primary" else "#3d3d3d"

        super().__init__(
            master,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            font=FONTS["bold"],
            relief="flat",
            bd=0,
            cursor="hand2",
            pady=10,
            padx=20,
        )

        self.default_bg = bg
        self.hover_bg = hover
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.config(bg=self.hover_bg)

    def on_leave(self, e):
        self.config(bg=self.default_bg)


class SidebarButton(tk.Button):
    def __init__(self, master, text, command, is_active=False):
        bg = COLORS["surface_light"] if is_active else COLORS["bg"]
        fg = COLORS["primary"] if is_active else COLORS["text_dim"]

        super().__init__(
            master,
            text=f"  {text}",
            command=command,
            bg=bg,
            fg=fg,
            anchor="w",
            font=("Segoe UI", 11),
            relief="flat",
            bd=0,
            cursor="hand2",
            pady=12,
            padx=15,
        )

        self.default_bg = bg
        self.active = is_active
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def set_active(self, active):
        self.active = active
        if active:
            self.config(bg=COLORS["surface_light"], fg=COLORS["primary"])
            self.default_bg = COLORS["surface_light"]
        else:
            self.config(bg=COLORS["bg"], fg=COLORS["text_dim"])
            self.default_bg = COLORS["bg"]

    def on_enter(self, e):
        if not self.active:
            self.config(bg="#1a1a1a", fg="white")

    def on_leave(self, e):
        self.config(
            bg=self.default_bg,
            fg=COLORS["primary"] if self.active else COLORS["text_dim"],
        )


class ModernEntry(tk.Entry):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(
            bg=COLORS["surface_light"],
            fg="white",
            insertbackground="white",
            relief="flat",
            font=FONTS["body"],
        )
        self.bind("<FocusIn>", self.on_focus)
        self.bind("<FocusOut>", self.on_blur)

    def on_focus(self, e):
        self.config(bg="#3a3a3a")

    def on_blur(self, e):
        self.config(bg=COLORS["surface_light"])


class Card(tk.Frame):
    def __init__(self, master, title=None):
        super().__init__(master, bg=COLORS["surface"], padx=20, pady=20)
        if title:
            tk.Label(
                self,
                text=title.upper(),
                bg=COLORS["surface"],
                fg=COLORS["primary"],
                font=("Segoe UI", 9, "bold"),
            ).pack(anchor="w", pady=(0, 15))


# --- MAIN APP ---


class UltimateRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Renamer Studio 2025")
        self.root.geometry("1200x850")
        self.root.configure(bg=COLORS["bg"])

        # Data & State
        self.df = None
        self.folder_isrc_cache = {}
        self.init_vars()
        self.style_ui()

        # Layout: Sidebar + Content
        self.setup_sidebar()
        self.setup_content_area()

        # Default View
        self.show_excel_view()

    def init_vars(self):
        # Excel Vars
        self.excel_path = tk.StringVar()
        self.root_folder_path = tk.StringVar()
        self.var_enable_isrc = tk.BooleanVar(value=True)
        # Utility Vars
        self.util_folder_path = tk.StringVar()
        self.util_find = tk.StringVar()
        self.util_replace = tk.StringVar()
        self.util_prefix = tk.StringVar()
        self.util_suffix = tk.StringVar()
        self.util_case = tk.StringVar(value="No Change")
        self.util_num_enable = tk.BooleanVar(value=False)
        self.util_num_start = tk.IntVar(value=1)

    def style_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        # Combobox
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["surface_light"],
            background=COLORS["surface"],
            foreground="white",
            arrowcolor="white",
            borderwidth=0,
        )
        style.map("TCombobox", fieldbackground=[("readonly", COLORS["surface_light"])])

        # Treeview
        style.configure(
            "Treeview",
            background=COLORS["surface_light"],
            foreground="white",
            fieldbackground=COLORS["surface_light"],
            borderwidth=0,
            rowheight=30,
            font=FONTS["body"],
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["surface"],
            foreground="white",
            font=FONTS["bold"],
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["primary"])],
            foreground=[("selected", "black")],
        )

    def setup_sidebar(self):
        # Sidebar Frame
        self.sidebar = tk.Frame(self.root, bg=COLORS["bg"], width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)  # Force width

        # App Title
        tk.Label(
            self.sidebar,
            text="Renamer\nStudio",
            justify="left",
            bg=COLORS["bg"],
            fg="white",
            font=("Segoe UI", 24, "bold"),
        ).pack(anchor="w", padx=20, pady=(30, 40))

        # Nav Buttons
        self.btn_nav_excel = SidebarButton(
            self.sidebar, "Smart Rename (Excel)", self.show_excel_view, is_active=True
        )
        self.btn_nav_excel.pack(fill="x")

        self.btn_nav_util = SidebarButton(
            self.sidebar,
            "Quick Tools (Utility)",
            self.show_utility_view,
            is_active=False,
        )
        self.btn_nav_util.pack(fill="x")

        # Footer
        tk.Label(
            self.sidebar,
            text="v2.5.0 Stable",
            bg=COLORS["bg"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 8),
        ).pack(side="bottom", anchor="w", padx=20, pady=20)

    def setup_content_area(self):
        self.main_area = tk.Frame(self.root, bg=COLORS["bg"])
        self.main_area.pack(side="left", fill="both", expand=True, padx=30, pady=30)

        # Header
        self.header_label = tk.Label(
            self.main_area,
            text="Dashboard",
            bg=COLORS["bg"],
            fg="white",
            font=FONTS["h1"],
        )
        self.header_label.pack(anchor="w", pady=(0, 20))

        # Dynamic Content Frame
        self.content_frame = tk.Frame(self.main_area, bg=COLORS["bg"])
        self.content_frame.pack(fill="both", expand=True)

    def switch_view(self, view_name):
        # clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if view_name == "excel":
            self.header_label.config(text="Smart Renaming (Excel Source)")
            self.btn_nav_excel.set_active(True)
            self.btn_nav_util.set_active(False)
        else:
            self.header_label.config(text="Quick Utility Tools")
            self.btn_nav_excel.set_active(False)
            self.btn_nav_util.set_active(True)

    # =========================================================================
    # VIEW: EXCEL
    # =========================================================================
    def show_excel_view(self):
        self.switch_view("excel")
        parent = self.content_frame

        # Top Config Card
        card_files = Card(parent, "1. Source Data")
        card_files.pack(fill="x", pady=(0, 20))

        # Grid for inputs
        grid = tk.Frame(card_files, bg=COLORS["surface"])
        grid.pack(fill="x")
        grid.columnconfigure(1, weight=1)  # Entry expands

        # Rows
        self.make_file_input(
            grid, 0, "Excel File:", self.excel_path, self.load_excel_preview
        )
        self.make_file_input(
            grid,
            1,
            "Music Folder:",
            self.root_folder_path,
            lambda: self.browse_folder(self.root_folder_path),
        )

        # Mapping Card
        card_map = Card(parent, "2. Smart Mapping")
        card_map.pack(fill="x", pady=(0, 20))

        map_grid = tk.Frame(card_map, bg=COLORS["surface"])
        map_grid.pack(fill="x")

        self.combo_folder = self.make_combo_field(map_grid, 0, 0, "Folder Column")
        self.combo_filename = self.make_combo_field(
            map_grid, 0, 1, "Current Filename Column"
        )
        self.combo_newname = self.make_combo_field(
            map_grid, 1, 0, "New English Name Column"
        )
        self.combo_isrc = self.make_combo_field(map_grid, 1, 1, "ISRC Column")

        # ISRC Toggle
        tk.Checkbutton(
            card_map,
            text=" Enable Smart ISRC (Ask if missing)",
            variable=self.var_enable_isrc,
            bg=COLORS["surface"],
            fg="white",
            selectcolor=COLORS["bg"],
            activebackground=COLORS["surface"],
            activeforeground="white",
            font=FONTS["body"],
        ).pack(anchor="w", pady=(15, 0))

        # Action Area
        btn_frame = tk.Frame(parent, bg=COLORS["bg"])
        btn_frame.pack(fill="x", pady=(10, 0))

        ModernButton(btn_frame, "START RENAMING PROCESS", self.run_excel_rename).pack(
            fill="x"
        )

        # Log
        self.log_area = scrolledtext.ScrolledText(
            parent,
            height=8,
            bg=COLORS["surface_light"],
            fg=COLORS["primary"],
            bd=0,
            font=FONTS["mono"],
        )
        self.log_area.pack(fill="both", expand=True, pady=20)

    # =========================================================================
    # VIEW: UTILITY
    # =========================================================================
    def show_utility_view(self):
        self.switch_view("util")
        parent = self.content_frame

        # Target Card
        card_target = Card(parent, "Target Selection")
        card_target.pack(fill="x", pady=(0, 20))

        grid = tk.Frame(card_target, bg=COLORS["surface"])
        grid.pack(fill="x")
        grid.columnconfigure(1, weight=1)

        self.make_file_input(
            grid,
            0,
            "Target Folder:",
            self.util_folder_path,
            self.browse_and_preview,
            is_dir=True,
        )

        # Rules Card
        card_rules = Card(parent, "Renaming Rules")
        card_rules.pack(fill="x", pady=(0, 20))

        r_grid = tk.Frame(card_rules, bg=COLORS["surface"])
        r_grid.pack(fill="x")

        # Helper for Rule Inputs
        def rule_field(r, c, lbl, var):
            f = tk.Frame(r_grid, bg=COLORS["surface"])
            f.grid(row=r, column=c, padx=15, pady=10, sticky="ew")
            tk.Label(f, text=lbl, bg=COLORS["surface"], fg=COLORS["text_dim"]).pack(
                anchor="w"
            )
            e = ModernEntry(f, textvariable=var, width=25)
            e.pack(fill="x", ipady=4)
            e.bind("<KeyRelease>", self.update_utility_preview)

        rule_field(0, 0, "Find:", self.util_find)
        rule_field(0, 1, "Replace:", self.util_replace)
        rule_field(1, 0, "Prefix:", self.util_prefix)
        rule_field(1, 1, "Suffix:", self.util_suffix)

        # Extras (Case & Num)
        f_extra = tk.Frame(r_grid, bg=COLORS["surface"])
        f_extra.grid(row=0, column=2, rowspan=2, padx=15, sticky="n")

        tk.Label(
            f_extra, text="Casing:", bg=COLORS["surface"], fg=COLORS["text_dim"]
        ).pack(anchor="w")
        cb_case = ttk.Combobox(
            f_extra,
            textvariable=self.util_case,
            values=["No Change", "UPPERCASE", "lowercase", "Title Case"],
        )
        cb_case.pack(fill="x", pady=(0, 15))
        cb_case.bind("<<ComboboxSelected>>", self.update_utility_preview)

        tk.Checkbutton(
            f_extra,
            text=" Append Number Sequence",
            variable=self.util_num_enable,
            bg=COLORS["surface"],
            fg="white",
            selectcolor=COLORS["bg"],
            activebackground=COLORS["surface"],
            command=self.update_utility_preview,
        ).pack(anchor="w")

        # Preview
        tk.Label(
            parent,
            text="PREVIEW CHANGES",
            bg=COLORS["bg"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        self.tree = ttk.Treeview(
            parent, columns=("Old", "New", "Status"), show="headings", height=8
        )
        self.tree.heading("Old", text="Original Name")
        self.tree.heading("New", text="New Name")
        self.tree.heading("Status", text="Status")
        self.tree.column("Old", width=300)
        self.tree.column("New", width=300)
        self.tree.column("Status", width=100)
        self.tree.pack(fill="both", expand=True, pady=5)

        ModernButton(parent, "APPLY CHANGES", self.run_utility_rename).pack(
            fill="x", pady=15
        )

    # =========================================================================
    # UI HELPERS
    # =========================================================================
    def make_file_input(self, parent, row, label, var, cmd, is_dir=False):
        tk.Label(parent, text=label, bg=COLORS["surface"], fg=COLORS["text_dim"]).grid(
            row=row, column=0, sticky="w", pady=10
        )

        f = tk.Frame(parent, bg=COLORS["surface"])
        f.grid(row=row, column=1, sticky="ew", padx=10)

        entry = ModernEntry(f, textvariable=var)
        entry.pack(side="left", fill="x", expand=True, ipady=4)

        btn = ModernButton(f, text="📂", command=cmd, type="secondary")
        btn.config(pady=2, padx=10, font=("Segoe UI", 10))  # Smaller button
        btn.pack(side="right", padx=(5, 0))

    def make_combo_field(self, parent, r, c, label):
        f = tk.Frame(parent, bg=COLORS["surface"])
        f.grid(row=r, column=c, padx=15, pady=10, sticky="ew")

        tk.Label(f, text=label, bg=COLORS["surface"], fg=COLORS["text_dim"]).pack(
            anchor="w", pady=(0, 5)
        )
        cb = ttk.Combobox(f)
        cb.pack(fill="x")
        return cb

    # =========================================================================
    # LOGIC (EXACT COPY OF STABLE LOGIC)
    # =========================================================================
    def log(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")
        self.root.update()

    def browse_folder(self, string_var):
        f = filedialog.askdirectory()
        if f:
            string_var.set(f)

    def browse_and_preview(self):
        self.browse_folder(self.util_folder_path)
        self.update_utility_preview()

    def load_excel_preview(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel/CSV", "*.xlsx *.xls *.csv")]
        )
        if not file_path:
            return
        self.excel_path.set(file_path)
        try:
            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path, header=1)
            else:
                self.df = pd.read_excel(file_path, header=1)

            # Header fallback
            if (
                "Folder Name" not in self.df.columns
                and "File Name" not in self.df.columns
            ):
                self.log("Note: Trying Row 1 headers...")
                if file_path.endswith(".csv"):
                    self.df = pd.read_csv(file_path, header=0)
                else:
                    self.df = pd.read_excel(file_path, header=0)

            cols = ["-- Select --"] + list(self.df.columns)
            for c in [
                self.combo_folder,
                self.combo_filename,
                self.combo_newname,
                self.combo_isrc,
            ]:
                c["values"] = cols
                c.current(0)

            # Auto-select
            self.safe_set(self.combo_folder, "Folder Name")
            self.safe_set(self.combo_filename, "File Name")
            self.safe_set(self.combo_newname, "English Track Name")
            isrcs = [x for x in self.df.columns if "ISRC" in x.upper()]
            if isrcs:
                self.safe_set(self.combo_isrc, isrcs[0])
            self.log(f"Loaded {len(self.df)} rows.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def safe_set(self, combo, val):
        if val in combo["values"]:
            combo.set(val)

    def run_excel_rename(self):
        root_dir = self.root_folder_path.get()
        if self.df is None:
            return messagebox.showwarning("Error", "Please load an Excel file first.")

        c_folder, c_file = self.combo_folder.get(), self.combo_filename.get()
        c_new, c_isrc = self.combo_newname.get(), self.combo_isrc.get()
        use_isrc = self.var_enable_isrc.get()

        self.log("--- STARTED ---")
        self.folder_isrc_cache = {}
        processed = 0

        for index, row in self.df.iterrows():
            try:
                folder = str(row[c_folder]).strip()
                fname = str(row[c_file]).strip()
                eng_name = str(row[c_new]).strip()

                if folder == "nan" or fname == "nan":
                    continue

                name_root, name_ext = os.path.splitext(fname)
                if not name_ext:
                    name_ext = ".wav"

                # Check paths
                path_sub = os.path.join(root_dir, folder, name_root + name_ext)
                path_root = os.path.join(root_dir, name_root + name_ext)

                if os.path.exists(path_sub):
                    old_path = path_sub
                    parent = os.path.join(root_dir, folder)
                elif os.path.exists(path_root):
                    old_path = path_root
                    parent = root_dir
                else:
                    continue

                # ISRC
                isrc_val = ""
                if use_isrc:
                    if c_isrc != "-- Select --" and pd.notna(row[c_isrc]):
                        isrc_val = str(row[c_isrc]).strip()
                    if not isrc_val:
                        if folder in self.folder_isrc_cache:
                            isrc_val = self.folder_isrc_cache[folder]
                        else:
                            ans = simpledialog.askstring(
                                "ISRC Needed", f"Enter ISRC for: {folder}"
                            )
                            isrc_val = ans.strip() if ans else ""
                            self.folder_isrc_cache[folder] = isrc_val

                # New Name
                base = (
                    f"_{name_root}" if (eng_name == "nan" or not eng_name) else eng_name
                )
                new_name = (
                    f"{base}_{isrc_val}{name_ext}" if isrc_val else f"{base}{name_ext}"
                )

                new_full = os.path.join(parent, new_name)
                if not os.path.exists(new_full):
                    os.rename(old_path, new_full)
                    self.log(f"OK: {name_root} -> {new_name}")
                    processed += 1
            except Exception as e:
                self.log(f"Error: {e}")

        messagebox.showinfo("Done", f"Processed {processed} files.")

    def update_utility_preview(self, event=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        folder = self.util_folder_path.get()
        if not folder or not os.path.isdir(folder):
            return

        files = sorted(
            [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        )
        find, rep = self.util_find.get(), self.util_replace.get()
        pre, suf = self.util_prefix.get(), self.util_suffix.get()
        case, do_num = self.util_case.get(), self.util_num_enable.get()
        count = self.util_num_start.get()

        for f in files:
            root, ext = os.path.splitext(f)
            new_r = root.replace(find, rep) if find else root

            if case == "UPPERCASE":
                new_r = new_r.upper()
            elif case == "lowercase":
                new_r = new_r.lower()
            elif case == "Title Case":
                new_r = new_r.title()

            new_r = f"{pre}{new_r}{suf}"
            if do_num:
                new_r = f"{new_r}_{str(count).zfill(3)}"
                count += 1

            final = new_r + ext
            status = "Ready" if final != f else "No Change"
            self.tree.insert("", "end", values=(f, final, status))

    def run_utility_rename(self):
        folder = self.util_folder_path.get()
        if not folder:
            return
        count = 0
        for item in self.tree.get_children():
            v = self.tree.item(item)["values"]
            if v[2] == "Ready":
                try:
                    os.rename(os.path.join(folder, v[0]), os.path.join(folder, v[1]))
                    count += 1
                except:
                    pass
        messagebox.showinfo("Success", f"Renamed {count} files.")
        self.update_utility_preview()


if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateRenamerApp(root)
    root.mainloop()
