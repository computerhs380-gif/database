"""
Validation test for Kurdish localization and RTL support in CIMS.
"""

import sys
import json
from pathlib import Path

# Configure utf-8 stdout on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


from config import SETTINGS_PATH, load_settings, save_settings, get_setting, set_setting
from locales import (
    t,
    is_rtl,
    LANG_EN,
    LANG_KU,
    get_department_options,
    canonical_department,
    display_department,
    get_status_filter_options,
    canonical_status_filter,
    display_status_filter,
)
from ui.main_window import MainWindow
from ui.chemical_dialog import ChemicalDialog
from ui.excel_dialog import ExcelReportDialog
from database import db


def run_localization_tests():
    print("=" * 65)
    print("RUNNING CIMS LOCALIZATION & RTL VERIFICATION TESTS")
    print("=" * 65)

    # 1. Test translation dictionaries and formatting
    print("\n[1] Testing translation dictionary lookups...")
    assert t("app_title", "ku") == "کۆگای ماددە کیمیاییەکان (CIMS)"
    assert t("app_title", "en") == "Chemical Inventory Management System (CIMS)"
    assert t("stat_total", "ku") == "کۆی گشتی"
    assert t("stat_expired", "ku") == "بەسەرچوو"
    assert t("btn_add", "ku") == "➕ زیادکردنی ماددە"
    assert t("btn_export", "ku") == "📤 هەناردەکردن بۆ ئێکسڵ"
    assert t("col_barcode", "ku") == "بارکۆد"
    assert is_rtl("ku") is True
    assert is_rtl("en") is False
    print("    Translation lookups verified.")

    # 2. Test department and status filter bidirectional mappings
    print("\n[2] Testing bidirectional mappings...")
    ku_depts = get_department_options("ku")
    assert "کیمیا" in ku_depts
    assert "بایۆلۆجی" in ku_depts
    assert canonical_department("کیمیا", "ku") == "Chemistry"
    assert display_department("Chemistry", "ku") == "کیمیا"

    ku_filters = get_status_filter_options("ku")
    assert "بەسەرچوو" in ku_filters
    assert "مەترسیدار" in ku_filters
    assert canonical_status_filter("بەسەرچوو", "ku") == "Expired"
    assert display_status_filter("Expired", "ku") == "بەسەرچوو"
    print("    Mappings verified.")

    # 3. Test settings persistence
    print("\n[3] Testing settings persistence in settings.json...")
    set_setting("language", "ku")
    assert get_setting("language") == "ku"
    assert SETTINGS_PATH.exists()
    settings = load_settings()
    assert settings["language"] == "ku"
    print(f"    Settings saved to {SETTINGS_PATH.name}: {settings}")

    # 4. Test MainWindow UI in Kurdish mode
    print("\n[4] Testing MainWindow in Kurdish (RTL) mode...")
    app = MainWindow()
    app.update()

    assert app.current_lang == "ku"
    assert "کۆگای ماددە کیمیاییەکان" in app.title()
    assert app.lang_switch.get() == "کوردی"
    assert app.btn_add.cget("text") == "➕ زیادکردنی ماددە"
    assert app.btn_export.cget("text") == "📤 هەناردەکردن بۆ ئێکسڵ"
    assert app.lbl_search.cget("text") == "🔍 گەڕان:"

    # Verify table headers in Kurdish
    headers = [app.tree.heading(col)["text"] for col in app.columns]
    print(f"    Treeview headers in Kurdish: {headers}")
    assert "ژمارە" in headers
    assert "بارکۆد" in headers
    assert "ناوی ماددە" in headers
    assert "بەسەرچوون" in headers

    # 5. Test dynamic switching to English
    print("\n[5] Testing dynamic toggle to English...")
    app._on_language_toggle("English")
    app.update()

    assert app.current_lang == "en"
    assert "Chemical Inventory Management System" in app.title()
    assert app.btn_add.cget("text") == "➕ Add Chemical"
    assert app.btn_export.cget("text") == "📤 Export to Excel"
    assert get_setting("language") == "en"

    en_headers = [app.tree.heading(col)["text"] for col in app.columns]
    print(f"    Treeview headers in English: {en_headers}")
    assert "ID" in en_headers
    assert "Barcode" in en_headers
    assert "Chemical Name" in en_headers

    # 6. Test dynamic switching back to Kurdish
    print("\n[6] Testing dynamic toggle back to Kurdish...")
    app._on_language_toggle("کوردی")
    app.update()

    assert app.current_lang == "ku"
    assert get_setting("language") == "ku"
    assert app.btn_add.cget("text") == "➕ زیادکردنی ماددە"

    # 7. Test Dialogs with language support
    print("\n[7] Testing ChemicalDialog with Kurdish (RTL)...")
    dlg = ChemicalDialog(app, lang="ku")
    dlg.update()
    assert "زیادکردنی ماددەی کیمیایی" in dlg.title()
    dlg.destroy()

    first_chem = db.get_all_chemicals()[0]
    dlg_edit = ChemicalDialog(app, chemical=first_chem, lang="ku")
    dlg_edit.update()
    assert "دەستکاریکردنی تۆماری ماددە" in dlg_edit.title()
    dlg_edit.destroy()

    print("\n[8] Testing ExcelReportDialog with Kurdish (RTL)...")
    dlg_rep = ExcelReportDialog(
        app,
        title="هەناردەکردنی ئێکسڵ",
        summary_msg="بە سەرکەوتوویی هەناردەکرا!",
        details=["پەڕگە پاشەکەوتکرا"],
        lang="ku",
    )
    dlg_rep.update()
    dlg_rep.destroy()

    app.destroy()

    print("\n" + "=" * 65)
    print("ALL LOCALIZATION & RTL TESTS PASSED SUCCESSFULLY (100%)!")
    print("=" * 65)


if __name__ == "__main__":
    run_localization_tests()
