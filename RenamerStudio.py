import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, simpledialog
import pandas as pd

# --- 2025 DESIGN SYSTEM (Deep Ocean Theme) ---
THEME = {
    "bg": "#0f172a",  # Deep Slate (Main Background)
    "panel": "#1e293b",  # Card Background
    "input_bg": "#334155",  # Input Field Background
    "text_main": "#f8fafc",  # White-ish text
    "text_sub": "#94a3b8",  # Grey text
    "accent": "#38bdf8",  # Sky Blue (Primary Action)
    "accent_hover": "#0ea5e9",  # Darker Sky Blue
    "success": "#22c55e",  # Green
    "border": "#475569",  # Subtle borders
}

FONTS = {
    "header": ("Segoe UI", 20, "bold"),
    "sub": ("Segoe UI", 12),
    "label": ("Segoe UI", 10, "bold"),
    "body": ("Segoe UI", 10),
    "mono": ("Consolas", 10),
}


# --- GRAPHICS ENGINE (For Rounded UI) ---
def rounded_rect(canvas, x, y, w, h, r, color):
    """Draws a high-quality rounded rectangle on a canvas"""
    pts = [
        x + r,
        y,
        x + w - r,
        y,
        x + w,
        y,
        x + w,
        y + r,
        x + w,
        y + h - r,
        x + w,
        y + h,
        x + w - r,
        y + h,
        x + r,
        y + h,
        x,
        y + h,
        x,
        y + h - r,
        x,
        y + r,
        x,
        y,
        x + r,
        y,
    ]
    return canvas.create_polygon(pts, smooth=True, fill=color, outline="")


class RoundedFrame(tk.Canvas):
    """A container that looks like a rounded card"""

    def __init__(
        self, master, width, height, bg_color=THEME["panel"], corner_radius=25
    ):
        super().__init__(
            master, width=width, height=height, bg=THEME["bg"], highlightthickness=0
        )
        self.bg_color = bg_color
        self.r = corner_radius
        self.w = width
        self.h = height

        # Draw background
        self.shape = rounded_rect(self, 0, 0, width, height, self.r, self.bg_color)

        # Inner container for widgets
        self.inner = tk.Frame(self, bg=self.bg_color)
        self.create_window(
            width / 2,
            height / 2,
            window=self.inner,
            width=width - 30,
            height=height - 30,
        )  # Padding inside card

    def add_widget(self, widget, **pack_kwargs):
        widget.pack(**pack_kwargs)


class RoundedButton(tk.Canvas):
    """A pill-shaped interactive button"""

    def __init__(
        self,
        master,
        text,
        command,
        width=160,
        height=45,
        bg=THEME["accent"],
        fg="#000000",
        radius=22,
    ):
        super().__init__(
            master, width=width, height=height, bg=master["bg"], highlightthickness=0
        )
        self.command = command
        self.bg_normal = bg
        self.bg_hover = THEME["accent_hover"]

        # Draw
        self.shape = rounded_rect(
            self, 2, 2, width - 2, height - 2, radius, self.bg_normal
        )
        self.text = self.create_text(
            width / 2, height / 2, text=text, fill=fg, font=("Segoe UI", 11, "bold")
        )

        # Events
        self.bind("<Enter>", self._hover)
        self.bind("<Leave>", self._leave)
        self.bind("<Button-1>", self._click)

    def _hover(self, e):
        self.itemconfig(self.shape, fill=self.bg_hover)

    def _leave(self, e):
        self.itemconfig(self.shape, fill=self.bg_normal)

    def _click(self, e):
        if self.command:
            self.command()


class RoundedEntry(tk.Canvas):
    """A rounded input field container"""

    def __init__(self, master, width=200, height=35, radius=15):
        super().__init__(
            master, width=width, height=height, bg=THEME["panel"], highlightthickness=0
        )

        rounded_rect(self, 2, 2, width - 2, height - 2, radius, THEME["input_bg"])

        self.entry = tk.Entry(
            self,
            bg=THEME["input_bg"],
            fg=THEME["text_main"],
            insertbackground="white",
            relief="flat",
            font=FONTS["body"],
        )
        self.create_window(width / 2, height / 2, window=self.entry, width=width - 20)

    def get(self):
        return self.entry.get()

    def insert(self, idx, s):
        self.entry.insert(idx, s)

    def delete(self, first, last):
        self.entry.delete(first, last)

    def set_var(self, text_var):
        self.entry.config(textvariable=text_var)


# --- MAIN APPLICATION ---


class UltimateRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Renamer Studio 2025")
        self.root.geometry("1280x900")
        self.root.configure(bg=THEME["bg"])

        # Logic State
        self.df = None
        self.folder_isrc_cache = {}
        self.excel_path = tk.StringVar()
        self.root_folder_path = tk.StringVar()
        self.var_enable_isrc = tk.BooleanVar(value=True)
        self.util_folder_path = tk.StringVar()
        self.util_find = tk.StringVar()
        self.util_replace = tk.StringVar()
        self.util_prefix = tk.StringVar()
        self.util_suffix = tk.StringVar()
        self.util_case = tk.StringVar(value="No Change")
        self.util_num_enable = tk.BooleanVar(value=False)
        self.util_num_start = tk.IntVar(value=1)

        self.setup_styles()
        self.build_layout()
        self.show_excel_view()

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        # Modern Combobox
        style.configure(
            "TCombobox",
            fieldbackground=THEME["input_bg"],
            background=THEME["panel"],
            foreground="white",
            arrowcolor=THEME["accent"],
            borderwidth=0,
        )
        style.map("TCombobox", fieldbackground=[("readonly", THEME["input_bg"])])

        # Modern Treeview
        style.configure(
            "Treeview",
            background=THEME["input_bg"],
            foreground="white",
            fieldbackground=THEME["input_bg"],
            borderwidth=0,
            rowheight=30,
            font=FONTS["body"],
        )
        style.configure(
            "Treeview.Heading",
            background=THEME["panel"],
            foreground="white",
            font=FONTS["label"],
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", THEME["accent"])],
            foreground=[("selected", "black")],
        )

    def build_layout(self):
        # 1. Sidebar
        self.sidebar = tk.Frame(self.root, bg=THEME["bg"], width=260)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        # Logo
        tk.Label(
            self.sidebar,
            text="RENAMER",
            bg=THEME["bg"],
            fg="white",
            font=("Segoe UI", 26, "bold"),
        ).pack(anchor="w", padx=30, pady=(50, 0))
        tk.Label(
            self.sidebar,
            text="STUDIO PRO",
            bg=THEME["bg"],
            fg=THEME["accent"],
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=32)

        # Nav
        self.nav_container = tk.Frame(self.sidebar, bg=THEME["bg"])
        self.nav_container.pack(fill="x", pady=50)

        self.btn_excel = self.nav_button("Smart Rename (Excel)", self.show_excel_view)
        self.btn_util = self.nav_button("Quick Utility Tools", self.show_util_view)

        # 2. Main Content
        self.main = tk.Frame(self.root, bg=THEME["bg"])
        self.main.pack(side="left", fill="both", expand=True, padx=40, pady=40)

        self.header = tk.Label(
            self.main, text="Overview", bg=THEME["bg"], fg="white", font=FONTS["header"]
        )
        self.header.pack(anchor="w", pady=(0, 20))

        self.workspace = tk.Frame(self.main, bg=THEME["bg"])
        self.workspace.pack(fill="both", expand=True)

    def nav_button(self, text, cmd):
        f = tk.Frame(self.nav_container, bg=THEME["bg"], pady=5)
        f.pack(fill="x")

        indicator = tk.Frame(f, width=4, height=35, bg=THEME["bg"])
        indicator.pack(side="left")

        b = tk.Button(
            f,
            text=f"  {text}",
            command=lambda: self.switch_tab(cmd, b, indicator),
            bg=THEME["bg"],
            fg=THEME["text_sub"],
            font=("Segoe UI", 11),
            bd=0,
            relief="flat",
            activebackground=THEME["bg"],
            activeforeground="white",
            anchor="w",
        )
        b.pack(side="left", fill="x", expand=True, padx=15)
        return {"btn": b, "ind": indicator}

    def switch_tab(self, cmd, btn_obj, ind_obj):
        # Reset
        for item in [self.btn_excel, self.btn_util]:
            item["ind"].config(bg=THEME["bg"])
            item["btn"].config(fg=THEME["text_sub"])
        # Active
        ind_obj.config(bg=THEME["accent"])
        btn_obj.config(fg="white")
        cmd()

    def clear_workspace(self):
        for w in self.workspace.winfo_children():
            w.destroy()

    # ================= VIEW: EXCEL =================
    def show_excel_view(self):
        self.clear_workspace()
        self.switch_tab(
            lambda: None, self.btn_excel["btn"], self.btn_excel["ind"]
        )  # Visual sync
        self.header.config(text="Smart Renaming")

        # Row 1: File Config (Rounded Panel)
        row1 = RoundedFrame(self.workspace, width=900, height=220)
        row1.pack(pady=0, anchor="w")

        inner = row1.inner
        tk.Label(
            inner,
            text="SOURCE FILES",
            bg=THEME["panel"],
            fg=THEME["text_sub"],
            font=FONTS["label"],
        ).pack(anchor="w", pady=(0, 15))

        self.make_file_picker(
            inner, "Excel Database:", self.excel_path, self.load_excel_preview
        )
        tk.Frame(inner, height=10, bg=THEME["panel"]).pack()  # Spacer
        self.make_file_picker(
            inner,
            "Music Folder:",
            self.root_folder_path,
            lambda: self.browse(self.root_folder_path),
        )

        # Row 2: Mapping (Rounded Panel)
        row2 = RoundedFrame(self.workspace, width=900, height=280)
        row2.pack(pady=20, anchor="w")

        inner2 = row2.inner
        tk.Label(
            inner2,
            text="COLUMN MAPPING",
            bg=THEME["panel"],
            fg=THEME["text_sub"],
            font=FONTS["label"],
        ).pack(anchor="w", pady=(0, 15))

        grid = tk.Frame(inner2, bg=THEME["panel"])
        grid.pack(fill="x")

        self.combo_folder = self.make_combo(grid, 0, 0, "Folder Name Column")
        self.combo_file = self.make_combo(grid, 0, 1, "Current Filename Column")
        self.combo_eng = self.make_combo(grid, 1, 0, "English Name Column")
        self.combo_isrc = self.make_combo(grid, 1, 1, "ISRC Column")

        # Toggle
        tk.Checkbutton(
            inner2,
            text=" Smart ISRC (Popup if missing)",
            variable=self.var_enable_isrc,
            bg=THEME["panel"],
            fg="white",
            selectcolor=THEME["bg"],
            activebackground=THEME["panel"],
            activeforeground="white",
            font=FONTS["body"],
        ).pack(anchor="w", pady=20)

        # Action & Log
        action_bar = tk.Frame(self.workspace, bg=THEME["bg"])
        action_bar.pack(fill="x", pady=0)

        RoundedButton(
            action_bar, "RUN RENAME", self.run_excel, width=180, bg=THEME["success"]
        ).pack(side="left")

        self.log_area = scrolledtext.ScrolledText(
            self.workspace,
            height=6,
            bg=THEME["input_bg"],
            fg=THEME["accent"],
            bd=0,
            font=FONTS["mono"],
        )
        self.log_area.pack(fill="both", pady=20)

    # ================= VIEW: UTILITY =================
    def show_util_view(self):
        self.clear_workspace()
        self.switch_tab(lambda: None, self.btn_util["btn"], self.btn_util["ind"])
        self.header.config(text="Quick Tools")

        # Config Panel
        panel = RoundedFrame(self.workspace, width=900, height=350)
        panel.pack(anchor="w")
        inner = panel.inner

        tk.Label(
            inner,
            text="TARGET & RULES",
            bg=THEME["panel"],
            fg=THEME["text_sub"],
            font=FONTS["label"],
        ).pack(anchor="w", pady=(0, 10))
        self.make_file_picker(
            inner,
            "Target Folder:",
            self.util_folder_path,
            lambda: [self.browse(self.util_folder_path), self.update_preview()],
        )

        # Rules Grid
        g = tk.Frame(inner, bg=THEME["panel"])
        g.pack(fill="x", pady=20)

        self.make_input_grid(g, 0, 0, "Find:", self.util_find)
        self.make_input_grid(g, 0, 1, "Replace:", self.util_replace)
        self.make_input_grid(g, 1, 0, "Prefix:", self.util_prefix)
        self.make_input_grid(g, 1, 1, "Suffix:", self.util_suffix)

        # Options
        opt = tk.Frame(inner, bg=THEME["panel"])
        opt.pack(fill="x")
        tk.Label(opt, text="Casing:", bg=THEME["panel"], fg=THEME["text_sub"]).pack(
            side="left"
        )
        cb = ttk.Combobox(
            opt,
            textvariable=self.util_case,
            values=["No Change", "UPPERCASE", "lowercase", "Title Case"],
            width=15,
        )
        cb.pack(side="left", padx=10)
        cb.bind("<<ComboboxSelected>>", self.update_preview)

        tk.Checkbutton(
            opt,
            text=" Add Numbering",
            variable=self.util_num_enable,
            command=self.update_preview,
            bg=THEME["panel"],
            fg="white",
            selectcolor=THEME["bg"],
            activebackground=THEME["panel"],
        ).pack(side="left", padx=20)

        # Preview
        tk.Label(
            self.workspace,
            text="PREVIEW",
            bg=THEME["bg"],
            fg=THEME["text_sub"],
            font=FONTS["label"],
        ).pack(anchor="w", pady=(20, 5))
        self.tree = ttk.Treeview(
            self.workspace, columns=("O", "N", "S"), show="headings", height=8
        )
        self.tree.heading("O", text="Original")
        self.tree.column("O", width=300)
        self.tree.heading("N", text="New Name")
        self.tree.column("N", width=300)
        self.tree.heading("S", text="Status")
        self.tree.column("S", width=100)
        self.tree.pack(fill="both", expand=True)

        RoundedButton(self.workspace, "APPLY CHANGES", self.run_util, width=200).pack(
            pady=20
        )

    # ================= WIDGET BUILDERS =================
    def make_file_picker(self, parent, label, var, cmd):
        f = tk.Frame(parent, bg=THEME["panel"])
        f.pack(fill="x")
        tk.Label(
            f, text=label, bg=THEME["panel"], fg="white", width=15, anchor="w"
        ).pack(side="left")

        e = RoundedEntry(f, width=500, height=35)
        e.set_var(var)
        e.pack(side="left", padx=10)

        RoundedButton(
            f, "📂", cmd, width=40, height=35, bg=THEME["input_bg"], fg=THEME["accent"]
        ).pack(side="left")

    def make_combo(self, parent, r, c, label):
        f = tk.Frame(parent, bg=THEME["panel"])
        f.grid(row=r, column=c, padx=15, pady=10, sticky="ew")
        tk.Label(f, text=label, bg=THEME["panel"], fg=THEME["text_sub"]).pack(
            anchor="w"
        )
        cb = ttk.Combobox(f)
        cb.pack(fill="x", pady=5)
        return cb

    def make_input_grid(self, parent, r, c, label, var):
        f = tk.Frame(parent, bg=THEME["panel"])
        f.grid(row=r, column=c, padx=10, pady=5, sticky="w")
        tk.Label(f, text=label, bg=THEME["panel"], fg=THEME["text_sub"]).pack(
            side="left"
        )
        e = RoundedEntry(f, width=200, height=30)
        e.set_var(var)
        e.entry.bind("<KeyRelease>", self.update_preview)
        e.pack(side="left", padx=10)

    # ================= LOGIC =================
    def log(self, msg):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"> {msg}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")
        self.root.update()

    def browse(self, var):
        f = filedialog.askdirectory()
        if f:
            var.set(f)

    def load_excel_preview(self):
        f = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls *.csv")])
        if not f:
            return
        self.excel_path.set(f)
        try:
            self.df = (
                pd.read_csv(f, header=1)
                if f.endswith(".csv")
                else pd.read_excel(f, header=1)
            )
            # Fallback
            if "Folder Name" not in self.df.columns:
                self.df = (
                    pd.read_csv(f, header=0)
                    if f.endswith(".csv")
                    else pd.read_excel(f, header=0)
                )

            cols = ["-- Select --"] + list(self.df.columns)
            for cb in [
                self.combo_folder,
                self.combo_file,
                self.combo_eng,
                self.combo_isrc,
            ]:
                cb["values"] = cols
                cb.current(0)

            self.safe_select(self.combo_folder, "Folder Name")
            self.safe_select(self.combo_file, "File Name")
            self.safe_select(self.combo_eng, "English Track Name")

            isrcs = [c for c in self.df.columns if "ISRC" in c.upper()]
            if isrcs:
                self.safe_select(self.combo_isrc, isrcs[0])

            self.log(f"Loaded {len(self.df)} rows.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def safe_select(self, cb, val):
        if val in cb["values"]:
            cb.set(val)

    def run_excel(self):
        root = self.root_folder_path.get()
        if self.df is None:
            return messagebox.showerror("Err", "Load Excel first")

        c_fold, c_file = self.combo_folder.get(), self.combo_file.get()
        c_eng, c_isrc = self.combo_eng.get(), self.combo_isrc.get()
        use_isrc = self.var_enable_isrc.get()

        self.log("Starting...")
        self.folder_isrc_cache = {}
        count = 0

        for i, row in self.df.iterrows():
            try:
                folder = str(row[c_fold]).strip()
                fname = str(row[c_file]).strip()
                eng = str(row[c_eng]).strip()
                if folder == "nan" or fname == "nan":
                    continue

                name, ext = os.path.splitext(fname)
                if not ext:
                    ext = ".wav"
                target_file = name + ext

                # Logic: Find file (Strict Case or Loose)
                found_path = None
                parent_dir = None

                # Check inner
                p1 = os.path.join(root, folder, target_file)
                if os.path.exists(p1):
                    found_path = p1
                    parent_dir = os.path.join(root, folder)
                else:
                    # Check root
                    p2 = os.path.join(root, target_file)
                    if os.path.exists(p2):
                        found_path = p2
                        parent_dir = root

                if not found_path:
                    continue

                # ISRC
                isrc = ""
                if use_isrc:
                    if c_isrc != "-- Select --" and pd.notna(row[c_isrc]):
                        isrc = str(row[c_isrc]).strip()
                    if not isrc:
                        if folder in self.folder_isrc_cache:
                            isrc = self.folder_isrc_cache[folder]
                        else:
                            val = simpledialog.askstring(
                                "ISRC", f"Enter ISRC for {folder}"
                            )
                            isrc = val.strip() if val else ""
                            self.folder_isrc_cache[folder] = isrc

                base = f"_{name}" if (eng == "nan" or not eng) else eng
                new_name = f"{base}_{isrc}{ext}" if isrc else f"{base}{ext}"

                new_full = os.path.join(parent_dir, new_name)

                if found_path != new_full:
                    # Handle Windows case-insensitivity
                    if found_path.lower() == new_full.lower():
                        os.rename(found_path, found_path + "_tmp")
                        os.rename(found_path + "_tmp", new_full)
                    else:
                        os.rename(found_path, new_full)
                    self.log(f"Renamed: {target_file} -> {new_name}")
                    count += 1
            except Exception as e:
                self.log(f"Err row {i}: {e}")
        messagebox.showinfo("Done", f"Processed {count} files.")

    def update_preview(self, e=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        f = self.util_folder_path.get()
        if not f or not os.path.isdir(f):
            return

        files = sorted([x for x in os.listdir(f) if os.path.isfile(os.path.join(f, x))])
        find, rep = self.util_find.get(), self.util_replace.get()
        pre, suf = self.util_prefix.get(), self.util_suffix.get()
        case, num = self.util_case.get(), self.util_num_enable.get()
        ctr = self.util_num_start.get()

        for name in files:
            r, ext = os.path.splitext(name)
            new_r = r.replace(find, rep) if find else r
            if case == "UPPERCASE":
                new_r = new_r.upper()
            elif case == "lowercase":
                new_r = new_r.lower()
            elif case == "Title Case":
                new_r = new_r.title()

            new_r = f"{pre}{new_r}{suf}"
            if num:
                new_r += f"_{str(ctr).zfill(3)}"
                ctr += 1

            final = new_r + ext
            stat = "Ready" if final != name else "No Change"
            self.tree.insert("", "end", values=(name, final, stat))

    def run_util(self):
        f = self.util_folder_path.get()
        if not f:
            return
        c = 0
        for item in self.tree.get_children():
            v = self.tree.item(item)["values"]
            if v[2] == "Ready":
                try:
                    os.rename(os.path.join(f, v[0]), os.path.join(f, v[1]))
                    c += 1
                except:
                    pass
        self.update_preview()
        messagebox.showinfo("Success", f"Renamed {c} files.")


if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateRenamerApp(root)
    root.mainloop()
