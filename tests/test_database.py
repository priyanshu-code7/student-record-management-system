"""Integration tests against a real MySQL server.

Skipped by default. To run them, start MySQL, fill in .env and use:
    Windows (PowerShell):  $env:RUN_DB_TESTS="1"; python -m unittest discover -s tests -t . -v
    Linux / macOS:         RUN_DB_TESTS=1 python -m unittest discover -s tests -t . -v
A separate database named student_records_test is created and used.
"""

import os
import unittest

from srms.database import DatabaseManager, load_config
from srms.exceptions import DuplicateRecordError
from srms.models import Student
from tests.helpers import sample_data


@unittest.skipUnless(os.getenv("RUN_DB_TESTS") == "1", "set RUN_DB_TESTS=1 to run MySQL tests")
class DatabaseManagerTests(unittest.TestCase):
    def setUp(self):
        config = load_config()
        config["database"] = "student_records_test"
        self.db = DatabaseManager(config)
        self.db.connect()
        self.db._execute("DELETE FROM students")

    def tearDown(self):
        self.db.close()

    def test_add_get_update_delete(self):
        student = Student(**sample_data())
        self.assertGreater(self.db.add(student), 0)

        loaded = self.db.get_by_roll("MCA-001")
        self.assertEqual(loaded.name, "Aarav Sharma")
        self.assertEqual(loaded.marks, [90.0, 80.0, 70.0, 60.0, 50.0])

        changed = Student(**sample_data(name="Aarav Kumar"))
        self.db.update(changed)
        self.assertEqual(self.db.get_by_roll("MCA-001").name, "Aarav Kumar")

        self.assertTrue(self.db.delete("MCA-001"))
        self.assertIsNone(self.db.get_by_roll("MCA-001"))

    def test_duplicate_roll_number(self):
        self.db.add(Student(**sample_data()))
        with self.assertRaises(DuplicateRecordError):
            self.db.add(Student(**sample_data(email="different@example.com")))

    def test_search(self):
        self.db.add(Student(**sample_data()))
        self.assertEqual(len(self.db.search("aarav")), 1)
        self.assertEqual(self.db.search("nobody"), [])


if __name__ == "__main__":
    unittest.main()
