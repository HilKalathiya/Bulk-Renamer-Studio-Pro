import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, simpledialog


class UltimateRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Audio Renamer (Dual Mode)")
        self.root.geometry("1100x850")

        # --- THEME SETTINGS ---
        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        self.entry_bg = "#404040"
        self.accent_color = "#00adb5"  # Cyan
        self.btn_bg = "#3a3a3a"
        self.nav_bg = "#1f1f1f"

        self.style_ui()

        # --- STATE VARIABLES ---
        self.current_mode = "EXCEL"  # or "UTILITY"

        # EXCEL VARS
        self.excel_path = tk.StringVar()
        self.root_folder_path = tk.StringVar()
        self.var_enable_isrc = tk.BooleanVar(value=True)  # New Feature
        self.df = None
        self.folder_isrc_cache = {}

        # UTILITY VARS
        self.util_folder_path = tk.StringVar()
        self.util_find = tk.StringVar()
        self.util_replace = tk.StringVar()
        self.util_prefix = tk.StringVar()
        self.util_suffix = tk.StringVar()
        self.util_case = tk.StringVar(value="No Change")
        self.util_num_enable = tk.BooleanVar(value=False)
        self.util_num_start = tk.IntVar(value=1)
        self.util_num_pad = tk.IntVar(value=3)  # e.g. 001

        # --- MAIN CONTAINER ---
        self.main_container = tk.Frame(root, bg=self.bg_color)
        self.main_container.pack(fill="both", expand=True)

        # --- TOP NAVIGATION ---
        self.nav_frame = tk.Frame(self.main_container, bg=self.nav_bg, pady=10, padx=20)
        self.nav_frame.pack(fill="x")

        self.lbl_title = tk.Label(
            self.nav_frame,
            text="MASTER EXCEL MODE",
            font=("Segoe UI", 16, "bold"),
            bg=self.nav_bg,
            fg=self.accent_color,
        )
        self.lbl_title.pack(side="left")

        self.btn_switch = tk.Button(
            self.nav_frame,
            text="⇄ SWITCH TO SIMPLE MODE",
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.toggle_mode,
            cursor="hand2",
        )
        self.btn_switch.pack(side="right")

        # --- MODE FRAMES ---
        self.frame_excel = tk.Frame(self.main_container, bg=self.bg_color)
        self.frame_utility = tk.Frame(self.main_container, bg=self.bg_color)

        # Initialize Logic
        self.setup_excel_mode()
        self.setup_utility_mode()

        # Show Default
        self.frame_excel.pack(fill="both", expand=True, padx=20, pady=10)

    def style_ui(self):
        self.root.configure(bg=self.bg_color)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TCombobox",
            fieldbackground=self.entry_bg,
            background=self.btn_bg,
            foreground="white",
        )
        style.map("TCombobox", fieldbackground=[("readonly", self.entry_bg)])
        style.configure(
            "Treeview",
            background="#333333",
            foreground="white",
            fieldbackground="#333333",
        )
        style.map("Treeview", background=[("selected", self.accent_color)])

    def toggle_mode(self):
        if self.current_mode == "EXCEL":
            self.current_mode = "UTILITY"
            self.lbl_title.config(text="SIMPLE UTILITY MODE")
            self.btn_switch.config(text="⇄ SWITCH TO EXCEL MODE")
            self.frame_excel.pack_forget()
            self.frame_utility.pack(fill="both", expand=True, padx=20, pady=10)
        else:
            self.current_mode = "EXCEL"
            self.lbl_title.config(text="MASTER EXCEL MODE")
            self.btn_switch.config(text="⇄ SWITCH TO SIMPLE MODE")
            self.frame_utility.pack_forget()
            self.frame_excel.pack(fill="both", expand=True, padx=20, pady=10)

    # =========================================================================
    # MODE A: EXCEL MASTER LOGIC
    # =========================================================================
    def setup_excel_mode(self):
        parent = self.frame_excel

        # 1. Config Frame
        cfg = tk.LabelFrame(
            parent,
            text="Configuration",
            bg=self.bg_color,
            fg=self.accent_color,
            font=("Bold", 11),
            padx=15,
            pady=15,
        )
        cfg.pack(fill="x", pady=5)

        tk.Label(cfg, text="Excel File:", bg=self.bg_color, fg=self.fg_color).grid(
            row=0, column=0, sticky="w"
        )
        tk.Entry(
            cfg, textvariable=self.excel_path, width=60, bg=self.entry_bg, fg="white"
        ).grid(row=0, column=1, padx=5)
        tk.Button(cfg, text="Browse", command=self.load_excel_preview).grid(
            row=0, column=2
        )

        tk.Label(cfg, text="Music Folder:", bg=self.bg_color, fg=self.fg_color).grid(
            row=1, column=0, sticky="w"
        )
        tk.Entry(
            cfg,
            textvariable=self.root_folder_path,
            width=60,
            bg=self.entry_bg,
            fg="white",
        ).grid(row=1, column=1, padx=5)
        tk.Button(
            cfg,
            text="Browse",
            command=lambda: self.browse_folder(self.root_folder_path),
        ).grid(row=1, column=2)

        # 2. Mapping Frame
        map_fr = tk.LabelFrame(
            parent,
            text="Column Mapping",
            bg=self.bg_color,
            fg=self.accent_color,
            font=("Bold", 11),
            padx=15,
            pady=15,
        )
        map_fr.pack(fill="x", pady=5)

        # Columns
        tk.Label(map_fr, text="Folder Name:", bg=self.bg_color, fg=self.fg_color).grid(
            row=0, column=0, sticky="w"
        )
        self.combo_folder = ttk.Combobox(map_fr, width=30)
        self.combo_folder.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(
            map_fr, text="Current File Name:", bg=self.bg_color, fg=self.fg_color
        ).grid(row=0, column=2, sticky="w")
        self.combo_filename = ttk.Combobox(map_fr, width=30)
        self.combo_filename.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(map_fr, text="English Name:", bg=self.bg_color, fg=self.fg_color).grid(
            row=1, column=0, sticky="w"
        )
        self.combo_newname = ttk.Combobox(map_fr, width=30)
        self.combo_newname.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(map_fr, text="ISRC Column:", bg=self.bg_color, fg=self.fg_color).grid(
            row=1, column=2, sticky="w"
        )
        self.combo_isrc = ttk.Combobox(map_fr, width=30)
        self.combo_isrc.grid(row=1, column=3, padx=5, pady=5)

        # 3. ISRC Toggle (New Feature)
        isrc_fr = tk.Frame(parent, bg=self.bg_color, pady=5)
        isrc_fr.pack(fill="x")
        chk_isrc = tk.Checkbutton(
            isrc_fr,
            text="Enable ISRC Processing (Ask/Apply Codes)",
            variable=self.var_enable_isrc,
            bg=self.bg_color,
            fg="white",
            selectcolor=self.entry_bg,
            activebackground=self.bg_color,
        )
        chk_isrc.pack(side="left")

        # 4. Action
        tk.Button(
            parent,
            text="START EXCEL RENAME",
            bg="green",
            fg="white",
            font=("Bold", 12),
            command=self.run_excel_rename,
        ).pack(fill="x", pady=10)

        # 5. Log
        self.log_area = scrolledtext.ScrolledText(
            parent, height=10, bg="#1e1e1e", fg="#00ff00"
        )
        self.log_area.pack(fill="both", expand=True)

    # =========================================================================
    # MODE B: UTILITY LOGIC
    # =========================================================================
    def setup_utility_mode(self):
        parent = self.frame_utility

        # 1. Folder Selection
        top = tk.Frame(parent, bg=self.bg_color, pady=10)
        top.pack(fill="x")
        tk.Label(top, text="Select Folder:", bg=self.bg_color, fg="white").pack(
            side="left"
        )
        tk.Entry(
            top,
            textvariable=self.util_folder_path,
            width=70,
            bg=self.entry_bg,
            fg="white",
        ).pack(side="left", padx=10)
        tk.Button(top, text="Browse", command=lambda: self.browse_and_preview()).pack(
            side="left"
        )

        # 2. Options Grid
        opts = tk.LabelFrame(
            parent,
            text="Renaming Rules",
            bg=self.bg_color,
            fg=self.accent_color,
            padx=10,
            pady=10,
        )
        opts.pack(fill="x")

        # Find / Replace
        tk.Label(opts, text="Find:", bg=self.bg_color, fg="white").grid(
            row=0, column=0, sticky="e"
        )
        e_find = tk.Entry(
            opts, textvariable=self.util_find, bg=self.entry_bg, fg="white"
        )
        e_find.grid(row=0, column=1, padx=5, pady=2)
        e_find.bind("<KeyRelease>", self.update_utility_preview)

        tk.Label(opts, text="Replace:", bg=self.bg_color, fg="white").grid(
            row=0, column=2, sticky="e"
        )
        e_rep = tk.Entry(
            opts, textvariable=self.util_replace, bg=self.entry_bg, fg="white"
        )
        e_rep.grid(row=0, column=3, padx=5, pady=2)
        e_rep.bind("<KeyRelease>", self.update_utility_preview)

        # Prefix / Suffix
        tk.Label(opts, text="Add Prefix:", bg=self.bg_color, fg="white").grid(
            row=1, column=0, sticky="e"
        )
        e_pre = tk.Entry(
            opts, textvariable=self.util_prefix, bg=self.entry_bg, fg="white"
        )
        e_pre.grid(row=1, column=1, padx=5, pady=2)
        e_pre.bind("<KeyRelease>", self.update_utility_preview)

        tk.Label(opts, text="Add Suffix:", bg=self.bg_color, fg="white").grid(
            row=1, column=2, sticky="e"
        )
        e_suf = tk.Entry(
            opts, textvariable=self.util_suffix, bg=self.entry_bg, fg="white"
        )
        e_suf.grid(row=1, column=3, padx=5, pady=2)
        e_suf.bind("<KeyRelease>", self.update_utility_preview)

        # Case
        tk.Label(opts, text="Casing:", bg=self.bg_color, fg="white").grid(
            row=2, column=0, sticky="e"
        )
        cb_case = ttk.Combobox(
            opts,
            textvariable=self.util_case,
            values=["No Change", "UPPERCASE", "lowercase", "Title Case"],
        )
        cb_case.grid(row=2, column=1, padx=5, pady=2)
        cb_case.bind("<<ComboboxSelected>>", self.update_utility_preview)

        # Numbering
        tk.Label(opts, text="Numbering:", bg=self.bg_color, fg="white").grid(
            row=3, column=0, sticky="e"
        )
        chk_num = tk.Checkbutton(
            opts,
            text="Append Number",
            variable=self.util_num_enable,
            bg=self.bg_color,
            fg="white",
            selectcolor=self.entry_bg,
            command=self.update_utility_preview,
        )
        chk_num.grid(row=3, column=1, sticky="w")

        tk.Label(opts, text="Start At:", bg=self.bg_color, fg="white").grid(
            row=3, column=2, sticky="e"
        )
        sp_start = tk.Spinbox(
            opts,
            from_=0,
            to=9999,
            textvariable=self.util_num_start,
            width=5,
            command=self.update_utility_preview,
        )
        sp_start.grid(row=3, column=3, sticky="w")

        # 3. Preview Table
        tk.Label(
            parent,
            text="Preview (Check before renaming):",
            bg=self.bg_color,
            fg="#aaaaaa",
        ).pack(pady=(10, 0), anchor="w")

        self.tree = ttk.Treeview(
            parent, columns=("Old", "New", "Status"), show="headings", height=15
        )
        self.tree.heading("Old", text="Original Name")
        self.tree.heading("New", text="New Name")
        self.tree.heading("Status", text="Status")
        self.tree.column("Old", width=300)
        self.tree.column("New", width=300)
        self.tree.column("Status", width=100)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # 4. Run Button
        tk.Button(
            parent,
            text="RENAME ALL FILES",
            bg=self.accent_color,
            fg="white",
            font=("Bold", 12),
            command=self.run_utility_rename,
        ).pack(fill="x", pady=10)

    # =========================================================================
    # COMMON HELPERS
    # =========================================================================
    def log(self, message, color="#00ff00"):
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

    # =========================================================================
    # EXCEL LOGIC IMPLEMENTATION
    # =========================================================================
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

            # Fallback headers
            if (
                "Folder Name" not in self.df.columns
                and "File Name" not in self.df.columns
            ):
                self.log("Switching to Row 1 headers...", "#ffff00")
                if file_path.endswith(".csv"):
                    self.df = pd.read_csv(file_path, header=0)
                else:
                    self.df = pd.read_excel(file_path, header=0)

            cols = ["-- Select Column --"] + list(self.df.columns)
            for c in [
                self.combo_folder,
                self.combo_filename,
                self.combo_newname,
                self.combo_isrc,
            ]:
                c["values"] = cols
                c.current(0)

            # Auto-select
            self.set_combo(self.combo_folder, "Folder Name")
            self.set_combo(self.combo_filename, "File Name")
            self.set_combo(self.combo_newname, "English Track Name")
            isrcs = [x for x in self.df.columns if "ISRC" in x.upper()]
            if isrcs:
                self.set_combo(self.combo_isrc, isrcs[0])
            self.log(f"Excel Loaded: {len(self.df)} rows.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def set_combo(self, combo, val):
        if val in combo["values"]:
            combo.set(val)

    def run_excel_rename(self):
        root_dir = self.root_folder_path.get()
        if not self.df is not None:
            return messagebox.showwarning("Err", "Load Excel")

        c_folder = self.combo_folder.get()
        c_file = self.combo_filename.get()
        c_new = self.combo_newname.get()
        c_isrc = self.combo_isrc.get()

        # Check if ISRC is enabled
        use_isrc = self.var_enable_isrc.get()

        self.log("--- STARTING EXCEL RENAME ---", self.accent_color)
        self.folder_isrc_cache = {}
        processed = 0

        for index, row in self.df.iterrows():
            try:
                folder = str(row[c_folder]).strip()
                fname = str(row[c_file]).strip()
                eng_name = str(row[c_new]).strip()

                if folder == "nan" or fname == "nan":
                    continue

                # Check extension
                name_root, name_ext = os.path.splitext(fname)
                if not name_ext:
                    name_ext = ".wav"
                curr_file_full = name_root + name_ext

                # Path resolution
                path_sub = os.path.join(root_dir, folder, curr_file_full)
                path_root = os.path.join(root_dir, curr_file_full)

                if os.path.exists(path_sub):
                    old_path = path_sub
                    parent = os.path.join(root_dir, folder)
                elif os.path.exists(path_root):
                    old_path = path_root
                    parent = root_dir
                else:
                    continue  # File not found

                # --- ISRC LOGIC (Conditional) ---
                isrc_val = ""
                if use_isrc:
                    # 1. Try Excel
                    if c_isrc != "-- Select Column --" and pd.notna(row[c_isrc]):
                        isrc_val = str(row[c_isrc]).strip()

                    # 2. Try Cache/Popup
                    if not isrc_val:
                        if folder in self.folder_isrc_cache:
                            isrc_val = self.folder_isrc_cache[folder]
                        else:
                            # Ask User
                            self.root.deiconify()
                            ans = simpledialog.askstring(
                                "ISRC Needed",
                                f"Enter ISRC for folder:\n{folder}\n(Cancel/Empty to skip)",
                                parent=self.root,
                            )
                            isrc_val = ans.strip() if ans else ""
                            self.folder_isrc_cache[folder] = isrc_val

                # --- NAME CONSTRUCTION ---
                if eng_name == "nan" or not eng_name:
                    base = f"_{name_root}"  # Fallback
                else:
                    base = eng_name

                if isrc_val:
                    new_name = f"{base}_{isrc_val}{name_ext}"
                else:
                    new_name = f"{base}{name_ext}"

                # Rename
                new_full = os.path.join(parent, new_name)
                if not os.path.exists(new_full):
                    os.rename(old_path, new_full)
                    self.log(f"[OK] {curr_file_full} -> {new_name}")
                    processed += 1
                else:
                    self.log(f"[SKIP] Exists: {new_name}")

            except Exception as e:
                self.log(f"Error row {index}: {e}", "red")

        messagebox.showinfo("Done", f"Processed {processed} files.")

    # =========================================================================
    # UTILITY LOGIC IMPLEMENTATION
    # =========================================================================
    def update_utility_preview(self, event=None):
        # Clear Tree
        for i in self.tree.get_children():
            self.tree.delete(i)

        folder = self.util_folder_path.get()
        if not folder or not os.path.isdir(folder):
            return

        files = sorted(
            [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        )

        find_txt = self.util_find.get()
        rep_txt = self.util_replace.get()
        prefix = self.util_prefix.get()
        suffix = self.util_suffix.get()
        case_mode = self.util_case.get()
        do_num = self.util_num_enable.get()
        start_num = self.util_num_start.get()

        count = start_num

        for f in files:
            name_root, name_ext = os.path.splitext(f)
            new_root = name_root

            # 1. Find/Replace
            if find_txt:
                new_root = new_root.replace(find_txt, rep_txt)

            # 2. Case
            if case_mode == "UPPERCASE":
                new_root = new_root.upper()
            elif case_mode == "lowercase":
                new_root = new_root.lower()
            elif case_mode == "Title Case":
                new_root = new_root.title()

            # 3. Prefix/Suffix
            new_root = f"{prefix}{new_root}{suffix}"

            # 4. Numbering
            if do_num:
                # Add _001 at end
                num_str = str(count).zfill(3)
                new_root = f"{new_root}_{num_str}"
                count += 1

            new_name = new_root + name_ext

            status = "Ready"
            if f == new_name:
                status = "No Change"

            self.tree.insert("", "end", values=(f, new_name, status))

    def run_utility_rename(self):
        folder = self.util_folder_path.get()
        if not folder:
            return

        items = self.tree.get_children()
        if not items:
            return

        count = 0
        for item in items:
            vals = self.tree.item(item)["values"]
            old_name = vals[0]
            new_name = vals[1]
            status = vals[2]

            if status == "Ready":
                try:
                    src = os.path.join(folder, old_name)
                    dst = os.path.join(folder, new_name)
                    os.rename(src, dst)
                    count += 1
                except Exception as e:
                    print(e)

        messagebox.showinfo("Success", f"Renamed {count} files.")
        self.update_utility_preview()


if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateRenamerApp(root)
    root.mainloop()
