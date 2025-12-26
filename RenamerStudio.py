import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import customtkinter as ctk  # pip install customtkinter pandas openpyxl
import pandas as pd

# --- THEME CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# High Contrast Palette
THEME = {
    "bg": "#131314",  # Deep Background
    "surface": "#1E1F20",  # Card Surface
    "surface_hover": "#2D2E30",  # Input Fields (Dark)
    "primary": "#A8C7FA",  # Light Blue (Buttons)
    "on_primary": "#000000",  # Black Text on Blue (High Contrast)
    "text_main": "#FFFFFF",  # Pure White Text
    "text_dim": "#E3E3E3",  # Light Grey
    "outline": "#8E918F",  # Borders
}

# BIGGER FONTS (Readability Focused)
FONTS = {
    "display": ("Poppins", 30, "bold"),
    "header": ("Poppins", 22, "bold"),
    "sub": ("Poppins", 16, "bold"),
    "body": ("Open Sans", 14),
    "label": ("Open Sans", 13, "bold"),
    "mono": ("Consolas", 13),
}

RADIUS = 10


class RenamerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Renamer Studio Pro")
        self.geometry("1450x1000")
        self.configure(fg_color=THEME["bg"])

        # Data
        self.df = None
        self.manual_overrides = {}

        # Vars
        self.excel_path = ctk.StringVar()
        self.root_folder_path = ctk.StringVar()
        self.util_folder_path = ctk.StringVar()

        self.var_header_row = ctk.IntVar(value=2)
        self.var_enable_isrc = ctk.BooleanVar(value=True)
        self.var_strict_case = ctk.BooleanVar(value=False)

        self.util_find = ctk.StringVar()
        self.util_replace = ctk.StringVar()
        self.util_prefix = ctk.StringVar()
        self.util_suffix = ctk.StringVar()
        self.util_case = ctk.StringVar(value="No Change")
        self.util_num_enable = ctk.BooleanVar(value=False)

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.style_treeview()
        self.setup_sidebar()
        self.setup_main_area()
        self.show_excel_view()

    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Bigger Text in Table
        style.configure(
            "Treeview",
            background=THEME["surface"],
            foreground=THEME["text_main"],
            fieldbackground=THEME["surface"],
            borderwidth=0,
            rowheight=40,
            font=("Open Sans", 13),
        )
        style.configure(
            "Treeview.Heading",
            background=THEME["surface_hover"],
            foreground=THEME["primary"],
            font=("Poppins", 13, "bold"),
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", THEME["primary"])],
            foreground=[("selected", "black")],  # Black text on selection
        )

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self, width=280, corner_radius=0, fg_color=THEME["bg"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        # Branding
        ctk.CTkLabel(
            self.sidebar,
            text="Renamer",
            font=FONTS["display"],
            text_color=THEME["text_main"],
        ).grid(row=0, column=0, padx=25, pady=(50, 0), sticky="w")
        ctk.CTkLabel(
            self.sidebar,
            text="STUDIO PRO",
            font=("Poppins", 12, "bold"),
            text_color=THEME["primary"],
        ).grid(row=1, column=0, padx=27, pady=(0, 50), sticky="w")

        # Nav Buttons
        self.btn_excel = self.create_nav_btn("📊 Smart Rename", self.show_excel_view, 2)
        self.btn_util = self.create_nav_btn("🛠 Quick Utility", self.show_util_view, 3)

    def create_nav_btn(self, text, command, row):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            command=command,
            fg_color="transparent",
            text_color=THEME["text_dim"],
            hover_color=THEME["surface"],
            anchor="w",
            height=55,
            font=FONTS["sub"],
            corner_radius=RADIUS,
        )
        btn.grid(row=row, column=0, padx=15, pady=8, sticky="ew")
        return btn

    def setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=THEME["bg"])
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.header_label = ctk.CTkLabel(
            self.main_frame,
            text="Overview",
            font=FONTS["header"],
            text_color=THEME["text_main"],
        )
        self.header_label.grid(row=0, column=0, sticky="w", padx=40, pady=(40, 20))

        self.content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=20)

    def set_active_nav(self, active_btn):
        self.btn_excel.configure(fg_color="transparent", text_color=THEME["text_dim"])
        self.btn_util.configure(fg_color="transparent", text_color=THEME["text_dim"])
        active_btn.configure(fg_color=THEME["surface"], text_color=THEME["primary"])

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # ================= EXCEL VIEW =================
    def show_excel_view(self):
        self.set_active_nav(self.btn_excel)
        self.clear_content()
        self.header_label.configure(text="Smart Renaming")

        # 1. Config Card
        card_conf = self.create_card("Source Configuration")

        # Header Row Logic (Reload button removed, just input)
        row_h = ctk.CTkFrame(card_conf, fg_color="transparent")
        row_h.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            row_h,
            text="Header Row:",
            text_color=THEME["text_main"],
            font=FONTS["label"],
        ).pack(side="left", padx=(0, 10))

        # High Contrast Entry
        ctk.CTkEntry(
            row_h,
            textvariable=self.var_header_row,
            width=60,
            font=FONTS["mono"],
            fg_color=THEME["surface_hover"],
            text_color="white",
            border_width=1,
            border_color=THEME["outline"],
        ).pack(side="left")
        ctk.CTkLabel(
            row_h,
            text="(Set this before browsing file)",
            text_color=THEME["text_dim"],
            font=("Open Sans", 12),
        ).pack(side="left", padx=10)

        # File Inputs (Re-browsing here will trigger reload)
        self.create_file_row(
            card_conf, "Excel Database:", self.excel_path, self.browse_excel
        )
        self.create_file_row(
            card_conf,
            "Music Folder:",
            self.root_folder_path,
            lambda: self.browse(self.root_folder_path),
        )

        # 2. Mapping Card
        card_map = self.create_card("Column Mapping")

        grid_map = ctk.CTkFrame(card_map, fg_color="transparent")
        grid_map.pack(fill="x", pady=10)
        grid_map.grid_columnconfigure((0, 1), weight=1)

        self.combo_folder = self.create_combo(grid_map, "Folder Name Column", 0, 0)
        self.combo_file = self.create_combo(grid_map, "Current Filename Column", 0, 1)
        self.combo_eng = self.create_combo(grid_map, "New Track Name Column", 1, 0)
        self.combo_isrc = self.create_combo(grid_map, "ISRC Column", 1, 1)

        row_tog = ctk.CTkFrame(card_map, fg_color="transparent")
        row_tog.pack(fill="x", pady=25)
        self.create_toggle(
            row_tog, "✨ Smart ISRC (Popup if missing)", self.var_enable_isrc
        )
        self.create_toggle(row_tog, "🔒 Strict Case Match", self.var_strict_case)

        self.create_action_btn("▶ Start Renaming", self.run_excel)

        # Log
        self.log_box = ctk.CTkTextbox(
            self.content,
            height=150,
            fg_color=THEME["surface"],
            text_color="white",
            font=FONTS["mono"],
            corner_radius=RADIUS,
            border_width=1,
            border_color=THEME["outline"],
        )
        self.log_box.pack(fill="x", padx=20, pady=20)
        self.log_box.configure(state="disabled")

    # ================= UTILITY VIEW =================
    def show_util_view(self):
        self.set_active_nav(self.btn_util)
        self.clear_content()
        self.header_label.configure(text="Quick Utility")

        card_rules = self.create_card("Bulk Operations")
        self.create_file_row(
            card_rules,
            "Target Folder:",
            self.util_folder_path,
            lambda: [self.browse(self.util_folder_path), self.update_preview()],
        )

        grid_in = ctk.CTkFrame(card_rules, fg_color="transparent")
        grid_in.pack(fill="x", pady=15)
        grid_in.grid_columnconfigure((0, 1), weight=1)

        self.create_input_pair(grid_in, "Find:", self.util_find, 0, 0)
        self.create_input_pair(grid_in, "Replace:", self.util_replace, 0, 1)
        self.create_input_pair(grid_in, "Prefix:", self.util_prefix, 1, 0)
        self.create_input_pair(grid_in, "Suffix:", self.util_suffix, 1, 1)

        row_opt = ctk.CTkFrame(card_rules, fg_color="transparent")
        row_opt.pack(fill="x", pady=10)

        ctk.CTkLabel(
            row_opt, text="Casing:", text_color=THEME["text_main"], font=FONTS["body"]
        ).pack(side="left")
        cb_case = ctk.CTkComboBox(
            row_opt,
            variable=self.util_case,
            values=["No Change", "UPPERCASE", "lowercase", "Title Case"],
            width=180,
            fg_color=THEME["surface_hover"],
            border_width=1,
            border_color=THEME["outline"],
            button_color=THEME["primary"],
            text_color="white",
            corner_radius=RADIUS,
            font=FONTS["body"],
        )
        cb_case.pack(side="left", padx=10)
        cb_case.configure(command=self.update_preview)

        self.create_toggle(
            row_opt, "#️⃣ Auto Numbering", self.util_num_enable, self.update_preview
        )

        # Preview
        ctk.CTkLabel(
            self.content,
            text="PREVIEW (Double-click to Edit)",
            font=FONTS["label"],
            text_color=THEME["text_dim"],
        ).pack(anchor="w", padx=20, pady=(15, 5))

        tree_frame = ctk.CTkFrame(
            self.content,
            fg_color=THEME["surface"],
            corner_radius=RADIUS,
            border_width=1,
            border_color=THEME["outline"],
        )
        tree_frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.tree = ttk.Treeview(
            tree_frame, columns=("O", "N", "S"), show="headings", height=8
        )
        self.tree.heading("O", text="Original Name")
        self.tree.column("O", width=400)
        self.tree.heading("N", text="New Name")
        self.tree.column("N", width=400)
        self.tree.heading("S", text="Status")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        self.create_action_btn("✓ Apply Changes", self.run_util)

    # --- HELPERS ---
    def create_card(self, title):
        card = ctk.CTkFrame(
            self.content, fg_color=THEME["surface"], corner_radius=RADIUS
        )
        card.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkLabel(
            card, text=title, font=FONTS["sub"], text_color=THEME["primary"]
        ).pack(anchor="w", padx=25, pady=(20, 15))
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=25, pady=(0, 25))
        return inner

    def create_file_row(self, parent, label, var, cmd):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", pady=8)
        ctk.CTkLabel(
            f,
            text=label,
            width=140,
            anchor="w",
            text_color=THEME["text_main"],
            font=FONTS["body"],
        ).pack(side="left")

        # High Contrast Entry
        ctk.CTkEntry(
            f,
            textvariable=var,
            height=45,
            fg_color=THEME["surface_hover"],
            border_width=1,
            border_color=THEME["outline"],
            text_color="white",
            corner_radius=RADIUS,
            font=FONTS["body"],
        ).pack(side="left", fill="x", expand=True, padx=10)

        # --- BIGGER ICON BUTTON ---
        ctk.CTkButton(
            f,
            text="📂",
            width=70,
            height=45,
            command=cmd,
            fg_color=THEME["surface_hover"],
            hover_color="gray",
            corner_radius=RADIUS,
            text_color="white",
            border_width=1,
            border_color=THEME["outline"],
            font=("Segoe UI", 30),  # HUGE FOLDER ICON
        ).pack(side="left")

    def create_combo(self, parent, label, r, c):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=r, column=c, padx=15, pady=10, sticky="ew")
        ctk.CTkLabel(
            f, text=label, text_color=THEME["text_dim"], anchor="w", font=FONTS["label"]
        ).pack(fill="x", pady=(0, 5))

        cb = ctk.CTkComboBox(
            f,
            height=45,
            fg_color=THEME["surface_hover"],
            border_width=1,
            border_color=THEME["outline"],
            button_color=THEME["primary"],
            button_hover_color="white",
            text_color="white",
            dropdown_fg_color=THEME["surface_hover"],
            corner_radius=RADIUS,
            font=FONTS["body"],
        )
        cb.pack(fill="x")
        return cb

    def create_input_pair(self, parent, label, var, r, c):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=r, column=c, padx=15, pady=10, sticky="ew")
        ctk.CTkLabel(
            f, text=label, text_color=THEME["text_dim"], anchor="w", font=FONTS["label"]
        ).pack(fill="x", pady=(0, 5))
        e = ctk.CTkEntry(
            f,
            textvariable=var,
            height=42,
            fg_color=THEME["surface_hover"],
            border_width=1,
            border_color=THEME["outline"],
            text_color="white",
            corner_radius=RADIUS,
            font=FONTS["body"],
        )
        e.bind("<KeyRelease>", self.update_preview)
        e.pack(fill="x")

    def create_toggle(self, parent, text, var, cmd=None):
        ctk.CTkCheckBox(
            parent,
            text=text,
            variable=var,
            command=cmd,
            fg_color=THEME["primary"],
            hover_color=THEME["primary"],
            checkmark_color="black",
            font=FONTS["body"],
            text_color=THEME["text_main"],
            corner_radius=6,
            border_width=2,
            border_color=THEME["outline"],
        ).pack(side="left", padx=(0, 25))

    def create_action_btn(self, text, cmd):
        # Black Text on Light Blue for Maximum Contrast
        ctk.CTkButton(
            self.content,
            text=text,
            command=cmd,
            height=55,
            width=240,
            fg_color=THEME["primary"],
            text_color="black",
            font=FONTS["sub"],
            corner_radius=28,
            hover_color="white",
        ).pack(anchor="w", padx=20, pady=25)

    # --- LOGIC ---
    def log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self.update()

    def browse(self, var):
        f = filedialog.askdirectory()
        if f:
            var.set(f)

    # Separate Browse Excel function to ensure proper flow
    def browse_excel(self):
        f = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls *.csv")])
        if f:
            self.excel_path.set(f)
            self.load_excel_preview()

    def load_excel_preview(self):
        file_path = self.excel_path.get()
        if not file_path:
            return

        try:
            h_row = self.var_header_row.get() - 1
            if h_row < 0:
                h_row = 0
        except:
            h_row = 1

        try:
            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path, header=h_row)
            else:
                self.df = pd.read_excel(file_path, header=h_row)

            cols = ["-- Select --"] + list(self.df.columns)
            for c in [
                self.combo_folder,
                self.combo_file,
                self.combo_eng,
                self.combo_isrc,
            ]:
                c.configure(values=cols)
                c.set(cols[0])

            # --- IMPROVED AUTO-SELECT LOGIC ---
            if len(cols) > 1:
                # 1. Folder
                guesses = [c for c in cols if "folder" in str(c).lower()]
                if guesses:
                    self.combo_folder.set(guesses[0])

                # 2. Filename
                guesses = [
                    c
                    for c in cols
                    if "file" in str(c).lower() and "name" in str(c).lower()
                ]
                if guesses:
                    self.combo_file.set(guesses[0])

                # 3. New Name (English Track Name)
                guesses = [
                    c
                    for c in cols
                    if "english track name" in str(c).lower()
                    or "new track" in str(c).lower()
                    or "english name" in str(c).lower()
                ]
                if guesses:
                    self.combo_eng.set(guesses[0])

                # 4. ISRC (ISRC Code)
                guesses = [c for c in cols if "isrc" in str(c).lower()]
                if guesses:
                    self.combo_isrc.set(guesses[0])

            self.log(f"Loaded {len(self.df)} rows (Header: {h_row+1}).")

        except Exception as e:
            messagebox.showerror("Error", f"Could not read Excel file.\n{e}")

    def run_excel(self):
        root = self.root_folder_path.get()
        if self.df is None:
            return messagebox.showerror("Error", "Please load an Excel file first.")

        c_fol, c_fil = self.combo_folder.get(), self.combo_file.get()
        c_new, c_isrc = self.combo_eng.get(), self.combo_isrc.get()
        strict = self.var_strict_case.get()

        self.log("Starting batch rename...")
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

                isrc = ""
                if self.var_enable_isrc.get():
                    if c_isrc != "-- Select --" and pd.notna(row[c_isrc]):
                        isrc = str(row[c_isrc]).strip()
                    if not isrc:
                        val = simpledialog.askstring(
                            "ISRC Required", f"Enter ISRC for:\n{target}"
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
                self.log(f"Err Row {i}: {e}")
        messagebox.showinfo("Done", f"Processed {count} files.")

    # --- UTILITY LOGIC ---
    def on_tree_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        vals = self.tree.item(item_id, "values")
        orig_name = vals[0]

        manual = simpledialog.askstring(
            "Manual Override", f"Enter new name for:\n{orig_name}", initialvalue=vals[1]
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

        for i, name in enumerate(files):
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
                    new_r += f"_{str(i+1).zfill(3)}"

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
    app = RenamerApp()
    app.mainloop()
