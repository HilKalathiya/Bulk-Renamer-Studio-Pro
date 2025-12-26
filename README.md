# 📊 Renamer Studio Pro (High-Vis Edition)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A professional, high-contrast bulk renaming tool designed for Audio Engineers and Data Managers. Built with a modern **Material Design 3** interface, it features intelligent Excel metadata mapping and powerful manual utility tools.

> **Copyright © 2025 SMK-Kundaldham**

---

## ✨ Key Features

### 📂 1. Smart Rename (Excel Mode)
* **Database Driven:** Renames `.wav` (or other) files based on metadata in an Excel (`.xlsx`) or CSV file.
* **Intelligent Auto-Mapping:** Automatically detects columns for *Folder Name*, *Filename*, *English Track Name*, and *ISRC Code*—no manual selection needed for standard formats.
* **Smart ISRC Injection:**
    * Automatically pulls ISRC codes from the spreadsheet.
    * **Interactive Fallback:** If an ISRC is missing, the app pauses and asks you to enter it manually for that specific file.
* **Strict Case Match:** Toggle switch to enforce exact capitalization matching (e.g., distinguishing `Song.wav` from `song.wav`).

### 🛠 2. Quick Utility (Manual Mode)
* **Bulk Operations:** Find & Replace, Add Prefix/Suffix, Change Casing (UPPER/lower/Title), and Auto-Numbering.
* **Manual Override System:**
    * **Double-click any file** in the preview list to manually rename just that specific file, overriding the bulk rules.
    * Perfect for fixing exceptions without stopping the whole batch.

### 🎨 3. High-Vis UI (Accessibility Focused)
* **High Contrast Theme:** Deep dark background (`#131314`) with pure white text and bright blue accents for maximum readability.
* **Large Typography:** Uses **Poppins** (Headers) and **Open Sans** (Body) at large sizes (14px+) to reduce eye strain.
* **Modern Components:** Pill-shaped buttons, rounded inputs, and smooth animations powered by `CustomTkinter`.

---

## 📸 Screenshots

*(this is My Excel Pro Renamer SS `![App Preview]![alt text](image.png)`)*
*(this is Utility Renamer SS `![App Preview]!![alt text](image-1.png)`)*

---

## ⚙️ Installation

### Option 1: Run as Executable (No Python Required)
1.  Download the latest `RenamerStudioPro.exe` from the Releases section.
2.  Double-click to run. No installation required.

### Option 2: Run from Source
**Prerequisites:**
* Python 3.10 or higher.
* Required libraries:
    ```bash
    pip install customtkinter pandas openpyxl packaging
    ```

**Run the app:**
```bash
python RenamerStudio.py