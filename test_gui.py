"""
Automated GUI smoke test: instantiates MainWindow and ChemicalDialog, checks rendering without crash.
"""

from ui.main_window import MainWindow
from ui.chemical_dialog import ChemicalDialog
from database import db

def test_gui_render():
    print("Testing GUI components...")
    app = MainWindow()
    app.update()
    print("  MainWindow rendered successfully!")

    # Test opening ChemicalDialog
    dlg = ChemicalDialog(app)
    dlg.update()
    print("  ChemicalDialog (Add mode) rendered successfully!")
    dlg.destroy()

    # Test opening ChemicalDialog in Edit mode
    first_chem = db.get_all_chemicals()[0]
    dlg_edit = ChemicalDialog(app, chemical=first_chem)
    dlg_edit.update()
    print(f"  ChemicalDialog (Edit mode for '{first_chem.name}') rendered successfully!")
    dlg_edit.destroy()

    app.destroy()
    print("GUI smoke test passed with 100% success!")

if __name__ == "__main__":
    test_gui_render()
