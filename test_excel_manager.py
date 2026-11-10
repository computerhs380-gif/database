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

    def test_generates_unique_barcodes_and_strips_imported_text(self):
        chemicals, errors = self.import_rows([
            ["Chemical Name", "Company", "CAS Number", "Location", "Notes"],
            [" Acetone ", " TurkLAB ", " 67-64-1 ", " Lab 1 ", " Keep closed "],
            [" Ethanol ", " himedia ", " 64-17-5 ", " Lab 2 ", " Flammable "],
        ])

        self.assertEqual(errors, [])
        self.assertEqual(len(chemicals), 2)
        self.assertTrue(all(chemical.barcode.startswith("AUTO-") for chemical in chemicals))
        self.assertEqual(len({chemical.barcode for chemical in chemicals}), 2)
        self.assertEqual(chemicals[0].name, "Acetone")
        self.assertEqual(chemicals[0].brand, "TurkLAB")
        self.assertEqual(chemicals[0].cas_number, "67-64-1")
        self.assertEqual(chemicals[0].location, "Lab 1")
        self.assertEqual(chemicals[0].notes, "Keep closed")
        self.assertEqual(chemicals[1].brand, "himedia")
        self.assertEqual(chemicals[1].cas_number, "64-17-5")

    def test_blank_barcode_does_not_skip_row_or_map_company_to_cas(self):
        chemicals, errors = self.import_rows([
            ["Barcode", "Name", "Company"],
            ["", "Sample Chemical 1", " TurkLAB "],
            ["", "Sample Chemical 2", " himedia "],
            ["", "Sample Chemical 3", " EMSURE "],
            ["", "Sample Chemical 4", " liofilchem "],
        ])

        self.assertEqual(errors, [])
        self.assertEqual(len(chemicals), 4)
        self.assertTrue(all(chemical.barcode.startswith("AUTO-") for chemical in chemicals))
        self.assertEqual(len({chemical.barcode for chemical in chemicals}), 4)
        self.assertEqual(
            [chemical.brand for chemical in chemicals],
            ["TurkLAB", "himedia", "EMSURE", "liofilchem"],
        )
        self.assertTrue(all(chemical.cas_number == "" for chemical in chemicals))

    def test_quantity_aliases_parse_numeric_values_and_infer_units(self):
        chemicals, errors = self.import_rows([
            ["Name", "Quanity", "Unit"],
            ["Chemical 1", "250 gram", ""],
            ["Chemical 2", "150 ml", ""],
            ["Chemical 3", "4 pakets", ""],
            ["Chemical 4", "1.5 L", ""],
            ["Chemical 5", "2.75", " bottle "],
        ])

        self.assertEqual(errors, [])
        self.assertEqual(
            [(chemical.remaining_quantity, chemical.units) for chemical in chemicals],
            [
                (250.0, "gram"),
                (150.0, "ml"),
                (4.0, "pakets"),
                (1.5, "L"),
                (2.75, "bottle"),
            ],
        )

    def test_quantity_typos_and_missing_numeric_values_are_safe(self):
        for quantity_header in ("qnty", "amount", "بڕ"):
            with self.subTest(quantity_header=quantity_header):
                chemicals, errors = self.import_rows([
                    ["Name", quantity_header, "Unit"],
                    ["Chemical 1", "no quantity", ""],
                ])

                self.assertEqual(errors, [])
                self.assertEqual(len(chemicals), 1)
                self.assertEqual(chemicals[0].remaining_quantity, 0.0)
                self.assertEqual(chemicals[0].units, "mL")


if __name__ == "__main__":
    unittest.main()
