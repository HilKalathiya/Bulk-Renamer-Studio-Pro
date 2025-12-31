import flet as ft
import os
import json
import subprocess
import platform
from parser import DataParser

# --- CONFIGURATION ---
GO_BINARY_NAME = (
    "renamer_engine.exe" if platform.system() == "Windows" else "renamer_engine"
)
GO_BINARY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "core_engine", GO_BINARY_NAME
)


def main(page: ft.Page):
    # --- 1. UI SETUP ---
    page.title = "Renamer Studio Pro X - Ultimate"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 1100
    page.window.height = 850
    page.bgcolor = "#0f172a"
    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap"
    }
    page.theme = ft.Theme(font_family="Inter")

    # --- GLOBAL STATE & HELPERS ---
    rename_tasks = []
    progress_ring = ft.ProgressRing(
        width=20, height=20, stroke_width=2, color="white", visible=False
    )

    def show_snack(text, color):
        page.snack_bar = ft.SnackBar(ft.Text(text), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def log_message(view_ref, text, color):
        view_ref.current.controls.append(ft.Text(text, color=color))
        view_ref.current.update()

    # =========================================
    # --- TAB 1: SMART RENAME LOGIC ---
    # =========================================
    sr_folder_path = ft.Ref[ft.TextField]()
    sr_file_path = ft.Ref[ft.TextField]()
    sr_header_row = ft.Ref[ft.TextField]()

    dd_folder_col = ft.Ref[ft.Dropdown]()
    dd_old_col = ft.Ref[ft.Dropdown]()
    dd_new_col = ft.Ref[ft.Dropdown]()

    cb_strict_case = ft.Ref[ft.Checkbox]()
    sr_col_selection = ft.Ref[ft.Column]()
    btn_sr_analyze = ft.Ref[ft.ElevatedButton]()
    btn_sr_run = ft.Ref[ft.ElevatedButton]()
    sr_log_view = ft.Ref[ft.ListView]()
    sr_results_table = ft.Ref[ft.DataTable]()

    def sr_pick_folder_result(e: ft.FilePickerResultEvent):
        if e.path:
            sr_folder_path.current.value = e.path
            sr_folder_path.current.update()
            validate_sr_inputs()

    def sr_pick_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            sr_file_path.current.value = file_path
            sr_file_path.current.update()
            load_excel_headers(file_path)
            validate_sr_inputs()

    def on_header_row_change(e):
        if sr_file_path.current.value:
            load_excel_headers(sr_file_path.current.value)

    def load_excel_headers(file_path):
        try:
            h_row = int(sr_header_row.current.value)
        except ValueError:
            h_row = 0

        headers = DataParser.get_headers(file_path, header_row=h_row)
        if headers:
            # Add empty option for optional columns
            optional_items = [ft.dropdown.Option("")] + [
                ft.dropdown.Option(h) for h in headers
            ]
            required_items = [ft.dropdown.Option(h) for h in headers]

            dd_folder_col.current.options = optional_items
            dd_old_col.current.options = required_items
            dd_new_col.current.options = required_items

            sr_col_selection.current.visible = True
            sr_col_selection.current.update()
            show_snack("Excel loaded! Please map columns.", ft.colors.BLUE)
        else:
            show_snack("Could not read headers. Check row number.", ft.colors.RED)
            sr_col_selection.current.visible = False
            sr_col_selection.current.update()

    def validate_sr_inputs(e=None):
        is_ready = False
        if (
            sr_folder_path.current.value
            and sr_file_path.current.value
            and sr_col_selection.current.visible
        ):
            if dd_old_col.current.value and dd_new_col.current.value:
                is_ready = True
        btn_sr_analyze.current.disabled = not is_ready
        btn_sr_analyze.current.update()

    def run_sr_preview(e):
        sr_log_view.current.controls.clear()
        log_message(sr_log_view, "🔎 Analyzing...", ft.colors.CYAN_400)

        folder = sr_folder_path.current.value
        data_file = sr_file_path.current.value
        h_row = int(sr_header_row.current.value)
        old_col = dd_old_col.current.value
        new_col = dd_new_col.current.value
        folder_col = dd_folder_col.current.value
        case_strict = cb_strict_case.current.value

        try:
            tasks_data = DataParser.parse_excel(
                data_file,
                old_col,
                new_col,
                h_row,
                folder_col if folder_col else None,
                case_strict,
            )
            if not tasks_data:
                log_message(sr_log_view, "⚠️ No valid data found.", ft.colors.AMBER)
                return

            rename_tasks.clear()
            preview_rows = []
            task_map = {t["old"]: t for t in tasks_data}

            if not os.path.exists(folder):
                log_message(
                    sr_log_view,
                    f"❌ Error: Folder '{folder}' not found.",
                    ft.colors.RED,
                )
                return

            for filename in os.listdir(folder):
                src_full = os.path.join(folder, filename)
                if not os.path.isfile(src_full):
                    continue

                match_key = filename if case_strict else filename.lower()

                if match_key in task_map:
                    task = task_map[match_key]
                    new_name = task["new"]
                    folder_name = task["folder"]

                    if "." not in new_name:
                        new_name += os.path.splitext(filename)[1]

                    if folder_name:
                        dst_full = os.path.join(folder, folder_name, new_name)
                    else:
                        dst_full = os.path.join(folder, new_name)

                    rename_tasks.append({"src": src_full, "dst": dst_full})
                    preview_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Icon(
                                        ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN
                                    )
                                ),
                                ft.DataCell(ft.Text(filename, color=ft.colors.WHITE70)),
                                ft.DataCell(
                                    ft.Text(
                                        os.path.relpath(dst_full, folder),
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.WHITE,
                                    )
                                ),
                            ]
                        )
                    )

            sr_results_table.current.rows = preview_rows
            log_message(
                sr_log_view,
                f"✅ Ready to rename {len(rename_tasks)} files.",
                ft.colors.GREEN_400,
            )
            btn_sr_run.current.disabled = not bool(rename_tasks)
            btn_sr_run.current.update()
            sr_results_table.current.update()

        except Exception as ex:
            log_message(sr_log_view, f"❌ Error: {str(ex)}", ft.colors.RED)

    def run_engine(btn_ref, log_ref):
        if not rename_tasks:
            return
        progress_ring.visible = True
        btn_ref.current.disabled = True
        page.update()

        # Create destination folders first in Python
        created_folders = set()
        for task in rename_tasks:
            dst_dir = os.path.dirname(task["dst"])
            if dst_dir and dst_dir not in created_folders:
                try:
                    os.makedirs(dst_dir, exist_ok=True)
                    created_folders.add(dst_dir)
                except Exception as ex:
                    log_message(
                        log_ref,
                        f"❌ Failed to create folder {dst_dir}: {ex}",
                        ft.colors.RED,
                    )
                    progress_ring.visible = False
                    btn_ref.current.disabled = False
                    page.update()
                    return

        json_payload = json.dumps(rename_tasks)
        try:
            result = subprocess.run(
                [GO_BINARY_PATH, json_payload], capture_output=True, text=True
            )
            log_ref.current.controls.clear()
            for line in result.stdout.split("\n"):
                if "✅" in line:
                    log_message(log_ref, line, ft.colors.GREEN_300)
                elif "❌" in line:
                    log_message(log_ref, line, ft.colors.RED_300)
        except FileNotFoundError:
            show_snack("Go Engine not found!", ft.colors.RED)

        progress_ring.visible = False
        btn_ref.current.disabled = False
        page.update()

    # =========================================
    # --- TAB 2: QUICK UTILITY LOGIC ---
    # =========================================
    qu_folder_path = ft.Ref[ft.TextField]()
    qu_find_text = ft.Ref[ft.TextField]()
    qu_replace_text = ft.Ref[ft.TextField]()
    qu_prefix_text = ft.Ref[ft.TextField]()
    qu_suffix_text = ft.Ref[ft.TextField]()
    qu_casing_dd = ft.Ref[ft.Dropdown]()
    qu_auto_num_cb = ft.Ref[ft.Checkbox]()
    btn_qu_preview = ft.Ref[ft.ElevatedButton]()
    btn_qu_run = ft.Ref[ft.ElevatedButton]()
    qu_log_view = ft.Ref[ft.ListView]()
    qu_results_table = ft.Ref[ft.DataTable]()

    def validate_qu_inputs(e=None):
        btn_qu_preview.current.disabled = not bool(qu_folder_path.current.value)
        btn_qu_preview.current.update()

    def run_qu_preview(e):
        qu_log_view.current.controls.clear()
        log_message(qu_log_view, "🔎 Generating Preview...", ft.colors.CYAN_400)
        folder = qu_folder_path.current.value
        if not os.path.isdir(folder):
            return

        find_txt, rep_txt = qu_find_text.current.value, qu_replace_text.current.value
        prefix, suffix = qu_prefix_text.current.value, qu_suffix_text.current.value
        casing, auto_num = qu_casing_dd.current.value, qu_auto_num_cb.current.value

        rename_tasks.clear()
        preview_rows = []
        try:
            files = sorted(
                [
                    f
                    for f in os.listdir(folder)
                    if os.path.isfile(os.path.join(folder, f))
                ]
            )
            for i, filename in enumerate(files):
                name_body, ext = os.path.splitext(filename)
                new_body = (
                    name_body.replace(find_txt, rep_txt) if find_txt else name_body
                )

                if casing == "lowercase":
                    new_body = new_body.lower()
                elif casing == "UPPERCASE":
                    new_body = new_body.upper()
                elif casing == "Title Case":
                    new_body = new_body.title()

                new_body = f"{prefix}{new_body}{suffix}"
                if auto_num:
                    new_body = f"{i+1:02d} - {new_body}"

                new_filename = f"{new_body}{ext}"
                if filename != new_filename:
                    rename_tasks.append(
                        {
                            "src": os.path.join(folder, filename),
                            "dst": os.path.join(folder, new_filename),
                        }
                    )
                    preview_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(filename, color=ft.colors.WHITE70)),
                                ft.DataCell(
                                    ft.Text(
                                        new_filename,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.WHITE,
                                    )
                                ),
                            ]
                        )
                    )

            qu_results_table.current.rows = preview_rows
            log_message(
                qu_log_view,
                f"✅ Generated {len(rename_tasks)} operations.",
                ft.colors.GREEN_400,
            )
            btn_qu_run.current.disabled = not bool(rename_tasks)
            btn_qu_run.current.update()
            qu_results_table.current.update()
        except Exception as ex:
            log_message(qu_log_view, f"❌ Error: {str(ex)}", ft.colors.RED)

    # =========================================
    # --- UI ASSEMBLY ---
    # =========================================
    sr_folder_picker = ft.FilePicker(on_result=sr_pick_folder_result)
    sr_file_picker = ft.FilePicker(on_result=sr_pick_file_result)
    qu_folder_picker = ft.FilePicker(
        on_result=lambda e: (
            [qu_folder_path.current.update(value=e.path), validate_qu_inputs()]
            if e.path
            else None
        )
    )
    page.overlay.extend([sr_folder_picker, sr_file_picker, qu_folder_picker])

    # Smart Rename Tab Content
    sr_content = ft.Container(
        padding=20,
        content=ft.Column(
            [
                ft.Text(
                    "SOURCE CONFIGURATION",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.GREY_500,
                ),
                ft.Row(
                    [
                        ft.TextField(
                            ref=sr_header_row,
                            label="Header Row (0-based)",
                            value="0",
                            width=150,
                            text_size=12,
                            on_change=on_header_row_change,
                        ),
                        ft.Text(
                            "(Set before browsing)",
                            size=12,
                            color=ft.colors.GREY_500,
                            italic=True,
                        ),
                    ]
                ),
                ft.Row(
                    [
                        ft.IconButton(
                            ft.icons.DESCRIPTION,
                            on_click=lambda _: sr_file_picker.pick_files(),
                            icon_color=ft.colors.PINK_400,
                        ),
                        ft.TextField(
                            ref=sr_file_path,
                            label="Excel Database File",
                            read_only=True,
                            expand=True,
                            text_size=12,
                        ),
                    ]
                ),
                ft.Row(
                    [
                        ft.IconButton(
                            ft.icons.FOLDER_OPEN,
                            on_click=lambda _: sr_folder_picker.get_directory_path(),
                            icon_color=ft.colors.CYAN_400,
                        ),
                        ft.TextField(
                            ref=sr_folder_path,
                            label="Music Folder",
                            read_only=True,
                            expand=True,
                            text_size=12,
                        ),
                    ]
                ),
                ft.Divider(height=20, color="transparent"),
                ft.Column(
                    ref=sr_col_selection,
                    visible=False,
                    controls=[
                        ft.Text(
                            "COLUMN MAPPING",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLUE_400,
                        ),
                        ft.Row(
                            [
                                ft.Dropdown(
                                    ref=dd_folder_col,
                                    label="Folder Name Column (Optional)",
                                    expand=True,
                                    on_change=validate_sr_inputs,
                                ),
                                ft.Dropdown(
                                    ref=dd_old_col,
                                    label="Current Filename (Required)",
                                    expand=True,
                                    on_change=validate_sr_inputs,
                                ),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Dropdown(
                                    ref=dd_new_col,
                                    label="New Track Name (Required)",
                                    expand=True,
                                    on_change=validate_sr_inputs,
                                ),
                                ft.Checkbox(
                                    ref=cb_strict_case,
                                    label="Strict Case Match",
                                    value=False,
                                ),
                            ]
                        ),
                    ],
                ),
                ft.Divider(height=20, color="transparent"),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Analyze & Preview",
                            icon=ft.icons.ANALYTICS,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.CYAN_600, color="white", padding=20
                            ),
                            on_click=run_sr_preview,
                            disabled=True,
                            ref=btn_sr_analyze,
                        ),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "🚀 Start Renaming",
                            on_click=lambda e: run_engine(btn_sr_run, sr_log_view),
                            disabled=True,
                            ref=btn_sr_run,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.GREEN_600, color="white", padding=20
                            ),
                        ),
                    ]
                ),
                ft.Divider(height=20, color="transparent"),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "PREVIEW & LOGS",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.GREY_500,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.DataTable(
                                            ref=sr_results_table,
                                            columns=[
                                                ft.DataColumn(ft.Text("Status")),
                                                ft.DataColumn(ft.Text("Original")),
                                                ft.DataColumn(ft.Text("New Path")),
                                            ],
                                            heading_row_color=ft.colors.BLACK12,
                                            expand=True,
                                        )
                                    ],
                                    scroll=ft.ScrollMode.ADAPTIVE,
                                ),
                                expand=True,
                                bgcolor="#0f172a",
                                border=ft.border.all(1, ft.colors.GREY_800),
                                border_radius=10,
                                height=300,
                            ),
                            ft.Container(
                                content=ft.ListView(
                                    ref=sr_log_view,
                                    expand=True,
                                    spacing=5,
                                    padding=10,
                                    auto_scroll=True,
                                ),
                                bgcolor="#0f172a",
                                border=ft.border.all(1, ft.colors.GREY_800),
                                border_radius=10,
                                height=150,
                                padding=5,
                            ),
                        ]
                    ),
                    expand=True,
                    padding=20,
                    bgcolor="#1e293b",
                    border_radius=15,
                ),
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
        ),
    )

    # Quick Utility Tab Content
    qu_content = ft.Container(
        padding=20,
        content=ft.Column(
            [
                ft.Text(
                    "BULK OPERATIONS",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.GREY_500,
                ),
                ft.Row(
                    [
                        ft.IconButton(
                            ft.icons.FOLDER_OPEN,
                            on_click=lambda _: qu_folder_picker.get_directory_path(),
                            icon_color=ft.colors.CYAN_400,
                        ),
                        ft.TextField(
                            ref=qu_folder_path,
                            label="Target Folder",
                            read_only=True,
                            expand=True,
                            text_size=12,
                        ),
                    ]
                ),
                ft.Divider(height=20, color="transparent"),
                ft.Row(
                    [
                        ft.TextField(
                            ref=qu_find_text, label="Find:", expand=True, text_size=12
                        ),
                        ft.TextField(
                            ref=qu_replace_text,
                            label="Replace with:",
                            expand=True,
                            text_size=12,
                        ),
                    ]
                ),
                ft.Row(
                    [
                        ft.TextField(
                            ref=qu_prefix_text,
                            label="Prefix:",
                            expand=True,
                            text_size=12,
                        ),
                        ft.TextField(
                            ref=qu_suffix_text,
                            label="Suffix:",
                            expand=True,
                            text_size=12,
                        ),
                    ]
                ),
                ft.Row(
                    [
                        ft.Dropdown(
                            ref=qu_casing_dd,
                            label="Casing",
                            options=[
                                ft.dropdown.Option("No Change"),
                                ft.dropdown.Option("lowercase"),
                                ft.dropdown.Option("UPPERCASE"),
                                ft.dropdown.Option("Title Case"),
                            ],
                            value="No Change",
                            width=150,
                        ),
                        ft.Checkbox(
                            ref=qu_auto_num_cb,
                            label="Auto Numbering (01 - ...)",
                            value=False,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=20, color="transparent"),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Preview Changes",
                            icon=ft.icons.PREVIEW,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.CYAN_600, color="white", padding=20
                            ),
                            on_click=run_qu_preview,
                            disabled=True,
                            ref=btn_qu_preview,
                        ),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "🚀 Apply Bulk Rename",
                            on_click=lambda e: run_engine(btn_qu_run, qu_log_view),
                            disabled=True,
                            ref=btn_qu_run,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.GREEN_600, color="white", padding=20
                            ),
                        ),
                    ]
                ),
                ft.Divider(height=20, color="transparent"),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "PREVIEW",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.GREY_500,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.DataTable(
                                            ref=qu_results_table,
                                            columns=[
                                                ft.DataColumn(ft.Text("Original")),
                                                ft.DataColumn(ft.Text("New Name")),
                                            ],
                                            heading_row_color=ft.colors.BLACK12,
                                            expand=True,
                                        )
                                    ],
                                    scroll=ft.ScrollMode.ADAPTIVE,
                                ),
                                expand=True,
                                bgcolor="#0f172a",
                                border=ft.border.all(1, ft.colors.GREY_800),
                                border_radius=10,
                                height=300,
                            ),
                            ft.Container(
                                content=ft.ListView(
                                    ref=qu_log_view,
                                    expand=True,
                                    spacing=5,
                                    padding=10,
                                    auto_scroll=True,
                                ),
                                bgcolor="#0f172a",
                                border=ft.border.all(1, ft.colors.GREY_800),
                                border_radius=10,
                                height=100,
                                padding=5,
                            ),
                        ]
                    ),
                    expand=True,
                    padding=20,
                    bgcolor="#1e293b",
                    border_radius=15,
                ),
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
        ),
    )

    # Main Layout
    header = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.icons.BOLT, color=ft.colors.CYAN_400, size=30),
                ft.Text(
                    "Renamer Studio", size=24, weight=ft.FontWeight.BOLD, color="white"
                ),
                ft.Text(
                    "Pro X",
                    size=24,
                    weight=ft.FontWeight.W_300,
                    color=ft.colors.CYAN_400,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=20,
        bgcolor="#1e293b",
    )
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Smart Rename", icon=ft.icons.SMART_BUTTON, content=sr_content),
            ft.Tab(text="Quick Utility", icon=ft.icons.BUILD, content=qu_content),
        ],
        expand=True,
    )
    footer = ft.Container(
        content=ft.Row(
            [
                progress_ring,
                ft.Text("Powered by Go Engine", size=10, color=ft.colors.WHITE24),
            ]
        ),
        padding=20,
        bgcolor="#111827",
    )
    page.add(header, tabs, footer)


if __name__ == "__main__":
    ft.app(target=main)
