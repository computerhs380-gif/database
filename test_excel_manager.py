import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from excel_manager import import_chemicals_from_excel


class ExcelImportTests(unittest.TestCase):
    def import_rows(self, rows):
        workbook = Workbook()
        worksheet = workbook.active
        for row in rows:
            worksheet.append(row)

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = Path(temp_dir) / "import.xlsx"
            workbook.save(filepath)
            return import_chemicals_from_excel(filepath)

    def test_finds_header_after_title_rows_and_matches_case_insensitive_aliases(self):
        chemicals, errors = self.import_rows([
            ["Chemical Inventory"],
            [],
            ["Prepared for laboratory use"],
            ["bAr CoDe", "CHEMICAL", "Company", "CAS NUMB", "DEPT", "COLLEGE"],
            ["BC-1", "Acetone", "Acme", "67-64-1", "Chemistry", "Science"],
        ])

        self.assertEqual(errors, [])
        self.assertEqual(len(chemicals), 1)
        self.assertEqual(chemicals[0].barcode, "BC-1")
        self.assertEqual(chemicals[0].name, "Acetone")
        self.assertEqual(chemicals[0].brand, "Acme")
        self.assertEqual(chemicals[0].cas_number, "67-64-1")
        self.assertEqual(chemicals[0].department, "Chemistry")
        self.assertEqual(chemicals[0].college, "Science")

    def test_matches_kurdish_column_aliases(self):
        chemicals, errors = self.import_rows([
            ["بارکۆد", "ناوی ماددە", "مارکە", "کۆدی cas", "بەش", "کۆلێژ"],
            ["BC-2", "ئاسیتۆن", "کۆمپانیا", "67-64-1", "کیمیا", "زانکۆ"],
        ])

        self.assertEqual(errors, [])
        self.assertEqual(len(chemicals), 1)
        self.assertEqual(chemicals[0].barcode, "BC-2")
        self.assertEqual(chemicals[0].name, "ئاسیتۆن")
        self.assertEqual(chemicals[0].brand, "کۆمپانیا")
        self.assertEqual(chemicals[0].cas_number, "67-64-1")
        self.assertEqual(chemicals[0].department, "کیمیا")
        self.assertEqual(chemicals[0].college, "زانکۆ")


if __name__ == "__main__":
    unittest.main()
