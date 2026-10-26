"""Tkinter graphical interface for the Student Record Management System."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .exceptions import (DatabaseError, DuplicateRecordError, RecordNotFoundError,
                         ValidationError)
from .models import COURSES, GRADES, SUBJECTS

HEADER_BG = "#1f3a5f"
ACCENT = "#2d6cdf"
FAIL_COLOR = "#b00020"


class StudentApp:
    def __init__(self, root, manager, on_exit=None):
        self.root = root
        self.manager = manager
        self.on_exit = on_exit or root.destroy
        self.students = {}          # roll_no -> Student currently shown in the table
        self.selected_roll = None   # roll number of the record being edited

        self.vars = {key: tk.StringVar() for key in
                     ("roll_no", "name", "email", "phone", "course", "semester")}
        self.mark_vars = [tk.StringVar() for _ in SUBJECTS]
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        self.root.title("Student Record Management System")
        self.root.geometry("1200x700")
        self.root.minsize(1050, 620)
        ttk.Style().theme_use("clam")

        tk.Label(self.root, text="Student Record Management System",
                 font=("Segoe UI", 20, "bold"), bg=HEADER_BG, fg="white",
                 pady=10).pack(fill="x")

        body = ttk.Frame(self.root, padding=10)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_form(body)
        self._build_table(body)

        tk.Label(self.root, textvariable=self.status_var, anchor="w", bg="#e8edf3",
                 padx=10, pady=4).pack(fill="x", side="bottom")

    def _build_form(self, parent):
        form = ttk.LabelFrame(parent, text="Student Details", padding=10)
        form.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        row = 0
        for label, key in (("Roll No", "roll_no"), ("Full Name", "name"),
                           ("Email", "email"), ("Phone", "phone")):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=3)
            entry = ttk.Entry(form, textvariable=self.vars[key], width=28)
            entry.grid(row=row, column=1, pady=3, sticky="w")
            if key == "roll_no":
                self.roll_entry = entry
            row += 1

        ttk.Label(form, text="Course").grid(row=row, column=0, sticky="w", pady=3)
        ttk.Combobox(form, textvariable=self.vars["course"], values=COURSES,
                     width=26).grid(row=row, column=1, pady=3, sticky="w")
        row += 1

        ttk.Label(form, text="Semester").grid(row=row, column=0, sticky="w", pady=3)
        ttk.Combobox(form, textvariable=self.vars["semester"], state="readonly",
                     values=[str(i) for i in range(1, 9)],
                     width=26).grid(row=row, column=1, pady=3, sticky="w")
        row += 1

        ttk.Separator(form).grid(row=row, column=0, columnspan=2, sticky="ew", pady=8)
        row += 1
        ttk.Label(form, text="Marks (out of 100)",
                  font=("Segoe UI", 10, "bold")).grid(row=row, column=0, columnspan=2,
                                                      sticky="w")
        row += 1
        for subject, var in zip(SUBJECTS, self.mark_vars):
            ttk.Label(form, text=subject).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(form, textvariable=var, width=10).grid(row=row, column=1,
                                                             pady=3, sticky="w")
            row += 1

        buttons = ttk.Frame(form)
        buttons.grid(row=row, column=0, columnspan=2, pady=(12, 0))
        for index, (text, command) in enumerate((("Add Student", self.on_add),
                                                 ("Update", self.on_update),
                                                 ("Delete", self.on_delete),
                                                 ("Clear", self.on_clear))):
            ttk.Button(buttons, text=text, command=command, width=13).grid(
                row=index // 2, column=index % 2, padx=4, pady=4)

    def _build_table(self, parent):
        right = ttk.Frame(parent)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        search = ttk.Frame(right)
        search.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(search, text="Search (roll no / name / course):").pack(side="left")
        entry = ttk.Entry(search, textvariable=self.search_var, width=28)
        entry.pack(side="left", padx=6)
        entry.bind("<Return>", lambda _event: self.on_search())
        ttk.Button(search, text="Search", command=self.on_search).pack(side="left", padx=2)
        ttk.Button(search, text="Show All", command=self.on_show_all).pack(side="left", padx=2)

        columns = (("roll_no", "Roll No", 100), ("name", "Name", 190),
                   ("course", "Course", 90), ("semester", "Sem", 50),
                   ("total", "Total", 70), ("percentage", "Percent", 80),
                   ("grade", "Grade", 60), ("result", "Result", 70))
        self.tree = ttk.Treeview(right, columns=[c[0] for c in columns],
                                 show="headings", selectmode="browse")
        for key, title, width in columns:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=width, anchor="w" if key == "name" else "center")
        self.tree.tag_configure("fail", foreground=FAIL_COLOR)
        self.tree.grid(row=1, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        scroll = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        scroll.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll.set)

        bottom = ttk.Frame(right)
        bottom.grid(row=2, column=0, columnspan=2, sticky="e", pady=(8, 0))
        ttk.Button(bottom, text="Statistics", command=self.on_statistics).pack(side="left", padx=4)
        ttk.Button(bottom, text="Export CSV", command=self.on_export).pack(side="left", padx=4)
        ttk.Button(bottom, text="Exit", command=self.on_exit).pack(side="left", padx=4)

    # ------------------------------------------------------------ helpers
    def _form_data(self):
        data = {key: var.get() for key, var in self.vars.items()}
        data["marks"] = [var.get() for var in self.mark_vars]
        return data

    def _fill_form(self, student):
        self.vars["roll_no"].set(student.roll_no)
        self.vars["name"].set(student.name)
        self.vars["email"].set(student.email)
        self.vars["phone"].set(student.phone)
        self.vars["course"].set(student.course)
        self.vars["semester"].set(str(student.semester))
        for var, mark in zip(self.mark_vars, student.marks):
            var.set(f"{mark:g}")

    def _handle(self, func, *args):
        """Run an action and show friendly messages for expected errors."""
        try:
            return func(*args)
        except (ValidationError, DuplicateRecordError, RecordNotFoundError) as err:
            messagebox.showwarning("Cannot complete action", str(err))
        except DatabaseError as err:
            messagebox.showerror("Database error", str(err))
        except OSError as err:
            messagebox.showerror("File error", str(err))
        return None

    def _populate(self, students):
        self.tree.delete(*self.tree.get_children())
        self.students = {s.roll_no: s for s in students}
        for s in students:
            self.tree.insert("", "end", iid=s.roll_no,
                             values=(s.roll_no, s.name, s.course, s.semester,
                                     f"{s.total:g}", f"{s.percentage:.2f}", s.grade, s.result),
                             tags=("fail",) if not s.passed else ())
        self.status_var.set(f"{len(students)} record(s) shown")

    def refresh(self):
        students = self._handle(self.manager.list_students)
        if students is not None:
            self._populate(students)

    # ------------------------------------------------------------ actions
    def on_add(self):
        student = self._handle(self.manager.add_student, self._form_data())
        if student:
            messagebox.showinfo("Success", f"{student.name} was added successfully.")
            self.on_clear()
            self.refresh()

    def on_update(self):
        if not self.selected_roll:
            messagebox.showinfo("Select a record", "Select a student from the table first.")
            return
        data = self._form_data()
        data["roll_no"] = self.selected_roll
        student = self._handle(self.manager.update_student, data)
        if student:
            messagebox.showinfo("Success", f"{student.name} was updated successfully.")
            self.on_clear()
            self.refresh()

    def on_delete(self):
        if not self.selected_roll:
            messagebox.showinfo("Select a record", "Select a student from the table first.")
            return
        if not messagebox.askyesno("Confirm delete",
                                   f"Delete record {self.selected_roll}? This cannot be undone."):
            return
        if self._handle(self.manager.delete_student, self.selected_roll):
            self.on_clear()
            self.refresh()

    def on_clear(self):
        for var in self.vars.values():
            var.set("")
        for var in self.mark_vars:
            var.set("")
        self.selected_roll = None
        self.roll_entry.config(state="normal")
        self.tree.selection_remove(self.tree.selection())

    def on_select(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        student = self.students.get(selection[0])
        if student:
            self._fill_form(student)
            self.selected_roll = student.roll_no
            self.roll_entry.config(state="readonly")  # roll number is the key; keep it fixed

    def on_search(self):
        students = self._handle(self.manager.search_students, self.search_var.get())
        if students is not None:
            self._populate(students)

    def on_show_all(self):
        self.search_var.set("")
        self.refresh()

    def on_export(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="students.csv",
                                            filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        count = self._handle(self.manager.export_csv, path)
        if count is not None:
            messagebox.showinfo("Export complete", f"{count} record(s) exported to:\n{path}")

    def on_statistics(self):
        stats = self._handle(self.manager.statistics)
        if stats is None:
            return
        if stats["total"] == 0:
            messagebox.showinfo("Statistics", "There are no records yet.")
            return
        self._show_statistics(stats)

    def _show_statistics(self, stats):
        window = tk.Toplevel(self.root)
        window.title("Class Statistics")
        window.resizable(False, False)
        window.transient(self.root)

        lines = [
            f"Total students      : {stats['total']}",
            f"Average percentage  : {stats['average']}%",
            f"Standard deviation  : {stats['std_dev']}",
            f"Topper              : {stats['highest'][0]} ({stats['highest'][1]}%)",
            f"Lowest              : {stats['lowest'][0]} ({stats['lowest'][1]}%)",
            f"Passed / Failed     : {stats['passed']} / {stats['failed']}",
            f"Pass percentage     : {stats['pass_percentage']}%",
            "",
            "Subject-wise average:",
        ]
        lines += [f"   {subject:<22}{avg}" for subject, avg in stats["subject_averages"].items()]
        tk.Label(window, text="\n".join(lines), justify="left", anchor="w",
                 font=("Consolas", 10), padx=16, pady=12).pack(fill="x")

        # simple bar chart of the grade distribution
        distribution = stats["grade_distribution"]
        canvas = tk.Canvas(window, width=420, height=200, bg="white", highlightthickness=0)
        canvas.pack(padx=16, pady=(0, 12))
        canvas.create_text(210, 14, text="Grade distribution", font=("Segoe UI", 10, "bold"))
        peak = max(distribution.values()) or 1
        for index, grade in enumerate(GRADES):
            count = distribution[grade]
            x0 = 24 + index * 56
            height = (count / peak) * 120
            canvas.create_rectangle(x0, 170 - height, x0 + 36, 170, fill=ACCENT, outline="")
            canvas.create_text(x0 + 18, 160 - height, text=str(count))
            canvas.create_text(x0 + 18, 184, text=grade)
        ttk.Button(window, text="Close", command=window.destroy).pack(pady=(0, 12))
