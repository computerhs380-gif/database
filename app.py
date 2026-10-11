"""
Chemical Inventory Management System (CIMS)
Entry point for launching the desktop application.
"""

import sys
import ctypes

# Ensure Windows terminal handles UTF-8 properly for Kurdish text
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from ui.main_window import MainWindow



def setup_windows_app_id():
    """Ensure Windows taskbar icon and group are properly associated."""
    try:
        myappid = "university.lab.chemical_inventory_system.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass


def main():
    setup_windows_app_id()
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
