import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, simpledialog


class DarkRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Master Audio Renamer (Dark Mode)")
        self.root.geometry("1000x800")

        # --- DARK THEME SETTINGS ---
        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        self.entry_bg = "#404040"
        self.accent_color = "#00adb5"
        self.button_bg = "#3a3a3a"

        self.style_ui()

        # --- Variables ---
        self.excel_path = tk.StringVar()
        self.root_folder_path = tk.StringVar()
        self.df = None

        # --- UI LAYOUT ---

        # 1. Header
        header_frame = tk.Frame(root, bg=self.bg_color)
        header_frame.pack(fill="x", pady=10)
        tk.Label(
            header_frame,
            text="AUDIO FILE RENAMER",
            font=("Segoe UI", 18, "bold"),
            bg=self.bg_color,
            fg=self.accent_color,
        ).pack()

        # 2. Configuration Section
        self.create_labeled_frame(
            "1. File & Folder Selection", self.build_file_selection
        )

        # 3. Column Mapping
        self.create_labeled_frame("2. Excel Column Mapping", self.build_column_mapping)

        # 4. Actions
        action_frame = tk.Frame(root, bg=self.bg_color, pady=10)
        action_frame.pack(fill="x", padx=20)

        self.btn_run = tk.Button(
            action_frame,
            text="▶ START BULK RENAME",
            bg=self.accent_color,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            padx=20,
            pady=5,
            cursor="hand2",
            command=self.start_renaming,
        )
        self.btn_run.pack(fill="x")

        # 5. Log Area
        log_frame = tk.LabelFrame(
            root,
            text="Process Log",
            bg=self.bg_color,
            fg=self.accent_color,
            padx=10,
            pady=10,
        )
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            state="disabled",
            bg="#1e1e1e",
            fg="#00ff00",
            insertbackground="white",
        )
        self.log_area.pack(fill="both", expand=True)

    def style_ui(self):
        self.root.configure(bg=self.bg_color)
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TCombobox",
            fieldbackground=self.entry_bg,
            background=self.button_bg,
            foreground="white",
        )
        style.map("TCombobox", fieldbackground=[("readonly", self.entry_bg)])
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)

    def create_labeled_frame(self, title, content_builder):
        frame = tk.LabelFrame(
            self.root,
            text=title,
            bg=self.bg_color,
            fg=self.accent_color,
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=15,
        )
        frame.pack(fill="x", padx=20, pady=5)
        content_builder(frame)

    def build_file_selection(self, parent):
        # Excel
        tk.Label(
            parent, text="Select Excel/CSV:", bg=self.bg_color, fg=self.fg_color
        ).grid(row=0, column=0, sticky="w")
        e1 = tk.Entry(
            parent,
            textvariable=self.excel_path,
            width=70,
            bg=self.entry_bg,
            fg="white",
            insertbackground="white",
            relief="flat",
        )
        e1.grid(row=0, column=1, padx=10, pady=5)
        tk.Button(
            parent,
            text="Browse",
            bg=self.button_bg,
            fg="white",
            command=self.load_excel_preview,
        ).grid(row=0, column=2)

        # Folder
        tk.Label(
            parent,
            text="Music Folder (Parent/Inner):",
            bg=self.bg_color,
            fg=self.fg_color,
        ).grid(row=1, column=0, sticky="w")
        e2 = tk.Entry(
            parent,
            textvariable=self.root_folder_path,
            width=70,
            bg=self.entry_bg,
            fg="white",
            insertbackground="white",
            relief="flat",
        )
        e2.grid(row=1, column=1, padx=10, pady=5)
        tk.Button(
            parent,
            text="Browse",
            bg=self.button_bg,
            fg="white",
            command=self.browse_folder,
        ).grid(row=1, column=2)

    def build_column_mapping(self, parent):
        grid_opts = {"padx": 5, "pady": 5, "sticky": "w"}

        tk.Label(
            parent, text="Folder Name Column:", bg=self.bg_color, fg=self.fg_color
        ).grid(row=0, column=0, **grid_opts)
        self.combo_folder = ttk.Combobox(parent, width=35)
        self.combo_folder.grid(row=0, column=1, **grid_opts)

        tk.Label(
            parent, text="Current File Name:", bg=self.bg_color, fg=self.fg_color
        ).grid(row=0, column=2, **grid_opts)
        self.combo_filename = ttk.Combobox(parent, width=35)
        self.combo_filename.grid(row=0, column=3, **grid_opts)

        tk.Label(
            parent, text="English Track Name:", bg=self.bg_color, fg=self.fg_color
        ).grid(row=1, column=0, **grid_opts)
        self.combo_newname = ttk.Combobox(parent, width=35)
        self.combo_newname.grid(row=1, column=1, **grid_opts)

        tk.Label(parent, text="ISRC Column:", bg=self.bg_color, fg=self.fg_color).grid(
            row=1, column=2, **grid_opts
        )
        self.combo_isrc = ttk.Combobox(parent, width=35)
        self.combo_isrc.grid(row=1, column=3, **grid_opts)

    def log(self, message, color="#00ff00"):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")
        self.root.update()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.root_folder_path.set(folder)

    def load_excel_preview(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel/CSV Files", "*.xlsx *.xls *.csv")]
        )
        if not file_path:
            return

        self.excel_path.set(file_path)
        try:
            # TRY READING ROW 1 (Index 1) AS HEADER FIRST (Fix for Studio Data row)
            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path, header=1)
            else:
                self.df = pd.read_excel(file_path, header=1)

            # Validation: If 'Folder Name' isn't found, maybe they don't have the Studio Data row?
            # Try reloading with header=0
            if (
                "Folder Name" not in self.df.columns
                and "File Name" not in self.df.columns
            ):
                self.log("Row 2 headers not detected. Trying Row 1...", "#ffff00")
                if file_path.endswith(".csv"):
                    self.df = pd.read_csv(file_path, header=0)
                else:
                    self.df = pd.read_excel(file_path, header=0)

            # Populate Comboboxes
            columns = list(self.df.columns)
            for combo in [
                self.combo_folder,
                self.combo_filename,
                self.combo_newname,
                self.combo_isrc,
            ]:
                combo["values"] = ["-- Select Column --"] + columns
                combo.current(0)

            # Smart Autoselect
            self.set_combo_if_exists(self.combo_folder, "Folder Name")
            self.set_combo_if_exists(self.combo_filename, "File Name")
            self.set_combo_if_exists(self.combo_newname, "English Track Name")

            isrc_cols = [c for c in columns if "ISRC" in c.upper()]
            if isrc_cols:
                self.set_combo_if_exists(self.combo_isrc, isrc_cols[0])

            self.log(f"Successfully Loaded Excel: {len(self.df)} rows ready.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Excel: {e}")

    def set_combo_if_exists(self, combo, col_name):
        values = combo["values"]
        if col_name in values:
            combo.set(col_name)

    def start_renaming(self):
        root_dir = self.root_folder_path.get()
        if not root_dir or not os.path.isdir(root_dir):
            messagebox.showwarning("Warning", "Select a valid Folder.")
            return

        if self.df is None:
            messagebox.showwarning("Warning", "Load Excel file first.")
            return

        # Get Columns
        c_folder = self.combo_folder.get()
        c_file = self.combo_filename.get()
        c_new = self.combo_newname.get()
        c_isrc = self.combo_isrc.get()

        if any(c == "-- Select Column --" for c in [c_folder, c_file, c_new]):
            messagebox.showwarning(
                "Warning", "Map Folder, File Name, and English Name columns."
            )
            return

        self.log("--- STARTING PROCESS ---", "#00adb5")

        processed = 0
        skipped = 0

        # Loop through Excel
        for index, row in self.df.iterrows():
            try:
                # Clean Data
                folder_name = str(row[c_folder]).strip()
                current_file = str(row[c_file]).strip()
                english_name = str(row[c_new]).strip()

                if folder_name == "nan" or current_file == "nan":
                    continue

                if not current_file.lower().endswith(".wav"):
                    current_file += ".wav"

                # 1. DETERMINE FILE PATH (Parent vs Inner Logic)
                # Strategy: Try finding file in Root/FolderName/File. If not, try Root/File.
                path_in_subfolder = os.path.join(root_dir, folder_name, current_file)
                path_direct = os.path.join(root_dir, current_file)

                actual_old_path = None

                if os.path.exists(path_in_subfolder):
                    actual_old_path = path_in_subfolder
                    parent_path = os.path.join(root_dir, folder_name)
                elif os.path.exists(path_direct):
                    actual_old_path = path_direct
                    parent_path = root_dir
                else:
                    # File not found
                    # Check if it was ALREADY renamed (idempotency)
                    # We can't easily guess the new name if ISRC was manual, so we just skip/log
                    skipped += 1
                    continue

                # 2. HANDLE MISSING ENGLISH NAME
                if english_name == "nan" or english_name == "":
                    new_filename = f"_ {current_file}"
                    self.log(f"[NO NAME] Renaming to: {new_filename}")
                else:
                    # 3. HANDLE ISRC (Automatic or Manual Popup)
                    isrc_val = ""

                    # Try fetch from Excel
                    if c_isrc != "-- Select Column --" and pd.notna(row[c_isrc]):
                        isrc_val = str(row[c_isrc]).strip()

                    # If Missing -> PAUSE AND ASK USER
                    if not isrc_val:
                        # Bring window to front
                        self.root.deiconify()
                        user_input = simpledialog.askstring(
                            "ISRC Missing",
                            f"ISRC missing for track:\nFolder: {folder_name}\nTrack: {english_name}\n\nEnter ISRC (or leave empty to skip ISRC):",
                            parent=self.root,
                        )
                        if user_input:
                            isrc_val = user_input.strip()

                    # Construct New Name
                    if isrc_val:
                        new_filename = f"{english_name}_{isrc_val}.wav"
                    else:
                        new_filename = f"{english_name}.wav"

                # 4. EXECUTE RENAME
                new_full_path = os.path.join(parent_path, new_filename)

                if os.path.exists(new_full_path):
                    self.log(f"[SKIP] Exists: {new_filename}")
                else:
                    os.rename(actual_old_path, new_full_path)
                    self.log(f"[OK] {current_file} -> {new_filename}")
                    processed += 1
    
            except Exception as e:
                self.log(f"[ERROR] Row {index}: {e}", "#ff5555")

        self.log(f"--- DONE. Processed: {processed} ---", "#00adb5")
        messagebox.showinfo("Complete", "Renaming process finished.")


if __name__ == "__main__":
    root = tk.Tk()
    app = DarkRenamerApp(root)
    root.mainloop()
