import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, simpledialog
import pandas as pd

# --- GEMINI DESIGN SYSTEM ---
THEME = {
    "bg": "#131314",  # Gemini Dark BG
    "panel": "#1E1F20",  # Card Surface
    "input_bg": "#2D2E30",  # Input Field
    "text_main": "#E3E3E3",  # Primary Text
    "text_sub": "#C4C7C5",  # Secondary Text
    "accent": "#8AB4F8",  # Gemini Blue
    "accent_hover": "#AECBFA",  # Lighter Blue
    "success": "#81C995",  # Soft Green
    "border": "#444746",  # Border outline
}

FONTS = {
    "header": ("Google Sans", 22, "bold"),
    "sub": ("Google Sans", 12),
    "label": ("Google Sans", 10, "bold"),
    "body": ("Roboto", 10),
    "mono": ("Roboto Mono", 10),
}


# --- GRAPHICS ENGINE ---
def rounded_rect(canvas, x, y, w, h, r, color):
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
    def __init__(
        self, master, width, height, bg_color=THEME["panel"], corner_radius=20
    ):
        super().__init__(
            master, width=width, height=height, bg=THEME["bg"], highlightthickness=0
        )
        self.bg_color = bg_color
        rounded_rect(self, 0, 0, width, height, corner_radius, self.bg_color)
        self.inner = tk.Frame(self, bg=self.bg_color)
        self.create_window(
            width / 2,
            height / 2,
            window=self.inner,
            width=width - 30,
            height=height - 30,
        )

    def add_widget(self, widget, **pack_kwargs):
        widget.pack(**pack_kwargs)


class RoundedButton(tk.Canvas):
    def __init__(
        self,
        master,
        text,
        command,
        width=140,
        height=40,
        bg=THEME["accent"],
        fg="#000000",
        radius=18,
    ):
        super().__init__(
            master, width=width, height=height, bg=master["bg"], highlightthickness=0
        )
        self.command = command
        self.bg_normal = bg
        self.bg_hover = THEME["accent_hover"]
        self.shape = rounded_rect(
            self, 2, 2, width - 2, height - 2, radius, self.bg_normal
        )
        self.text = self.create_text(
            width / 2, height / 2, text=text, fill=fg, font=("Google Sans", 10, "bold")
        )
        self.bind("<Enter>", lambda e: self.itemconfig(self.shape, fill=self.bg_hover))
        self.bind("<Leave>", lambda e: self.itemconfig(self.shape, fill=self.bg_normal))
        self.bind("<Button-1>", lambda e: command() if command else None)


class RoundedEntry(tk.Canvas):
    def __init__(self, master, width=200, height=35, radius=12):
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


# --- APP CLASS ---
class UltimateRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Renamer AI (Gemini Edition)")
        self.root.geometry("1300x950")
        self.root.configure(bg=THEME["bg"])

        # Data
        self.df = None
        self.manual_overrides = (
            {}
        )  # Stores manual filenames {original_name: new_manual_name}

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

        self.setup_styles()
        self.build_ui()
        self.show_excel_view()  # Default

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "TCombobox",
            fieldbackground=THEME["input_bg"],
            background=THEME["panel"],
            foreground="white",
            arrowcolor=THEME["accent"],
            borderwidth=0,
        )
        style.map("TCombobox", fieldbackground=[("readonly", THEME["input_bg"])])

        style.configure(
            "Treeview",
            background=THEME["input_bg"],
            foreground=THEME["text_main"],
            fieldbackground=THEME["input_bg"],
            borderwidth=0,
            rowheight=40,
            font=FONTS["body"],
        )
        style.configure(
            "Treeview.Heading",
            background=THEME["panel"],
            foreground=THEME["text_main"],
            font=FONTS["label"],
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", THEME["accent"])],
            foreground=[("selected", "black")],
        )

    def build_ui(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=THEME["bg"], width=260)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="Gemini",
            bg=THEME["bg"],
            fg="white",
            font=("Google Sans", 26),
        ).pack(anchor="w", padx=30, pady=(40, 0))
        tk.Label(
            self.sidebar,
            text="RENAMER TOOL",
            bg=THEME["bg"],
            fg=THEME["accent"],
            font=("Google Sans", 10, "bold"),
        ).pack(anchor="w", padx=32)

        self.nav_frame = tk.Frame(self.sidebar, bg=THEME["bg"])
        self.nav_frame.pack(fill="x", pady=60)

        self.btn_excel = self.create_nav_btn("Smart Rename", self.show_excel_view)
        self.btn_util = self.create_nav_btn("Quick Utility", self.show_util_view)

        # Content
        self.main = tk.Frame(self.root, bg=THEME["bg"])
        self.main.pack(side="left", fill="both", expand=True, padx=40, pady=40)
        self.header = tk.Label(
            self.main, text="Overview", bg=THEME["bg"], fg="white", font=FONTS["header"]
        )
        self.header.pack(anchor="w", pady=(0, 20))
        self.workspace = tk.Frame(self.main, bg=THEME["bg"])
        self.workspace.pack(fill="both", expand=True)

    def create_nav_btn(self, text, cmd):
        f = tk.Frame(self.nav_frame, bg=THEME["bg"], pady=5)
        f.pack(fill="x")
        ind = tk.Frame(f, width=4, height=40, bg=THEME["bg"])
        ind.pack(side="left")
        b = tk.Button(
            f,
            text=f"  {text}",
            command=lambda: self.switch_view(cmd, b, ind),
            bg=THEME["bg"],
            fg=THEME["text_sub"],
            font=("Google Sans", 11),
            bd=0,
            activebackground=THEME["bg"],
            activeforeground="white",
            anchor="w",
        )
        b.pack(side="left", fill="x", padx=15)
        return {"btn": b, "ind": ind}

    def switch_view(self, cmd, b, ind):
        for item in [self.btn_excel, self.btn_util]:
            item["ind"].config(bg=THEME["bg"])
            item["btn"].config(fg=THEME["text_sub"], font=("Google Sans", 11))
        ind.config(bg=THEME["accent"])
        b.config(fg="white", font=("Google Sans", 11, "bold"))
        cmd()

    def clear_view(self):
        for w in self.workspace.winfo_children():
            w.destroy()

    # --- VIEW: EXCEL ---
    def show_excel_view(self):
        self.clear_view()
        self.switch_view(lambda: None, self.btn_excel["btn"], self.btn_excel["ind"])
        self.header.config(text="Smart Renaming (Excel)")

        # Config Panel
        panel = RoundedFrame(self.workspace, width=900, height=220)
        panel.pack(anchor="w")
        inner = panel.inner

        tk.Label(
            inner,
            text="SOURCE CONFIG",
            bg=THEME["panel"],
            fg=THEME["text_sub"],
            font=FONTS["label"],
        ).pack(anchor="w", pady=(0, 10))

        # Header Row
        h_box = tk.Frame(inner, bg=THEME["panel"])
        h_box.pack(anchor="w", pady=(0, 10))
        tk.Label(
            h_box, text="Header Row:", bg=THEME["panel"], fg=THEME["text_main"]
        ).pack(side="left")
        tk.Spinbox(
            h_box,
            from_=1,
            to=10,
            textvariable=self.var_header_row,
            width=3,
            bg=THEME["input_bg"],
            fg="white",
            buttonbackground=THEME["input_bg"],
        ).pack(side="left", padx=10)

        self.make_file_input(
            inner, "Excel File:", self.excel_path, self.load_excel_preview
        )
        tk.Frame(inner, height=10, bg=THEME["panel"]).pack()
        self.make_file_input(
            inner,
            "Music Folder:",
            self.root_folder_path,
            lambda: self.browse(self.root_folder_path),
        )

        # Mapping Panel
        panel2 = RoundedFrame(self.workspace, width=900, height=300)
        panel2.pack(anchor="w", pady=20)
        inner2 = panel2.inner

        tk.Label(
            inner2,
            text="DATA MAPPING",
            bg=THEME["panel"],
            fg=THEME["text_sub"],
            font=FONTS["label"],
        ).pack(anchor="w", pady=(0, 10))

        g = tk.Frame(inner2, bg=THEME["panel"])
        g.pack(fill="x")
        self.combo_folder = self.make_combo(g, 0, 0, "Folder Column")
        self.combo_file = self.make_combo(g, 0, 1, "Filename Column")
        self.combo_eng = self.make_combo(g, 1, 0, "New Name Column")
        self.combo_isrc = self.make_combo(g, 1, 1, "ISRC Column")

        # Options
        opt = tk.Frame(inner2, bg=THEME["panel"])
        opt.pack(fill="x", pady=20)
        self.make_chk(opt, "Smart ISRC (Ask if missing)", self.var_enable_isrc)
        self.make_chk(opt, "Strict Case Match", self.var_strict_case)

        # Action
        act = tk.Frame(self.workspace, bg=THEME["bg"])
        act.pack(fill="x")
        RoundedButton(
            act, "RUN RENAME", self.run_excel, width=180, bg=THEME["success"]
        ).pack(side="left")

        # Log
        self.log_area = scrolledtext.ScrolledText(
            self.workspace,
            height=10,
            bg=THEME["input_bg"],
            fg=THEME["accent"],
            bd=0,
            font=FONTS["mono"],
        )
        self.log_area.pack(fill="both", pady=20)

    # --- VIEW: UTILITY ---
    def show_util_view(self):
        self.clear_view()
        self.switch_view(lambda: None, self.btn_util["btn"], self.btn_util["ind"])
        self.header.config(text="Quick Utility (Manual Override)")

        # Config
        panel = RoundedFrame(self.workspace, width=900, height=400)
        panel.pack(anchor="w")
        inner = panel.inner

        tk.Label(
            inner,
            text="BULK RULES",
            bg=THEME["panel"],
            fg=THEME["text_sub"],
            font=FONTS["label"],
        ).pack(anchor="w", pady=(0, 10))
        self.make_file_input(
            inner,
            "Target Folder:",
            self.util_folder_path,
            lambda: [self.browse(self.util_folder_path), self.update_preview()],
        )

        g = tk.Frame(inner, bg=THEME["panel"])
        g.pack(fill="x", pady=20)
        self.make_entry_row(g, 0, 0, "Find:", self.util_find)
        self.make_entry_row(g, 0, 1, "Replace:", self.util_replace)
        self.make_entry_row(g, 1, 0, "Prefix:", self.util_prefix)
        self.make_entry_row(g, 1, 1, "Suffix:", self.util_suffix)

        opt = tk.Frame(inner, bg=THEME["panel"])
        opt.pack(fill="x", pady=10)
        tk.Label(opt, text="Casing:", bg=THEME["panel"], fg=THEME["text_main"]).pack(
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

        self.make_chk(opt, "Auto Numbering", self.util_num_enable, self.update_preview)

        # Preview
        tk.Label(
            self.workspace,
            text="PREVIEW (Double-Click file to Edit Manually)",
            bg=THEME["bg"],
            fg=THEME["text_sub"],
            font=FONTS["label"],
        ).pack(anchor="w", pady=(20, 5))

        self.tree = ttk.Treeview(
            self.workspace, columns=("O", "N", "S"), show="headings", height=8
        )
        self.tree.heading("O", text="Original Name")
        self.tree.column("O", width=300)
        self.tree.heading("N", text="New Name (Editable)")
        self.tree.column("N", width=300)
        self.tree.heading("S", text="Status")
        self.tree.column("S", width=100)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_tree_double_click)  # BIND CLICK

        RoundedButton(self.workspace, "APPLY CHANGES", self.run_util, width=200).pack(
            pady=20
        )

    # --- HELPERS ---
    def make_file_input(self, parent, label, var, cmd):
        f = tk.Frame(parent, bg=THEME["panel"])
        f.pack(fill="x")
        tk.Label(
            f,
            text=label,
            bg=THEME["panel"],
            fg=THEME["text_main"],
            width=15,
            anchor="w",
        ).pack(side="left")
        e = RoundedEntry(f, width=500)
        e.set_var(var)
        e.pack(side="left", padx=10)
        RoundedButton(
            f, "📂", cmd, width=40, height=35, bg=THEME["input_bg"], fg=THEME["accent"]
        ).pack(side="left")

    def make_combo(self, parent, r, c, label):
        f = tk.Frame(parent, bg=THEME["panel"])
        f.grid(row=r, column=c, padx=20, pady=10, sticky="ew")
        tk.Label(f, text=label, bg=THEME["panel"], fg=THEME["text_sub"]).pack(
            anchor="w"
        )
        cb = ttk.Combobox(f)
        cb.pack(fill="x", pady=5)
        return cb

    def make_entry_row(self, parent, r, c, label, var):
        f = tk.Frame(parent, bg=THEME["panel"])
        f.grid(row=r, column=c, padx=15, pady=5, sticky="w")
        tk.Label(f, text=label, bg=THEME["panel"], fg=THEME["text_sub"]).pack(
            side="left"
        )
        e = RoundedEntry(f, width=180, height=30)
        e.set_var(var)
        e.entry.bind("<KeyRelease>", self.update_preview)
        e.pack(side="left", padx=10)

    def make_chk(self, parent, text, var, cmd=None):
        c = tk.Checkbutton(
            parent,
            text=text,
            variable=var,
            command=cmd,
            bg=THEME["panel"],
            fg="white",
            selectcolor=THEME["bg"],
            activebackground=THEME["panel"],
        )
        c.pack(side="left", padx=15)

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

                # ISRC (Ask Every Time)
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

    # --- MANUAL EDIT FEATURE ---
    def on_tree_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        vals = self.tree.item(item_id, "values")
        orig_name = vals[0]
        curr_new = vals[1]

        # Ask user for manual override
        manual = simpledialog.askstring(
            "Manual Edit",
            f"Edit Name for:\n{orig_name}",
            initialvalue=curr_new,
            parent=self.root,
        )

        if manual:
            self.manual_overrides[orig_name] = manual
            # Update visual immediately
            self.tree.item(item_id, values=(orig_name, manual, "Manual"))

    def update_preview(self, e=None):
        # Clear tree
        for i in self.tree.get_children():
            self.tree.delete(i)
        f = self.util_folder_path.get()
        if not f or not os.path.isdir(f):
            return

        files = sorted([x for x in os.listdir(f) if os.path.isfile(os.path.join(f, x))])

        # Bulk settings
        find, rep = self.util_find.get(), self.util_replace.get()
        pre, suf = self.util_prefix.get(), self.util_suffix.get()
        case, num = self.util_case.get(), self.util_num_enable.get()
        ctr = self.util_num_start.get()

        for name in files:
            # CHECK MANUAL OVERRIDE FIRST
            if name in self.manual_overrides:
                final = self.manual_overrides[name]
                status = "Manual"
            else:
                # Apply Bulk Logic
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
            if v[2] in ["Ready", "Manual"]:
                try:
                    os.rename(os.path.join(f, v[0]), os.path.join(f, v[1]))
                    c += 1
                except:
                    pass

        # Clear manual overrides after run
        self.manual_overrides = {}
        self.update_preview()
        messagebox.showinfo("Success", f"Renamed {c} files.")


if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateRenamerApp(root)
    root.mainloop()
