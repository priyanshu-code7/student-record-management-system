"""DatabaseManager: all MySQL code lives here (parameterized queries only)."""

import os
import re
from datetime import datetime

from .exceptions import DatabaseError, DuplicateRecordError
from .models import SUBJECTS, Student

try:  # optional: read settings from a .env file
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # pragma: no cover
    pass

try:
    import mysql.connector as mysql_connector
    from mysql.connector import Error as MySQLError
except ImportError:  # pragma: no cover
    mysql_connector = None

    class MySQLError(Exception):
        """Placeholder so the module still imports without the MySQL driver."""

MARK_COLUMNS = [f"mark_{i}" for i in range(1, len(SUBJECTS) + 1)]
_MARK_DDL = ",\n    ".join(f"{col} DECIMAL(5,2) NOT NULL" for col in MARK_COLUMNS)

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(10) NOT NULL,
    course VARCHAR(50) NOT NULL,
    semester INT NOT NULL,
    {_MARK_DDL},
    created_at DATETIME NOT NULL
)
"""

_INSERT_COLUMNS = ["roll_no", "name", "email", "phone", "course", "semester",
                   *MARK_COLUMNS, "created_at"]


def load_config():
    """Read connection settings from environment variables."""
    try:
        port = int(os.getenv("DB_PORT", "3306"))
    except ValueError:
        port = 3306
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": port,
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "student_records"),
    }


def _row_to_student(row):
    return Student(
        roll_no=row["roll_no"], name=row["name"], email=row["email"],
        phone=row["phone"], course=row["course"], semester=row["semester"],
        marks=[float(row[col]) for col in MARK_COLUMNS],
        student_id=row["id"], created_at=row["created_at"],
    )


class DatabaseManager:
    """Creates the connection, runs queries, commits and closes."""

    def __init__(self, config=None):
        self.config = config or load_config()
        self.connection = None

    # ---------- connection ----------
    def connect(self):
        if mysql_connector is None:
            raise DatabaseError("mysql-connector-python is not installed. "
                                "Run: pip install -r requirements.txt")
        db_name = self.config["database"]
        if not re.fullmatch(r"[A-Za-z0-9_]+", db_name):
            raise DatabaseError("DB_NAME may contain only letters, digits and underscores.")
        try:
            self.connection = mysql_connector.connect(
                host=self.config["host"], port=self.config["port"],
                user=self.config["user"], password=self.config["password"])
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
            self.connection.database = db_name
            cursor.execute(CREATE_TABLE_SQL)
            self.connection.commit()
            cursor.close()
        except MySQLError as err:
            self.connection = None
            raise DatabaseError(f"Could not connect to MySQL: {err}") from err

    def _ensure_connection(self):
        if self.connection is None or not self.connection.is_connected():
            self.connect()

    def close(self):
        if self.connection is not None:
            try:
                self.connection.close()
            except MySQLError:  # pragma: no cover
                pass
            self.connection = None

    # ---------- query helper ----------
    def _execute(self, sql, params=(), fetch=False):
        self._ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(sql, params)
            if fetch:
                return cursor.fetchall()
            self.connection.commit()
            return cursor.lastrowid, cursor.rowcount
        except MySQLError as err:
            self.connection.rollback()
            if getattr(err, "errno", None) == 1062:
                message = str(getattr(err, "msg", err)).lower()
                field = "email address" if "email" in message else "roll number"
                raise DuplicateRecordError(f"A student with this {field} already exists.") from err
            raise DatabaseError(f"Database error: {err}") from err
        finally:
            cursor.close()

    # ---------- CRUD ----------
    def add(self, student):
        placeholders = ", ".join(["%s"] * len(_INSERT_COLUMNS))
        sql = f"INSERT INTO students ({', '.join(_INSERT_COLUMNS)}) VALUES ({placeholders})"
        values = (student.roll_no, student.name, student.email, student.phone,
                  student.course, student.semester, *student.marks, datetime.now())
        new_id, _ = self._execute(sql, values)
        return new_id

    def update(self, student):
        mark_sets = ", ".join(f"{col} = %s" for col in MARK_COLUMNS)
        sql = (f"UPDATE students SET name = %s, email = %s, phone = %s, course = %s, "
               f"semester = %s, {mark_sets} WHERE roll_no = %s")
        values = (student.name, student.email, student.phone, student.course,
                  student.semester, *student.marks, student.roll_no)
        self._execute(sql, values)

    def delete(self, roll_no):
        _, affected = self._execute("DELETE FROM students WHERE roll_no = %s", (roll_no,))
        return affected > 0

    def get_by_roll(self, roll_no):
        rows = self._execute("SELECT * FROM students WHERE roll_no = %s", (roll_no,), fetch=True)
        return _row_to_student(rows[0]) if rows else None

    def get_all(self):
        rows = self._execute("SELECT * FROM students ORDER BY roll_no", fetch=True)
        return [_row_to_student(row) for row in rows]

    def search(self, keyword):
        like = f"%{keyword.strip()}%"
        rows = self._execute(
            "SELECT * FROM students WHERE roll_no LIKE %s OR name LIKE %s OR course LIKE %s "
            "ORDER BY roll_no", (like, like, like), fetch=True)
        return [_row_to_student(row) for row in rows]
