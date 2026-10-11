"""
Excel Import / Export Results Dialog Modal.
Shows detailed summary of imported records, duplicates handled, and errors.
Supports Kurdish and English localization with RTL alignment.
"""

from typing import List, Optional
import customtkinter as ctk
from ui.styles import FONTS
from locales import t, is_rtl, LANG_EN


class ExcelReportDialog(ctk.CTkToplevel):
    def __init__(
        self,
        parent,
        title: str,
        summary_msg: str,
        details: Optional[List[str]] = None,
        lang: Optional[str] = None,
    ):
        super().__init__(parent)
        self.lang = lang or getattr(parent, "current_lang", LANG_EN)
        rtl = is_rtl(self.lang)
        text_anchor = "e" if rtl else "w"

        self.title(title)
        self.geometry("620x460")
        self.transient(parent)
        self.grab_set()

        # Center on parent window
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() - 620) // 2
            y = parent.winfo_y() + (parent.winfo_height() - 460) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        # Content container
        frame = ctk.CTkFrame(self, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        lbl_title = ctk.CTkLabel(frame, text=title, font=FONTS["title"], anchor=text_anchor)
        lbl_title.pack(fill="x", pady=(0, 6))

        is_success = any(w in summary_msg.lower() for w in ["success", "completed", "سەرکەوتوو", "تەواوبوو"])
        lbl_summary = ctk.CTkLabel(
            frame,
            text=summary_msg,
            font=FONTS["body_bold"],
            text_color="#10B981" if is_success else "#F59E0B",
            anchor=text_anchor,
            wraplength=560,
        )
        lbl_summary.pack(fill="x", pady=(0, 12))

        if details:
            log_title = t("excel_dlg_log_title", self.lang)
            lbl_det_title = ctk.CTkLabel(frame, text=log_title, font=FONTS["subheading"], anchor=text_anchor)
            lbl_det_title.pack(fill="x", pady=(0, 4))

            txt_box = ctk.CTkTextbox(frame, height=220, font=FONTS["code"])
            txt_box.pack(fill="both", expand=True, pady=(0, 15))
            txt_box.insert("0.0", "\n".join(details))
            txt_box.configure(state="disabled")

        btn_close_text = t("excel_dlg_close", self.lang)
        btn_ok = ctk.CTkButton(
            frame,
            text=btn_close_text,
            width=120,
            height=36,
            font=FONTS["body_bold"],
            command=self.destroy,
        )
        btn_ok.pack(side="left" if rtl else "right")
