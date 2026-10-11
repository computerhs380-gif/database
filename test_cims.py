"""
Automated validation test for CIMS components (Database, Models, Excel).
"""

import sys
from pathlib import Path
from models import Chemical
from database import db
from excel_manager import export_chemicals_to_excel, import_chemicals_from_excel, generate_sample_excel_file

def run_tests():
    print("=" * 60)
    print("Testing Chemical Inventory Management System (CIMS)")
    print("=" * 60)

    # 1. Test database connection & table creation
    print("\n[1] Testing database initialization...")
    db.init_database()
    print("    Database initialized successfully.")

    # 2. Test sample Excel generation
    sample_file = Path("test_sample.xlsx")
    print(f"\n[2] Testing sample Excel generation -> {sample_file}...")
    success = generate_sample_excel_file(sample_file)
    assert success, "Failed to generate sample Excel file!"
    print("    Sample Excel generated successfully.")

    # 3. Test Excel import
    print("\n[3] Testing Excel import...")
    chems, errors = import_chemicals_from_excel(sample_file)
    print(f"    Parsed {len(chems)} chemicals, {len(errors)} warnings.")
    assert len(chems) > 0, "No chemicals parsed from sample file!"
    for c in chems[:2]:
        print(f"    - Chemical: {c.name} | CAS: {c.cas_number} | Exp Status: {c.get_expiration_status()} | Low Stock: {c.is_low_stock()}")

    # 4. Test database bulk upsert
    print("\n[4] Testing database bulk upsert...")
    inserted, updated, db_errs = db.bulk_upsert_chemicals(chems)
    print(f"    Inserted: {inserted}, Updated: {updated}, DB Errors: {len(db_errs)}")
    assert inserted > 0 or updated > 0, "Failed to upsert chemicals into database!"

    # 5. Test CRUD queries
    print("\n[5] Testing query and search filters...")
    all_chems = db.get_all_chemicals()
    print(f"    Total in database: {len(all_chems)}")

    chem_search = db.get_all_chemicals(search_query="Acid")
    print(f"    Search for 'Acid': found {len(chem_search)}")
    assert len(chem_search) > 0, "Search for 'Acid' failed!"

    stats = db.get_dashboard_stats()
    print("    Dashboard stats:", stats)
    assert stats["total"] > 0, "Dashboard total count should be > 0"

    # 6. Test Excel export
    export_file = Path("test_export.xlsx")
    print(f"\n[6] Testing Excel export -> {export_file}...")
    exp_ok, msg = export_chemicals_to_excel(all_chems, export_file)
    print(f"    Export result: {exp_ok} | {msg}")
    assert exp_ok, f"Export failed: {msg}"

    # Cleanup test files
    if sample_file.exists():
        sample_file.unlink()
    if export_file.exists():
        export_file.unlink()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! BACKEND & EXCEL READY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
