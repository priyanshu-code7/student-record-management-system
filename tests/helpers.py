"""Shared test helpers."""


def sample_data(**overrides):
    data = {
        "roll_no": "MCA-001",
        "name": "Aarav Sharma",
        "email": "aarav@example.com",
        "phone": "9876543210",
        "course": "MCA",
        "semester": "2",
        "marks": ["90", "80", "70", "60", "50"],
    }
    data.update(overrides)
    return data


class MemoryRepository:
    """Dictionary-backed stand-in for DatabaseManager (no MySQL needed)."""

    def __init__(self):
        self.rows = {}
        self._next_id = 1

    def add(self, student):
        student.student_id = self._next_id
        self._next_id += 1
        self.rows[student.roll_no] = student
        return student.student_id

    def update(self, student):
        self.rows[student.roll_no] = student

    def delete(self, roll_no):
        return self.rows.pop(roll_no, None) is not None

    def get_by_roll(self, roll_no):
        return self.rows.get(roll_no)

    def get_all(self):
        return [self.rows[key] for key in sorted(self.rows)]

    def search(self, keyword):
        keyword = keyword.lower()
        return [s for s in self.get_all()
                if keyword in s.roll_no.lower() or keyword in s.name.lower()
                or keyword in s.course.lower()]
