"""RecordManager: the controller between the GUI and the database layer."""

import csv
from collections import Counter

import numpy as np

from .exceptions import DuplicateRecordError, RecordNotFoundError
from .models import GRADES, PASS_MARK, SUBJECTS, Student


class RecordManager:
    """Business logic for student records. Works with any repository object
    that provides add, update, delete, get_by_roll, get_all and search."""

    def __init__(self, repository):
        self.repo = repository

    @staticmethod
    def _build(data):
        return Student(
            roll_no=data.get("roll_no", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            course=data.get("course", ""),
            semester=data.get("semester", ""),
            marks=data.get("marks", []),
        )

    # ---------- CRUD ----------
    def add_student(self, data):
        student = self._build(data)
        if self.repo.get_by_roll(student.roll_no) is not None:
            raise DuplicateRecordError("A student with this roll number already exists.")
        student.student_id = self.repo.add(student)
        return student

    def update_student(self, data):
        student = self._build(data)
        if self.repo.get_by_roll(student.roll_no) is None:
            raise RecordNotFoundError("No student found with this roll number.")
        self.repo.update(student)
        return student

    def delete_student(self, roll_no):
        roll_no = str(roll_no).strip().upper()
        if self.repo.get_by_roll(roll_no) is None:
            raise RecordNotFoundError("No student found with this roll number.")
        self.repo.delete(roll_no)
        return True

    def list_students(self):
        return self.repo.get_all()

    def search_students(self, keyword):
        keyword = str(keyword).strip()
        return self.repo.search(keyword) if keyword else self.repo.get_all()

    # ---------- statistics (NumPy) ----------
    def statistics(self, students=None):
        students = self.repo.get_all() if students is None else students
        if not students:
            return {"total": 0}

        marks = np.array([s.marks for s in students], dtype=float)  # shape (n, subjects)
        percentages = marks.mean(axis=1)
        passed = (marks >= PASS_MARK).all(axis=1)
        best, worst = int(np.argmax(percentages)), int(np.argmin(percentages))

        counts = Counter(s.grade for s in students)
        return {
            "total": len(students),
            "average": round(float(percentages.mean()), 2),
            "std_dev": round(float(percentages.std()), 2),
            "highest": (students[best].name, round(float(percentages[best]), 2)),
            "lowest": (students[worst].name, round(float(percentages[worst]), 2)),
            "passed": int(passed.sum()),
            "failed": int((~passed).sum()),
            "pass_percentage": round(float(passed.mean()) * 100, 2),
            "grade_distribution": {grade: counts.get(grade, 0) for grade in GRADES},
            "subject_averages": {subject: round(float(avg), 2)
                                 for subject, avg in zip(SUBJECTS, marks.mean(axis=0))},
        }

    # ---------- export ----------
    def export_csv(self, path, students=None):
        students = self.repo.get_all() if students is None else students
        header = ["Roll No", "Name", "Email", "Phone", "Course", "Semester",
                  *SUBJECTS, "Total", "Percentage", "Grade", "Result"]
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            for s in students:
                writer.writerow([s.roll_no, s.name, s.email, s.phone, s.course, s.semester,
                                 *s.marks, s.total, s.percentage, s.grade, s.result])
        return len(students)
