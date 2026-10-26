import unittest

from srms.exceptions import ValidationError
from srms.models import Student
from tests.helpers import sample_data


def make(**overrides):
    return Student(**sample_data(**overrides))


class StudentCalculationTests(unittest.TestCase):
    def test_total_and_percentage(self):
        student = make()
        self.assertEqual(student.total, 350.0)
        self.assertEqual(student.percentage, 70.0)

    def test_normalises_input(self):
        student = make(roll_no="  mca-009 ", name="  Aarav   Sharma ", email=" AARAV@Example.COM ")
        self.assertEqual(student.roll_no, "MCA-009")
        self.assertEqual(student.name, "Aarav Sharma")
        self.assertEqual(student.email, "aarav@example.com")

    def test_grade_boundaries(self):
        cases = {"95": "A+", "90": "A+", "85": "A", "75": "B+", "65": "B", "55": "C", "45": "D"}
        for mark, grade in cases.items():
            with self.subTest(mark=mark):
                self.assertEqual(make(marks=[mark] * 5).grade, grade)

    def test_failing_one_subject_fails_overall(self):
        student = make(marks=["95", "95", "95", "95", "39"])
        self.assertFalse(student.passed)
        self.assertEqual(student.grade, "F")
        self.assertEqual(student.result, "Fail")

    def test_pass_mark_is_inclusive(self):
        student = make(marks=["40"] * 5)
        self.assertTrue(student.passed)
        self.assertEqual(student.grade, "D")

    def test_zero_and_full_marks_are_valid(self):
        self.assertEqual(make(marks=["0"] * 5).percentage, 0.0)
        self.assertEqual(make(marks=["100"] * 5).percentage, 100.0)


class StudentValidationTests(unittest.TestCase):
    def assert_invalid(self, **overrides):
        with self.assertRaises(ValidationError):
            make(**overrides)

    def test_invalid_roll_no(self):
        for roll in ("", "ab", "MCA 001", "MCA/001", "X" * 21):
            with self.subTest(roll=roll):
                self.assert_invalid(roll_no=roll)

    def test_invalid_name(self):
        for name in ("", "A", "123", "=cmd", "Aarav@"):
            with self.subTest(name=name):
                self.assert_invalid(name=name)

    def test_invalid_email(self):
        for email in ("", "plain", "a@b", "@example.com", "+x@example.com"):
            with self.subTest(email=email):
                self.assert_invalid(email=email)

    def test_invalid_phone(self):
        for phone in ("", "12345", "98765432101", "98765abcde"):
            with self.subTest(phone=phone):
                self.assert_invalid(phone=phone)

    def test_invalid_semester(self):
        for semester in ("", "0", "9", "two", "1.5"):
            with self.subTest(semester=semester):
                self.assert_invalid(semester=semester)

    def test_invalid_marks(self):
        for marks in (["101", "0", "0", "0", "0"], ["-1", "0", "0", "0", "0"],
                      ["abc", "0", "0", "0", "0"], ["", "0", "0", "0", "0"],
                      ["nan", "0", "0", "0", "0"], ["50", "50", "50"]):
            with self.subTest(marks=marks):
                self.assert_invalid(marks=marks)


if __name__ == "__main__":
    unittest.main()
