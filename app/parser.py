import pandas as pd
import os


class DataParser:
    @staticmethod
    def get_headers(file_path, header_row=0):
        """Reads the specified row of an Excel file to get column names."""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in [".xlsx", ".xls"]:
                return []

            # Read just the headers from the specified row (0-indexed)
            df = pd.read_excel(file_path, header=header_row, nrows=0)
            return [str(c).strip() for c in df.columns]
        except Exception as e:
            print(f"Error reading headers: {e}")
            return []

    @staticmethod
    def parse_excel(
        file_path,
        old_col_name,
        new_col_name,
        header_row=0,
        folder_col_name=None,
        case_sensitive=False,
    ):
        """
        Reads Excel with user options. Returns a list of tasks:
        [{'old': 'song.wav', 'new': 'NewSong.wav', 'folder': 'AlbumA'}]
        """
        try:
            df = pd.read_excel(file_path, header=header_row)

            # Clean column names
            df.columns = [str(c).strip() for c in df.columns]

            # Validate columns
            if old_col_name not in df.columns or new_col_name not in df.columns:
                raise ValueError(f"Essential columns not found.")

            if folder_col_name and folder_col_name not in df.columns:
                raise ValueError(f"Folder Column '{folder_col_name}' not found.")

            # Drop empty rows in essential columns
            df = df.dropna(subset=[old_col_name, new_col_name])

            tasks = []
            for _, row in df.iterrows():
                old_name = str(row[old_col_name]).strip()
                new_name = str(row[new_col_name]).strip()

                folder_name = None
                if folder_col_name:
                    folder_val = row[folder_col_name]
                    if pd.notna(folder_val):
                        folder_name = str(folder_val).strip()

                # Lowercase for case-insensitive matching
                if not case_sensitive:
                    old_name = old_name.lower()

                tasks.append({"old": old_name, "new": new_name, "folder": folder_name})

            return tasks
        except Exception as e:
            print(f"Error parsing data: {e}")
            return []
