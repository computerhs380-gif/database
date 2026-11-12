import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from database import DatabaseManager
from ui import main_window


class BatchDeleteTests(unittest.TestCase):
    def test_batch_delete_removes_only_requested_chemicals(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = DatabaseManager(Path(temp_dir) / "chemicals.db")
            with manager.get_connection() as conn:
                conn.executemany(
                    "INSERT INTO chemicals (barcode, name) VALUES (?, ?)",
                    [
                        ("BC-1", "Chemical 1"),
                        ("BC-2", "Chemical 2"),
                        ("BC-3", "Chemical 3"),
                        ("BC-4", "Chemical 4"),
                    ],
                )
                conn.commit()
                chemical_ids = [
                    row[0]
                    for row in conn.execute(
                        "SELECT id FROM chemicals ORDER BY id"
                    ).fetchall()
                ]

            success, message = manager.delete_chemicals_batch(
                [chemical_ids[0], chemical_ids[2], chemical_ids[3]]
            )

            self.assertTrue(success, message)
            with manager.get_connection() as conn:
                remaining = conn.execute(
                    "SELECT id FROM chemicals ORDER BY id"
                ).fetchall()
            self.assertEqual([row[0] for row in remaining], [chemical_ids[1]])

    def test_batch_delete_rejects_empty_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = DatabaseManager(Path(temp_dir) / "chemicals.db")

            success, message = manager.delete_chemicals_batch([])

            self.assertFalse(success)
            self.assertIn("No chemical IDs", message)

    @patch.object(main_window.messagebox, "askyesno", return_value=True)
    @patch.object(main_window, "db")
    def test_multiple_selected_rows_are_confirmed_and_deleted_as_a_batch(
        self, mock_db, mock_askyesno
    ):
        refresh_data = Mock()
        window = SimpleNamespace(
            current_lang="en",
            tree=SimpleNamespace(selection=Mock(return_value=("12", "24", "36"))),
            refresh_data=refresh_data,
        )
        mock_db.delete_chemicals_batch.return_value = (True, "Deleted")

        main_window.MainWindow._on_delete_chemical(window)

        mock_askyesno.assert_called_once_with(
            "Confirm Delete",
            "Are you sure you want to delete 3 selected chemicals?",
            icon="warning",
            parent=window,
        )
        mock_db.delete_chemicals_batch.assert_called_once_with([12, 24, 36])
        mock_db.delete_chemical.assert_not_called()
        refresh_data.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
