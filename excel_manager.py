"""
Excel Import and Export Manager for CIMS.
Uses pandas and openpyxl with automatic column mapping and validation.
"""

from pathlib import Path
from typing import List, Tuple, Dict, Any
from datetime import datetime, date
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from models import Chemical
from config import SAMPLE_EXCEL_PATH

# Standard Column Name Mapping for Import/Export
STANDARD_HEADERS = [
    "Barcode",
    "Name",
    "CAS Number",
    "Location",
    "Date In",
    "Expiration Date",
    "Storage Group",
    "Bottle / Container Size",
    "Remaining Quantity",
    "Units",
    "State",
    "MSDS",
    "College",
    "Department",
    "Security Risk",
    "Health Hazard",
    "Physical Hazard",
    "Hazard Tags",
    "Notes",
]

# Aliases to match flexible column headers in imported files
COLUMN_ALIASES: Dict[str, List[str]] = {
    "barcode": ["barcode", "code", "barcode id", "item code", "id barcode", "tag"],
    "name": ["name", "chemical name", "item name", "compound", "chemical", "description"],
    "cas_number": ["cas number", "cas", "cas #", "cas no", "cas_no", "cas no."],
    "location": ["location", "shelf", "cabinet", "room", "storage location", "rack"],
    "date_in": ["date in", "date received", "arrival date", "received date", "entry date"],
    "expiration_date": ["expiration date", "expiry date", "exp date", "expiration", "expiry"],
    "storage_group": ["storage group", "storage class", "hazard class", "group", "class"],
    "container_size": ["bottle / container size and units", "bottle / container size", "container size", "bottle size", "size"],
    "remaining_quantity": ["remaining quantity", "remaining qty", "quantity", "qty", "amount remaining", "remaining"],
    "units": ["units", "unit", "uom", "quantity units"],
    "state": ["state", "physical state", "form", "phase"],
    "msds": ["msds", "sds", "safety data sheet", "msds link", "msds / sds", "sds link"],
    "college": ["college", "faculty", "school", "col"],
    "department": ["owner/department", "department", "owner", "dept", "lab"],
    "hazard_security": ["security risk", "security hazard", "security", "controlled"],
    "hazard_health": ["health hazard", "health risk", "health", "toxic hazard"],
    "hazard_physical": ["physical hazard", "physical risk", "physical"],
    "hazard_tags": ["hazard tags", "ghs hazards", "ghs classifications", "detailed hazards"],
    "notes": ["notes", "remarks", "comments", "description notes"],
}


def _normalize_header(header: str) -> str:
    """Normalize a header string for alias matching."""
    return "".join(c.lower() for c in str(header).strip() if c.isalnum() or c.isspace())


def _parse_bool(val: Any) -> bool:
    """Parse various truthy/falsy representations."""
    if pd.isna(val) or val is None:
        return False
    if isinstance(val, (bool, int, float)):
        return bool(val)
    s = str(val).strip().lower()
    return s in ["true", "yes", "y", "1", "x", "checked", "positive"]


def _parse_date(val: Any) -> str:
    """Safely format a date into YYYY-MM-DD."""
    if pd.isna(val) or val is None or str(val).strip() == "":
        return ""
    if isinstance(val, (datetime, date)):
        return val.strftime("%Y-%m-%d")
    s = str(val).strip()
    # Try parsing common formats
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s.split(" ")[0], fmt.split(" ")[0]).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return s  # Return as is if already a valid string representation


def export_chemicals_to_excel(chemicals: List[Chemical], filepath: Path) -> Tuple[bool, str]:
    """
    Export chemical inventory to a styled Excel file using pandas & openpyxl.
    """
    try:
        rows = []
        for c in chemicals:
            rows.append({
                "Barcode": c.barcode,
                "Name": c.name,
                "CAS Number": c.cas_number,
                "Location": c.location,
                "Date In": c.date_in,
                "Expiration Date": c.expiration_date,
                "Storage Group": c.storage_group,
                "Bottle / Container Size": c.container_size,
                "Remaining Quantity": c.remaining_quantity,
                "Units": c.units,
                "State": c.state,
                "MSDS": c.msds,
                "College": getattr(c, "college", "College of Science"),
                "Department": c.department,
                "Security Risk": "Yes" if c.hazard_security else "No",
                "Health Hazard": "Yes" if c.hazard_health else "No",
                "Physical Hazard": "Yes" if c.hazard_physical else "No",
                "Hazard Tags": "|".join(c.get_hazard_tags()),
                "Notes": c.notes,
                "Expiration Status": c.get_expiration_status(),
                "Low Stock Alert": "LOW" if c.is_low_stock() else "OK",
            })

        df = pd.DataFrame(rows)
        if df.empty:
            df = pd.DataFrame(columns=STANDARD_HEADERS + ["Expiration Status", "Low Stock Alert"])

        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Chemicals_Inventory")
            ws = writer.sheets["Chemicals_Inventory"]

            # Styling
            header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
            header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            thin_border = Border(
                left=Side(style="thin", color="E2E8F0"),
                right=Side(style="thin", color="E2E8F0"),
                top=Side(style="thin", color="E2E8F0"),
                bottom=Side(style="thin", color="E2E8F0"),
            )

            # Apply header styles
            for col_idx in range(1, len(df.columns) + 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Apply data row border and auto width
            for col_idx, col_name in enumerate(df.columns, start=1):
                max_len = max(
                    len(str(col_name)),
                    max((len(str(val)) for val in df[col_name]), default=0)
                )
                ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 4, 35)

                for row_idx in range(2, len(df) + 2):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.border = thin_border
                    cell.alignment = Alignment(vertical="center")

        return True, f"Successfully exported {len(chemicals)} records to {filepath.name}"
    except Exception as e:
        return False, f"Failed to export Excel file: {str(e)}"


def import_chemicals_from_excel(filepath: Path) -> Tuple[List[Chemical], List[str]]:
    """
    Reads an Excel file, maps columns intelligently, and returns a list of Chemical objects.
    """
    try:
        df = pd.read_excel(filepath, dtype=str)
    except Exception as e:
        return [], [f"Could not read Excel file: {str(e)}"]

    if df.empty:
        return [], ["Excel file has no data rows."]

    # Create mapping of actual file column names to model fields
    header_mapping = {}
    for col in df.columns:
        norm_col = _normalize_header(col)
        matched = False
        for field_name, aliases in COLUMN_ALIASES.items():
            if field_name in header_mapping:
                continue
            for alias in aliases:
                if norm_col == _normalize_header(alias):
                    header_mapping[field_name] = col
                    matched = True
                    break
            if matched:
                break

    if "barcode" not in header_mapping or "name" not in header_mapping:
        return [], [
            "Missing required columns! The Excel file must have columns for 'Barcode' and 'Name'."
        ]

    chemicals: List[Chemical] = []
    errors: List[str] = []

    for idx, row in df.iterrows():
        row_num = idx + 2  # Excel 1-based index plus header

        def get_val(f_name: str, default: Any = "") -> Any:
            col_name = header_mapping.get(f_name)
            if col_name and col_name in row and not pd.isna(row[col_name]):
                return row[col_name]
            return default

        barcode_val = str(get_val("barcode")).strip()
        name_val = str(get_val("name")).strip()

        if not barcode_val or barcode_val.lower() == "nan" or not name_val or name_val.lower() == "nan":
            errors.append(f"Row {row_num}: Barcode or Name is missing; row skipped.")
            continue

        # Remaining quantity parsing
        raw_qty = get_val("remaining_quantity", "0")
        try:
            qty = float(str(raw_qty).replace(",", "").strip())
        except (ValueError, TypeError):
            qty = 0.0

        raw_hazard_tags = str(get_val("hazard_tags")).strip()
        hazard_tags = [] if raw_hazard_tags.lower() in ("", "nan") else [
            tag.strip() for tag in raw_hazard_tags.replace(";", "|").split("|") if tag.strip()
        ]

        chem = Chemical(
            barcode=barcode_val,
            name=name_val,
            cas_number=str(get_val("cas_number")),
            location=str(get_val("location")),
            date_in=_parse_date(get_val("date_in")),
            expiration_date=_parse_date(get_val("expiration_date")),
            storage_group=str(get_val("storage_group", "General Storage")),
            container_size=str(get_val("container_size")),
            remaining_quantity=qty,
            units=str(get_val("units", "mL")),
            state=str(get_val("state", "Liquid")),
            msds=str(get_val("msds")),
            college=str(get_val("college", "College of Science")),
            department=str(get_val("department", "Chemistry")),
            hazard_security=_parse_bool(get_val("hazard_security")),
            hazard_health=_parse_bool(get_val("hazard_health")),
            hazard_physical=_parse_bool(get_val("hazard_physical")),
            hazard_tags=hazard_tags,
            notes=str(get_val("notes")),
        )
        chemicals.append(chem)

    return chemicals, errors


def generate_sample_excel_file(filepath: Path = SAMPLE_EXCEL_PATH) -> bool:
    """Creates a sample Excel file populated with realistic laboratory chemicals."""
    sample_chemicals = [
        Chemical(
            barcode="CHEM-00101",
            name="Hydrochloric Acid 37%",
            cas_number="7647-01-0",
            location="Room 204 - Acid Cabinet A1",
            date_in="2025-01-15",
            expiration_date="2027-01-15",
            storage_group="Corrosive - Acid",
            container_size="2.5 L",
            remaining_quantity=1.8,
            units="L",
            state="Liquid",
            msds="https://pubchem.ncbi.nlm.nih.gov/compound/313",
            college="College of Science",
            department="Chemistry",
            hazard_security=False,
            hazard_health=True,
            hazard_physical=True,
            notes="Handle inside fume hood. Use acid-resistant gloves.",
        ),
        Chemical(
            barcode="CHEM-00102",
            name="Ethanol 99.8% ACS Grade",
            cas_number="64-17-5",
            location="Room 101 - Flammables Cabinet F2",
            date_in="2025-03-10",
            expiration_date="2026-03-10",
            storage_group="Flammable Liquid",
            container_size="1 L",
            remaining_quantity=0.15,  # Low stock
            units="L",
            state="Liquid",
            msds="https://pubchem.ncbi.nlm.nih.gov/compound/702",
            college="College of Education",
            department="Biology",
            hazard_security=False,
            hazard_health=True,
            hazard_physical=True,
            notes="Low stock - order replenishment soon.",
        ),
        Chemical(
            barcode="CHEM-00103",
            name="Sodium Hydroxide Pellets",
            cas_number="1310-73-2",
            location="Room 204 - Base Cabinet B2",
            date_in="2024-06-01",
            expiration_date="2025-06-01",  # Expired
            storage_group="Corrosive - Base",
            container_size="500 g",
            remaining_quantity=350.0,
            units="g",
            state="Pellets",
            msds="https://pubchem.ncbi.nlm.nih.gov/compound/14798",
            college="College of Science",
            department="Chemistry",
            hazard_security=False,
            hazard_health=True,
            hazard_physical=True,
            notes="Hygroscopic. Keep bottle tightly closed.",
        ),
        Chemical(
            barcode="CHEM-00104",
            name="Potassium Cyanide Pure",
            cas_number="151-50-8",
            location="Locked Safe Room 301",
            date_in="2025-08-20",
            expiration_date="2028-08-20",
            storage_group="Toxic / Poison",
            container_size="100 g",
            remaining_quantity=85.0,
            units="g",
            state="Solid",
            msds="https://pubchem.ncbi.nlm.nih.gov/compound/8958",
            college="College of Science",
            department="Chemistry",
            hazard_security=True,
            hazard_health=True,
            hazard_physical=False,
            notes="High security controlled substance. Sign-out log required.",
        ),
        Chemical(
            barcode="CHEM-00105",
            name="Acetone Histological Grade",
            cas_number="67-64-1",
            location="Biology Prep Room - Shelf 4",
            date_in="2025-02-12",
            expiration_date="2026-11-01",  # Expiring soon
            storage_group="Flammable Liquid",
            container_size="4 L",
            remaining_quantity=0.5,
            units="L",
            state="Liquid",
            msds="https://pubchem.ncbi.nlm.nih.gov/compound/180",
            college="College of Education",
            department="Biology",
            hazard_security=False,
            hazard_health=True,
            hazard_physical=True,
            notes="Keep away from heat sources and open flames.",
        ),
        Chemical(
            barcode="CHEM-00106",
            name="Liquid Nitrogen",
            cas_number="7727-37-9",
            location="Cryo Storage Facility",
            date_in="2026-01-05",
            expiration_date="",
            storage_group="Compressed Gas",
            container_size="50 L Dewar",
            remaining_quantity=42.0,
            units="L",
            state="Liquid",
            msds="",
            college="College of Education",
            department="Physics",
            hazard_security=False,
            hazard_health=True,
            hazard_physical=True,
            notes="Cryogenic protective gloves and face shield mandatory.",
        ),
    ]

    success, _ = export_chemicals_to_excel(sample_chemicals, filepath)
    return success
