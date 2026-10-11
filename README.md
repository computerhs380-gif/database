# Chemical Inventory Management System (CIMS)
**A Standalone Local Desktop Application for University Laboratory Safety & Inventory Tracking**

Designed for university departments (Chemistry, Biology, Physics, Biochemistry, etc.) to manage chemicals locally with an intuitive, modern, lab-assistant-friendly graphical interface.

---

## 🌟 Key Features

1. **Dashboard & Live Analytics Cards**:
   - Real-time counters for **Total Chemicals**, **⚠️ Expired**, **⏳ Expiring Soon (<30 days)**, **📉 Low Stock**, and **☣️ Hazardous Items**.
   - One-click quick-filter chips to instantly view only expired, low-stock, or hazardous items.

2. **Chemical Data Management (CRUD)**:
   - **Add / Edit Modal Dialog**: Clean, organized 4-section form with field validation.
   - **Barcode Support**: Manual entry or automatic random barcode generation (`CHEM-XXXXX`).
   - **Date Helpers**: Quick buttons for "Today", "+1 Year", "+2 Years", and "No Expiry".
   - **Safety & Hazards**: Checkboxes for *Security Risk (Controlled Substance)*, *Health Hazard*, and *Physical Hazard*.
   - **MSDS Integration**: Direct "Open" button to view online web links or local PDF safety sheets.

3. **High-Performance Search & Multi-Filter**:
   - Real-time search across Barcode, Chemical Name, CAS Number, and Storage Location.
   - Filter by Department (Chemistry, Biology, Physics, Biochemistry, etc.).
   - Sortable columns (click any column header to sort ascending/descending).
   - High-contrast color-coded alerts (Red for Expired, Amber for Expiring Soon, Orange for Low Stock).

4. **Excel Import & Export**:
   - **Export to Excel**: Exports active inventory or filtered views into styled `.xlsx` spreadsheets with auto-fitted columns.
   - **Import from Excel**: Flexible column header matching (accepts variations like `CAS #`, `CAS Number`, `Expiration Date`, `Qty`, etc.) with comprehensive import reports.
   - **Excel Template Generator**: One-click download of a pre-formatted template with example rows.

5. **Local & Standalone**:
   - Uses a local SQLite database (`cims_inventory.db`) with zero internet or cloud dependencies.

---

## 📁 Project Structure

```text
داتابەیس/
├── app.py                      # Main entry point to launch the application
├── config.py                   # Dropdowns, thresholds, file paths, and themes
├── models.py                   # Chemical dataclass and status calculations
├── database.py                 # SQLite database layer with CRUD, indexing, & bulk upsert
├── excel_manager.py            # Excel import/export logic with pandas & openpyxl
├── requirements.txt            # Python dependencies
├── run_app.bat                 # 1-Click Windows batch launcher
├── ui/
│   ├── __init__.py
│   ├── styles.py               # Color tokens, fonts, and Treeview theme setup
│   ├── main_window.py          # Dashboard, stats cards, search bar, table, toolbar
│   ├── chemical_dialog.py      # Add / Edit Chemical modal window with validation
│   └── excel_dialog.py         # Import/Export feedback and activity log dialog
└── sample_data/
    └── chemical_inventory_template.xlsx # Pre-populated lab inventory template
```

---

## 🚀 Quick Start Guide

### Option 1: One-Click Launch (Windows)
Double-click [`run_app.bat`](file:///c:/Users/HealthSafety/Music/%D8%AF%D8%A7%D8%AA%D8%A7%D8%A8%DB%95%DB%8C%D8%B3/run_app.bat). The virtual environment is already prepared with all required packages.

### Option 2: Running from Terminal / PowerShell

```powershell
# 1. Activate the virtual environment
.venv\Scripts\activate

# 2. Run the application
python app.py
```

---

## 📋 Database Fields & Template Specification

| Field Name | Type | Description |
| :--- | :--- | :--- |
| **Barcode** | Text (Unique) | Unique identifier or barcode for the container |
| **Name** | Text (Required) | Name of the chemical compound (e.g. *Hydrochloric Acid 37%*) |
| **CAS Number** | Text | Chemical Abstracts Service registry number (e.g. *7647-01-0*) |
| **Location** | Text | Specific cabinet, shelf, or room (e.g. *Room 204 - Acid Cabinet A1*) |
| **Date In** | Date (`YYYY-MM-DD`) | Date received or checked into the inventory |
| **Expiration Date** | Date (`YYYY-MM-DD`) | Expiration or retest date |
| **Storage Group** | Text (Dropdown) | E.g. *Flammable Liquid*, *Corrosive - Acid*, *Corrosive - Base*, *Oxidizer*, *Toxic*, etc. |
| **Bottle / Container Size** | Text | Size of container (e.g. *500 mL*, *2.5 L*, *1 kg*) |
| **Remaining Quantity** | Number (Float) | Current quantity remaining in container |
| **Units** | Text (Dropdown) | Measurement units (*mL*, *L*, *g*, *mg*, *kg*, etc.) |
| **State** | Text (Dropdown) | Physical state (*Liquid*, *Solid*, *Powder*, *Pellets*, *Gas*, etc.) |
| **MSDS** | Text (URL / Path) | Link to web MSDS or path to local PDF safety data sheet |
| **Owner / Department** | Text (Dropdown) | Managing department (*Chemistry*, *Biology*, *Physics*, etc.) |
| **Security Risk** | Boolean (Checkbox) | Controlled substance or high-theft risk |
| **Health Hazard** | Boolean (Checkbox) | Toxic, carcinogenic, or irritant |
| **Physical Hazard** | Boolean (Checkbox) | Flammable, explosive, or reactive |
| **Notes** | Text | Handling precautions, storage instructions, or remarks |

---

## 📦 Creating a Standalone Windows Executable (.EXE)

To bundle the application into a single `.exe` file that can be distributed to university lab computers without needing Python installed:

```powershell
.venv\Scripts\pip install pyinstaller
.venv\Scripts\pyinstaller --noconsole --onefile --name "CIMS" --add-data "sample_data;sample_data" app.py
```
The standalone `.exe` will be generated inside the `dist/` folder.
