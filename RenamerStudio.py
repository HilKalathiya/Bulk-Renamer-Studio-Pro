import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, simpledialog
import pandas as pd

# --- MATERIAL 3 DESIGN SYSTEM (Dark) ---
THEME = {
    "bg": "#131314",  # Main Background
    "surface": "#1E1F20",  # Card Surface
    "surface_container": "#28292A",  # Input Field Background
    "primary": "#D3E3FD",  # Soft Blue (Active Buttons)
    "on_primary": "#041E49",  # Text on Primary Buttons
    "secondary": "#C4C7C5",  # Muted Text / Inactive Icons
    "text_main": "#E3E3E3",  # Main Body Text
    "text_sub": "#444746",  # Borders / Dividers
    "outline": "#8E918F",  # Input Borders
    "success": "#6DD58C",  # Success Green
    "error": "#F2B8B5",  # Error Red
}

# Matching Google Sans Weights using Segoe UI
FONTS = {
    "display": ("Segoe UI", 28, "bold"),
    "headline": ("Segoe UI", 20, "bold"),
    "title": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 11),
    "label": ("Segoe UI", 10, "bold"),
    "mono": ("Consolas", 10),
}


# --- GRAPHICS ENGINE ---
def draw_stadium(canvas, x, y, w, h, color):
    """Draws a 'Stadium' shape (Full rounded sides)"""
    r = h / 2
    return draw_rounded_rect(canvas, x, y, w, h, r, color)


def draw_rounded_rect(canvas, x, y, w, h, r, color):
    """Draws a standard rounded rectangle"""
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


class SurfaceCard(tk.Canvas):
    """A Material 3 Card container"""

    def __init__(self, master, width, height, radius=24):
        super().__init__(
            master, width=width, height=height, bg=THEME["bg"], highlightthickness=0
        )
        self.bg_color = THEME["surface"]

        # Draw Card
        self.shape = draw_rounded_rect(self, 0, 0, width, height, radius, self.bg_color)

        # Inner container
        self.inner = tk.Frame(self, bg=self.bg_color)
        self.create_window(
            width / 2,
            height / 2,
            window=self.inner,
            width=width - 40,
            height=height - 40,
        )


class ActionButton(tk.Canvas):
    """A 'Filled' Material 3 Button"""

    def __init__(
        self,
        master,
        text,
        command,
        width=140,
        height=45,
        bg=THEME["primary"],
        fg=THEME["on_primary"],
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=master["bg"] if "bg" in master.keys() else THEME["bg"],
            highlightthickness=0,
        )
        self.command = command
        self.bg_normal = bg
        self.bg_hover = "#E8F0FE"  # Lighter on hover

        # Stadium Shape
        self.shape = draw_stadium(self, 2, 2, width - 2, height - 2, self.bg_normal)
        self.text = self.create_text(
            width / 2, height / 2, text=text, fill=fg, font=("Segoe UI", 11, "bold")
        )

        self.bind("<Enter>", lambda e: self.itemconfig(self.shape, fill=self.bg_hover))
        self.bind("<Leave>", lambda e: self.itemconfig(self.shape, fill=self.bg_normal))
        self.bind("<Button-1>", lambda e: command() if command else None)


class InputField(tk.Canvas):
    """A Material 3 Input Field"""

    def __init__(self, master, width=200, height=40):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=THEME["surface"],
            highlightthickness=0,
        )

        # Background
        draw_rounded_rect(
            self, 2, 2, width - 2, height - 2, 12, THEME["surface_container"]
        )

        self.entry = tk.Entry(
            self,
            bg=THEME["surface_container"],
            fg=THEME["text_main"],
            insertbackground=THEME["primary"],
            relief="flat",
            font=FONTS["body"],
        )
        self.create_window(width / 2, height / 2, window=self.entry, width=width - 30)

    def get(self):
        return self.entry.get()

    def insert(self, idx, s):
        self.entry.insert(idx, s)

    def delete(self, first, last):
        self.entry.delete(first, last)

    def set_var(self, text_var):
        self.entry.config(textvariable=text_var)

    def bind_key(self, func):
        self.entry.bind("<KeyRelease>", func)


# --- APP LOGIC ---


class UltimateRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Renamer Studio")
        self.root.geometry("1400x950")
        self.root.configure(bg=THEME["bg"])

        # Data & State
        self.df = None
        self.manual_overrides = {}

        # Vars
        self.excel_path = tk.StringVar()
        self.root_folder_path = tk.StringVar()
        self.var_enable_isrc = tk.BooleanVar(value=True)
        self.var_strict_case = tk.BooleanVar(value=False)
        self.var_header_row = tk.IntVar(value=2)

        self.util_folder_path = tk.StringVar()
        self.util_find = tk.StringVar()
        self.util_replace = tk.StringVar()
        self.util_prefix = tk.StringVar()
        self.util_suffix = tk.StringVar()
        self.util_case = tk.StringVar(value="No Change")
        self.util_num_enable = tk.BooleanVar(value=False)
        self.util_num_start = tk.IntVar(value=1)

        self.style_widgets()
        self.build_ui()
        self.show_excel_view()

    def style_widgets(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        # Combobox
        style.configure(
            "TCombobox",
            fieldbackground=THEME["surface_container"],
            background=THEME["surface"],
            foreground="white",
            arrowcolor=THEME["primary"],
            borderwidth=0,
        )
        style.map(
            "TCombobox", fieldbackground=[("readonly", THEME["surface_container"])]
        )

        # Treeview
        style.configure(
            "Treeview",
            background=THEME["surface_container"],
            foreground=THEME["text_main"],
            fieldbackground=THEME["surface_container"],
            borderwidth=0,
            rowheight=45,
            font=FONTS["body"],
        )
        style.configure(
            "Treeview.Heading",
            background=THEME["surface"],
            foreground=THEME["primary"],
            font=FONTS["label"],
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", "#3C4043")],
            foreground=[("selected", THEME["primary"])],
        )

    def build_ui(self):
        # 1. Sidebar
        self.sidebar = tk.Frame(self.root, bg=THEME["bg"], width=280)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Branding
        tk.Label(
            self.sidebar,
            text="Renamer",
            bg=THEME["bg"],
            fg=THEME["text_main"],
            font=FONTS["display"],
        ).pack(anchor="w", padx=30, pady=(50, 0))
        tk.Label(
            self.sidebar,
            text="STUDIO PRO",
            bg=THEME["bg"],
            fg=THEME["primary"],
            font=FONTS["label"],
        ).pack(anchor="w", padx=32)

        self.nav_frame = tk.Frame(self.sidebar, bg=THEME["bg"])
        self.nav_frame.pack(fill="x", pady=60)

        self.btn_excel = self.create_nav("Smart Rename", self.show_excel_view)
        self.btn_util = self.create_nav("Quick Utility", self.show_util_view)

        # 2. Main Content
        self.main = tk.Frame(self.root, bg=THEME["bg"])
        self.main.pack(side="left", fill="both", expand=True, padx=40, pady=40)

        self.header = tk.Label(
            self.main,
            text="Overview",
            bg=THEME["bg"],
            fg=THEME["text_main"],
            font=FONTS["headline"],
        )
        self.header.pack(anchor="w", pady=(0, 30))

        self.workspace = tk.Frame(self.main, bg=THEME["bg"])
        self.workspace.pack(fill="both", expand=True)

    def create_nav(self, text, cmd):
        f = tk.Frame(self.nav_frame, bg=THEME["bg"], pady=8)
        f.pack(fill="x")

        # Rounded Indicator (Pill)
        ind = tk.Frame(f, width=6, height=35, bg=THEME["bg"])
        ind.pack(side="left")

        b = tk.Button(
            f,
            text=f"  {text}",
            command=lambda: self.switch_view(cmd, b, ind),
            bg=THEME["bg"],
            fg=THEME["secondary"],
            font=FONTS["body"],
            bd=0,
            activebackground=THEME["bg"],
            activeforeground=THEME["primary"],
            anchor="w",
        )
        b.pack(side="left", fill="x", padx=15)
        return {"btn": b, "ind": ind}

    def switch_view(self, cmd, b, ind):
        for item in [self.btn_excel, self.btn_util]:
            item["ind"].config(bg=THEME["bg"])
            item["btn"].config(fg=THEME["secondary"], font=("Segoe UI", 11))

        # Active State
        ind.config(bg=THEME["primary"])
        b.config(fg=THEME["text_main"], font=("Segoe UI", 11, "bold"))
        cmd()

    def clear_ws(self):
        for w in self.workspace.winfo_children():
            w.destroy()

    # --- EXCEL VIEW ---
    def show_excel_view(self):
        self.clear_ws()
        self.switch_view(lambda: None, self.btn_excel["btn"], self.btn_excel["ind"])
        self.header.config(text="Smart Renaming")

        # Config Card
        card = SurfaceCard(self.workspace, width=950, height=220)
        card.pack(anchor="w", pady=(0, 20))
        inner = card.inner

        tk.Label(
            inner,
            text="SOURCE CONFIGURATION",
            bg=THEME["surface"],
            fg=THEME["primary"],
            font=FONTS["label"],
        ).pack(anchor="w", pady=(0, 15))

        # Header Row
        h_row = tk.Frame(inner, bg=THEME["surface"])
        h_row.pack(anchor="w", pady=(0, 10))
        tk.Label(
            h_row,
            text="Header Row Number:",
            bg=THEME["surface"],
            fg=THEME["text_main"],
            font=FONTS["body"],
        ).pack(side="left")
        tk.Spinbox(
            h_row,
            from_=1,
            to=10,
            textvariable=self.var_header_row,
            width=3,
            font=FONTS["body"],
            bg=THEME["surface_container"],
            fg="white",
            buttonbackground=THEME["surface_container"],
        ).pack(side="left", padx=10)

        self.make_file_row(
            inner, "Excel File:", self.excel_path, self.load_excel_preview
        )
        tk.Frame(inner, height=10, bg=THEME["surface"]).pack()
        self.make_file_row(
            inner,
            "Music Folder:",
            self.root_folder_path,
            lambda: self.browse(self.root_folder_path),
        )

        # Mapping Card
        card2 = SurfaceCard(self.workspace, width=950, height=320)
        card2.pack(anchor="w", pady=10)
        i2 = card2.inner

        tk.Label(
            i2,
            text="DATA MAPPING",
            bg=THEME["surface"],
            fg=THEME["primary"],
            font=FONTS["label"],
        ).pack(anchor="w", pady=(0, 15))

        g = tk.Frame(i2, bg=THEME["surface"])
        g.pack(fill="x")
        self.combo_folder = self.make_combo(g, 0, 0, "Folder Column")
        self.combo_file = self.make_combo(g, 0, 1, "Filename Column")
        self.combo_eng = self.make_combo(g, 1, 0, "New Name Column")
        self.combo_isrc = self.make_combo(g, 1, 1, "ISRC Column")

        # Toggles
        opts = tk.Frame(i2, bg=THEME["surface"])
        opts.pack(fill="x", pady=25)
        self.make_check(opts, "Smart ISRC (Ask if missing)", self.var_enable_isrc)
        self.make_check(opts, "Strict Case Match", self.var_strict_case)

        # Action Area
        act = tk.Frame(self.workspace, bg=THEME["bg"])
        act.pack(fill="x", pady=10)
        ActionButton(act, "Start Process", self.run_excel, width=180).pack(side="left")

        # Log
        self.log_area = scrolledtext.ScrolledText(
            self.workspace,
            height=8,
            bg=THEME["surface_container"],
            fg=THEME["primary"],
            bd=0,
            font=FONTS["mono"],
        )
        self.log_area.pack(fill="both", pady=20)

    # --- UTILITY VIEW ---
    def show_util_view(self):
        self.clear_ws()
        self.switch_view(lambda: None, self.btn_util["btn"], self.btn_util["ind"])
        self.header.config(text="Quick Utility")

        # Config Card
        card = SurfaceCard(self.workspace, width=950, height=380)
        card.pack(anchor="w")
        inner = card.inner

        tk.Label(
            inner,
            text="BULK OPERATIONS",
            bg=THEME["surface"],
            fg=THEME["primary"],
            font=FONTS["label"],
        ).pack(anchor="w", pady=(0, 15))
        self.make_file_row(
            inner,
            "Target Folder:",
            self.util_folder_path,
            lambda: [self.browse(self.util_folder_path), self.update_preview()],
        )

        g = tk.Frame(inner, bg=THEME["surface"])
        g.pack(fill="x", pady=20)
        self.make_input_row(g, 0, 0, "Find:", self.util_find)
        self.make_input_row(g, 0, 1, "Replace:", self.util_replace)
        self.make_input_row(g, 1, 0, "Prefix:", self.util_prefix)
        self.make_input_row(g, 1, 1, "Suffix:", self.util_suffix)

        # Options
        opt = tk.Frame(inner, bg=THEME["surface"])
        opt.pack(fill="x", pady=10)
        tk.Label(
            opt,
            text="Casing:",
            bg=THEME["surface"],
            fg=THEME["text_main"],
            font=FONTS["body"],
        ).pack(side="left")
        cb = ttk.Combobox(
            opt,
            textvariable=self.util_case,
            values=["No Change", "UPPERCASE", "lowercase", "Title Case"],
            width=15,
            font=FONTS["body"],
        )
        cb.pack(side="left", padx=10)
        cb.bind("<<ComboboxSelected>>", self.update_preview)

        self.make_check(
            opt, "Auto Numbering", self.util_num_enable, self.update_preview
        )

        # Preview
        tk.Label(
            self.workspace,
            text="PREVIEW (Double-Click file to Edit Manually)",
            bg=THEME["bg"],
            fg=THEME["secondary"],
            font=FONTS["label"],
        ).pack(anchor="w", pady=(25, 5))

        self.tree = ttk.Treeview(
            self.workspace, columns=("O", "N", "S"), show="headings", height=8
        )
        self.tree.heading("O", text="Original Name")
        self.tree.column("O", width=350)
        self.tree.heading("N", text="New Name (Editable)")
        self.tree.column("N", width=350)
        self.tree.heading("S", text="Status")
        self.tree.column("S", width=100)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_tree_double_click)  # MANUAL EDIT

        act = tk.Frame(self.workspace, bg=THEME["bg"])
        act.pack(fill="x", pady=20)
        ActionButton(act, "Apply Changes", self.run_util, width=200).pack(side="left")

    # --- WIDGET HELPERS ---
    def make_file_row(self, parent, label, var, cmd):
        f = tk.Frame(parent, bg=THEME["surface"])
        f.pack(fill="x")
        tk.Label(
            f,
            text=label,
            bg=THEME["surface"],
            fg=THEME["text_main"],
            font=FONTS["body"],
            width=15,
            anchor="w",
        ).pack(side="left")
        e = InputField(f, width=500)
        e.set_var(var)
        e.pack(side="left", padx=10)
        ActionButton(
            f,
            "Browse",
            cmd,
            width=80,
            height=40,
            bg=THEME["surface_container"],
            fg=THEME["primary"],
        ).pack(side="left")

    def make_combo(self, parent, r, c, label):
        f = tk.Frame(parent, bg=THEME["surface"])
        f.grid(row=r, column=c, padx=20, pady=10, sticky="ew")
        tk.Label(
            f,
            text=label,
            bg=THEME["surface"],
            fg=THEME["secondary"],
            font=FONTS["body"],
        ).pack(anchor="w")
        cb = ttk.Combobox(f, font=FONTS["body"])
        cb.pack(fill="x", pady=5)
        return cb

    def make_input_row(self, parent, r, c, label, var):
        f = tk.Frame(parent, bg=THEME["surface"])
        f.grid(row=r, column=c, padx=15, pady=8, sticky="w")
        tk.Label(
            f,
            text=label,
            bg=THEME["surface"],
            fg=THEME["text_main"],
            font=FONTS["body"],
        ).pack(side="left")
        e = InputField(f, width=200)
        e.set_var(var)
        e.bind_key(self.update_preview)
        e.pack(side="left", padx=10)

    def make_check(self, parent, text, var, cmd=None):
        c = tk.Checkbutton(
            parent,
            text=text,
            variable=var,
            command=cmd,
            bg=THEME["surface"],
            fg="white",
            selectcolor=THEME["bg"],
            activebackground=THEME["surface"],
            font=FONTS["body"],
        )
        c.pack(side="left", padx=20)

    # --- LOGIC ---
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
        f = filedialog.askopenfilename()
        if not f:
            return
        self.excel_path.set(f)
        try:
            hr = self.var_header_row.get() - 1
            if hr < 0:
                hr = 0
            self.df = (
                pd.read_csv(f, header=hr)
                if f.endswith(".csv")
                else pd.read_excel(f, header=hr)
            )

            cols = ["-- Select --"] + list(self.df.columns)
            for c in [
                self.combo_folder,
                self.combo_file,
                self.combo_eng,
                self.combo_isrc,
            ]:
                c["values"] = cols
                c.current(0)
            self.log(f"Loaded {len(self.df)} rows.")
        except Exception as e:
            messagebox.showerror("Err", str(e))

    def run_excel(self):
        root = self.root_folder_path.get()
        if self.df is None:
            return messagebox.showerror("Error", "Load Excel first")

        c_fol, c_fil = self.combo_folder.get(), self.combo_file.get()
        c_new, c_isrc = self.combo_eng.get(), self.combo_isrc.get()
        strict = self.var_strict_case.get()

        self.log("Starting...")
        count = 0

        for i, row in self.df.iterrows():
            try:
                fol = str(row[c_fol]).strip()
                fil = str(row[c_fil]).strip()
                eng = str(row[c_new]).strip()
                if fol == "nan" or fil == "nan":
                    continue

                name, ext = os.path.splitext(fil)
                if not ext:
                    ext = ".wav"
                target = name + ext

                # Search
                found_p, parent = None, None
                paths = [os.path.join(root, fol), root]
                for p in paths:
                    if not os.path.exists(p):
                        continue
                    if strict:
                        if target in os.listdir(p):
                            found_p, parent = os.path.join(p, target), p
                            break
                    else:
                        cand = os.path.join(p, target)
                        if os.path.exists(cand):
                            found_p, parent = cand, p
                            break

                if not found_p:
                    continue

                # ISRC
                isrc = ""
                if self.var_enable_isrc.get():
                    if c_isrc != "-- Select --" and pd.notna(row[c_isrc]):
                        isrc = str(row[c_isrc]).strip()
                    if not isrc:
                        val = simpledialog.askstring(
                            "ISRC Needed", f"Enter ISRC for:\n{target}"
                        )
                        isrc = val.strip() if val else ""

                base = f"_{name}" if (eng == "nan" or not eng) else eng
                final = f"{base}_{isrc}{ext}" if isrc else f"{base}{ext}"

                new_full = os.path.join(parent, final)
                if found_p != new_full:
                    if found_p.lower() == new_full.lower():
                        os.rename(found_p, found_p + "_tmp")
                        os.rename(found_p + "_tmp", new_full)
                    else:
                        os.rename(found_p, new_full)
                    self.log(f"Renamed: {target} -> {final}")
                    count += 1
            except Exception as e:
                self.log(f"Err {i}: {e}")
        messagebox.showinfo("Done", f"Processed {count}")

    # --- MANUAL EDIT LOGIC ---
    def on_tree_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        vals = self.tree.item(item_id, "values")
        orig_name = vals[0]

        # Prompt user
        manual = simpledialog.askstring(
            "Manual Edit",
            f"Enter new name for:\n{orig_name}",
            initialvalue=vals[1],
            parent=self.root,
        )
        if manual:
            self.manual_overrides[orig_name] = manual
            self.update_preview()

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
            if name in self.manual_overrides:
                final = self.manual_overrides[name]
                status = "MANUAL"
            else:
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
                status = "Ready" if final != name else "No Change"

            self.tree.insert("", "end", values=(name, final, status))

    def run_util(self):
        f = self.util_folder_path.get()
        if not f:
            return
        c = 0
        for item in self.tree.get_children():
            v = self.tree.item(item)["values"]
            if v[2] in ["Ready", "MANUAL"]:
                try:
                    os.rename(os.path.join(f, v[0]), os.path.join(f, v[1]))
                    c += 1
                except:
                    pass

        self.manual_overrides = {}
        self.update_preview()
        messagebox.showinfo("Success", f"Renamed {c} files.")


if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateRenamerApp(root)
    root.mainloop()
