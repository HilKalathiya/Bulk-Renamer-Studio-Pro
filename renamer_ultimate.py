import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, simpledialog
import pandas as pd

# --- CONFIGURATION & PALETTE ---
COLORS = {
    "bg": "#121212",  # Main Window Background (Deepest)
    "sidebar": "#181818",  # Sidebar Background
    "card": "#222222",  # Card/Panel Background
    "card_border": "#333333",  # Subtle border for definition
    "input_bg": "#2b2b2b",  # Input field background
    "input_fg": "#e0e0e0",  # Input text color
    "text_main": "#ffffff",
    "text_dim": "#a0a0a0",
    "accent": "#00d4ff",  # Neon Cyan (Primary)
    "accent_hover": "#66e5ff",
    "success": "#00e676",  # Vibrant Green
    "success_hover": "#69f0ae",
    "danger": "#ff5252",
    "shadow": "#000000",
}

FONTS = {
    "display": ("Segoe UI", 24, "bold"),
    "h1": ("Segoe UI", 16, "bold"),
    "h2": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10),
    "bold": ("Segoe UI", 10, "bold"),  # FIXED: Added missing key
    "input": ("Segoe UI", 11),
    "mono": ("Consolas", 9),
}


# --- CUSTOM UTILS FOR ROUNDED SHAPES ---
def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    """Draw a rounded rectangle on a canvas"""
    points = [
        x1 + radius,
        y1,
        x1 + radius,
        y1,
        x2 - radius,
        y1,
        x2 - radius,
        y1,
        x2,
        y1,
        x2,
        y1 + radius,
        x2,
        y1 + radius,
        x2,
        y2 - radius,
        x2,
        y2 - radius,
        x2,
        y2,
        x2 - radius,
        y2,
        x2 - radius,
        y2,
        x1 + radius,
        y2,
        x1 + radius,
        y2,
        x1,
        y2,
        x1,
        y2 - radius,
        x1,
        y2 - radius,
        x1,
        y1 + radius,
        x1,
        y1 + radius,
        x1,
        y1,
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)


# --- MODERN WIDGETS ---


class RoundedButton(tk.Canvas):
    """A Button that isn't a box! It's a smooth rounded pill."""

    def __init__(
        self,
        master,
        text,
        command,
        width=150,
        height=40,
        radius=20,
        bg_color=COLORS["accent"],
        text_color=COLORS["bg"],
    ):
        super().__init__(
            master, width=width, height=height, bg=COLORS["card"], highlightthickness=0
        )
        self.command = command
        self.text_str = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.radius = radius
        self.w = width
        self.h = height

        # Draw initial state
        self.rect = draw_rounded_rect(
            self, 2, 2, width - 2, height - 2, radius, fill=bg_color, outline=""
        )
        self.text = self.create_text(
            width / 2,
            height / 2,
            text=text,
            fill=text_color,
            font=("Segoe UI", 10, "bold"),
        )

        # Bindings
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_click(self, e):
        if self.command:
            self.command()

    def on_enter(self, e):
        # Lighten color
        self.itemconfig(
            self.rect,
            fill=(
                COLORS["accent_hover"]
                if self.bg_color == COLORS["accent"]
                else "#444444"
            ),
        )
        self.configure(cursor="hand2")

    def on_leave(self, e):
        self.itemconfig(self.rect, fill=self.bg_color)


class ElegantEntry(tk.Entry):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(
            bg=COLORS["input_bg"],
            fg=COLORS["input_fg"],
            insertbackground="white",
            relief="flat",
            font=FONTS["input"],
            bd=5,  # Internal padding simulation
        )


class FloatingCard(tk.Frame):
    """A Frame that looks like a floating card with a header"""

    def __init__(self, master, title="", **kwargs):
        super().__init__(master, bg=COLORS["card"], padx=25, pady=25)

        # Header
        if title:
            h_frame = tk.Frame(self, bg=COLORS["card"])
            h_frame.pack(fill="x", pady=(0, 20))

            # Accent pill
            tk.Frame(h_frame, width=4, height=20, bg=COLORS["accent"]).pack(
                side="left", padx=(0, 10)
            )

            tk.Label(
                h_frame,
                text=title.upper(),
                bg=COLORS["card"],
                fg=COLORS["text_dim"],
                font=("Segoe UI", 9, "bold"),
            ).pack(side="left")


# --- MAIN APP ---


class UltimateRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Renamer Studio 2025")
        self.root.geometry("1250x850")
        self.root.configure(bg=COLORS["bg"])

        # State
        self.current_mode = "EXCEL"
        self.init_vars()
        self.style_tk_widgets()

        # --- LAYOUT ---
        # 1. Sidebar (Left)
        self.create_sidebar()

        # 2. Main Content (Right)
        self.create_main_area()

        # Load Default
        self.show_excel_view()

    def init_vars(self):
        self.df = None
        self.folder_isrc_cache = {}
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

    def style_tk_widgets(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        # Combobox
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["input_bg"],
            background=COLORS["card"],
            foreground="white",
            arrowcolor="white",
            borderwidth=0,
        )
        style.map("TCombobox", fieldbackground=[("readonly", COLORS["input_bg"])])

        # Treeview
        style.configure(
            "Treeview",
            background=COLORS["input_bg"],
            foreground="white",
            fieldbackground=COLORS["input_bg"],
            borderwidth=0,
            rowheight=32,
            font=FONTS["body"],
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["card"],
            foreground="white",
            font=FONTS["bold"],
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", "black")],
        )

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=COLORS["sidebar"], width=280)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)  # Strict width

        # Brand
        brand_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        brand_frame.pack(fill="x", padx=30, pady=40)
        tk.Label(
            brand_frame,
            text="Renamer",
            bg=COLORS["sidebar"],
            fg="white",
            font=("Segoe UI Light", 28),
        ).pack(anchor="w")
        tk.Label(
            brand_frame,
            text="STUDIO 2025",
            bg=COLORS["sidebar"],
            fg=COLORS["accent"],
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=2)

        # Nav Menu
        self.nav_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar"])
        self.nav_frame.pack(fill="x", padx=20)

        self.btn_excel = self.create_nav_btn(
            "Smart Rename (Excel)", self.show_excel_view, active=True
        )
        self.btn_util = self.create_nav_btn(
            "Quick Tools (Utility)", self.show_utility_view, active=False
        )

    def create_nav_btn(self, text, command, active=False):
        btn_frame = tk.Frame(self.nav_frame, bg=COLORS["sidebar"], pady=5)
        btn_frame.pack(fill="x")

        # Indicator line
        indicator = tk.Frame(
            btn_frame,
            width=4,
            height=40,
            bg=COLORS["accent"] if active else COLORS["sidebar"],
        )
        indicator.pack(side="left")

        # Actual button
        fg = "white" if active else COLORS["text_dim"]
        f = ("Segoe UI", 11, "bold") if active else ("Segoe UI", 11)

        btn = tk.Button(
            btn_frame,
            text=f"  {text}",
            command=lambda: self.switch_mode(command, btn_frame, indicator),
            bg=COLORS["sidebar"],
            fg=fg,
            font=f,
            anchor="w",
            bd=0,
            relief="flat",
            activebackground=COLORS["sidebar"],
            activeforeground=COLORS["accent"],
        )
        btn.pack(side="left", fill="x", expand=True, padx=10)

        return {"frame": btn_frame, "indicator": indicator, "btn": btn}

    def switch_mode(self, func, frame, indicator):
        # Reset all
        for b in [self.btn_excel, self.btn_util]:
            b["indicator"].config(bg=COLORS["sidebar"])
            b["btn"].config(fg=COLORS["text_dim"], font=("Segoe UI", 11))

        # Set active
        indicator.config(bg=COLORS["accent"])
        frame.winfo_children()[1].config(fg="white", font=("Segoe UI", 11, "bold"))

        func()

    def create_main_area(self):
        self.main_container = tk.Frame(self.root, bg=COLORS["bg"])
        self.main_container.pack(
            side="left", fill="both", expand=True, padx=40, pady=40
        )

        # Dynamic Header
        self.header_lbl = tk.Label(
            self.main_container,
            text="Dashboard",
            bg=COLORS["bg"],
            fg="white",
            font=FONTS["h1"],
        )
        self.header_lbl.pack(anchor="w", pady=(0, 20))

        # Content Holder
        self.content_frame = tk.Frame(self.main_container, bg=COLORS["bg"])
        self.content_frame.pack(fill="both", expand=True)

    # =========================================================================
    # VIEW GENERATORS
    # =========================================================================

    def show_excel_view(self):
        self.clear_content()
        self.header_lbl.config(text="Smart Renaming (Excel Source)")

        parent = self.content_frame

        # CARD 1: File Setup
        card1 = FloatingCard(parent, "Source Configuration")
        card1.pack(fill="x", pady=(0, 20))

        # Grid layout for inputs inside card
        grid1 = tk.Frame(card1, bg=COLORS["card"])
        grid1.pack(fill="x")
        grid1.columnconfigure(1, weight=1)

        self.add_file_row(
            grid1, 0, "Excel File:", self.excel_path, self.load_excel_preview
        )
        self.add_file_row(
            grid1,
            1,
            "Music Folder:",
            self.root_folder_path,
            lambda: self.browse_folder(self.root_folder_path),
        )

        # CARD 2: Mapping
        card2 = FloatingCard(parent, "Data Mapping")
        card2.pack(fill="x", pady=(0, 20))

        grid2 = tk.Frame(card2, bg=COLORS["card"])
        grid2.pack(fill="x")
        # Equal columns
        grid2.columnconfigure(0, weight=1)
        grid2.columnconfigure(1, weight=1)

        # Left Side Mapping
        self.combo_folder = self.add_combo_row(grid2, 0, 0, "Folder Name Column")
        self.combo_filename = self.add_combo_row(grid2, 1, 0, "Current Filename Column")

        # Right Side Mapping
        self.combo_newname = self.add_combo_row(grid2, 0, 1, "English Name Column")
        self.combo_isrc = self.add_combo_row(grid2, 1, 1, "ISRC Column")

        # ISRC Toggle
        tk.Checkbutton(
            card2,
            text=" Enable Smart ISRC (Ask popup if missing)",
            variable=self.var_enable_isrc,
            bg=COLORS["card"],
            fg="white",
            selectcolor=COLORS["bg"],
            activebackground=COLORS["card"],
            activeforeground="white",
            font=FONTS["body"],
        ).pack(anchor="w", pady=(15, 0))

        # ACTION AREA
        action_row = tk.Frame(parent, bg=COLORS["bg"])
        action_row.pack(fill="x", pady=10)

        # Custom Rounded Button
        btn = RoundedButton(
            action_row,
            "START RENAMING",
            self.run_excel_rename,
            width=200,
            bg_color=COLORS["success"],
            text_color="#000000",
        )
        btn.pack(side="left")

        # Log Console
        self.log_area = scrolledtext.ScrolledText(
            parent,
            height=6,
            bg=COLORS["input_bg"],
            fg=COLORS["accent"],
            bd=0,
            font=FONTS["mono"],
        )
        self.log_area.pack(fill="both", expand=True, pady=20)

    def show_utility_view(self):
        self.clear_content()
        self.header_lbl.config(text="Quick Tools (Pattern Rename)")

        parent = self.content_frame

        # CARD 1: Setup
        card1 = FloatingCard(parent, "Target Selection")
        card1.pack(fill="x", pady=(0, 20))

        grid1 = tk.Frame(card1, bg=COLORS["card"])
        grid1.pack(fill="x")
        grid1.columnconfigure(1, weight=1)

        self.add_file_row(
            grid1,
            0,
            "Folder:",
            self.util_folder_path,
            self.browse_and_preview,
            is_dir=True,
        )

        # CARD 2: Rules
        card2 = FloatingCard(parent, "Transformation Rules")
        card2.pack(fill="x", pady=(0, 20))

        grid2 = tk.Frame(card2, bg=COLORS["card"])
        grid2.pack(fill="x")

        # Helper to add rule inputs
        def rule_in(r, c, label, var):
            f = tk.Frame(grid2, bg=COLORS["card"])
            f.grid(row=r, column=c, padx=10, pady=5, sticky="ew")
            tk.Label(f, text=label, bg=COLORS["card"], fg=COLORS["text_dim"]).pack(
                anchor="w"
            )
            e = ElegantEntry(f, textvariable=var, width=22)
            e.pack(fill="x")
            e.bind("<KeyRelease>", self.update_utility_preview)

        rule_in(0, 0, "Find:", self.util_find)
        rule_in(0, 1, "Replace:", self.util_replace)
        rule_in(1, 0, "Prefix:", self.util_prefix)
        rule_in(1, 1, "Suffix:", self.util_suffix)

        # Extras
        f_ex = tk.Frame(grid2, bg=COLORS["card"])
        f_ex.grid(row=0, column=2, rowspan=2, padx=20, sticky="n")

        tk.Label(f_ex, text="Casing:", bg=COLORS["card"], fg=COLORS["text_dim"]).pack(
            anchor="w"
        )
        cb = ttk.Combobox(
            f_ex,
            textvariable=self.util_case,
            values=["No Change", "UPPERCASE", "lowercase", "Title Case"],
        )
        cb.pack(fill="x", pady=(0, 10))
        cb.bind("<<ComboboxSelected>>", self.update_utility_preview)

        tk.Checkbutton(
            f_ex,
            text=" Add Numbering",
            variable=self.util_num_enable,
            bg=COLORS["card"],
            fg="white",
            selectcolor=COLORS["bg"],
            activebackground=COLORS["card"],
            command=self.update_utility_preview,
        ).pack(anchor="w")

        # PREVIEW TABLE
        tk.Label(
            parent,
            text="LIVE PREVIEW",
            bg=COLORS["bg"],
            fg=COLORS["text_dim"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        self.tree = ttk.Treeview(
            parent, columns=("Old", "New", "Status"), show="headings", height=8
        )
        self.tree.heading("Old", text="Original Name")
        self.tree.column("Old", width=300)
        self.tree.heading("New", text="New Name")
        self.tree.column("New", width=300)
        self.tree.heading("Status", text="Status")
        self.tree.column("Status", width=100)
        self.tree.pack(fill="both", expand=True, pady=10)

        btn = RoundedButton(
            parent,
            "APPLY CHANGES",
            self.run_utility_rename,
            width=200,
            bg_color=COLORS["accent"],
            text_color="#000000",
        )
        btn.pack(pady=10)

    # =========================================================================
    # HELPERS
    # =========================================================================
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def add_file_row(self, parent, r, label, var, cmd, is_dir=False):
        tk.Label(parent, text=label, bg=COLORS["card"], fg=COLORS["text_dim"]).grid(
            row=r, column=0, sticky="w", pady=10
        )

        f = tk.Frame(parent, bg=COLORS["card"])
        f.grid(row=r, column=1, sticky="ew", padx=15)

        e = ElegantEntry(f, textvariable=var)
        e.pack(side="left", fill="x", expand=True)

        # Small icon button for browse
        b = tk.Button(
            f,
            text="📂",
            command=cmd,
            bg=COLORS["input_bg"],
            fg=COLORS["accent"],
            bd=0,
            relief="flat",
            font=("Segoe UI", 12),
        )
        b.pack(side="right", padx=(10, 0))

    def add_combo_row(self, parent, r, c, label):
        f = tk.Frame(parent, bg=COLORS["card"])
        f.grid(row=r, column=c, padx=10, pady=10, sticky="ew")

        tk.Label(f, text=label, bg=COLORS["card"], fg=COLORS["text_dim"]).pack(
            anchor="w", pady=(0, 5)
        )
        cb = ttk.Combobox(f)
        cb.pack(fill="x")
        return cb

    # =========================================================================
    # LOGIC CORE
    # =========================================================================
    def log(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"> {message}\n")
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

            if (
                "Folder Name" not in self.df.columns
                and "File Name" not in self.df.columns
            ):
                self.log("Note: Trying Row 1 headers (fallback)...")
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

            self.safe_set(self.combo_folder, "Folder Name")
            self.safe_set(self.combo_filename, "File Name")
            self.safe_set(self.combo_newname, "English Track Name")
            isrcs = [x for x in self.df.columns if "ISRC" in x.upper()]
            if isrcs:
                self.safe_set(self.combo_isrc, isrcs[0])
            self.log(f"Success: Loaded {len(self.df)} rows from Excel.")
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

        self.log("Starting batch process (Case Sensitive Matching)...")
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

                target_filename = name_root + name_ext

                # --- STRICT CASE SENSITIVE CHECK ---
                found = False
                old_path = None
                parent = None

                # 1. Check inner folder
                inner_dir = os.path.join(root_dir, folder)
                if os.path.isdir(inner_dir):
                    # listdir gives actual filenames on disk
                    files_in_inner = os.listdir(inner_dir)
                    if target_filename in files_in_inner:
                        old_path = os.path.join(inner_dir, target_filename)
                        parent = inner_dir
                        found = True

                # 2. Check root folder (if not found in inner)
                if not found:
                    files_in_root = os.listdir(root_dir)
                    if target_filename in files_in_root:
                        old_path = os.path.join(root_dir, target_filename)
                        parent = root_dir
                        found = True

                if not found:
                    # File does not exist with EXACT casing
                    continue

                # --- ISRC LOGIC ---
                isrc_val = ""
                if use_isrc:
                    if c_isrc != "-- Select --" and pd.notna(row[c_isrc]):
                        isrc_val = str(row[c_isrc]).strip()
                    if not isrc_val:
                        if folder in self.folder_isrc_cache:
                            isrc_val = self.folder_isrc_cache[folder]
                        else:
                            ans = simpledialog.askstring(
                                "ISRC Missing", f"Enter ISRC for folder:\n{folder}"
                            )
                            isrc_val = ans.strip() if ans else ""
                            self.folder_isrc_cache[folder] = isrc_val

                base = (
                    f"_{name_root}" if (eng_name == "nan" or not eng_name) else eng_name
                )
                new_name = (
                    f"{base}_{isrc_val}{name_ext}" if isrc_val else f"{base}{name_ext}"
                )

                new_full = os.path.join(parent, new_name)

                # --- SAFE RENAME (Handle Case-Only Changes on Windows) ---
                if os.path.exists(new_full) and new_full != old_path:
                    # If target exists and it's strictly a different file
                    if new_full.lower() == old_path.lower():
                        # Case-only rename! Windows needs a temp step.
                        temp_path = old_path + "__temp"
                        os.rename(old_path, temp_path)
                        os.rename(temp_path, new_full)
                        self.log(f"Renamed (Case Fix): {target_filename} -> {new_name}")
                        processed += 1
                    else:
                        self.log(f"Skipped (Exists): {new_name}")
                elif not os.path.exists(new_full):
                    os.rename(old_path, new_full)
                    self.log(f"Renamed: {target_filename} -> {new_name}")
                    processed += 1

            except Exception as e:
                self.log(f"Error Row {index}: {e}")

        messagebox.showinfo("Complete", f"Processed {processed} files successfully.")

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
