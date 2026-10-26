import csv
import os
import tempfile
import unittest

from srms.exceptions import DuplicateRecordError, RecordNotFoundError, ValidationError
from srms.manager import RecordManager
from tests.helpers import MemoryRepository, sample_data


class RecordManagerTests(unittest.TestCase):
    def setUp(self):
        self.repo = MemoryRepository()
        self.manager = RecordManager(self.repo)

    def add(self, roll, name, marks, course="MCA"):
        email = f"{roll.lower()}@example.com"
        return self.manager.add_student(
            sample_data(roll_no=roll, name=name, email=email, marks=marks, course=course))

    # ---------- CRUD ----------
    def test_add_student(self):
        student = self.manager.add_student(sample_data())
        self.assertEqual(student.student_id, 1)
        self.assertEqual(len(self.manager.list_students()), 1)

    def test_add_duplicate_roll_number(self):
        self.manager.add_student(sample_data())
        with self.assertRaises(DuplicateRecordError):
            self.manager.add_student(sample_data(email="other@example.com"))

    def test_add_invalid_student_is_not_saved(self):
        with self.assertRaises(ValidationError):
            self.manager.add_student(sample_data(phone="123"))
        self.assertEqual(self.manager.list_students(), [])

    def test_update_student(self):
        self.manager.add_student(sample_data())
        self.manager.update_student(sample_data(name="Aarav Kumar", marks=["100"] * 5))
        saved = self.repo.get_by_roll("MCA-001")
        self.assertEqual(saved.name, "Aarav Kumar")
        self.assertEqual(saved.percentage, 100.0)

    def test_update_missing_student(self):
        with self.assertRaises(RecordNotFoundError):
            self.manager.update_student(sample_data())

    def test_delete_student(self):
        self.manager.add_student(sample_data())
        self.assertTrue(self.manager.delete_student(" mca-001 "))
        self.assertEqual(self.manager.list_students(), [])

    def test_delete_missing_student(self):
        with self.assertRaises(RecordNotFoundError):
            self.manager.delete_student("MCA-404")

    # ---------- search ----------
    def test_search(self):
        self.add("MCA-001", "Aarav Sharma", ["80"] * 5)
        self.add("BCA-001", "Simran Kaur", ["70"] * 5, course="BCA")
        self.assertEqual([s.roll_no for s in self.manager.search_students("simran")], ["BCA-001"])
        self.assertEqual(len(self.manager.search_students("mca")), 1)
        self.assertEqual(self.manager.search_students("zzz"), [])

    def test_blank_search_returns_everyone(self):
        self.add("MCA-001", "Aarav Sharma", ["80"] * 5)
        self.add("MCA-002", "Simran Kaur", ["70"] * 5)
        self.assertEqual(len(self.manager.search_students("   ")), 2)

    # ---------- statistics ----------
    def test_statistics_empty(self):
        self.assertEqual(self.manager.statistics(), {"total": 0})

    def test_statistics(self):
        self.add("MCA-001", "Aarav Sharma", ["90"] * 5)             # 90%  -> A+
        self.add("MCA-002", "Simran Kaur", ["60"] * 5)              # 60%  -> B
        self.add("MCA-003", "Rohan Verma", ["80", "80", "80", "80", "20"])  # 68%  -> F
        stats = self.manager.statistics()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["average"], 72.67)
        self.assertEqual(stats["highest"], ("Aarav Sharma", 90.0))
        self.assertEqual(stats["lowest"], ("Simran Kaur", 60.0))
        self.assertEqual(stats["passed"], 2)
        self.assertEqual(stats["failed"], 1)
        self.assertEqual(stats["pass_percentage"], 66.67)
        self.assertEqual(stats["grade_distribution"]["A+"], 1)
        self.assertEqual(stats["grade_distribution"]["B"], 1)
        self.assertEqual(stats["grade_distribution"]["F"], 1)
        self.assertEqual(stats["subject_averages"]["Python"], 76.67)

    # ---------- export ----------
    def test_export_csv(self):
        self.add("MCA-001", "Aarav Sharma", ["90"] * 5)
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "students.csv")
            self.assertEqual(self.manager.export_csv(path), 1)
            with open(path, newline="", encoding="utf-8") as handle:
                rows = list(csv.reader(handle))
        self.assertEqual(rows[0][:3], ["Roll No", "Name", "Email"])
        self.assertEqual(rows[1][0], "MCA-001")
        self.assertEqual(rows[1][-2:], ["A+", "Pass"])


if __name__ == "__main__":
    unittest.main()
