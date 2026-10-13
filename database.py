"""
SQLite Database Layer for Chemical Inventory Management System.
Handles schema initialization, CRUD operations, transactions, and search queries.
"""

import json
import sqlite3
from datetime import datetime, date
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
from config import DATABASE_PATH, EXPIRING_SOON_DAYS, LOW_STOCK_DEFAULT_THRESHOLD
from models import Chemical


class DatabaseManager:
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Returns SQLite connection with row factory."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self) -> None:
        """Initializes tables and indexes."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS chemicals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    barcode TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    cas_number TEXT,
                    location TEXT,
                    date_in TEXT,
                    expiration_date TEXT,
                    storage_group TEXT,
                    container_size TEXT,
                    remaining_quantity REAL DEFAULT 0.0,
                    units TEXT,
                    state TEXT,
                    msds TEXT,
                    college TEXT DEFAULT 'College of Science',
                    department TEXT,
                    hazard_security INTEGER DEFAULT 0,
                    hazard_health INTEGER DEFAULT 0,
                    hazard_physical INTEGER DEFAULT 0,
                    hazard_tags TEXT NOT NULL DEFAULT '[]',
                    notes TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )

            # Safe migration: Add 'college' column if it does not exist yet
            cursor.execute("PRAGMA table_info(chemicals)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            if "college" not in existing_columns:
                cursor.execute("ALTER TABLE chemicals ADD COLUMN college TEXT DEFAULT 'College of Science'")
            if "hazard_tags" not in existing_columns:
                cursor.execute("ALTER TABLE chemicals ADD COLUMN hazard_tags TEXT NOT NULL DEFAULT '[]'")

            # Preserve old broad flags without pretending they identify a specific GHS class.
            cursor.execute(
                "SELECT id, hazard_security, hazard_health, hazard_physical "
                "FROM chemicals WHERE hazard_tags IS NULL OR hazard_tags = '' OR hazard_tags = '[]'"
            )
            for row in cursor.fetchall():
                tags = []
                if row[1]:
                    tags.append("other_security")
                if row[2]:
                    tags.append("health_hazard")
                if row[3]:
                    tags.append("other_physical")
                if tags:
                    cursor.execute(
                        "UPDATE chemicals SET hazard_tags = ? WHERE id = ?",
                        (json.dumps(tags), row[0]),
                    )

            # Update existing records to match college hierarchy if needed
            cursor.execute(
                "UPDATE chemicals SET college = 'College of Education' WHERE department IN ('Biology', 'Physics') AND (college IS NULL OR college = '' OR college = 'College of Science')"
            )
            cursor.execute(
                "UPDATE chemicals SET college = 'College of Medicine' WHERE department = 'General Medicine' AND (college IS NULL OR college = '')"
            )
            cursor.execute(
                "UPDATE chemicals SET college = 'College of Science' WHERE college IS NULL OR college = ''"
            )

            # Performance indexes for fast searching and filtering
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chem_barcode ON chemicals(barcode)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chem_name ON chemicals(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chem_cas ON chemicals(cas_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chem_college ON chemicals(college)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chem_dept ON chemicals(department)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chem_exp ON chemicals(expiration_date)")
            conn.commit()

    def add_chemical(self, chem: Chemical) -> Tuple[bool, str, Optional[int]]:
        """
        Add a new chemical.
        Returns (success: bool, message: str, new_id: Optional[int]).
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chem.sync_hazard_flags()
        chem.created_at = now
        chem.updated_at = now

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO chemicals (
                        barcode, name, cas_number, location, date_in, expiration_date,
                        storage_group, container_size, remaining_quantity, units,
                        state, msds, college, department, hazard_security, hazard_health,
                        hazard_physical, hazard_tags, notes, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chem.barcode.strip(),
                        chem.name.strip(),
                        chem.cas_number.strip(),
                        chem.location.strip(),
                        chem.date_in.strip(),
                        chem.expiration_date.strip(),
                        chem.storage_group.strip(),
                        chem.container_size.strip(),
                        float(chem.remaining_quantity),
                        chem.units.strip(),
                        chem.state.strip(),
                        chem.msds.strip(),
                        getattr(chem, "college", "College of Science") or "College of Science",
                        chem.department.strip(),
                        1 if chem.hazard_security else 0,
                        1 if chem.hazard_health else 0,
                        1 if chem.hazard_physical else 0,
                        json.dumps(chem.hazard_tags),
                        chem.notes.strip(),
                        chem.created_at,
                        chem.updated_at,
                    ),
                )
                new_id = cursor.lastrowid
                conn.commit()
                return True, "Chemical added successfully!", new_id
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: chemicals.barcode" in str(e):
                return False, f"Barcode '{chem.barcode}' already exists in database.", None
            return False, f"Database integrity error: {str(e)}", None
        except Exception as e:
            return False, f"Error adding chemical: {str(e)}", None

    def update_chemical(self, chem: Chemical) -> Tuple[bool, str]:
        """
        Updates an existing chemical by ID.
        Returns (success: bool, message: str).
        """
        if not chem.id:
            return False, "Cannot update chemical without a valid ID."

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chem.sync_hazard_flags()
        chem.updated_at = now

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE chemicals SET
                        barcode = ?,
                        name = ?,
                        cas_number = ?,
                        location = ?,
                        date_in = ?,
                        expiration_date = ?,
                        storage_group = ?,
                        container_size = ?,
                        remaining_quantity = ?,
                        units = ?,
                        state = ?,
                        msds = ?,
                        college = ?,
                        department = ?,
                        hazard_security = ?,
                        hazard_health = ?,
                        hazard_physical = ?,
                        hazard_tags = ?,
                        notes = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        chem.barcode.strip(),
                        chem.name.strip(),
                        chem.cas_number.strip(),
                        chem.location.strip(),
                        chem.date_in.strip(),
                        chem.expiration_date.strip(),
                        chem.storage_group.strip(),
                        chem.container_size.strip(),
                        float(chem.remaining_quantity),
                        chem.units.strip(),
                        chem.state.strip(),
                        chem.msds.strip(),
                        getattr(chem, "college", "College of Science") or "College of Science",
                        chem.department.strip(),
                        1 if chem.hazard_security else 0,
                        1 if chem.hazard_health else 0,
                        1 if chem.hazard_physical else 0,
                        json.dumps(chem.hazard_tags),
                        chem.notes.strip(),
                        chem.updated_at,
                        chem.id,
                    ),
                )
                conn.commit()
                return True, "Chemical updated successfully!"
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: chemicals.barcode" in str(e):
                return False, f"Barcode '{chem.barcode}' is already in use by another record.",
            return False, f"Database integrity error: {str(e)}"
        except Exception as e:
            return False, f"Error updating chemical: {str(e)}"

    def delete_chemical(self, chemical_id: int) -> Tuple[bool, str]:
        """Deletes a chemical by ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM chemicals WHERE id = ?", (chemical_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    return True, "Chemical deleted successfully."
                return False, "Record not found."
        except Exception as e:
            return False, f"Error deleting chemical: {str(e)}"

    def get_chemical_by_id(self, chemical_id: int) -> Optional[Chemical]:
        """Retrieves a single chemical by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chemicals WHERE id = ?", (chemical_id,))
            row = cursor.fetchone()
            if row:
                cols = [desc[0] for desc in cursor.description]
                return Chemical.from_row(tuple(row), cols)
        return None

    def get_chemical_by_barcode(self, barcode: str) -> Optional[Chemical]:
        """Retrieves a single chemical by barcode."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chemicals WHERE barcode = ?", (barcode.strip(),))
            row = cursor.fetchone()
            if row:
                cols = [desc[0] for desc in cursor.description]
                return Chemical.from_row(tuple(row), cols)
        return None

    def get_all_chemicals(
        self,
        search_query: str = "",
        college: str = "All",
        department: str = "All",
        filter_status: str = "All",
        hazard_filter: str = "All",
    ) -> List[Chemical]:
        """
        Query chemicals with flexible search, college & department filtering, and alert filtering.
        filter_status options: 'All', 'Expired', 'Expiring Soon', 'Low Stock', 'Hazards'
        """
        today_str = date.today().strftime("%Y-%m-%d")

        query = "SELECT * FROM chemicals WHERE 1=1"
        params: List[Any] = []

        # College filter
        if college and college != "All":
            query += " AND college = ?"
            params.append(college)

        # Department filter
        if department and department != "All":
            query += " AND department = ?"
            params.append(department)

        # Search Query across Barcode, Name, CAS Number, Location
        if search_query and search_query.strip():
            sq = f"%{search_query.strip()}%"
            query += " AND (barcode LIKE ? OR name LIKE ? OR cas_number LIKE ? OR location LIKE ?)"
            params.extend([sq, sq, sq, sq])

        # Status alert filter in SQL
        if filter_status == "Expired":
            query += " AND expiration_date != '' AND expiration_date < ?"
            params.append(today_str)
        elif filter_status == "Expiring Soon":
            # expiration_date between today and today + EXPIRING_SOON_DAYS
            query += f" AND expiration_date != '' AND expiration_date >= ? AND expiration_date <= date(?, '+{EXPIRING_SOON_DAYS} days')"
            params.extend([today_str, today_str])
        elif filter_status == "Low Stock":
            query += " AND remaining_quantity <= ?"
            params.append(LOW_STOCK_DEFAULT_THRESHOLD)
        elif filter_status == "Hazards":
            query += " AND (hazard_security = 1 OR hazard_health = 1 OR hazard_physical = 1)"

        if hazard_filter and hazard_filter != "All":
            query += " AND hazard_tags LIKE ?"
            params.append(f'%"{hazard_filter}"%')

        query += " ORDER BY id DESC"

        chemicals = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            cols = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                chemicals.append(Chemical.from_row(tuple(row), cols))

        return chemicals

    def get_dashboard_stats(self) -> Dict[str, int]:
        """Returns counts for dashboard summary cards."""
        today_str = date.today().strftime("%Y-%m-%d")

        stats = {
            "total": 0,
            "expired": 0,
            "expiring_soon": 0,
            "low_stock": 0,
            "hazardous": 0,
        }

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Total
            cursor.execute("SELECT COUNT(*) FROM chemicals")
            stats["total"] = cursor.fetchone()[0]

            # Expired
            cursor.execute(
                "SELECT COUNT(*) FROM chemicals WHERE expiration_date != '' AND expiration_date < ?",
                (today_str,),
            )
            stats["expired"] = cursor.fetchone()[0]

            # Expiring Soon
            cursor.execute(
                f"SELECT COUNT(*) FROM chemicals WHERE expiration_date != '' AND expiration_date >= ? AND expiration_date <= date(?, '+{EXPIRING_SOON_DAYS} days')",
                (today_str, today_str),
            )
            stats["expiring_soon"] = cursor.fetchone()[0]

            # Low Stock
            cursor.execute(
                "SELECT COUNT(*) FROM chemicals WHERE remaining_quantity <= ?",
                (LOW_STOCK_DEFAULT_THRESHOLD,),
            )
            stats["low_stock"] = cursor.fetchone()[0]

            # Hazardous
            cursor.execute(
                "SELECT COUNT(*) FROM chemicals WHERE hazard_security = 1 OR hazard_health = 1 OR hazard_physical = 1"
            )
            stats["hazardous"] = cursor.fetchone()[0]

        return stats

    def bulk_upsert_chemicals(
        self, chemicals: List[Chemical], overwrite_existing: bool = True
    ) -> Tuple[int, int, List[str]]:
        """
        Batch imports chemicals from Excel.
        Returns: (inserted_count, updated_count, error_messages)
        """
        inserted = 0
        updated = 0
        errors = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            for chem in chemicals:
                if not chem.barcode or not chem.name:
                    errors.append(f"Skipped row without Barcode or Name: {chem}")
                    continue

                # Check if barcode exists
                cursor.execute("SELECT id FROM chemicals WHERE barcode = ?", (chem.barcode.strip(),))
                existing = cursor.fetchone()

                if existing:
                    if overwrite_existing:
                        chem.id = existing[0]
                        chem.updated_at = now
                        chem.sync_hazard_flags()
                        cursor.execute(
                            """
                            UPDATE chemicals SET
                                name = ?, cas_number = ?, location = ?, date_in = ?,
                                expiration_date = ?, storage_group = ?, container_size = ?,
                                remaining_quantity = ?, units = ?, state = ?, msds = ?,
                                college = ?, department = ?, hazard_security = ?, hazard_health = ?,
                                hazard_physical = ?, hazard_tags = ?, notes = ?, updated_at = ?
                            WHERE id = ?
                            """,
                            (
                                chem.name.strip(),
                                chem.cas_number.strip(),
                                chem.location.strip(),
                                chem.date_in.strip(),
                                chem.expiration_date.strip(),
                                chem.storage_group.strip(),
                                chem.container_size.strip(),
                                float(chem.remaining_quantity),
                                chem.units.strip(),
                                chem.state.strip(),
                                chem.msds.strip(),
                                getattr(chem, "college", "College of Science") or "College of Science",
                                chem.department.strip(),
                                1 if chem.hazard_security else 0,
                                1 if chem.hazard_health else 0,
                                1 if chem.hazard_physical else 0,
                                json.dumps(chem.hazard_tags),
                                chem.notes.strip(),
                                chem.updated_at,
                                chem.id,
                            ),
                        )
                        updated += 1
                    else:
                        errors.append(f"Barcode '{chem.barcode}' already exists (skipped).")
                else:
                    chem.created_at = now
                    chem.updated_at = now
                    chem.sync_hazard_flags()
                    cursor.execute(
                        """
                        INSERT INTO chemicals (
                            barcode, name, cas_number, location, date_in, expiration_date,
                            storage_group, container_size, remaining_quantity, units,
                            state, msds, college, department, hazard_security, hazard_health,
                            hazard_physical, hazard_tags, notes, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            chem.barcode.strip(),
                            chem.name.strip(),
                            chem.cas_number.strip(),
                            chem.location.strip(),
                            chem.date_in.strip(),
                            chem.expiration_date.strip(),
                            chem.storage_group.strip(),
                            chem.container_size.strip(),
                            float(chem.remaining_quantity),
                            chem.units.strip(),
                            chem.state.strip(),
                            chem.msds.strip(),
                            getattr(chem, "college", "College of Science") or "College of Science",
                            chem.department.strip(),
                            1 if chem.hazard_security else 0,
                            1 if chem.hazard_health else 0,
                            1 if chem.hazard_physical else 0,
                            json.dumps(chem.hazard_tags),
                            chem.notes.strip(),
                            chem.created_at,
                            chem.updated_at,
                        ),
                    )
                    inserted += 1

            conn.commit()

        return inserted, updated, errors


# Singleton database instance
db = DatabaseManager()
