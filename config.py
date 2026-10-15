"""
Configuration settings for Chemical Inventory Management System (CIMS).
"""

from pathlib import Path
import sys

# Application Metadata
APP_TITLE = "Chemical Inventory Management System (CIMS)"
APP_VERSION = "1.0.0"
APP_SUBTITLE = "University Laboratory Chemical & Safety Tracker"

# Paths
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "cims_inventory.db"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
SAMPLE_DATA_DIR.mkdir(exist_ok=True)
SAMPLE_EXCEL_PATH = SAMPLE_DATA_DIR / "chemical_inventory_template.xlsx"

# Alert Thresholds
EXPIRING_SOON_DAYS = 30  # Days threshold to mark chemical as expiring soon
LOW_STOCK_DEFAULT_THRESHOLD = 5.0  # Default value for low quantity alert

COLLEGES_AND_DEPARTMENTS = {
    "College of Science": ["Chemistry", "Food Science", "Biomedical Science"],
    "College of Education": ["Chemistry", "Physics", "Biology"],
    "College of Medicine": ["General Medicine"],
}
COLLEGES = list(COLLEGES_AND_DEPARTMENTS.keys())

STORAGE_GROUPS = [
    "General Storage",
    "Flammable Liquid",
    "Flammable Solid",
    "Corrosive - Acid",
    "Corrosive - Base",
    "Oxidizer",
    "Toxic / Poison",
    "Water Reactive",
    "Pyrophoric",
    "Compressed Gas",
    "Refrigerated / Cold Storage",
    "Solid",
    "Liquid",
    "Gas",
]

UNITS = [
    "mL",
    "L",
    "g",
    "mg",
    "kg",
    "oz",
    "lb",
    "gal",
    "vials",
    "bottles",
]

PHYSICAL_STATES = [
    "Liquid",
    "Solid",
    "Powder",
    "Crystalline",
    "Pellets",
    "Gas",
    "Solution",
    "Gel",
    "Suspension",
]

# UI Appearance & Localization Defaults
DEFAULT_THEME = "dark"      # "dark" or "light" or "system"
COLOR_THEME = "blue"        # "blue", "dark-blue", "green"
DEFAULT_LANGUAGE = "ku"     # "ku" (Kurdish) or "en" (English)
SETTINGS_PATH = BASE_DIR / "settings.json"


def load_settings() -> dict:
    """Loads persistent user settings from settings.json."""
    defaults = {
        "theme": DEFAULT_THEME,
        "language": DEFAULT_LANGUAGE,
    }
    if SETTINGS_PATH.exists():
        try:
            import json
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
    return defaults


def save_settings(settings: dict) -> None:
    """Saves user settings to settings.json."""
    try:
        import json
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception:
        pass


def get_setting(key: str, default=None):
    """Retrieves a single setting value."""
    settings = load_settings()
    return settings.get(key, default)


def set_setting(key: str, value) -> None:
    """Updates and persists a single setting value."""
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
