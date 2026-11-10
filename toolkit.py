"""Create, inspect and validate an Employee Sentiment Analysis intake workbook."""
import argparse
import csv
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

HEADER = ("company", "quarter", "topic", "favorable", "responses")
HERE = Path(__file__).resolve().parent


def create(path):
    wb = Workbook()
    sheet = wb.active
    sheet.title = "Responses"
    sheet.append(HEADER)
    with (HERE / "examples/responses.csv").open(newline="") as stream:
        for row in csv.DictReader(stream):
            sheet.append([row["company"], row["quarter"], row["topic"], int(row["favorable"]), int(row["responses"])])
    sheet.freeze_panes = "D2"
    sheet.auto_filter.ref = sheet.dimensions
    for column, width in zip("ABCDE", (24, 18, 30, 15, 15)):
        sheet.column_dimensions[column].width = width
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="235647")
    rule = DataValidation(type="whole", operator="greaterThanOrEqual", formula1="0", allow_blank=False)
    rule.showErrorMessage = True
    sheet.add_data_validation(rule)
    rule.add("D2:E10001")
    wb.save(path)


def inspect(path):
    wb = load_workbook(path, read_only=True, data_only=False)
    try:
        rows = iter(wb["Responses"].values)
        if next(rows, None) != HEADER:
            raise ValueError("The Responses header must match the example workbook.")
        seen, valid = set(), []
        for number, row in enumerate(rows, 2):
            if all(value is None for value in row):
                continue
            company, quarter, topic, favorable, responses = row
            if any(not isinstance(v, str) or not v.strip() or v.lstrip().startswith(("=", "+", "-", "@")) for v in row[:3]):
                raise ValueError(f"Row {number}: missing or unsafe label")
            if type(responses) is not int or type(favorable) is not int or not 0 <= favorable <= responses or not responses:
                raise ValueError(f"Row {number}: counts must be whole numbers, with favorable at most responses")
            key = tuple(v.strip().casefold() for v in row[:3])
            if key in seen:
                raise ValueError(f"Row {number}: duplicate company, quarter and topic")
            seen.add(key)
            valid.append(row)
        if not valid:
            raise ValueError("No response rows.")
        return valid
    finally:
        wb.close()


def export(source, target):
    rows = inspect(source)
    with target.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(HEADER)
        writer.writerows(rows)
    return len(rows)


def desktop():
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    win = tk.Tk()
    win.title("Employee Sentiment Analysis | Workbook intake")
    def run(action):
        try:
            if action == "create":
                dest = filedialog.asksaveasfilename(defaultextension=".xlsx")
                if dest: create(dest)
            else:
                src = filedialog.askopenfilename(filetypes=[("Workbook", "*.xlsx")])
                if not src: return
                if action == "validate": messagebox.showinfo("Validation", f"{len(inspect(src))} valid rows")
                else:
                    dest = filedialog.asksaveasfilename(defaultextension=".csv")
                    if dest: messagebox.showinfo("Export", f"Exported {export(src, Path(dest))} rows")
        except Exception as error:
            messagebox.showerror("Workbook", str(error))
    for action, label in [("create", "Create example workbook"), ("validate", "Check workbook"), ("export", "Export validated CSV")]:
        ttk.Button(win, text=label, command=lambda a=action: run(a)).pack(fill="x", padx=24, pady=8)
    win.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    cmds = parser.add_subparsers(dest="cmd", required=True)
    for action in ("create", "validate", "export"):
        sub = cmds.add_parser(action)
        sub.add_argument("workbook", type=Path)
        if action == "export": sub.add_argument("csv", type=Path)
    cmds.add_parser("desktop")
    a = parser.parse_args()
    if a.cmd == "desktop": desktop()
    elif a.cmd == "create": create(a.workbook)
    elif a.cmd == "validate": print(len(inspect(a.workbook)), "valid rows")
    else: print(export(a.workbook, a.csv), "rows exported")
