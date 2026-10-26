"""Student Record Management System - entry point.

Run with:  python main.py
"""

import sys
import tkinter as tk
from tkinter import messagebox

from srms.database import DatabaseManager
from srms.exceptions import DatabaseError
from srms.gui import StudentApp
from srms.manager import RecordManager


def main():
    root = tk.Tk()
    database = DatabaseManager()

    try:
        database.connect()
    except DatabaseError as err:
        messagebox.showerror(
            "Database connection failed",
            f"{err}\n\nCheck the settings in your .env file and make sure "
            "MySQL Server is running.")
        root.destroy()
        return 1

    def on_close():
        database.close()
        root.destroy()

    StudentApp(root, RecordManager(database), on_exit=on_close)
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
