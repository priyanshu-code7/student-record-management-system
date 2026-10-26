"""Student model with validation and NumPy-based result calculation."""

import re

import numpy as np

from .exceptions import ValidationError

SUBJECTS = ("Python", "DBMS", "Mathematics", "Computer Networks", "Software Engineering")
COURSES = ("MCA", "BCA", "B.Tech", "M.Tech", "MBA", "B.Sc IT")
MAX_MARKS = 100.0
PASS_MARK = 40.0
GRADES = ("A+", "A", "B+", "B", "C", "D", "F")
GRADE_SCALE = ((90, "A+"), (80, "A"), (70, "B+"), (60, "B"), (50, "C"), (40, "D"))

_ROLL_RE = re.compile(r"^[A-Z0-9\-]{3,20}$")
_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .'\-]{1,99}$")
_EMAIL_RE = re.compile(r"^[A-Za-z0-9][\w.+\-]*@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)+$")
_PHONE_RE = re.compile(r"^\d{10}$")
_COURSE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 .\-&]{1,49}$")


class Student:
    """A single student record."""

    def __init__(self, roll_no, name, email, phone, course, semester, marks,
                 student_id=None, created_at=None):
        self.student_id = student_id
        self.roll_no = str(roll_no).strip().upper()
        self.name = " ".join(str(name).split())
        self.email = str(email).strip().lower()
        self.phone = str(phone).strip()
        self.course = str(course).strip()
        self.semester = self._to_int(semester)
        self.marks = self._to_marks(marks)
        self.created_at = created_at
        self.validate()

    # ---------- conversion helpers ----------
    @staticmethod
    def _to_int(value):
        try:
            return int(str(value).strip())
        except ValueError:
            raise ValidationError("Semester must be a whole number between 1 and 8.")

    @staticmethod
    def _to_marks(marks):
        marks = list(marks)
        if len(marks) != len(SUBJECTS):
            raise ValidationError(f"Marks are required for all {len(SUBJECTS)} subjects.")
        converted = []
        for subject, mark in zip(SUBJECTS, marks):
            try:
                converted.append(float(str(mark).strip()))
            except ValueError:
                raise ValidationError(f"Marks for {subject} must be a number.")
        return converted

    # ---------- validation ----------
    def validate(self):
        if not _ROLL_RE.match(self.roll_no):
            raise ValidationError("Roll number must be 3-20 characters: letters, digits or '-'.")
        if not _NAME_RE.match(self.name):
            raise ValidationError("Name must start with a letter and contain only letters, "
                                  "spaces, '.', apostrophe or '-'.")
        if not _EMAIL_RE.match(self.email):
            raise ValidationError("Enter a valid email address.")
        if not _PHONE_RE.match(self.phone):
            raise ValidationError("Phone number must be exactly 10 digits.")
        if not _COURSE_RE.match(self.course):
            raise ValidationError("Enter a valid course name.")
        if not 1 <= self.semester <= 8:
            raise ValidationError("Semester must be between 1 and 8.")
        for subject, mark in zip(SUBJECTS, self.marks):
            if not 0 <= mark <= MAX_MARKS:
                raise ValidationError(
                    f"Marks for {subject} must be between 0 and {int(MAX_MARKS)}.")

    # ---------- calculated properties (NumPy) ----------
    @property
    def total(self):
        return round(float(np.sum(self.marks)), 2)

    @property
    def percentage(self):
        return round(float(np.mean(self.marks)) * 100 / MAX_MARKS, 2)

    @property
    def passed(self):
        return bool(np.all(np.array(self.marks) >= PASS_MARK))

    @property
    def grade(self):
        if not self.passed:
            return "F"
        for threshold, grade in GRADE_SCALE:
            if self.percentage >= threshold:
                return grade
        return "D"

    @property
    def result(self):
        return "Pass" if self.passed else "Fail"

    def __repr__(self):
        return f"Student({self.roll_no!r}, {self.name!r}, {self.course!r}, sem={self.semester})"
