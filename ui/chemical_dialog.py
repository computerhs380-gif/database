"""
Add and Edit Chemical Dialog Modal Window.
Provides an organized, user-friendly form with validation, quick shortcuts,
full Kurdish (Sorani) and English localization, and adaptive RTL layout.
"""

import random
import string
import webbrowser
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Callable
import tkinter.filedialog as fd

import customtkinter as ctk

from models import Chemical, HAZARD_GROUPS
from config import UNITS
from ui.styles import FONTS
from locales import (
    t,
    is_rtl,
    LANG_EN,
    get_department_options,
    canonical_department,
    display_department,
    get_storage_group_options,
    canonical_storage_group,
    display_storage_group,
    get_physical_state_options,
    canonical_physical_state,
    display_physical_state,
)


class ChemicalDialog(ctk.CTkToplevel):
    def __init__(
        self,
        parent,
        chemical: Optional[Chemical] = None,
        on_save_callback: Optional[Callable[[Chemical], bool]] = None,
        lang: Optional[str] = None,
    ):
        super().__init__(parent)

        self.parent = parent
        self.chemical = chemical
        self.is_edit_mode = chemical is not None
        self.on_save_callback = on_save_callback
        self.lang = lang or getattr(parent, "current_lang", LANG_EN)
        self.rtl = is_rtl(self.lang)

        # Window Setup
        window_title = t("form_edit_title" if self.is_edit_mode else "form_add_title", self.lang)
        self.title(window_title)
        self.geometry("840x780")
        self.minsize(780, 680)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent window
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() - 840) // 2
            y = parent.winfo_y() + (parent.winfo_height() - 780) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        self._build_ui()
        if self.is_edit_mode:
            self._populate_fields()

    def _build_ui(self):
        text_anchor = "e" if self.rtl else "w"
        label_side = "right" if self.rtl else "left"
        input_side = "right" if self.rtl else "left"
        button_side = "left" if self.rtl else "right"

        # Main scrollable canvas container
        self.scroll_frame = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        # Title header
        title_key = "form_edit_heading" if self.is_edit_mode else "form_add_heading"
        title_text = t(title_key, self.lang)
        subtitle_text = t("form_subtitle", self.lang)

        lbl_title = ctk.CTkLabel(self.scroll_frame, text=title_text, font=FONTS["title"], anchor=text_anchor)
        lbl_title.pack(fill="x", pady=(0, 2))

        lbl_sub = ctk.CTkLabel(
            self.scroll_frame,
            text=subtitle_text,
            font=FONTS["subtitle"],
            text_color="gray",
            anchor=text_anchor,
        )
        lbl_sub.pack(fill="x", pady=(0, 16))

        # Error notification banner
        self.error_label = ctk.CTkLabel(
            self.scroll_frame,
            text="",
            font=FONTS["body_bold"],
            text_color="#EF4444",
            anchor=text_anchor,
        )
        self.error_label.pack(fill="x", pady=(0, 6))

        # --- SECTION 1: IDENTIFICATION ---
        sec1 = self._create_section(self.scroll_frame, t("form_sec1_title", self.lang))

        # Barcode Row
        f_barcode = ctk.CTkFrame(sec1, fg_color="transparent")
        f_barcode.pack(fill="x", pady=4)

        lbl_b = ctk.CTkLabel(f_barcode, text=t("form_barcode", self.lang), width=160, anchor=text_anchor, font=FONTS["body_bold"])
        lbl_b.pack(side=label_side, padx=(6, 0) if self.rtl else (0, 6))

        self.entry_barcode = ctk.CTkEntry(
            f_barcode,
            placeholder_text=t("form_barcode_placeholder", self.lang),
            font=FONTS["body"],
        )

        btn_gen_barcode = ctk.CTkButton(
            f_barcode,
            text=t("form_btn_gen_barcode", self.lang),
            width=120,
            command=self._generate_random_barcode,
            fg_color="#475569",
            hover_color="#334155",
            font=FONTS["body"],
        )

        if self.rtl:
            btn_gen_barcode.pack(side="left")
            self.entry_barcode.pack(side="right", fill="x", expand=True, padx=(8, 8))
        else:
            self.entry_barcode.pack(side="left", fill="x", expand=True, padx=(0, 10))
            btn_gen_barcode.pack(side="left")

        # Name Row
        f_name = ctk.CTkFrame(sec1, fg_color="transparent")
        f_name.pack(fill="x", pady=4)
        lbl_n = ctk.CTkLabel(f_name, text=t("form_name", self.lang), width=160, anchor=text_anchor, font=FONTS["body_bold"])
        lbl_n.pack(side=label_side, padx=(6, 0) if self.rtl else (0, 6))

        self.entry_name = ctk.CTkEntry(
            f_name,
            placeholder_text=t("form_name_placeholder", self.lang),
            font=FONTS["body"],
        )
        self.entry_name.pack(side=input_side, fill="x", expand=True)

        # CAS Number & Department Row
        f_cas_dept = ctk.CTkFrame(sec1, fg_color="transparent")
        f_cas_dept.pack(fill="x", pady=4)

        if self.rtl:
            # Department first (on right), then CAS on left
            lbl_dept = ctk.CTkLabel(f_cas_dept, text=t("form_department", self.lang), width=120, anchor="e", font=FONTS["body_bold"])
            lbl_dept.pack(side="right", padx=(6, 0))
            dept_choices = get_department_options(self.lang, include_all=False)
            self.opt_department = ctk.CTkOptionMenu(f_cas_dept, values=dept_choices, font=FONTS["body"], width=170)
            self.opt_department.pack(side="right", padx=(0, 15))

            lbl_cas = ctk.CTkLabel(f_cas_dept, text=t("form_cas", self.lang), width=100, anchor="e", font=FONTS["body"])
            lbl_cas.pack(side="right", padx=(6, 0))
            self.entry_cas = ctk.CTkEntry(f_cas_dept, placeholder_text=t("form_cas_placeholder", self.lang), width=170, font=FONTS["body"])
            self.entry_cas.pack(side="right", fill="x", expand=True)
        else:
            lbl_cas = ctk.CTkLabel(f_cas_dept, text=t("form_cas", self.lang), width=160, anchor="w", font=FONTS["body"])
            lbl_cas.pack(side="left", padx=(0, 6))
            self.entry_cas = ctk.CTkEntry(f_cas_dept, placeholder_text=t("form_cas_placeholder", self.lang), width=200, font=FONTS["body"])
            self.entry_cas.pack(side="left", padx=(0, 20))

            lbl_dept = ctk.CTkLabel(f_cas_dept, text=t("form_department", self.lang), width=110, anchor="w", font=FONTS["body_bold"])
            lbl_dept.pack(side="left", padx=(0, 6))
            dept_choices = get_department_options(self.lang, include_all=False)
            self.opt_department = ctk.CTkOptionMenu(f_cas_dept, values=dept_choices, font=FONTS["body"])
            self.opt_department.pack(side="left", fill="x", expand=True)

        # --- SECTION 2: STORAGE & CONTAINER ---
        sec2 = self._create_section(self.scroll_frame, t("form_sec2_title", self.lang))

        # Location Row
        f_loc = ctk.CTkFrame(sec2, fg_color="transparent")
        f_loc.pack(fill="x", pady=4)
        lbl_loc = ctk.CTkLabel(f_loc, text=t("form_location", self.lang), width=160, anchor=text_anchor, font=FONTS["body"])
        lbl_loc.pack(side=label_side, padx=(6, 0) if self.rtl else (0, 6))
        self.entry_location = ctk.CTkEntry(f_loc, placeholder_text=t("form_location_placeholder", self.lang), font=FONTS["body"])
        self.entry_location.pack(side=input_side, fill="x", expand=True)

        # Storage Group & Physical State Row
        f_grp_state = ctk.CTkFrame(sec2, fg_color="transparent")
        f_grp_state.pack(fill="x", pady=4)

        storage_group_choices = get_storage_group_options(self.lang)
        state_choices = get_physical_state_options(self.lang)

        if self.rtl:
            lbl_grp = ctk.CTkLabel(f_grp_state, text=t("form_storage_group", self.lang), width=140, anchor="e", font=FONTS["body"])
            lbl_grp.pack(side="right", padx=(6, 0))
            self.opt_storage_group = ctk.CTkOptionMenu(f_grp_state, values=storage_group_choices, width=200, font=FONTS["body"])
            self.opt_storage_group.pack(side="right", padx=(0, 15))

            lbl_st = ctk.CTkLabel(f_grp_state, text=t("form_physical_state", self.lang), width=110, anchor="e", font=FONTS["body"])
            lbl_st.pack(side="right", padx=(6, 0))
            self.opt_state = ctk.CTkOptionMenu(f_grp_state, values=state_choices, font=FONTS["body"])
            self.opt_state.pack(side="right", fill="x", expand=True)
        else:
            lbl_grp = ctk.CTkLabel(f_grp_state, text=t("form_storage_group", self.lang), width=160, anchor="w", font=FONTS["body"])
            lbl_grp.pack(side="left", padx=(0, 6))
            self.opt_storage_group = ctk.CTkOptionMenu(f_grp_state, values=storage_group_choices, width=220, font=FONTS["body"])
            self.opt_storage_group.pack(side="left", padx=(0, 20))

            lbl_st = ctk.CTkLabel(f_grp_state, text=t("form_physical_state", self.lang), width=110, anchor="w", font=FONTS["body"])
            lbl_st.pack(side="left", padx=(0, 6))
            self.opt_state = ctk.CTkOptionMenu(f_grp_state, values=state_choices, font=FONTS["body"])
            self.opt_state.pack(side="left", fill="x", expand=True)

        # Container Size Row
        f_size = ctk.CTkFrame(sec2, fg_color="transparent")
        f_size.pack(fill="x", pady=4)
        lbl_cs = ctk.CTkLabel(f_size, text=t("form_container_size", self.lang), width=160, anchor=text_anchor, font=FONTS["body"])
        lbl_cs.pack(side=label_side, padx=(6, 0) if self.rtl else (0, 6))
        self.entry_container_size = ctk.CTkEntry(f_size, placeholder_text=t("form_container_size_placeholder", self.lang), font=FONTS["body"])
        self.entry_container_size.pack(side=input_side, fill="x", expand=True)

        # --- SECTION 3: QUANTITY & DATES ---
        sec3 = self._create_section(self.scroll_frame, t("form_sec3_title", self.lang))

        # Remaining Quantity & Units
        f_qty = ctk.CTkFrame(sec3, fg_color="transparent")
        f_qty.pack(fill="x", pady=4)

        if self.rtl:
            lbl_qty = ctk.CTkLabel(f_qty, text=t("form_remaining_qty", self.lang), width=140, anchor="e", font=FONTS["body_bold"])
            lbl_qty.pack(side="right", padx=(6, 0))
            self.entry_qty = ctk.CTkEntry(f_qty, placeholder_text=t("form_remaining_qty_placeholder", self.lang), width=180, font=FONTS["body"])
            self.entry_qty.pack(side="right", padx=(0, 15))

            lbl_u = ctk.CTkLabel(f_qty, text=t("form_units", self.lang), width=120, anchor="e", font=FONTS["body"])
            lbl_u.pack(side="right", padx=(6, 0))
            self.opt_units = ctk.CTkOptionMenu(f_qty, values=UNITS, width=120, font=FONTS["body"])
            self.opt_units.pack(side="right")
        else:
            lbl_qty = ctk.CTkLabel(f_qty, text=t("form_remaining_qty", self.lang), width=160, anchor="w", font=FONTS["body_bold"])
            lbl_qty.pack(side="left", padx=(0, 6))
            self.entry_qty = ctk.CTkEntry(f_qty, placeholder_text=t("form_remaining_qty_placeholder", self.lang), width=200, font=FONTS["body"])
            self.entry_qty.pack(side="left", padx=(0, 20))

            lbl_u = ctk.CTkLabel(f_qty, text=t("form_units", self.lang), width=130, anchor="w", font=FONTS["body"])
            lbl_u.pack(side="left", padx=(0, 6))
            self.opt_units = ctk.CTkOptionMenu(f_qty, values=UNITS, width=120, font=FONTS["body"])
            self.opt_units.pack(side="left")

        # Date In Row
        f_date_in = ctk.CTkFrame(sec3, fg_color="transparent")
        f_date_in.pack(fill="x", pady=4)

        lbl_di = ctk.CTkLabel(f_date_in, text=t("form_date_in", self.lang), width=160, anchor=text_anchor, font=FONTS["body"])
        lbl_di.pack(side=label_side, padx=(6, 0) if self.rtl else (0, 6))

        self.entry_date_in = ctk.CTkEntry(f_date_in, placeholder_text="YYYY-MM-DD", width=200, font=FONTS["body"])
        self.entry_date_in.pack(side=input_side, padx=(0, 10) if not self.rtl else (10, 0))

        btn_today_in = ctk.CTkButton(
            f_date_in,
            text=t("form_btn_today", self.lang),
            width=80,
            command=self._set_date_in_today,
            fg_color="#334155",
            hover_color="#1E293B",
            font=FONTS["body"],
        )
        btn_today_in.pack(side=input_side)

        # Expiration Date Row
        f_exp_date = ctk.CTkFrame(sec3, fg_color="transparent")
        f_exp_date.pack(fill="x", pady=4)

        lbl_ed = ctk.CTkLabel(f_exp_date, text=t("form_exp_date", self.lang), width=160, anchor=text_anchor, font=FONTS["body"])
        lbl_ed.pack(side=label_side, padx=(6, 0) if self.rtl else (0, 6))

        self.entry_exp_date = ctk.CTkEntry(f_exp_date, placeholder_text="YYYY-MM-DD", width=200, font=FONTS["body"])
        self.entry_exp_date.pack(side=input_side, padx=(0, 10) if not self.rtl else (10, 0))

        btn_exp_1y = ctk.CTkButton(
            f_exp_date,
            text=t("form_btn_exp_1y", self.lang),
            width=75,
            command=lambda: self._add_years_expiry(1),
            fg_color="#334155",
            hover_color="#1E293B",
            font=FONTS["body"],
        )
        btn_exp_1y.pack(side=input_side, padx=(0, 6) if not self.rtl else (6, 0))

        btn_exp_2y = ctk.CTkButton(
            f_exp_date,
            text=t("form_btn_exp_2y", self.lang),
            width=75,
            command=lambda: self._add_years_expiry(2),
            fg_color="#334155",
            hover_color="#1E293B",
            font=FONTS["body"],
        )
        btn_exp_2y.pack(side=input_side, padx=(0, 6) if not self.rtl else (6, 0))

        btn_clear_exp = ctk.CTkButton(
            f_exp_date,
            text=t("form_btn_no_exp", self.lang),
            width=90,
            command=lambda: self.entry_exp_date.delete(0, "end"),
            fg_color="#334155",
            hover_color="#1E293B",
            font=FONTS["body"],
        )
        btn_clear_exp.pack(side=input_side)

        # --- SECTION 4: SAFETY, HAZARDS & NOTES ---
        sec4 = self._create_section(self.scroll_frame, t("form_sec4_title", self.lang))

        # Color-coded detailed hazard classifications
        f_haz = ctk.CTkFrame(sec4, fg_color="transparent")
        f_haz.pack(fill="x", pady=6)

        lbl_hf = ctk.CTkLabel(
            f_haz,
            text=t("form_hazard_flags", self.lang),
            anchor=text_anchor,
            font=FONTS["body_bold"],
        )
        lbl_hf.pack(fill="x", pady=(0, 6))

        hazard_cards = ctk.CTkFrame(f_haz, fg_color="transparent")
        hazard_cards.pack(fill="x")
        self.hazard_checkboxes = {}
        groups = [
            ("security", "#EF4444"),
            ("health", "#3B82F6"),
            ("physical", "#F59E0B"),
        ]
        if self.rtl:
            groups.reverse()
        for column, (group, color) in enumerate(groups):
            card = ctk.CTkFrame(hazard_cards, border_width=1, border_color=color, corner_radius=8)
            card.grid(row=0, column=column, sticky="nsew", padx=4)
            hazard_cards.grid_columnconfigure(column, weight=1, uniform="hazard_cards")
            heading = ctk.CTkLabel(
                card,
                text=t(f"form_hazard_{group}", self.lang),
                font=FONTS["body_bold"],
                text_color=color,
                anchor=text_anchor,
            )
            heading.pack(fill="x", padx=10, pady=(8, 4))
            for hazard_id in HAZARD_GROUPS[group]:
                checkbox = ctk.CTkCheckBox(
                    card,
                    text=t(f"hazard_label_{hazard_id}", self.lang),
                    font=FONTS["caption"],
                    checkbox_height=18,
                    checkbox_width=18,
                    fg_color=color,
                    hover_color=color,
                )
                checkbox.pack(fill="x", padx=10, pady=3)
                self.hazard_checkboxes[hazard_id] = checkbox

        # MSDS Row
        f_msds = ctk.CTkFrame(sec4, fg_color="transparent")
        f_msds.pack(fill="x", pady=4)

        lbl_ms = ctk.CTkLabel(f_msds, text=t("form_msds", self.lang), width=160, anchor=text_anchor, font=FONTS["body"])
        lbl_ms.pack(side=label_side, padx=(6, 0) if self.rtl else (0, 6))

        self.entry_msds = ctk.CTkEntry(
            f_msds,
            placeholder_text=t("form_msds_placeholder", self.lang),
            font=FONTS["body"],
        )

        btn_browse_msds = ctk.CTkButton(
            f_msds,
            text=t("form_btn_browse_msds", self.lang),
            width=110,
            command=self._browse_msds_file,
            fg_color="#334155",
            hover_color="#1E293B",
            font=FONTS["body"],
        )

        btn_open_msds = ctk.CTkButton(
            f_msds,
            text=t("form_btn_open_msds", self.lang),
            width=70,
            command=self._open_msds,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=FONTS["body"],
        )

        if self.rtl:
            btn_open_msds.pack(side="left")
            btn_browse_msds.pack(side="left", padx=(0, 6))
            self.entry_msds.pack(side="right", fill="x", expand=True, padx=(8, 8))
        else:
            self.entry_msds.pack(side="left", fill="x", expand=True, padx=(0, 8))
            btn_browse_msds.pack(side="left", padx=(0, 6))
            btn_open_msds.pack(side="left")

        # Notes Row
        f_notes = ctk.CTkFrame(sec4, fg_color="transparent")
        f_notes.pack(fill="x", pady=6)
        lbl_nt = ctk.CTkLabel(f_notes, text=t("form_notes", self.lang), width=160, anchor="ne" if self.rtl else "nw", font=FONTS["body"])
        lbl_nt.pack(side=label_side, padx=(6, 0) if self.rtl else (0, 6))
        self.txt_notes = ctk.CTkTextbox(f_notes, height=70, font=FONTS["body"])
        self.txt_notes.pack(side=input_side, fill="x", expand=True)

        # --- FOOTER BUTTON BAR ---
        f_footer = ctk.CTkFrame(self, fg_color="transparent")
        f_footer.pack(fill="x", padx=20, pady=(5, 15))

        btn_cancel_text = t("form_btn_cancel", self.lang)
        btn_save_key = "form_btn_save_changes" if self.is_edit_mode else "form_btn_save_add"
        btn_save_text = t(btn_save_key, self.lang)

        btn_cancel = ctk.CTkButton(
            f_footer,
            text=btn_cancel_text,
            width=120,
            height=38,
            font=FONTS["body_bold"],
            fg_color="#475569",
            hover_color="#334155",
            command=self.destroy,
        )

        btn_save = ctk.CTkButton(
            f_footer,
            text=btn_save_text,
            width=180,
            height=38,
            font=FONTS["body_bold"],
            fg_color="#10B981" if self.is_edit_mode else "#2563EB",
            hover_color="#059669" if self.is_edit_mode else "#1D4ED8",
            command=self._on_save,
        )

        if self.rtl:
            # In RTL, action button on left, cancel next to it
            btn_save.pack(side="left")
            btn_cancel.pack(side="left", padx=(10, 0))
        else:
            btn_cancel.pack(side="right", padx=(10, 0))
            btn_save.pack(side="right")

    def _create_section(self, parent, title: str) -> ctk.CTkFrame:
        """Helper to create a visually distinct card-style section frame."""
        text_anchor = "e" if self.rtl else "w"
        frame = ctk.CTkFrame(parent, corner_radius=8)
        frame.pack(fill="x", pady=8, padx=2)

        lbl = ctk.CTkLabel(frame, text=title, font=FONTS["heading"], anchor=text_anchor)
        lbl.pack(fill="x", padx=16, pady=(12, 8))

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=(0, 12))
        return inner

    def _generate_random_barcode(self):
        """Generates a unique barcode in standard format CHEM-XXXXX."""
        code = "CHEM-" + "".join(random.choices(string.digits, k=5))
        self.entry_barcode.delete(0, "end")
        self.entry_barcode.insert(0, code)

    def _set_date_in_today(self):
        self.entry_date_in.delete(0, "end")
        self.entry_date_in.insert(0, date.today().strftime("%Y-%m-%d"))

    def _add_years_expiry(self, years: int):
        target = date.today() + timedelta(days=365 * years)
        self.entry_exp_date.delete(0, "end")
        self.entry_exp_date.insert(0, target.strftime("%Y-%m-%d"))

    def _browse_msds_file(self):
        filepath = fd.askopenfilename(
            title=t("form_msds", self.lang),
            filetypes=[("PDF Documents", "*.pdf"), ("All Files", "*.*")],
        )
        if filepath:
            self.entry_msds.delete(0, "end")
            self.entry_msds.insert(0, filepath)

    def _open_msds(self):
        link = self.entry_msds.get().strip()
        if not link:
            self.error_label.configure(text=t("val_msds_empty", self.lang))
            return
        try:
            webbrowser.open(link)
        except Exception as e:
            self.error_label.configure(text=t("val_msds_open_error", self.lang, error=str(e)))

    def _populate_fields(self):
        """Populates the form when editing an existing chemical record."""
        c = self.chemical
        if not c:
            return

        self.entry_barcode.insert(0, c.barcode or "")
        self.entry_name.insert(0, c.name or "")
        self.entry_cas.insert(0, c.cas_number or "")
        self.entry_location.insert(0, c.location or "")
        self.entry_date_in.insert(0, c.date_in or "")
        self.entry_exp_date.insert(0, c.expiration_date or "")
        self.entry_container_size.insert(0, c.container_size or "")
        self.entry_qty.insert(0, str(c.remaining_quantity))
        self.entry_msds.insert(0, c.msds or "")
        self.txt_notes.insert("0.0", c.notes or "")

        # Map canonical DB values to display values for dropdowns
        disp_dept = display_department(c.department, self.lang)
        self.opt_department.set(disp_dept)

        disp_grp = display_storage_group(c.storage_group, self.lang)
        self.opt_storage_group.set(disp_grp)

        disp_state = display_physical_state(c.state, self.lang)
        self.opt_state.set(disp_state)

        if c.units in UNITS:
            self.opt_units.set(c.units)

        for hazard_id in c.get_hazard_tags():
            checkbox = self.hazard_checkboxes.get(hazard_id)
            if checkbox:
                checkbox.select()

    def _validate_form(self) -> Optional[Chemical]:
        """Validates input fields and constructs a Chemical object."""
        barcode = self.entry_barcode.get().strip()
        name = self.entry_name.get().strip()

        if not barcode:
            self.error_label.configure(text=t("val_barcode_empty", self.lang))
            self.entry_barcode.focus()
            return None

        if not name:
            self.error_label.configure(text=t("val_name_empty", self.lang))
            self.entry_name.focus()
            return None

        raw_qty = self.entry_qty.get().strip()
        try:
            qty = float(raw_qty) if raw_qty else 0.0
            if qty < 0:
                self.error_label.configure(text=t("val_qty_negative", self.lang))
                return None
        except ValueError:
            self.error_label.configure(text=t("val_qty_invalid", self.lang))
            self.entry_qty.focus()
            return None

        # Expiry date validation
        exp_date = self.entry_exp_date.get().strip()
        if exp_date:
            try:
                date.fromisoformat(exp_date)
            except ValueError:
                self.error_label.configure(text=t("val_exp_format", self.lang))
                self.entry_exp_date.focus()
                return None

        # Date In validation
        date_in = self.entry_date_in.get().strip()
        if date_in:
            try:
                date.fromisoformat(date_in)
            except ValueError:
                self.error_label.configure(text=t("val_date_in_format", self.lang))
                self.entry_date_in.focus()
                return None

        chem_id = self.chemical.id if self.chemical else None

        # Convert localized dropdown choices back to canonical DB values
        canonical_dept = canonical_department(self.opt_department.get(), self.lang)
        canonical_grp = canonical_storage_group(self.opt_storage_group.get(), self.lang)
        canonical_st = canonical_physical_state(self.opt_state.get(), self.lang)

        selected_hazards = [
            hazard_id for hazard_id, checkbox in self.hazard_checkboxes.items()
            if checkbox.get()
        ]
        return Chemical(
            id=chem_id,
            barcode=barcode,
            name=name,
            cas_number=self.entry_cas.get().strip(),
            location=self.entry_location.get().strip(),
            date_in=date_in,
            expiration_date=exp_date,
            storage_group=canonical_grp,
            container_size=self.entry_container_size.get().strip(),
            remaining_quantity=qty,
            units=self.opt_units.get(),
            state=canonical_st,
            msds=self.entry_msds.get().strip(),
            department=canonical_dept,
            hazard_security=any(tag in HAZARD_GROUPS["security"] for tag in selected_hazards),
            hazard_health=any(tag in HAZARD_GROUPS["health"] for tag in selected_hazards),
            hazard_physical=any(tag in HAZARD_GROUPS["physical"] for tag in selected_hazards),
            hazard_tags=selected_hazards,
            notes=self.txt_notes.get("0.0", "end").strip(),
        )

    def _on_save(self):
        chem = self._validate_form()
        if not chem:
            return

        if self.on_save_callback:
            success = self.on_save_callback(chem)
            if success:
                self.destroy()
        else:
            self.destroy()
