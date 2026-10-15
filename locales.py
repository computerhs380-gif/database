"""
Localization and Translation module for Chemical Inventory Management System (CIMS).
Provides full Kurdish (Central Kurdish / Sorani) and English dictionaries,
RTL helpers, and bidirectional lookup mappings for filters and departments.
"""

from typing import Dict, Any, List, Optional
from config import COLLEGES_AND_DEPARTMENTS

# Supported languages
LANG_EN = "en"
LANG_KU = "ku"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # App Info
        "app_title": "Chemical Inventory Management System (CIMS)",
        "app_subtitle": "University Laboratory Inventory, Safety Compliance & Expiration Tracker",
        "theme_label": "Theme:",
        "lang_label": "Language:",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "lang_english": "English",
        "lang_kurdish": "کوردی",

        # Stat Cards
        "stat_total": "Total Chemicals",
        "stat_expired": "Expired",
        "stat_expiring": "Expiring Soon (<30d)",
        "stat_low": "Low Quantity",
        "stat_hazards": "Hazardous Items",

        # Toolbar Actions
        "btn_add": "➕ Add Chemical",
        "btn_edit": "✏️ Edit",
        "btn_delete": "🗑️ Delete",
        "btn_msds": "📄 View MSDS",
        "btn_refresh": "🔄 Refresh",
        "btn_template": "📋 Excel Template",
        "btn_export": "📤 Export to Excel",
        "btn_import": "📥 Import from Excel",

        # Search & Filters
        "lbl_search": "🔍 Search:",
        "placeholder_search": "Filter by Barcode, Chemical Name, CAS #, Location...",
        "lbl_college": "College:",
        "lbl_department": "Department:",
        "lbl_quick_filter": "Quick Filter:",
        "btn_clear_filters": "Clear Filters",

        # Filter Options
        "filter_all": "All",
        "filter_expired": "Expired",
        "filter_expiring_soon": "Expiring Soon",
        "filter_low_stock": "Low Stock",
        "filter_hazards": "Hazards",
        "lbl_hazard_filter": "Hazard:",
        "hazard_filter_all": "All hazards",

        # Table Column Headers
        "col_id": "ID",
        "col_barcode": "Barcode",
        "col_name": "Chemical Name",
        "col_cas": "CAS Number",
        "col_college": "College",
        "col_department": "Department",
        "col_location": "Storage Location",
        "col_qty": "Qty",
        "col_units": "Units",
        "col_expiration": "Expiration",
        "col_status": "Status",
        "col_stock": "Stock",
        "col_hazards": "Hazards",

        # Table Row Values / Badges
        "status_expired": "Expired",
        "status_expiring_soon": "Expiring Soon",
        "status_normal": "Normal",
        "stock_low": "⚠️ LOW",
        "stock_ok": "OK",
        "hazard_security": "🔒Sec",
        "hazard_health": "☣️Hlt",
        "hazard_physical": "🔥Phy",
        "hazard_none": "None",
        "hazard_label_cwc": "🔒 Chemical Weapons Convention (CWC)",
        "hazard_label_theft": "🔒 High theft/diversion risk",
        "hazard_label_other_security": "🔒 Other security risk",
        "hazard_label_carcinogen_mutagen": "☣️ Carcinogen / mutagen",
        "hazard_label_health_hazard": "☣️ Systemic / chronic health hazard",
        "hazard_label_irritant_sensitizer": "⚠️ Irritant / sensitizer",
        "hazard_label_acute_toxicity": "☠️ Acute toxicity",
        "hazard_label_corrosive": "🧪 Corrosive",
        "hazard_label_explosive": "💥 Explosive",
        "hazard_label_flammable": "🔥 Flammable",
        "hazard_label_oxidizer": "⭕ Oxidizer",
        "hazard_label_compressed_gas": "💨 Compressed gas",
        "hazard_label_other_physical": "⚠️ Other physical hazard",
        "hazard_badge_cwc": "🔒CWC",
        "hazard_badge_theft": "🔒Theft",
        "hazard_badge_other_security": "🔒Sec",
        "hazard_badge_carcinogen_mutagen": "☣️Carc",
        "hazard_badge_health_hazard": "☣️Health",
        "hazard_badge_irritant_sensitizer": "⚠️Irrit",
        "hazard_badge_acute_toxicity": "☠️Tox",
        "hazard_badge_corrosive": "🧪Corr",
        "hazard_badge_explosive": "💥Expl",
        "hazard_badge_flammable": "🔥Flam",
        "hazard_badge_oxidizer": "⭕Oxid",
        "hazard_badge_compressed_gas": "💨Gas",
        "hazard_badge_other_physical": "⚠️Phys",
        "val_none": "None",

        # Status Bar
        "status_ready": "Ready.",
        "status_db_connected": "🟢 Database: Connected (Local SQLite)",
        "status_showing_count": "Showing {count} of {total} chemicals ({filter_info})",
        "status_filter_tag": "Filter",
        "status_college_tag": "College",
        "status_dept_tag": "Dept",
        "status_search_tag": "Search",
        "status_barcode_copied": "📋 Barcode '{barcode}' copied to clipboard.",

        # Context Menu
        "menu_edit": "✏️ Edit Chemical",
        "menu_msds": "📄 Open MSDS Sheet",
        "menu_copy_barcode": "📋 Copy Barcode",
        "menu_delete": "🗑️ Delete Record",

        # Dialogs & Prompts
        "dialog_selection_required": "Selection Required",
        "dialog_select_to_edit": "Please select a chemical row to edit.",
        "dialog_select_to_delete": "Please select a chemical row to delete.",
        "dialog_select_to_msds": "Please select a chemical to view its MSDS.",
        "dialog_confirm_delete_title": "Confirm Delete",
        "dialog_confirm_delete_msg": "Are you sure you want to permanently delete:\n\n'{name}' (Barcode: {barcode})?\n\nThis cannot be undone.",
        "dialog_delete_failed": "Delete Failed",
        "dialog_no_msds_title": "No MSDS Link Stored",
        "dialog_no_msds_msg": "No MSDS sheet link is saved for '{name}'.\n\nWould you like to search PubChem online for '{query}'?",
        "dialog_msds_error": "MSDS Error",
        "dialog_msds_error_msg": "Could not open MSDS link: {error}",

        # Excel Dialogs
        "dialog_export_title": "Export Chemicals to Excel",
        "dialog_export_complete_title": "Excel Export Complete",
        "dialog_export_success_msg": "Successfully exported {count} chemical records!",
        "dialog_export_saved_to": "Saved to: {path}",
        "dialog_export_total_count": "Total items exported: {count}",
        "dialog_export_failed_title": "Export Failed",
        "dialog_import_title": "Select Excel File to Import",
        "dialog_import_failed_title": "Excel Import Failed",
        "dialog_import_failed_msg": "Could not parse chemicals from selected file.",
        "dialog_import_results_title": "Excel Import Results",
        "dialog_import_summary": "Import Complete: {inserted} inserted, {updated} updated.",
        "dialog_import_inserted_log": "• Successfully imported/inserted: {count} new chemicals",
        "dialog_import_updated_log": "• Updated existing chemicals: {count}",
        "dialog_import_parse_warnings": "\n--- Parse Warnings ---",
        "dialog_import_db_warnings": "\n--- Database Warnings ---",
        "dialog_template_save_title": "Save Chemical Inventory Excel Template",
        "dialog_template_created_title": "Template Created",
        "dialog_template_created_msg": "Standard Excel template generated successfully at:\n{path}\n\nYou can fill it in and use 'Import from Excel' at any time!",
        "dialog_template_error_title": "Error",
        "dialog_template_error_msg": "Could not generate template file.",
        "dialog_error_adding_title": "Error Adding Chemical",
        "dialog_error_updating_title": "Error Updating Chemical",

        # Chemical Form Dialog
        "form_add_title": "Add New Chemical",
        "form_edit_title": "Edit Chemical Record",
        "form_add_heading": "🧪 Add New Chemical Record",
        "form_edit_heading": "✏️ Edit Chemical Record",
        "form_subtitle": "Fill in the chemical information below. Required fields are marked with (*).",
        "form_sec1_title": "1. Chemical Identification",
        "form_sec2_title": "2. Storage & Location",
        "form_sec3_title": "3. Quantity & Tracking Dates",
        "form_sec4_title": "4. Safety, Hazards & MSDS",

        "form_barcode": "Barcode ID (*):",
        "form_barcode_placeholder": "e.g. CHEM-00101 or scan barcode",
        "form_btn_gen_barcode": "Generate Code",
        "form_name": "Chemical Name (*):",
        "form_name_placeholder": "e.g. Hydrochloric Acid 37%",
        "form_cas": "CAS Number:",
        "form_cas_placeholder": "e.g. 7647-01-0",
        "form_college": "College (*):",
        "form_department": "Department (*):",
        "form_location": "Storage Location:",
        "form_location_placeholder": "e.g. Room 204 - Acid Cabinet A1",
        "form_storage_group": "Storage Group:",
        "form_physical_state": "Physical State:",
        "form_container_size": "Container Capacity:",
        "form_container_size_placeholder": "e.g. 500 mL, 2.5 L, 1 kg",
        "form_remaining_qty": "Remaining Qty (*):",
        "form_remaining_qty_placeholder": "e.g. 1.5",
        "form_units": "Measurement Units:",
        "form_date_in": "Date In (YYYY-MM-DD):",
        "form_btn_today": "Today",
        "form_exp_date": "Expiration Date:",
        "form_btn_exp_1y": "+1 Year",
        "form_btn_exp_2y": "+2 Years",
        "form_btn_no_exp": "No Expiry",
        "form_hazard_flags": "Hazard Flags:",
        "form_hazard_security": "Security Alerts",
        "form_hazard_health": "Health Hazards",
        "form_hazard_physical": "Physical Hazards",
        "form_chk_security": "🔒 Security Risk (Controlled / Theft Risk)",
        "form_chk_health": "☣️ Health Hazard (Toxic / Carcinogen)",
        "form_chk_physical": "🔥 Physical Hazard (Flammable / Explosive)",
        "form_msds": "MSDS / SDS Link:",
        "form_msds_placeholder": "URL link or path to PDF file",
        "form_btn_browse_msds": "Browse File",
        "form_btn_open_msds": "Open",
        "form_notes": "Notes / Instructions:",
        "form_btn_cancel": "Cancel",
        "form_btn_save_changes": "Save Changes",
        "form_btn_save_add": "Add Chemical",

        # Validation Messages
        "val_barcode_empty": "⚠️ Please enter or generate a Barcode ID.",
        "val_name_empty": "⚠️ Chemical Name cannot be blank.",
        "val_qty_negative": "⚠️ Remaining Quantity cannot be negative.",
        "val_qty_invalid": "⚠️ Please enter a valid number for Remaining Quantity.",
        "val_exp_format": "⚠️ Expiration Date must be in YYYY-MM-DD format (e.g. 2026-12-31).",
        "val_date_in_format": "⚠️ Date In must be in YYYY-MM-DD format (e.g. 2025-01-15).",
        "val_msds_empty": "No MSDS link or file specified.",
        "val_msds_open_error": "Could not open MSDS link: {error}",

        # Excel Report Dialog
        "excel_dlg_log_title": "Activity Log / Messages:",
        "excel_dlg_close": "Close",

        # Colleges & Departments
        "College": "College",
        "College of Science": "College of Science",
        "College of Education": "College of Education",
        "College of Medicine": "College of Medicine",
        "Chemistry": "Chemistry",
        "Biology": "Biology",
        "Physics": "Physics",
        "Food Science": "Food Science",
        "Biomedical Science": "Biomedical Science",
        "General Medicine": "General Medicine",
    },

    "ku": {
        # App Info
        "app_title": "کۆگای ماددە کیمیاییەکان (CIMS)",
        "app_subtitle": "بەڕێوەبردنی تاقیگە، سەلامەتی و بەسەرچوونی ماددەکان",
        "theme_label": "ڕووکار:",
        "lang_label": "زمان:",
        "theme_dark": "تاریک",
        "theme_light": "ڕووناک",
        "lang_english": "English",
        "lang_kurdish": "کوردی",

        # Stat Cards
        "stat_total": "کۆی گشتی",
        "stat_expired": "بەسەرچوو",
        "stat_expiring": "نزیک لە بەسەرچوون",
        "stat_low": "بڕی کەم",
        "stat_hazards": "مەترسیدار",

        # Toolbar Actions
        "btn_add": "➕ زیادکردنی ماددە",
        "btn_edit": "✏️ دەستکاریکردن",
        "btn_delete": "🗑️ سڕینەوە",
        "btn_msds": "📄 پیشاندانی MSDS",
        "btn_refresh": "🔄 نوێکردنەوە",
        "btn_template": "📋 قاڵبی ئێکسڵ",
        "btn_export": "📤 هەناردەکردن بۆ ئێکسڵ",
        "btn_import": "📥 هاوردەکردن لە ئێکسڵ",

        # Search & Filters
        "lbl_search": "🔍 گەڕان:",
        "placeholder_search": "گەڕان بەپێی بارکۆد، ناوی ماددە، کۆدی CAS، شوێن...",
        "lbl_college": "کۆلێژ:",
        "lbl_department": "بەش:",
        "lbl_quick_filter": "فلتەری خێرا:",
        "btn_clear_filters": "پاککردنەوەی فلتەر",

        # Filter Options
        "filter_all": "هەموو",
        "filter_expired": "بەسەرچوو",
        "filter_expiring_soon": "نزیک لە بەسەرچوون",
        "filter_low_stock": "بڕی کەم",
        "filter_hazards": "مەترسیدار",
        "lbl_hazard_filter": "مەترسی:",
        "hazard_filter_all": "هەموو مەترسییەکان",

        # Table Column Headers
        "col_id": "ژمارە",
        "col_barcode": "بارکۆد",
        "col_name": "ناوی ماددە",
        "col_cas": "کۆدی CAS",
        "col_college": "کۆلێژ",
        "col_department": "بەش",
        "col_location": "شوێنی کۆگا",
        "col_qty": "بڕ",
        "col_units": "یەکە",
        "col_expiration": "بەسەرچوون",
        "col_status": "دۆخ",
        "col_stock": "کۆگا",
        "col_hazards": "مەترسییەکان",

        # Table Row Values / Badges
        "status_expired": "بەسەرچوو",
        "status_expiring_soon": "نزیک لە بەسەرچوون",
        "status_normal": "ئاسایی",
        "stock_low": "⚠️ کەم",
        "stock_ok": "باشە",
        "hazard_security": "🔒ئەمنی",
        "hazard_health": "☣️تەندروستی",
        "hazard_physical": "🔥فیزیایی",
        "hazard_none": "هیچ",
        "hazard_label_cwc": "🔒 پێوەندی چەکە کیمیاییەکان (CWC)",
        "hazard_label_theft": "🔒 مەترسیی بەرزی دزین / لادان",
        "hazard_label_other_security": "🔒 مەترسیی ئەمنیی تر",
        "hazard_label_carcinogen_mutagen": "☣️ شێرپەنجەدروستکەر / گۆڕانکاریی جینی",
        "hazard_label_health_hazard": "☣️ مەترسیی تەندروستیی سیستەمی / درێژخایەن",
        "hazard_label_irritant_sensitizer": "⚠️ هەوێنەر / هەستیارکەر",
        "hazard_label_acute_toxicity": "☠️ ژەهراویبوونی توند",
        "hazard_label_corrosive": "🧪 داخورێنەر",
        "hazard_label_explosive": "💥 تەقینەوە",
        "hazard_label_flammable": "🔥 سووتێنەر",
        "hazard_label_oxidizer": "⭕ ئۆکسێنەر",
        "hazard_label_compressed_gas": "💨 گازی پەستێنراو",
        "hazard_label_other_physical": "⚠️ مەترسیی فیزیاییی تر",
        "hazard_badge_cwc": "🔒CWC",
        "hazard_badge_theft": "🔒دزین",
        "hazard_badge_other_security": "🔒ئەمنی",
        "hazard_badge_carcinogen_mutagen": "☣️شێرپە",
        "hazard_badge_health_hazard": "☣️تەندروستی",
        "hazard_badge_irritant_sensitizer": "⚠️هەستیار",
        "hazard_badge_acute_toxicity": "☠️ژەهراوی",
        "hazard_badge_corrosive": "🧪داخورێنەر",
        "hazard_badge_explosive": "💥تەقینەوە",
        "hazard_badge_flammable": "🔥سووتێنەر",
        "hazard_badge_oxidizer": "⭕ئۆکسێنەر",
        "hazard_badge_compressed_gas": "💨گاز",
        "hazard_badge_other_physical": "⚠️فیزیایی",
        "val_none": "هیچ",

        # Status Bar
        "status_ready": "ئامادەیە.",
        "status_db_connected": "🟢 بنکەی دراوە: پەیوەستکراوە (SQLite خۆجێیی)",
        "status_showing_count": "پیشاندانی {count} لە کۆی {total} ماددەی کیمیایی ({filter_info})",
        "status_filter_tag": "فلتەر",
        "status_college_tag": "کۆلێژ",
        "status_dept_tag": "بەش",
        "status_search_tag": "گەڕان",
        "status_barcode_copied": "📋 بارکۆدی '{barcode}' لەبەرگیرایەوە بۆ کلیپبۆرد.",

        # Context Menu
        "menu_edit": "✏️ دەستکاریکردنی ماددە",
        "menu_msds": "📄 کردنەوەی پەڕەی MSDS",
        "menu_copy_barcode": "📋 لەبەرگرتنەوەی بارکۆد",
        "menu_delete": "🗑️ سڕینەوەی تۆمار",

        # Dialogs & Prompts
        "dialog_selection_required": "دیاریکردن پێویستە",
        "dialog_select_to_edit": "تکایە دێڕێکی ماددە دیاریبکە بۆ دەستکاریکردن.",
        "dialog_select_to_delete": "تکایە دێڕێکی ماددە دیاریبکە بۆ سڕینەوە.",
        "dialog_select_to_msds": "تکایە دێڕێکی ماددە دیاریبکە بۆ پیشاندانی MSDS.",
        "dialog_confirm_delete_title": "دڵنیابوونەوە لە سڕینەوە",
        "dialog_confirm_delete_msg": "ئایا دڵنیایت لە سڕینەوەی یەکجارەکی بۆ:\n\n'{name}' (بارکۆد: {barcode})؟\n\nئەم کردارە ناگەڕێندرێتەوە.",
        "dialog_delete_failed": "سڕینەوە سەرکەوتوو نەبوو",
        "dialog_no_msds_title": "هیچ بەستەرێکی MSDS تۆمار نەکراوە",
        "dialog_no_msds_msg": "هیچ بەستەرێکی پەڕەی MSDS بۆ '{name}' تۆمار نەکراوە.\n\nئایا دەتەوێت لە PubChem بگەڕێیت بۆ '{query}'؟",
        "dialog_msds_error": "هەڵەی MSDS",
        "dialog_msds_error_msg": "نەتوانرا بەستەری MSDS بکرێتەوە: {error}",

        # Excel Dialogs
        "dialog_export_title": "هەناردەکردنی ماددە کیمیاییەکان بۆ ئێکسڵ",
        "dialog_export_complete_title": "هەناردەکردنی ئێکسڵ تەواوبوو",
        "dialog_export_success_msg": "بە سەرکەوتوویی {count} تۆماری ماددەی کیمیایی هەناردەکران!",
        "dialog_export_saved_to": "پاشەکەوتکرا لە: {path}",
        "dialog_export_total_count": "کۆی گشتی ماددە هەناردەکراوەکان: {count}",
        "dialog_export_failed_title": "هەناردەکردن سەرکەوتوو نەبوو",
        "dialog_import_title": "دیاریکردنی پەڕگەی ئێکسڵ بۆ هاوردەکردن",
        "dialog_import_failed_title": "هاوردەکردنی ئێکسڵ سەرکەوتوو نەبوو",
        "dialog_import_failed_msg": "نەتوانرا ماددە کیمیاییەکان لە پەڕگەی دیاریکراو بخوێندرێنەوە.",
        "dialog_import_results_title": "ئەنجامی هاوردەکردنی ئێکسڵ",
        "dialog_import_summary": "هاوردەکردن تەواوبوو: {inserted} نوێ زیادکران، {updated} نوێکرانەوە.",
        "dialog_import_inserted_log": "• بە سەرکەوتوویی {count} ماددەی کیمیایی نوێ هاوردەکران",
        "dialog_import_updated_log": "• نوێکردنەوەی ماددە کۆنەکان: {count}",
        "dialog_import_parse_warnings": "\n--- ئاگادارییەکانی خوێندنەوە ---",
        "dialog_import_db_warnings": "\n--- ئاگادارییەکانی بنکەی دراوە ---",
        "dialog_template_save_title": "پاشەکەوتکردنی قاڵبی ئێکسڵ",
        "dialog_template_created_title": "قاڵب دروستکرا",
        "dialog_template_created_msg": "قاڵبی ستانداردی ئێکسڵ بە سەرکەوتوویی دروستکرا لە:\n{path}\n\nدەتوانیت پڕی بکەیتەوە و هەرکاتێک ویستت 'هاوردەکردن لە ئێکسڵ' بەکاربهێنیت!",
        "dialog_template_error_title": "هەڵە",
        "dialog_template_error_msg": "نەتوانرا پەڕگەی قاڵب دروستبکرێت.",
        "dialog_error_adding_title": "هەڵە لە زیادکردنی ماددە",
        "dialog_error_updating_title": "هەڵە لە نوێکردنەوەی ماددە",

        # Chemical Form Dialog
        "form_add_title": "زیادکردنی ماددەی کیمیایی نوێ",
        "form_edit_title": "دەستکاریکردنی تۆماری ماددە",
        "form_add_heading": "🧪 زیادکردنی ماددەی کیمیایی نوێ",
        "form_edit_heading": "✏️ دەستکاریکردنی تۆماری ماددە",
        "form_subtitle": "زانیارییەکانی ماددە لە خوارەوە پڕبکەرەوە. خانە پێویستەکان بە (*) دیاریکراون.",
        "form_sec1_title": "١. ناسینەوەی ماددەی کیمیایی",
        "form_sec2_title": "٢. هەڵگرتن و شوێن",
        "form_sec3_title": "٣. بڕ و بەروارەکانی بەدواداچوون",
        "form_sec4_title": "٤. سەلامەتی، مەترسییەکان و MSDS",

        "form_barcode": "کۆدی بارکۆد (*):",
        "form_barcode_placeholder": "نموونە: CHEM-00101 یان بارکۆد سکان بکە",
        "form_btn_gen_barcode": "دروستکردنی کۆد",
        "form_name": "ناوی ماددەی کیمیایی (*):",
        "form_name_placeholder": "نموونە: ترشی هایدرۆکلۆریک 37%",
        "form_cas": "کۆدی CAS:",
        "form_cas_placeholder": "نموونە: 7647-01-0",
        "form_college": "کۆلێژ (*):",
        "form_department": "بەش (*):",
        "form_location": "شوێنی هەڵگرتن:",
        "form_location_placeholder": "نموونە: ژووری 204 - دۆڵابی ترشەکان A1",
        "form_storage_group": "گرووپی هەڵگرتن:",
        "form_physical_state": "دۆخی فیزیایی:",
        "form_container_size": "قەبارەی دەفر:",
        "form_container_size_placeholder": "نموونە: 500 mL, 2.5 L, 1 kg",
        "form_remaining_qty": "بڕی ماوە (*):",
        "form_remaining_qty_placeholder": "نموونە: 1.5",
        "form_units": "یەکەی پێوانە:",
        "form_date_in": "بەرواری هاتن (YYYY-MM-DD):",
        "form_btn_today": "ئەمڕۆ",
        "form_exp_date": "بەرواری بەسەرچوون:",
        "form_btn_exp_1y": "+١ ساڵ",
        "form_btn_exp_2y": "+٢ ساڵ",
        "form_btn_no_exp": "بێ بەسەرچوون",
        "form_hazard_flags": "ئاگاداری مەترسییەکان:",
        "form_hazard_security": "ئاگادارییە ئەمنییەکان",
        "form_hazard_health": "مەترسییەکانی تەندروستی",
        "form_hazard_physical": "مەترسییە فیزیاییەکان",
        "form_chk_security": "🔒 مەترسی ئەمنی (کۆنترۆڵکراو / دزین)",
        "form_chk_health": "☣️ مەترسی تەندروستی (ژەهراوی / شێرپەنجە)",
        "form_chk_physical": "🔥 مەترسی فیزیایی (سووتێنەر / تەقینەوە)",
        "form_msds": "بەستەری MSDS / SDS:",
        "form_msds_placeholder": "بەستەری ماڵپەڕ یان ناونیشانی پەڕگەی PDF",
        "form_btn_browse_msds": "گەڕان بۆ پەڕگە",
        "form_btn_open_msds": "کردنەوە",
        "form_notes": "تێبینییەکان / ڕێنماییەکان:",
        "form_btn_cancel": "پاشگەزبوونەوە",
        "form_btn_save_changes": "پاشەکەوتکردنی گۆڕانکارییەکان",
        "form_btn_save_add": "زیادکردنی ماددە",

        # Validation Messages
        "val_barcode_empty": "⚠️ تکایە کۆدی بارکۆد بنووسە یان دروستی بکە.",
        "val_name_empty": "⚠️ ناوی ماددەی کیمیایی نابێت بەتاڵ بێت.",
        "val_qty_negative": "⚠️ بڕی ماوە نابێت کەمتر بێت لە سفر.",
        "val_qty_invalid": "⚠️ تکایە ژمارەیەکی دروست بۆ بڕی ماوە بنووسە.",
        "val_exp_format": "⚠️ بەرواری بەسەرچوون دەبێت بە شێوازی YYYY-MM-DD بێت (نموونە: 2026-12-31).",
        "val_date_in_format": "⚠️ بەرواری هاتن دەبێت بە شێوازی YYYY-MM-DD بێت (نموونە: 2025-01-15).",
        "val_msds_empty": "هیچ بەستەر یان پەڕگەیەکی MSDS دیاری نەکراوە.",
        "val_msds_open_error": "نەتوانرا بەستەری MSDS بکرێتەوە: {error}",

        # Excel Report Dialog
        "excel_dlg_log_title": "تۆماری چالاکی / پەیامەکان:",
        "excel_dlg_close": "داخستن",
        # Colleges & Departments
        "College": "کۆلێژ",
        "College of Education": "کۆلێژی پەروەردە",
        "College of Science": "کۆلێژی زانست",
        "College of Medicine": "کۆلێژی پزیشکی",
        "Chemistry": "کیمیا",
        "Biology": "بایۆلۆجی",
        "Physics": "فیزیا",
        "Food Science": "خۆراکزانی",
        "Biomedical Science": "بایۆمێدیکاڵ",
        "General Medicine": "پزیشکیی گشتی",
    },
}

# College translations mapping (English canonical <-> Kurdish display)
COLLEGE_MAP = {
    "All": {"en": "All", "ku": "هەموو"},
    "College of Science": {"en": "College of Science", "ku": "کۆلێژی زانست"},
    "College of Education": {"en": "College of Education", "ku": "کۆلێژی پەروەردە"},
    "College of Medicine": {"en": "College of Medicine", "ku": "کۆلێژی پزیشکی"},
}

# Department translations mapping (English canonical <-> Kurdish display)
DEPARTMENT_MAP = {
    "All": {"en": "All", "ku": "هەموو"},
    "Chemistry": {"en": "Chemistry", "ku": "کیمیا"},
    "Biology": {"en": "Biology", "ku": "بایۆلۆجی"},
    "Physics": {"en": "Physics", "ku": "فیزیا"},
    "Food Science": {"en": "Food Science", "ku": "خۆراکزانی"},
    "Biomedical Science": {"en": "Biomedical Science", "ku": "بایۆمێدیکاڵ"},
    "General Medicine": {"en": "General Medicine", "ku": "پزیشکیی گشتی"},
}

# Quick status filter mapping
STATUS_FILTER_MAP = {
    "All": {"en": "All", "ku": "هەموو"},
    "Expired": {"en": "Expired", "ku": "بەسەرچوو"},
    "Expiring Soon": {"en": "Expiring Soon", "ku": "نزیک لە بەسەرچوون"},
    "Low Stock": {"en": "Low Stock", "ku": "بڕی کەم"},
    "Hazards": {"en": "Hazards", "ku": "مەترسیدار"},
}

# Storage groups translations
STORAGE_GROUP_MAP = {
    "General Storage": {"en": "General Storage", "ku": "کۆگای گشتی"},
    "Flammable Liquid": {"en": "Flammable Liquid", "ku": "شلی سووتێنەر"},
    "Flammable Solid": {"en": "Flammable Solid", "ku": "ڕەقی سووتێنەر"},
    "Corrosive - Acid": {"en": "Corrosive - Acid", "ku": "داخورێنەر - ترش"},
    "Corrosive - Base": {"en": "Corrosive - Base", "ku": "داخورێنەر - تفت"},
    "Oxidizer": {"en": "Oxidizer", "ku": "ئۆکسێنەر"},
    "Toxic / Poison": {"en": "Toxic / Poison", "ku": "ژەهراوی"},
    "Water Reactive": {"en": "Water Reactive", "ku": "کارلێککار لەگەڵ ئاو"},
    "Pyrophoric": {"en": "Pyrophoric", "ku": "خۆسووتێنەر"},
    "Compressed Gas": {"en": "Compressed Gas", "ku": "گازی پەستێنراو"},
    "Refrigerated / Cold Storage": {"en": "Refrigerated / Cold Storage", "ku": "ساردکەرەوە / کۆگای سارد"},
    "Solid": {"en": "Solid", "ku": "ڕەق"},
    "Liquid": {"en": "Liquid", "ku": "شل"},
    "Gas": {"en": "Gas", "ku": "گاز"},
}

# Physical states translations
PHYSICAL_STATE_MAP = {
    "Liquid": {"en": "Liquid", "ku": "شل"},
    "Solid": {"en": "Solid", "ku": "ڕەق"},
    "Powder": {"en": "Powder", "ku": "تۆز"},
    "Crystalline": {"en": "Crystalline", "ku": "کریستاڵی"},
    "Pellets": {"en": "Pellets", "ku": "دەنکۆڵە"},
    "Gas": {"en": "Gas", "ku": "گاز"},
    "Solution": {"en": "Solution", "ku": "گیراوە"},
    "Gel": {"en": "Gel", "ku": "جێڵ"},
    "Suspension": {"en": "Suspension", "ku": "هەڵواسراو (ساسپێنشن)"},
}


def t(key: str, lang: str = LANG_EN, **kwargs) -> str:
    """
    Get localized string by key and language.
    Falls back to English if key is missing in chosen language,
    or returns key itself if not found.
    Supports variable interpolation using str.format(**kwargs).
    """
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS[LANG_EN])
    text = lang_dict.get(key)
    if text is None:
        text = TRANSLATIONS[LANG_EN].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def is_rtl(lang: str) -> bool:
    """Returns True if the language is Right-to-Left (e.g. Kurdish)."""
    return lang == LANG_KU


def get_college_options(lang: str = LANG_EN, include_all: bool = True) -> List[str]:
    """Returns list of college display names in chosen language."""
    items = []
    if include_all:
        items.append(COLLEGE_MAP["All"].get(lang, "All"))
    for canonical, names in COLLEGE_MAP.items():
        if canonical != "All":
            items.append(names.get(lang, canonical))
    return items


def canonical_college(display_val: str, lang: str = LANG_EN) -> str:
    """Maps a localized college display string back to canonical English string."""
    for canonical, names in COLLEGE_MAP.items():
        if display_val in names.values() or canonical == display_val:
            return canonical
    return display_val


def display_college(canonical_val: str, lang: str = LANG_EN) -> str:
    """Maps canonical college to localized display string."""
    mapping = COLLEGE_MAP.get(canonical_val)
    if mapping:
        return mapping.get(lang, canonical_val)
    return canonical_val


def get_department_options(lang: str = LANG_EN, include_all: bool = True, college: str = None) -> List[str]:
    """Returns list of department display names in chosen language.
    If college is specified (canonical English), only returns departments for that college."""
    from config import COLLEGES_AND_DEPARTMENTS
    items = []
    if include_all:
        items.append(DEPARTMENT_MAP["All"].get(lang, "All"))
    if college == "All":
        return items
    if college and college != "All":
        # Only show departments that belong to this college
        depts = COLLEGES_AND_DEPARTMENTS.get(college, [])
        for dept in depts:
            mapping = DEPARTMENT_MAP.get(dept)
            if mapping:
                items.append(mapping.get(lang, dept))
            else:
                items.append(dept)
    else:
        # Show all departments (de-duplicate since Chemistry is in two colleges)
        seen = set()
        for canonical, names in DEPARTMENT_MAP.items():
            if canonical != "All" and canonical not in seen:
                seen.add(canonical)
                items.append(names.get(lang, canonical))
    return items


def canonical_department(display_val: str, lang: str = LANG_EN) -> str:
    """Maps a localized department display string back to canonical English string."""
    for canonical, names in DEPARTMENT_MAP.items():
        if display_val in names.values() or canonical == display_val:
            return canonical
    return display_val


def display_department(canonical_val: str, lang: str = LANG_EN) -> str:
    """Maps canonical department to localized display string."""
    mapping = DEPARTMENT_MAP.get(canonical_val)
    if mapping:
        return mapping.get(lang, canonical_val)
    return canonical_val


def get_status_filter_options(lang: str = LANG_EN) -> List[str]:
    """Returns list of quick status filter display names."""
    return [names.get(lang, canonical) for canonical, names in STATUS_FILTER_MAP.items()]


def canonical_status_filter(display_val: str, lang: str = LANG_EN) -> str:
    """Maps localized quick filter value back to canonical English filter key."""
    for canonical, names in STATUS_FILTER_MAP.items():
        if names.get(lang) == display_val or names.get(LANG_EN) == display_val or canonical == display_val:
            return canonical
    return display_val


HAZARD_FILTER_IDS = [
    "cwc", "theft", "other_security", "carcinogen_mutagen", "health_hazard",
    "irritant_sensitizer", "acute_toxicity", "corrosive", "explosive", "flammable",
    "oxidizer", "compressed_gas", "other_physical",
]


def get_hazard_filter_options(lang: str = LANG_EN) -> List[str]:
    return [t("hazard_filter_all", lang)] + [t(f"hazard_label_{tag}", lang) for tag in HAZARD_FILTER_IDS]


def canonical_hazard_filter(display_val: str, lang: str = LANG_EN) -> str:
    if display_val == t("hazard_filter_all", lang) or display_val in ("All", "All hazards"):
        return "All"
    for tag in HAZARD_FILTER_IDS:
        if display_val == t(f"hazard_label_{tag}", lang):
            return tag
    return display_val


def display_hazard_filter(canonical_val: str, lang: str = LANG_EN) -> str:
    if canonical_val == "All":
        return t("hazard_filter_all", lang)
    if canonical_val in HAZARD_FILTER_IDS:
        return t(f"hazard_label_{canonical_val}", lang)
    return canonical_val


def display_status_filter(canonical_val: str, lang: str = LANG_EN) -> str:
    """Maps canonical status filter key to localized display string."""
    mapping = STATUS_FILTER_MAP.get(canonical_val)
    if mapping:
        return mapping.get(lang, canonical_val)
    return canonical_val


def get_storage_group_options(lang: str = LANG_EN) -> List[str]:
    """Returns list of storage group display names."""
    return [names.get(lang, canonical) for canonical, names in STORAGE_GROUP_MAP.items()]


def canonical_storage_group(display_val: str, lang: str = LANG_EN) -> str:
    for canonical, names in STORAGE_GROUP_MAP.items():
        if names.get(lang) == display_val or names.get(LANG_EN) == display_val or canonical == display_val:
            return canonical
    return display_val


def display_storage_group(canonical_val: str, lang: str = LANG_EN) -> str:
    mapping = STORAGE_GROUP_MAP.get(canonical_val)
    if mapping:
        return mapping.get(lang, canonical_val)
    return canonical_val


def get_physical_state_options(lang: str = LANG_EN) -> List[str]:
    """Returns list of physical state display names."""
    return [names.get(lang, canonical) for canonical, names in PHYSICAL_STATE_MAP.items()]


def canonical_physical_state(display_val: str, lang: str = LANG_EN) -> str:
    for canonical, names in PHYSICAL_STATE_MAP.items():
        if names.get(lang) == display_val or names.get(LANG_EN) == display_val or canonical == display_val:
            return canonical
    return display_val


def display_physical_state(canonical_val: str, lang: str = LANG_EN) -> str:
    mapping = PHYSICAL_STATE_MAP.get(canonical_val)
    if mapping:
        return mapping.get(lang, canonical_val)
    return canonical_val
