"""
Main Application Window for Chemical Inventory Management System (CIMS).
Modern CustomTkinter Dashboard with real-time search, filters, statistics cards,
custom-styled Treeview table, full CRUD + Excel integration,
full Kurdish (Sorani) & English localization, and dynamic RTL/LTR layout adaptation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.filedialog as fd
import webbrowser
from typing import Optional, List

import customtkinter as ctk

from config import (
    APP_VERSION,
    SAMPLE_EXCEL_PATH,
    COLOR_THEME,
    DEFAULT_LANGUAGE,
    DEFAULT_THEME,
    get_setting,
    set_setting,
)
from database import db
from models import Chemical
from excel_manager import (
    export_chemicals_to_excel,
    import_chemicals_from_excel,
    generate_sample_excel_file,
)
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
    get_hazard_filter_options,
    canonical_hazard_filter,
    display_hazard_filter,
)
from ui.styles import COLORS, FONTS, configure_treeview_style
from ui.chemical_dialog import ChemicalDialog
from ui.excel_dialog import ExcelReportDialog


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Load persisted settings or fallback to defaults
        self.current_theme = get_setting("theme", DEFAULT_THEME)
        self.current_lang = get_setting("language", DEFAULT_LANGUAGE)

        # Window Configuration
        self.geometry("1300x820")
        self.minsize(1050, 680)

        # Set appearance
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme(COLOR_THEME)

        # State Variables
        self.search_var = tk.StringVar()
        self.department_var = tk.StringVar(value="All")
        self.status_filter_var = tk.StringVar(value="All")
        self.sort_column = "id"
        self.sort_descending = True
        self.cached_chemicals: List[Chemical] = []
        self._is_switching_lang = False

        # Build UI layout components
        self._build_header()
        self._build_stats_cards()
        self._build_toolbar()
        self._build_search_filter_bar()
        self._build_table()
        self._build_status_bar()

        # Context Menu
        self._build_context_menu()

        # Seed sample data on first run if database is empty
        self._seed_initial_data_if_empty()

        # Apply localized text, headers, and RTL/LTR alignment
        self._apply_language(refresh_after=False)

        # Initial data load
        self.refresh_data()

    def _build_header(self):
        """Top header with application branding, lab subtitle, theme, and language toggles."""
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=24, pady=(16, 8))

        # Title & Subtitle container
        self.title_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")

        self.title_lbl = ctk.CTkLabel(
            self.title_box,
            text="",
            font=FONTS["title"],
        )
        self.title_lbl.pack(fill="x")

        self.sub_lbl = ctk.CTkLabel(
            self.title_box,
            text="",
            font=FONTS["subtitle"],
            text_color="gray",
        )
        self.sub_lbl.pack(fill="x")

        # Controls container (Theme & Language switches)
        self.controls_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")

        # Language Switch Box
        self.lang_box = ctk.CTkFrame(self.controls_box, fg_color="transparent")
        self.lbl_lang_title = ctk.CTkLabel(self.lang_box, text="", font=FONTS["body_bold"])
        self.lbl_lang_title.pack(side="left", padx=(0, 6))

        self.lang_switch = ctk.CTkSegmentedButton(
            self.lang_box,
            values=["English", "کوردی"],
            command=self._on_language_toggle,
            font=FONTS["caption"],
        )
        self.lang_switch.set("کوردی" if self.current_lang == LANG_KU else "English")
        self.lang_switch.pack(side="left")

        # Theme Switch Box
        self.theme_box = ctk.CTkFrame(self.controls_box, fg_color="transparent")
        self.lbl_theme_title = ctk.CTkLabel(self.theme_box, text="", font=FONTS["body_bold"])
        self.lbl_theme_title.pack(side="left", padx=(0, 6))

        self.theme_switch = ctk.CTkSegmentedButton(
            self.theme_box,
            values=["Dark", "Light"],
            command=self._on_theme_toggle,
            font=FONTS["caption"],
        )
        self.theme_switch.set("Dark" if self.current_theme.lower() == "dark" else "Light")
        self.theme_switch.pack(side="left")

    def _build_stats_cards(self):
        """Visual dashboard cards highlighting total inventory and active alerts."""
        self.stats_container = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_container.pack(fill="x", padx=24, pady=8)

        # 5 responsive cards
        self.card_total = self._create_stat_card("stat_total", "#3B82F6", "📦")
        self.card_expired = self._create_stat_card("stat_expired", "#EF4444", "⚠️")
        self.card_expiring = self._create_stat_card("stat_expiring", "#F59E0B", "⏳")
        self.card_low = self._create_stat_card("stat_low", "#F97316", "📉")
        self.card_hazard = self._create_stat_card("stat_hazards", "#8B5CF6", "☣️")

        self.stat_cards = [
            self.card_total,
            self.card_expired,
            self.card_expiring,
            self.card_low,
            self.card_hazard,
        ]

    def _create_stat_card(self, title_key: str, accent_color: str, icon: str):
        card = ctk.CTkFrame(self.stats_container, corner_radius=10, height=72)
        card.title_key = title_key
        card.icon = icon
        card.accent_color = accent_color

        stripe = ctk.CTkFrame(card, width=5, corner_radius=2, fg_color=accent_color)
        content = ctk.CTkFrame(card, fg_color="transparent")

        lbl_title = ctk.CTkLabel(
            content,
            text="",
            font=FONTS["stat_label"],
            text_color="gray",
        )
        lbl_title.pack(fill="x")

        lbl_val = ctk.CTkLabel(
            content,
            text="0",
            font=FONTS["stat_num"],
            text_color=accent_color,
        )
        lbl_val.pack(fill="x")

        card.stripe = stripe
        card.content = content
        card.title_label = lbl_title
        card.val_label = lbl_val
        return card

    def _build_toolbar(self):
        """Action toolbar with buttons for Add, Edit, Delete, MSDS, Excel import/export."""
        self.toolbar = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=24, pady=8)

        self.toolbar_primary = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        self.toolbar_secondary = ctk.CTkFrame(self.toolbar, fg_color="transparent")

        # Primary actions
        self.btn_add = ctk.CTkButton(
            self.toolbar_primary,
            text="",
            font=FONTS["body_bold"],
            fg_color="#10B981",
            hover_color="#059669",
            width=140,
            height=36,
            command=self._on_add_chemical,
        )

        self.btn_edit = ctk.CTkButton(
            self.toolbar_primary,
            text="",
            font=FONTS["body_bold"],
            fg_color="#3B82F6",
            hover_color="#2563EB",
            width=110,
            height=36,
            command=self._on_edit_chemical,
        )

        self.btn_delete = ctk.CTkButton(
            self.toolbar_primary,
            text="",
            font=FONTS["body_bold"],
            fg_color="#EF4444",
            hover_color="#DC2626",
            width=100,
            height=36,
            command=self._on_delete_chemical,
        )

        self.btn_msds = ctk.CTkButton(
            self.toolbar_primary,
            text="",
            font=FONTS["body_bold"],
            fg_color="#475569",
            hover_color="#334155",
            width=130,
            height=36,
            command=self._on_view_msds,
        )

        # Secondary actions (Excel & refresh)
        self.btn_refresh = ctk.CTkButton(
            self.toolbar_secondary,
            text="",
            font=FONTS["body"],
            fg_color="#334155",
            hover_color="#1E293B",
            width=105,
            height=36,
            command=self.refresh_data,
        )

        self.btn_template = ctk.CTkButton(
            self.toolbar_secondary,
            text="",
            font=FONTS["body"],
            fg_color="#334155",
            hover_color="#1E293B",
            width=125,
            height=36,
            command=self._on_download_template,
        )

        self.btn_export = ctk.CTkButton(
            self.toolbar_secondary,
            text="",
            font=FONTS["body_bold"],
            fg_color="#0284C7",
            hover_color="#0369A1",
            width=145,
            height=36,
            command=self._on_export_excel,
        )

        self.btn_import = ctk.CTkButton(
            self.toolbar_secondary,
            text="",
            font=FONTS["body_bold"],
            fg_color="#0D9488",
            hover_color="#0F766E",
            width=155,
            height=36,
            command=self._on_import_excel,
        )

    def _build_search_filter_bar(self):
        """Search input and department/alert filter dropdowns."""
        self.filter_bar = ctk.CTkFrame(self, corner_radius=8)
        self.filter_bar.pack(fill="x", padx=24, pady=6)

        self.filter_inner = ctk.CTkFrame(self.filter_bar, fg_color="transparent")
        self.filter_inner.pack(fill="x", padx=12, pady=10)
        self.filter_primary = ctk.CTkFrame(self.filter_inner, fg_color="transparent")
        self.filter_primary.pack(fill="x")
        self.filter_secondary = ctk.CTkFrame(self.filter_inner, fg_color="transparent")
        self.filter_secondary.pack(fill="x", pady=(8, 0))

        # Search Block
        self.search_block = ctk.CTkFrame(self.filter_primary, fg_color="transparent")
        self.lbl_search = ctk.CTkLabel(self.search_block, text="", font=FONTS["body_bold"])
        self.entry_search = ctk.CTkEntry(
            self.search_block,
            placeholder_text="",
            width=300,
            textvariable=self.search_var,
            font=FONTS["body"],
        )
        self.search_var.trace_add("write", lambda *args: self._on_filter_changed())

        # Department Block
        self.dept_block = ctk.CTkFrame(self.filter_primary, fg_color="transparent")
        self.lbl_department = ctk.CTkLabel(self.dept_block, text="", font=FONTS["body_bold"])
        dept_options = get_department_options(self.current_lang)
        self.opt_department = ctk.CTkOptionMenu(
            self.dept_block,
            values=dept_options,
            command=lambda val: self._on_filter_changed(),
            width=150,
            font=FONTS["body"],
        )
        self.opt_department.set(display_department("All", self.current_lang))

        # Quick Filter Block
        self.qfilter_block = ctk.CTkFrame(self.filter_primary, fg_color="transparent")
        self.lbl_quick_filter = ctk.CTkLabel(self.qfilter_block, text="", font=FONTS["body_bold"])
        status_options = get_status_filter_options(self.current_lang)
        self.btn_status_filter = ctk.CTkSegmentedButton(
            self.qfilter_block,
            values=status_options,
            command=lambda val: self._on_filter_changed(),
            font=FONTS["body"],
        )
        self.btn_status_filter.set(display_status_filter("All", self.current_lang))

        self.hazard_filter_block = ctk.CTkFrame(self.filter_secondary, fg_color="transparent")
        self.lbl_hazard_filter = ctk.CTkLabel(self.hazard_filter_block, text="", font=FONTS["body_bold"])
        self.opt_hazard_filter = ctk.CTkOptionMenu(
            self.hazard_filter_block,
            values=get_hazard_filter_options(self.current_lang),
            command=lambda val: self._on_filter_changed(),
            width=230,
            font=FONTS["body"],
        )
        self.opt_hazard_filter.set(display_hazard_filter("All", self.current_lang))

        # Clear Filters Button
        self.btn_clear = ctk.CTkButton(
            self.filter_secondary,
            text="",
            width=100,
            font=FONTS["caption"],
            fg_color="#475569",
            hover_color="#334155",
            command=self._clear_filters,
        )

    def _build_table(self):
        """Build the modern ttk.Treeview data table inside a custom container."""
        self.table_container = ctk.CTkFrame(self, corner_radius=8)
        self.table_container.pack(fill="both", expand=True, padx=24, pady=(6, 8))

        # Configure style
        configure_treeview_style(self.current_theme)

        # Columns definition
        self.columns = (
            "id",
            "barcode",
            "name",
            "cas_number",
            "department",
            "location",
            "remaining_quantity",
            "units",
            "expiration_date",
            "exp_status",
            "stock_alert",
            "hazards",
        )

        self.tree = ttk.Treeview(
            self.table_container,
            columns=self.columns,
            show="headings",
            style="Modern.Treeview",
            selectmode="browse",
        )

        # Scrollbars
        self.vsb = ttk.Scrollbar(self.table_container, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        # Grid placement
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")

        self.table_container.grid_rowconfigure(0, weight=1)
        self.table_container.grid_columnconfigure(0, weight=1)

        # Bind events
        self.tree.bind("<Double-1>", lambda event: self._on_edit_chemical())
        self.tree.bind("<Button-3>", self._show_context_menu)  # Right click
        self.tree.bind("<Return>", lambda event: self._on_edit_chemical())

        # Configure Row Tag Colors
        self._configure_tag_colors()

    def _configure_tag_colors(self):
        """Sets up row tag styles for expired, warning, low stock, and normal rows."""
        if self.current_theme.lower() == "dark":
            self.tree.tag_configure("expired", background="#450A0A", foreground="#FCA5A5")
            self.tree.tag_configure("expiring_soon", background="#451A03", foreground="#FCD34D")
            self.tree.tag_configure("low_stock", background="#431407", foreground="#FDBA74")
            self.tree.tag_configure("evenrow", background="#1E293B", foreground="#F8FAFC")
            self.tree.tag_configure("oddrow", background="#162032", foreground="#F8FAFC")
        else:
            self.tree.tag_configure("expired", background="#FEE2E2", foreground="#991B1B")
            self.tree.tag_configure("expiring_soon", background="#FEF3C7", foreground="#92400E")
            self.tree.tag_configure("low_stock", background="#FFEDD5", foreground="#9A3412")
            self.tree.tag_configure("evenrow", background="#FFFFFF", foreground="#0F172A")
            self.tree.tag_configure("oddrow", background="#F8FAFC", foreground="#0F172A")

    def _build_status_bar(self):
        """Bottom status bar showing inventory count, active filter, and DB connection."""
        self.status_frame = ctk.CTkFrame(self, height=28, fg_color="transparent")
        self.status_frame.pack(fill="x", padx=24, pady=(0, 10))

        self.lbl_status_count = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=FONTS["caption"],
            text_color="gray",
        )

        self.lbl_db_info = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=FONTS["caption"],
            text_color="#10B981",
        )

    def _build_context_menu(self):
        """Right-click popup context menu with localized labels."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(
            label=t("menu_edit", self.current_lang), command=self._on_edit_chemical
        )
        self.context_menu.add_command(
            label=t("menu_msds", self.current_lang), command=self._on_view_msds
        )
        self.context_menu.add_command(
            label=t("menu_copy_barcode", self.current_lang), command=self._copy_selected_barcode
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label=t("menu_delete", self.current_lang), command=self._on_delete_chemical
        )

    def _show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def _apply_language(self, refresh_after: bool = True):
        """
        Dynamically applies translations, font alignments, and mirrors layouts for RTL/LTR.
        Ensures smooth transition between English and Kurdish without restart.
        """
        self._is_switching_lang = True
        lang = self.current_lang
        rtl = is_rtl(lang)
        text_anchor = "e" if rtl else "w"

        # 1. Window Title
        self.title(f"{t('app_title', lang)} v{APP_VERSION}")

        # 2. Header Layout & Content
        self.title_lbl.configure(text=f"🧪 {t('app_title', lang)}", anchor=text_anchor)
        self.sub_lbl.configure(text=t("app_subtitle", lang), anchor=text_anchor)
        self.lbl_lang_title.configure(text=t("lang_label", lang))
        self.lbl_theme_title.configure(text=t("theme_label", lang))

        # Mirror Header layout
        self.title_box.pack_forget()
        self.controls_box.pack_forget()
        self.lang_box.pack_forget()
        self.theme_box.pack_forget()

        if rtl:
            self.title_box.pack(side="right")
            self.controls_box.pack(side="left")
            self.lang_box.pack(side="left", padx=(0, 14))
            self.theme_box.pack(side="left")
        else:
            self.title_box.pack(side="left")
            self.controls_box.pack(side="right")
            self.theme_box.pack(side="right", padx=(14, 0))
            self.lang_box.pack(side="right")

        # 3. Stats Cards Layout & Labels
        for card in self.stat_cards:
            card.pack_forget()
            card.stripe.pack_forget()
            card.content.pack_forget()

            card.title_label.configure(
                text=f"{card.icon} {t(card.title_key, lang)}",
                anchor=text_anchor,
            )
            card.val_label.configure(anchor=text_anchor)

            if rtl:
                card.pack(side="right", fill="both", expand=True, padx=4)
                card.stripe.pack(side="right", fill="y", padx=(10, 0))
                card.content.pack(side="right", fill="both", expand=True, pady=8)
            else:
                card.pack(side="left", fill="both", expand=True, padx=4)
                card.stripe.pack(side="left", fill="y", padx=(0, 10))
                card.content.pack(side="left", fill="both", expand=True, pady=8)

        # 4. Toolbar Layout & Buttons
        self.btn_add.configure(text=t("btn_add", lang))
        self.btn_edit.configure(text=t("btn_edit", lang))
        self.btn_delete.configure(text=t("btn_delete", lang))
        self.btn_msds.configure(text=t("btn_msds", lang))
        self.btn_refresh.configure(text=t("btn_refresh", lang))
        self.btn_template.configure(text=t("btn_template", lang))
        self.btn_export.configure(text=t("btn_export", lang))
        self.btn_import.configure(text=t("btn_import", lang))

        # Unpack toolbar frames and buttons
        self.toolbar_primary.pack_forget()
        self.toolbar_secondary.pack_forget()
        for b in [self.btn_add, self.btn_edit, self.btn_delete, self.btn_msds]:
            b.pack_forget()
        for b in [self.btn_refresh, self.btn_template, self.btn_export, self.btn_import]:
            b.pack_forget()

        if rtl:
            self.toolbar_primary.pack(side="right")
            self.toolbar_secondary.pack(side="left")

            self.btn_add.pack(side="right", padx=(8, 0))
            self.btn_edit.pack(side="right", padx=(8, 0))
            self.btn_delete.pack(side="right", padx=(8, 0))
            self.btn_msds.pack(side="right", padx=(8, 0))

            self.btn_refresh.pack(side="left", padx=(0, 8))
            self.btn_template.pack(side="left", padx=(0, 8))
            self.btn_export.pack(side="left", padx=(0, 8))
            self.btn_import.pack(side="left", padx=(0, 8))
        else:
            self.toolbar_primary.pack(side="left")
            self.toolbar_secondary.pack(side="right")

            self.btn_add.pack(side="left", padx=(0, 8))
            self.btn_edit.pack(side="left", padx=(0, 8))
            self.btn_delete.pack(side="left", padx=(0, 8))
            self.btn_msds.pack(side="left", padx=(0, 8))

            self.btn_refresh.pack(side="right", padx=(8, 0))
            self.btn_template.pack(side="right", padx=(8, 0))
            self.btn_export.pack(side="right", padx=(8, 0))
            self.btn_import.pack(side="right", padx=(8, 0))

        # 5. Search & Filter Bar Layout & Content
        self.lbl_search.configure(text=t("lbl_search", lang))
        self.entry_search.configure(placeholder_text=t("placeholder_search", lang))
        self.lbl_department.configure(text=t("lbl_department", lang))
        self.lbl_quick_filter.configure(text=t("lbl_quick_filter", lang))
        self.lbl_hazard_filter.configure(text=t("lbl_hazard_filter", lang))
        self.btn_clear.configure(text=t("btn_clear_filters", lang))

        # Update department options and retain current selection
        cur_canonical_dept = canonical_department(self.opt_department.get(), LANG_KU if lang == LANG_EN else LANG_EN)
        dept_options = get_department_options(lang)
        self.opt_department.configure(values=dept_options)
        self.opt_department.set(display_department(cur_canonical_dept, lang))

        # Update status quick filter options and retain current selection
        cur_canonical_filter = canonical_status_filter(self.btn_status_filter.get(), LANG_KU if lang == LANG_EN else LANG_EN)
        status_options = get_status_filter_options(lang)
        self.btn_status_filter.configure(values=status_options)
        self.btn_status_filter.set(display_status_filter(cur_canonical_filter, lang))

        previous_hazard_lang = LANG_KU if lang == LANG_EN else LANG_EN
        cur_canonical_hazard = canonical_hazard_filter(self.opt_hazard_filter.get(), previous_hazard_lang)
        hazard_options = get_hazard_filter_options(lang)
        self.opt_hazard_filter.configure(values=hazard_options)
        self.opt_hazard_filter.set(display_hazard_filter(cur_canonical_hazard, lang))

        # Unpack filter components
        self.search_block.pack_forget()
        self.lbl_search.pack_forget()
        self.entry_search.pack_forget()
        self.dept_block.pack_forget()
        self.lbl_department.pack_forget()
        self.opt_department.pack_forget()
        self.qfilter_block.pack_forget()
        self.lbl_quick_filter.pack_forget()
        self.btn_status_filter.pack_forget()
        self.hazard_filter_block.pack_forget()
        self.lbl_hazard_filter.pack_forget()
        self.opt_hazard_filter.pack_forget()
        self.btn_clear.pack_forget()

        if rtl:
            self.search_block.pack(side="right", padx=(0, 16))
            self.lbl_search.pack(side="right", padx=(6, 0))
            self.entry_search.pack(side="right")

            self.dept_block.pack(side="right", padx=(0, 16))
            self.lbl_department.pack(side="right", padx=(6, 0))
            self.opt_department.pack(side="right")

            self.qfilter_block.pack(side="right", padx=(0, 16))
            self.lbl_quick_filter.pack(side="right", padx=(6, 0))
            self.btn_status_filter.pack(side="right")

            self.hazard_filter_block.pack(side="right")
            self.lbl_hazard_filter.pack(side="right", padx=(6, 0))
            self.opt_hazard_filter.pack(side="right")
            self.btn_clear.pack(side="left")
        else:
            self.search_block.pack(side="left", padx=(0, 16))
            self.lbl_search.pack(side="left", padx=(0, 6))
            self.entry_search.pack(side="left")

            self.dept_block.pack(side="left", padx=(0, 16))
            self.lbl_department.pack(side="left", padx=(0, 6))
            self.opt_department.pack(side="left")

            self.qfilter_block.pack(side="left", padx=(0, 16))
            self.lbl_quick_filter.pack(side="left", padx=(0, 6))
            self.btn_status_filter.pack(side="left")

            self.hazard_filter_block.pack(side="left")
            self.lbl_hazard_filter.pack(side="left", padx=(0, 6))
            self.opt_hazard_filter.pack(side="left")
            self.btn_clear.pack(side="right")

        # 6. Table Headers and Columns Configuration
        col_meta = [
            ("id", "col_id", 45, "center"),
            ("barcode", "col_barcode", 110, "center" if rtl else "w"),
            ("name", "col_name", 230, "e" if rtl else "w"),
            ("cas_number", "col_cas", 100, "center" if rtl else "w"),
            ("department", "col_department", 110, "e" if rtl else "w"),
            ("location", "col_location", 150, "e" if rtl else "w"),
            ("remaining_quantity", "col_qty", 65, "e"),
            ("units", "col_units", 65, "center" if rtl else "w"),
            ("expiration_date", "col_expiration", 95, "center"),
            ("exp_status", "col_status", 105, "center"),
            ("stock_alert", "col_stock", 75, "center"),
            ("hazards", "col_hazards", 250, "center"),
        ]

        for col_id, col_key, width, align in col_meta:
            self.tree.heading(
                col_id,
                text=t(col_key, lang),
                anchor=align,
                command=lambda c=col_id: self._sort_by_column(c),
            )
            self.tree.column(col_id, width=width, minwidth=40, anchor=align)

        # 7. Status Bar Layout
        self.lbl_status_count.pack_forget()
        self.lbl_db_info.pack_forget()
        self.lbl_db_info.configure(text=t("status_db_connected", lang))

        if rtl:
            self.lbl_status_count.pack(side="right")
            self.lbl_status_count.configure(anchor="e")
            self.lbl_db_info.pack(side="left")
            self.lbl_db_info.configure(anchor="w")
        else:
            self.lbl_status_count.pack(side="left")
            self.lbl_status_count.configure(anchor="w")
            self.lbl_db_info.pack(side="right")
            self.lbl_db_info.configure(anchor="e")

        # 8. Rebuild Context Menu
        self._build_context_menu()

        self._is_switching_lang = False

        if refresh_after:
            self.refresh_data()

    def _on_language_toggle(self, value: str):
        """Switch language between English and Kurdish dynamically."""
        new_lang = LANG_KU if value == "کوردی" else LANG_EN
        if new_lang != self.current_lang:
            self.current_lang = new_lang
            set_setting("language", new_lang)
            self._apply_language(refresh_after=True)

    def _on_theme_toggle(self, mode: str):
        """Switch between dark and light themes dynamically and persist."""
        self.current_theme = mode.lower()
        set_setting("theme", self.current_theme)
        ctk.set_appearance_mode(self.current_theme)
        configure_treeview_style(self.current_theme)
        self._configure_tag_colors()
        self.refresh_data()

    def _seed_initial_data_if_empty(self):
        """If the database is completely empty on first launch, load realistic sample chemicals."""
        stats = db.get_dashboard_stats()
        if stats["total"] == 0:
            generate_sample_excel_file(SAMPLE_EXCEL_PATH)
            sample_chems, _ = import_chemicals_from_excel(SAMPLE_EXCEL_PATH)
            if sample_chems:
                db.bulk_upsert_chemicals(sample_chems)

    def refresh_data(self):
        """Fetch filtered chemicals from database, populate Treeview, and update stat cards."""
        if self._is_switching_lang:
            return

        lang = self.current_lang
        search_query = self.search_var.get().strip()

        # Map display values to canonical query values for database
        canonical_dept = canonical_department(self.opt_department.get(), lang)
        canonical_filter = canonical_status_filter(self.btn_status_filter.get(), lang)
        canonical_hazard = canonical_hazard_filter(self.opt_hazard_filter.get(), lang)

        # Query database
        chemicals = db.get_all_chemicals(
            search_query=search_query,
            department=canonical_dept,
            filter_status=canonical_filter,
            hazard_filter=canonical_hazard,
        )
        self.cached_chemicals = chemicals

        # Remember selected row ID if any
        selected_row_ids = self.tree.selection()
        selected_id = selected_row_ids[0] if selected_row_ids else None

        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert records into Treeview
        for idx, c in enumerate(chemicals):
            exp_status_canonical = c.get_expiration_status()
            is_low = c.is_low_stock()

            # Hazard indicators localized
            hazards_str = self._format_hazards(c)

            # Localized status text
            if exp_status_canonical == "Expired":
                exp_status_display = t("status_expired", lang)
                row_tag = "expired"
            elif exp_status_canonical == "Expiring Soon":
                exp_status_display = t("status_expiring_soon", lang)
                row_tag = "expiring_soon"
            else:
                exp_status_display = t("status_normal", lang)
                row_tag = "evenrow" if idx % 2 == 0 else "oddrow"

            # Stock alert text
            if is_low:
                stock_str = t("stock_low", lang)
                if row_tag not in ("expired", "expiring_soon"):
                    row_tag = "low_stock"
            else:
                stock_str = t("stock_ok", lang)

            dept_display = display_department(c.department, lang)
            exp_date_display = c.expiration_date or t("val_none", lang)

            vals = (
                c.id,
                c.barcode,
                c.name,
                c.cas_number or "-",
                dept_display,
                c.location or "-",
                f"{c.remaining_quantity:g}",
                c.units,
                exp_date_display,
                exp_status_display,
                stock_str,
                hazards_str,
            )
            self.tree.insert("", "end", iid=str(c.id), values=vals, tags=(row_tag,))

        # Re-select row if it still exists
        if selected_id and self.tree.exists(selected_id):
            self.tree.selection_set(selected_id)

        # Update Stat Cards
        stats = db.get_dashboard_stats()
        self.card_total.val_label.configure(text=str(stats["total"]))
        self.card_expired.val_label.configure(text=str(stats["expired"]))
        self.card_expiring.val_label.configure(text=str(stats["expiring_soon"]))
        self.card_low.val_label.configure(text=str(stats["low_stock"]))
        self.card_hazard.val_label.configure(text=str(stats["hazardous"]))

        # Update Status bar
        display_filt = display_status_filter(canonical_filter, lang)
        display_hazard = display_hazard_filter(canonical_hazard, lang)
        display_d = display_department(canonical_dept, lang)
        filter_tag = t("status_filter_tag", lang)
        dept_tag = t("status_dept_tag", lang)
        search_tag = t("status_search_tag", lang)

        filter_info = f"{filter_tag}: {display_filt} | {dept_tag}: {display_d} | {t('lbl_hazard_filter', lang)} {display_hazard}"
        if search_query:
            filter_info += f" | {search_tag}: '{search_query}'"

        status_text = t(
            "status_showing_count",
            lang,
            count=len(chemicals),
            total=stats["total"],
            filter_info=filter_info,
        )
        self.lbl_status_count.configure(text=status_text)

    def _format_hazards(self, chemical: Chemical) -> str:
        tags = chemical.get_hazard_tags()
        if not tags:
            return t("hazard_none", self.current_lang)
        return " ".join(t(f"hazard_badge_{tag}", self.current_lang) for tag in tags)

    def _get_selected_chemical(self) -> Optional[Chemical]:
        """Returns the Chemical model corresponding to the currently selected row."""
        selected = self.tree.selection()
        if not selected:
            return None
        chem_id = int(selected[0])
        return db.get_chemical_by_id(chem_id)

    def _on_filter_changed(self):
        if not self._is_switching_lang:
            self.refresh_data()

    def _clear_filters(self):
        self.search_var.set("")
        self.opt_department.set(display_department("All", self.current_lang))
        self.btn_status_filter.set(display_status_filter("All", self.current_lang))
        self.opt_hazard_filter.set(display_hazard_filter("All", self.current_lang))
        self.refresh_data()

    def _sort_by_column(self, col: str):
        """Sorts Treeview rows when clicking a column header."""
        if self.sort_column == col:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = col
            self.sort_descending = False

        def get_sort_key(c: Chemical):
            val = getattr(c, col, None)
            if val is None:
                if col == "exp_status":
                    return c.get_expiration_status()
                elif col == "stock_alert":
                    return c.is_low_stock()
                elif col == "hazards":
                    return c.has_any_hazard()
                return ""
            if isinstance(val, (int, float)):
                return val
            return str(val).lower()

        self.cached_chemicals.sort(key=get_sort_key, reverse=self.sort_descending)

        for row in self.tree.get_children():
            self.tree.delete(row)

        lang = self.current_lang
        for idx, c in enumerate(self.cached_chemicals):
            exp_status_canonical = c.get_expiration_status()
            is_low = c.is_low_stock()

            hazards_str = self._format_hazards(c)

            if exp_status_canonical == "Expired":
                exp_status_display = t("status_expired", lang)
                row_tag = "expired"
            elif exp_status_canonical == "Expiring Soon":
                exp_status_display = t("status_expiring_soon", lang)
                row_tag = "expiring_soon"
            else:
                exp_status_display = t("status_normal", lang)
                row_tag = "evenrow" if idx % 2 == 0 else "oddrow"

            if is_low:
                stock_str = t("stock_low", lang)
                if row_tag not in ("expired", "expiring_soon"):
                    row_tag = "low_stock"
            else:
                stock_str = t("stock_ok", lang)

            dept_display = display_department(c.department, lang)
            exp_date_display = c.expiration_date or t("val_none", lang)

            vals = (
                c.id,
                c.barcode,
                c.name,
                c.cas_number or "-",
                dept_display,
                c.location or "-",
                f"{c.remaining_quantity:g}",
                c.units,
                exp_date_display,
                exp_status_display,
                stock_str,
                hazards_str,
            )
            self.tree.insert("", "end", iid=str(c.id), values=vals, tags=(row_tag,))

    def _on_add_chemical(self):
        """Open Add Chemical dialog."""
        lang = self.current_lang

        def save_handler(chem: Chemical) -> bool:
            success, msg, new_id = db.add_chemical(chem)
            if success:
                self.refresh_data()
                if new_id and self.tree.exists(str(new_id)):
                    self.tree.selection_set(str(new_id))
                    self.tree.see(str(new_id))
                return True
            else:
                err_title = t("dialog_error_adding_title", lang)
                messagebox.showerror(err_title, msg, parent=self)
                return False

        ChemicalDialog(self, chemical=None, on_save_callback=save_handler, lang=lang)

    def _on_edit_chemical(self):
        """Open Edit Chemical dialog for selected record."""
        lang = self.current_lang
        chem = self._get_selected_chemical()
        if not chem:
            messagebox.showinfo(
                t("dialog_selection_required", lang),
                t("dialog_select_to_edit", lang),
                parent=self,
            )
            return

        def save_handler(updated_chem: Chemical) -> bool:
            success, msg = db.update_chemical(updated_chem)
            if success:
                self.refresh_data()
                if self.tree.exists(str(updated_chem.id)):
                    self.tree.selection_set(str(updated_chem.id))
                return True
            else:
                err_title = t("dialog_error_updating_title", lang)
                messagebox.showerror(err_title, msg, parent=self)
                return False

        ChemicalDialog(self, chemical=chem, on_save_callback=save_handler, lang=lang)

    def _on_delete_chemical(self):
        """Delete selected chemical with localized confirmation."""
        lang = self.current_lang
        chem = self._get_selected_chemical()
        if not chem:
            messagebox.showinfo(
                t("dialog_selection_required", lang),
                t("dialog_select_to_delete", lang),
                parent=self,
            )
            return

        confirm_title = t("dialog_confirm_delete_title", lang)
        confirm_msg = t(
            "dialog_confirm_delete_msg",
            lang,
            name=chem.name,
            barcode=chem.barcode,
        )

        confirm = messagebox.askyesno(
            confirm_title,
            confirm_msg,
            icon="warning",
            parent=self,
        )
        if confirm:
            success, msg = db.delete_chemical(chem.id)
            if success:
                self.refresh_data()
            else:
                messagebox.showerror(t("dialog_delete_failed", lang), msg, parent=self)

    def _on_view_msds(self):
        """Open MSDS URL or file link in browser/PDF viewer with localized prompts."""
        lang = self.current_lang
        chem = self._get_selected_chemical()
        if not chem:
            messagebox.showinfo(
                t("dialog_selection_required", lang),
                t("dialog_select_to_msds", lang),
                parent=self,
            )
            return

        if not chem.msds or not chem.msds.strip():
            query = chem.cas_number or chem.name
            search_pubchem = messagebox.askyesno(
                t("dialog_no_msds_title", lang),
                t("dialog_no_msds_msg", lang, name=chem.name, query=query),
                parent=self,
            )
            if search_pubchem:
                url = f"https://pubchem.ncbi.nlm.nih.gov/#query={query}"
                webbrowser.open(url)
            return

        try:
            webbrowser.open(chem.msds.strip())
        except Exception as e:
            messagebox.showerror(
                t("dialog_msds_error", lang),
                t("dialog_msds_error_msg", lang, error=str(e)),
                parent=self,
            )

    def _copy_selected_barcode(self):
        """Copy barcode of selected item to system clipboard."""
        chem = self._get_selected_chemical()
        if chem and chem.barcode:
            self.clipboard_clear()
            self.clipboard_append(chem.barcode)
            self.lbl_status_count.configure(
                text=t("status_barcode_copied", self.current_lang, barcode=chem.barcode)
            )

    def _on_export_excel(self):
        """Export current filtered view to Excel with full localization."""
        lang = self.current_lang
        filepath = fd.asksaveasfilename(
            title=t("dialog_export_title", lang),
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile="chemical_inventory_export.xlsx",
        )
        if not filepath:
            return

        items_to_export = self.cached_chemicals if self.cached_chemicals else db.get_all_chemicals()
        success, msg = export_chemicals_to_excel(items_to_export, filepath)

        if success:
            ExcelReportDialog(
                self,
                title=t("dialog_export_complete_title", lang),
                summary_msg=t("dialog_export_success_msg", lang, count=len(items_to_export)),
                details=[
                    t("dialog_export_saved_to", lang, path=filepath),
                    t("dialog_export_total_count", lang, count=len(items_to_export)),
                ],
                lang=lang,
            )
        else:
            messagebox.showerror(t("dialog_export_failed_title", lang), msg, parent=self)

    def _on_import_excel(self):
        """Import chemicals from user-selected Excel file with localized feedback."""
        lang = self.current_lang
        filepath = fd.askopenfilename(
            title=t("dialog_import_title", lang),
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")],
        )
        if not filepath:
            return

        chemicals, errors = import_chemicals_from_excel(filepath)
        if not chemicals and errors:
            ExcelReportDialog(
                self,
                title=t("dialog_import_failed_title", lang),
                summary_msg=t("dialog_import_failed_msg", lang),
                details=errors,
                lang=lang,
            )
            return

        inserted, updated, db_errors = db.bulk_upsert_chemicals(chemicals, overwrite_existing=True)
        self.refresh_data()

        all_logs = []
        all_logs.append(t("dialog_import_inserted_log", lang, count=inserted))
        all_logs.append(t("dialog_import_updated_log", lang, count=updated))
        if errors:
            all_logs.append(t("dialog_import_parse_warnings", lang))
            all_logs.extend(errors)
        if db_errors:
            all_logs.append(t("dialog_import_db_warnings", lang))
            all_logs.extend(db_errors)

        ExcelReportDialog(
            self,
            title=t("dialog_import_results_title", lang),
            summary_msg=t("dialog_import_summary", lang, inserted=inserted, updated=updated),
            details=all_logs,
            lang=lang,
        )

    def _on_download_template(self):
        """Generate and save the standard blank/sample Excel template."""
        lang = self.current_lang
        filepath = fd.asksaveasfilename(
            title=t("dialog_template_save_title", lang),
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile="chemical_inventory_template.xlsx",
        )
        if not filepath:
            return

        success = generate_sample_excel_file(filepath)
        if success:
            messagebox.showinfo(
                t("dialog_template_created_title", lang),
                t("dialog_template_created_msg", lang, path=filepath),
                parent=self,
            )
        else:
            messagebox.showerror(
                t("dialog_template_error_title", lang),
                t("dialog_template_error_msg", lang),
                parent=self,
            )
