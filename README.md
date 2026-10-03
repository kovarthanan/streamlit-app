# Class Gradebook

A Streamlit web app for managing student marks and grades. It started as a console-based Python program and was rebuilt with a web interface and extra features.

## Features

- Add students with validation for empty names, mark range (0–100), and duplicate names
- Class summary showing student count, average, highest, lowest, and pass rate
- Search, filter by grade, and sort results
- Edit names and marks directly in the table, or delete rows; grades recalculate automatically
- Grade distribution chart, top three students, and students below the pass mark
- Median, range, and standard deviation of marks
- Import students from a CSV file (add to or replace the current list)
- Export results as CSV
- Load a sample class to try the app quickly

## Grade scale

| Grade | Marks    |
|-------|----------|
| A     | 90–100   |
| B     | 80–89    |
| C     | 70–79    |
| D     | 60–69    |
| E     | Below 60 |

Pass mark is 60.

## Requirements

- Python 3.10+
- Streamlit 1.27+
- Pandas

## Setup

```bash
pip install streamlit pandas
```

## Run

```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

## CSV import format

The file needs two columns, `name` and `mark`:

```csv
name,mark
Arun,92
Divya,85.5
Karthik,74
```

Rows with a missing name, an invalid mark, or a duplicate name are skipped.

## Configuration

Grade boundaries and the pass mark are defined at the top of `app.py`:

```python
GRADE_BANDS = [(90, "A"), (80, "B"), (70, "C"), (60, "D"), (0, "E")]
PASS_MARK = 60
```

Change these to match your own grading system.

## Note

Data is stored in the browser session only. Refreshing the page or restarting the app clears it, so export to CSV if you want to keep your results.

## Tech stack

Python, Streamlit, Pandas
