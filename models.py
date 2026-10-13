"""
Data models for Chemical Inventory Management System.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Optional, Dict, Any
from config import EXPIRING_SOON_DAYS, LOW_STOCK_DEFAULT_THRESHOLD

HAZARD_GROUPS = {
    "security": ("cwc", "theft", "other_security"),
    "health": ("carcinogen_mutagen", "health_hazard", "irritant_sensitizer", "acute_toxicity"),
    "physical": ("corrosive", "explosive", "flammable", "oxidizer", "compressed_gas", "other_physical"),
}
LEGACY_HAZARD_TAGS = {
    "security": "other_security",
    "health": "health_hazard",
    "physical": "other_physical",
}


@dataclass
class Chemical:
    id: Optional[int] = None
    barcode: str = ""
    name: str = ""
    cas_number: str = ""
    location: str = ""
    date_in: str = ""           # YYYY-MM-DD
    expiration_date: str = ""   # YYYY-MM-DD
    storage_group: str = "General Storage"
    container_size: str = ""    # e.g., "500 mL", "1 kg"
    remaining_quantity: float = 0.0
    units: str = "mL"
    state: str = "Liquid"
    msds: str = ""              # URL or file path
    college: str = "College of Science"
    department: str = "Chemistry"
    hazard_security: bool = False
    hazard_health: bool = False
    hazard_physical: bool = False
    hazard_tags: list = field(default_factory=list)
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""

    def get_expiration_status(self) -> str:
        """
        Returns expiration status: 'Expired', 'Expiring Soon', 'Valid', or 'No Expiry'.
        """
        if not self.expiration_date or self.expiration_date.strip() == "":
            return "No Expiry"
        
        try:
            exp_date = datetime.strptime(self.expiration_date.strip(), "%Y-%m-%d").date()
            today = date.today()
            delta = (exp_date - today).days

            if delta < 0:
                return "Expired"
            elif delta <= EXPIRING_SOON_DAYS:
                return "Expiring Soon"
            else:
                return "Valid"
        except ValueError:
            return "Invalid Date"

    def is_low_stock(self, threshold: float = LOW_STOCK_DEFAULT_THRESHOLD) -> bool:
        """Checks if chemical is below low stock threshold."""
        try:
            return float(self.remaining_quantity) <= threshold
        except (ValueError, TypeError):
            return False

    def has_any_hazard(self) -> bool:
        """Returns True if any hazard flag is active."""
        return bool(self.get_hazard_tags())

    def get_hazard_tags(self) -> list:
        """Return valid detailed tags, conservatively preserving legacy broad flags."""
        valid_tags = {tag for group in HAZARD_GROUPS.values() for tag in group}
        tags = list(dict.fromkeys(tag for tag in self.hazard_tags if tag in valid_tags))
        if tags:
            return tags
        legacy_flags = {
            "security": self.hazard_security,
            "health": self.hazard_health,
            "physical": self.hazard_physical,
        }
        for group, legacy_tag in LEGACY_HAZARD_TAGS.items():
            if legacy_flags[group] and not any(tag in HAZARD_GROUPS[group] for tag in tags):
                tags.append(legacy_tag)
        return tags

    def sync_hazard_flags(self) -> None:
        """Keep legacy broad flags aligned with the detailed classifications."""
        tags = self.get_hazard_tags()
        self.hazard_tags = tags
        self.hazard_security = any(tag in HAZARD_GROUPS["security"] for tag in tags)
        self.hazard_health = any(tag in HAZARD_GROUPS["health"] for tag in tags)
        self.hazard_physical = any(tag in HAZARD_GROUPS["physical"] for tag in tags)

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to dictionary."""
        d = asdict(self)
        d["expiration_status"] = self.get_expiration_status()
        d["is_low_stock"] = self.is_low_stock()
        d["has_hazards"] = self.has_any_hazard()
        return d

    @classmethod
    def from_row(cls, row: tuple, columns: list):
        """Construct Chemical from SQLite row tuple and column names."""
        data = dict(zip(columns, row))
        return cls(
            id=data.get("id"),
            barcode=str(data.get("barcode") or ""),
            name=str(data.get("name") or ""),
            cas_number=str(data.get("cas_number") or ""),
            location=str(data.get("location") or ""),
            date_in=str(data.get("date_in") or ""),
            expiration_date=str(data.get("expiration_date") or ""),
            storage_group=str(data.get("storage_group") or "General Storage"),
            container_size=str(data.get("container_size") or ""),
            remaining_quantity=float(data.get("remaining_quantity") or 0.0),
            units=str(data.get("units") or "mL"),
            state=str(data.get("state") or "Liquid"),
            msds=str(data.get("msds") or ""),
            college=str(data.get("college") or "College of Science"),
            department=str(data.get("department") or "Chemistry"),
            hazard_security=bool(data.get("hazard_security", 0)),
            hazard_health=bool(data.get("hazard_health", 0)),
            hazard_physical=bool(data.get("hazard_physical", 0)),
            hazard_tags=_parse_hazard_tags(data.get("hazard_tags")),
            notes=str(data.get("notes") or ""),
            created_at=str(data.get("created_at") or ""),
            updated_at=str(data.get("updated_at") or "")
        )


def _parse_hazard_tags(value) -> list:
    if not value:
        return []
    try:
        tags = json.loads(value) if isinstance(value, str) else value
        return tags if isinstance(tags, list) else []
    except (TypeError, ValueError):
        return []
