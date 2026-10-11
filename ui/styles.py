"""
Design tokens, theme configuration, and style helpers for CIMS.
"""

import tkinter.ttk as ttk
import customtkinter as ctk

# Color Palette (Tailored modern laboratory UI)
COLORS = {
    "dark": {
        "bg_primary": "#0F172A",      # Slate 900
        "bg_secondary": "#1E293B",    # Slate 800
        "bg_tertiary": "#334155",     # Slate 700
        "card_bg": "#1E293B",
        "border": "#334155",
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
        "text_muted": "#64748B",
        "accent": "#3B82F6",          # Blue 500
        "accent_hover": "#2563EB",    # Blue 600
        "success": "#10B981",         # Emerald 500
        "success_bg": "#064E3B",
        "warning": "#F59E0B",         # Amber 500
        "warning_bg": "#451A03",
        "danger": "#EF4444",          # Red 500
        "danger_bg": "#450A0A",
        "orange": "#F97316",          # Orange 500
        "purple": "#8B5CF6",          # Purple 500
        "tree_bg": "#1E293B",
        "tree_fg": "#F8FAFC",
        "tree_select_bg": "#3B82F6",
        "tree_select_fg": "#FFFFFF",
        "tree_header_bg": "#0F172A",
        "tree_header_fg": "#94A3B8",
    },
    "light": {
        "bg_primary": "#F8FAFC",      # Slate 50
        "bg_secondary": "#FFFFFF",    # White
        "bg_tertiary": "#F1F5F9",     # Slate 100
        "card_bg": "#FFFFFF",
        "border": "#CBD5E1",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "text_muted": "#94A3B8",
        "accent": "#2563EB",          # Blue 600
        "accent_hover": "#1D4ED8",    # Blue 700
        "success": "#059669",
        "success_bg": "#D1FAE5",
        "warning": "#D97706",
        "warning_bg": "#FEF3C7",
        "danger": "#DC2626",
        "danger_bg": "#FEE2E2",
        "orange": "#EA580C",
        "purple": "#7C3AED",
        "tree_bg": "#FFFFFF",
        "tree_fg": "#0F172A",
        "tree_select_bg": "#2563EB",
        "tree_select_fg": "#FFFFFF",
        "tree_header_bg": "#E2E8F0",
        "tree_header_fg": "#334155",
    },
}

FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "subtitle": ("Segoe UI", 12),
    "heading": ("Segoe UI", 14, "bold"),
    "subheading": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 11),
    "body_bold": ("Segoe UI", 11, "bold"),
    "caption": ("Segoe UI", 10),
    "code": ("Consolas", 11),
    "stat_num": ("Segoe UI", 22, "bold"),
    "stat_label": ("Segoe UI", 11, "bold"),
}


def configure_treeview_style(mode: str = "dark"):
    """Configures modern styling for the ttk.Treeview table widget to match CustomTkinter."""
    palette = COLORS.get(mode, COLORS["dark"])
    style = ttk.Style()
    style.theme_use("clam")

    # Main Treeview appearance
    style.configure(
        "Modern.Treeview",
        background=palette["tree_bg"],
        foreground=palette["tree_fg"],
        fieldbackground=palette["tree_bg"],
        borderwidth=0,
        font=FONTS["body"],
        rowheight=32,
    )

    style.map(
        "Modern.Treeview",
        background=[("selected", palette["tree_select_bg"])],
        foreground=[("selected", palette["tree_select_fg"])],
    )

    # Heading / Column header styling
    style.configure(
        "Modern.Treeview.Heading",
        background=palette["tree_header_bg"],
        foreground=palette["tree_header_fg"],
        font=FONTS["subheading"],
        borderwidth=1,
        relief="flat",
        padding=(8, 8),
    )

    style.map(
        "Modern.Treeview.Heading",
        background=[("active", palette["bg_tertiary"])],
        foreground=[("active", palette["text_primary"])],
    )
