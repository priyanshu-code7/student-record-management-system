# Student Record Management System

A desktop application built with **Python**, **Tkinter**, **NumPy** and **MySQL** for managing student records. Add, update, delete and search students, enter subject marks, and get automatic totals, percentages, grades, pass/fail results and class statistics. All records are stored permanently in a MySQL database.

## Features

- Add, update and delete student records
- Search by roll number, name or course
- Automatic **total, percentage, grade (A+ to F) and Pass/Fail result** for each student
- Input validation for roll number, name, email, phone (10 digits), semester (1-8) and marks (0-100)
- Duplicate roll number / email detection
- **Statistics window** (NumPy): class average, standard deviation, topper, lowest scorer, pass percentage, subject-wise averages and a grade distribution chart
- **Export to CSV**
- Failed students are highlighted in red in the table
- Friendly error messages through exception handling

## Technologies Used

| Technology | Purpose |
| --- | --- |
| Python 3.x | Core language and logic |
| Tkinter | Graphical user interface |
| NumPy | Marks arrays, percentages, statistics |
| OOP | `Student`, `DatabaseManager`, `RecordManager`, `StudentApp` classes |
| MySQL | Permanent storage of records |
| mysql-connector-python | Python to MySQL connectivity |
| python-dotenv | Database settings from a `.env` file |
| csv, re, datetime | Export, validation, timestamps |
| unittest | Testing |

## Project Structure

```
student-record-management-system/
├── main.py              # Entry point
├── database.sql         # MySQL schema + sample data
├── requirements.txt     # Python packages
├── .env.example         # Database settings template
├── README.md
├── srms/
│   ├── models.py        # Student class: validation, total, percentage, grade
│   ├── database.py      # DatabaseManager: all MySQL code
│   ├── manager.py       # RecordManager: CRUD logic, statistics, CSV export
│   ├── gui.py           # Tkinter interface
│   └── exceptions.py    # Custom exceptions
└── tests/
    ├── test_student.py  # Validation and grade tests
    ├── test_manager.py  # CRUD, search, statistics, export tests
    ├── test_database.py # MySQL integration tests (optional)
    └── helpers.py
```

The code is layered: the GUI talks only to `RecordManager`, which talks only to `DatabaseManager`. SQL is never written inside the GUI.

## Installation

1. Install **Python 3.x** (with Tkinter) and **MySQL Server**.
2. Install the packages from the project folder:

   ```
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and enter your MySQL details:

   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=student_records
   ```

4. *(Optional)* Open `database.sql` in MySQL Workbench and run it to create the database with sample records. If you skip this step, the application creates the database and table automatically on first start.

## Running the Application

```
python main.py
```

## How to Use

1. Fill in the student details and the five subject marks, then click **Add Student**.
2. Click a row in the table to load it into the form. Edit the fields and click **Update** (the roll number cannot be changed).
3. Click **Delete** to remove the selected record (a confirmation is asked).
4. Use the search box and **Search** / **Show All** to filter the table.
5. Click **Statistics** for class analysis, or **Export CSV** to save the data.

## Grading Rules

| Percentage | Grade |
| --- | --- |
| 90 and above | A+ |
| 80 - 89.99 | A |
| 70 - 79.99 | B+ |
| 60 - 69.99 | B |
| 50 - 59.99 | C |
| 40 - 49.99 | D |
| Below 40, or any subject below 40 | F (Fail) |

A student passes only if **every** subject is 40 or above.

## Database Schema

Table: `students`

| Field | Type | Constraint |
| --- | --- | --- |
| id | INT | PRIMARY KEY, AUTO_INCREMENT |
| roll_no | VARCHAR(20) | NOT NULL, UNIQUE |
| name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(100) | NOT NULL, UNIQUE |
| phone | VARCHAR(10) | NOT NULL |
| course | VARCHAR(50) | NOT NULL |
| semester | INT | NOT NULL |
| mark_1 ... mark_5 | DECIMAL(5,2) | NOT NULL |
| created_at | DATETIME | NOT NULL |

All queries are parameterized, which protects against SQL injection.

## Running the Tests

```
python -m unittest discover -s tests -t . -v
```

The MySQL integration tests are skipped by default. To include them (uses a separate `student_records_test` database):

```
# Windows PowerShell
$env:RUN_DB_TESTS="1"; python -m unittest discover -s tests -t . -v

# Linux / macOS
RUN_DB_TESTS=1 python -m unittest discover -s tests -t . -v
```

## Future Enhancements

- Login system for admin and teachers
- Attendance tracking
- Printable PDF report cards
- Charts for subject-wise performance
- Web version using Flask or Django
- Cloud database support

## Author

Your Name - Your UID - Your Course
