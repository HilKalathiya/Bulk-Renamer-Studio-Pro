import os
import json
import subprocess
import platform
import argparse
from parser import DataParser

# --- CONFIGURATION ---
GO_BINARY_NAME = (
    "renamer_engine.exe" if platform.system() == "Windows" else "renamer_engine"
)
GO_BINARY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "core_engine", GO_BINARY_NAME
)


def run_renamer():
    print("=========================================================")
    print("   File Renamer through Excel and Text and Utility      ")
    print("=========================================================")

    # 1. Get Inputs
    target_dir = input(
        "Enter the Folder Path containing files/folders to rename: "
    ).strip()
    source_file = input("Enter the path to your Data File (.xlsx or .txt): ").strip()

    if not os.path.exists(target_dir) or not os.path.exists(source_file):
        print("❌ Error: Target directory or Source file not found.")
        return

    # 2. Parse Data
    rename_map = {}
    ext = os.path.splitext(source_file)[1].lower()

    if ext in [".xlsx", ".xls"]:
        print("📊 Detected Excel File. Using 'Match' mode.")
        rename_map = DataParser.parse_excel(source_file)

    elif ext == ".txt":
        print("📄 Detected Text File.")
        mode = input(
            "Choose Mode - (1) Match [Old,New] or (2) Sequential [Line-by-Line]: "
        ).strip()
        if mode == "2":
            rename_map = DataParser.parse_text(
                source_file, mode="sequential", target_dir=target_dir
            )
        else:
            rename_map = DataParser.parse_text(source_file, mode="match")

    else:
        print("❌ Unsupported file format.")
        return

    if not rename_map:
        print("⚠️ No rename data found or file is empty.")
        return

    # 3. Build Task List for Go Engine
    # Python prepares the JSON data structure
    tasks = []
    print("\nPreparing Tasks...")

    # Iterate through the directory to find matches (for Match mode)
    # Note: Sequential mode already gave us direct mappings, but we sanitize paths here.

    # We construct full paths
    for old_name, new_name in rename_map.items():
        src_full = os.path.join(target_dir, old_name)

        # Handle extension preservation if new_name doesn't have one
        if os.path.isfile(src_full) and "." not in new_name:
            src_ext = os.path.splitext(old_name)[1]
            new_name += src_ext

        dst_full = os.path.join(target_dir, new_name)

        tasks.append({"src": src_full, "dst": dst_full})

    # 4. Execute via Go (High Performance)
    if tasks:
        json_payload = json.dumps(tasks)
        print(f"🚀 Offloading {len(tasks)} tasks to Go Engine...")

        try:
            # Call the compiled Go binary
            result = subprocess.run(
                [GO_BINARY_PATH, json_payload], capture_output=True, text=True
            )
            print(result.stdout)
            if result.stderr:
                print(f"Go Engine Error: {result.stderr}")
        except FileNotFoundError:
            print(f"❌ Critical Error: Go binary not found at {GO_BINARY_PATH}")
            print("Did you forget to compile the Go code?")
    else:
        print("No matching files found to rename.")


if __name__ == "__main__":
    run_renamer()
