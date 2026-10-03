import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Gradebook", page_icon="📘", layout="wide")

GRADE_BANDS = [(90, "A"), (80, "B"), (70, "C"), (60, "D"), (0, "E")]
GRADES = [g for _, g in GRADE_BANDS]
GRADE_COLORS = {
    "A": "#1F6E43",
    "B": "#2B5FA8",
    "C": "#8A6D1A",
    "D": "#B5541C",
    "E": "#B3261E",
}
PASS_MARK = 60

SAMPLE_CLASS = [
    ("Arun", 92), ("Divya", 85.5), ("Karthik", 74), ("Meena", 66),
    ("Rahul", 58), ("Priya", 97), ("Suresh", 81), ("Lakshmi", 70.5),
]

# ---------------------------------------------------------------------------
# Styling: an exercise-book page with a red margin line
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700&family=Atkinson+Hyperlegible:wght@400;700&display=swap');

    html, body, .stApp, input, textarea, button, select {
        font-family: 'Atkinson Hyperlegible', system-ui, sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Bricolage Grotesque', system-ui, sans-serif !important;
        color: #1E3A6E !important;
        letter-spacing: -0.01em;
    }
    .stApp {
        background-color: #FBFBF7;
        background-image: repeating-linear-gradient(
            to bottom, transparent 0 35px, #E6ECF5 35px 36px
        );
    }
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; bottom: 0; left: 48px;
        width: 2px;
        background: #E8A3A0;
        z-index: 0;
        pointer-events: none;
    }
    section[data-testid="stSidebar"] {
        background: #F1F4F9;
        border-right: 1px solid #DCE3EE;
    }
    .stat {
        background: #FFFFFF;
        border: 1px solid #DCE3EE;
        border-left: 4px solid #1E3A6E;
        border-radius: 6px;
        padding: 0.8rem 1rem;
    }
    .stat-label { color: #5B6B82; font-size: 0.9rem; }
    .stat-value {
        font-family: 'Bricolage Grotesque', system-ui, sans-serif;
        font-size: 1.9rem; font-weight: 700; color: #1E3A6E; line-height: 1.2;
    }
    .stat-note { color: #5B6B82; font-size: 0.8rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# State and helpers
# ---------------------------------------------------------------------------
if "students" not in st.session_state:
    st.session_state.students = []
if "flash" not in st.session_state:
    st.session_state.flash = None


def calculate_grade(mark: float) -> str:
    for cutoff, grade in GRADE_BANDS:
        if mark >= cutoff:
            return grade
    return "E"


def make_student(name: str, mark: float) -> dict:
    mark = float(mark)
    return {"name": name.strip(), "mark": mark, "grade": calculate_grade(mark)}


def name_taken(name: str) -> bool:
    return any(s["name"].lower() == name.strip().lower() for s in st.session_state.students)


def flash(message: str) -> None:
    """Show a toast after the next rerun."""
    st.session_state.flash = message


def students_df() -> pd.DataFrame:
    rows = [
        {"Name": s["name"], "Mark": s["mark"], "Grade": s["grade"]}
        for s in st.session_state.students
    ]
    return pd.DataFrame(rows, columns=["Name", "Mark", "Grade"])


def color_grade(value: str) -> str:
    return f"color: {GRADE_COLORS.get(value, '#333')}; font-weight: 700;"


def color_grades(styler):
    # Styler.map is pandas 2.1+, applymap is the older name
    apply = styler.map if hasattr(styler, "map") else styler.applymap
    return apply(color_grade, subset=["Grade"])


def styled(df: pd.DataFrame):
    return color_grades(df.style.format({"Mark": "{:.1f}"}))


def stat_card(col, label: str, value: str, note: str = "") -> None:
    col.markdown(
        f"""<div class="stat">
              <div class="stat-label">{label}</div>
              <div class="stat-value">{value}</div>
              <div class="stat-note">{note}&nbsp;</div>
            </div>""",
        unsafe_allow_html=True,
    )


if st.session_state.flash:
    st.toast(st.session_state.flash)
    st.session_state.flash = None

# ---------------------------------------------------------------------------
# Sidebar: add a student
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Add a student")
    with st.form("add_student", clear_on_submit=True):
        name = st.text_input("Name", placeholder="e.g. Priya")
        mark = st.number_input("Mark", min_value=0.0, max_value=100.0, step=0.5, value=None,
                               placeholder="0 to 100")
        submitted = st.form_submit_button("Add student", type="primary")

    if submitted:
        if not name.strip():
            st.error("Enter a name to add the student.")
        elif mark is None:
            st.error("Enter a mark between 0 and 100.")
        elif name_taken(name):
            st.error(f"'{name.strip()}' is already in the list. Use a different name.")
        else:
            st.session_state.students.append(make_student(name, mark))
            flash(f"Added {name.strip()} with grade {calculate_grade(mark)}.")
            st.rerun()

    st.divider()
    st.subheader("Grade scale")
    scale = pd.DataFrame(
        {"Grade": GRADES, "Marks": ["90–100", "80–89", "70–79", "60–69", "Below 60"]}
    )
    st.dataframe(color_grades(scale.style), hide_index=True)

    if st.session_state.students:
        st.divider()
        confirm = st.checkbox("I want to remove every student")
        if st.button("Clear all students", disabled=not confirm):
            st.session_state.students = []
            flash("All students removed.")
            st.rerun()

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
st.title("Class gradebook")
st.caption(f"Pass mark is {PASS_MARK}. Grades update automatically when marks change.")

df = students_df()

if df.empty:
    st.info("No students yet. Add one from the sidebar, or load a sample class to explore.")
    if st.button("Load sample class"):
        st.session_state.students = [make_student(n, m) for n, m in SAMPLE_CLASS]
        flash("Sample class loaded.")
        st.rerun()
    st.stop()

# Summary
passed = int((df["Mark"] >= PASS_MARK).sum())
top = df.loc[df["Mark"].idxmax()]
low = df.loc[df["Mark"].idxmin()]

c1, c2, c3, c4, c5 = st.columns(5)
stat_card(c1, "Students", str(len(df)))
stat_card(c2, "Class average", f"{df['Mark'].mean():.1f}", f"Grade {calculate_grade(df['Mark'].mean())}")
stat_card(c3, "Highest", f"{top['Mark']:.1f}", top["Name"])
stat_card(c4, "Lowest", f"{low['Mark']:.1f}", low["Name"])
stat_card(c5, "Pass rate", f"{passed / len(df):.0%}", f"{passed} of {len(df)} passed")

st.write("")
tab_results, tab_edit, tab_insights, tab_data = st.tabs(
    ["Results", "Edit or remove", "Insights", "Import and export"]
)

# --- Results ---------------------------------------------------------------
with tab_results:
    f1, f2, f3 = st.columns([2, 2, 1.4])
    search = f1.text_input("Search by name", placeholder="Type part of a name")
    picked = f2.multiselect("Show grades", GRADES, default=GRADES)
    sort_by = f3.selectbox("Sort by", ["Mark, high to low", "Mark, low to high", "Name, A to Z"])

    view = df[df["Grade"].isin(picked)]
    if search:
        view = view[view["Name"].str.contains(search, case=False, regex=False)]

    if sort_by == "Mark, high to low":
        view = view.sort_values("Mark", ascending=False)
    elif sort_by == "Mark, low to high":
        view = view.sort_values("Mark")
    else:
        view = view.sort_values("Name", key=lambda s: s.str.lower())

    if view.empty:
        st.warning("No students match these filters. Clear the search or pick more grades.")
    else:
        st.dataframe(
            styled(view.reset_index(drop=True)),
            hide_index=True,
            column_config={
                "Mark": st.column_config.ProgressColumn(
                    "Mark", min_value=0, max_value=100, format="%.1f"
                ),
            },
        )
        st.caption(f"Showing {len(view)} of {len(df)} students")

# --- Edit or remove --------------------------------------------------------
with tab_edit:
    st.write("Change a name or mark directly in the table. "
             "To remove a student, select the row and press Delete. Then save.")
    edited = st.data_editor(
        df[["Name", "Mark"]],
        num_rows="dynamic",
        hide_index=True,
        key="editor",
        column_config={
            "Name": st.column_config.TextColumn("Name", required=True),
            "Mark": st.column_config.NumberColumn(
                "Mark", min_value=0.0, max_value=100.0, step=0.5, required=True
            ),
        },
    )

    if st.button("Save changes", type="primary"):
        errors, cleaned, seen = [], [], set()
        for i, row in edited.reset_index(drop=True).iterrows():
            row_name = str(row["Name"]).strip() if pd.notna(row["Name"]) else ""
            row_mark = row["Mark"]
            if not row_name and pd.isna(row_mark):
                continue  # fully blank row, ignore
            if not row_name:
                errors.append(f"Row {i + 1}: name is empty.")
            elif pd.isna(row_mark) or not 0 <= float(row_mark) <= 100:
                errors.append(f"Row {i + 1}: mark must be between 0 and 100.")
            elif row_name.lower() in seen:
                errors.append(f"Row {i + 1}: '{row_name}' appears more than once.")
            else:
                seen.add(row_name.lower())
                cleaned.append(make_student(row_name, row_mark))

        if errors:
            st.error("Nothing was saved. Fix these rows first:\n\n- " + "\n- ".join(errors))
        else:
            st.session_state.students = cleaned
            flash("Changes saved.")
            st.rerun()

# --- Insights --------------------------------------------------------------
with tab_insights:
    left, right = st.columns([3, 2])

    with left:
        st.subheader("Grade distribution")
        counts = df["Grade"].value_counts().reindex(GRADES, fill_value=0)
        st.bar_chart(counts, color="#2B5FA8")

    with right:
        st.subheader("Top three")
        st.dataframe(styled(df.nlargest(3, "Mark").reset_index(drop=True)), hide_index=True)

        st.subheader("Below pass mark")
        below = df[df["Mark"] < PASS_MARK].sort_values("Mark")
        if below.empty:
            st.success("Everyone passed.")
        else:
            st.dataframe(styled(below.reset_index(drop=True)), hide_index=True)

    st.subheader("Mark spread")
    spread = df["Mark"]
    s1, s2, s3 = st.columns(3)
    s1.metric("Median", f"{spread.median():.1f}")
    s2.metric("Range", f"{spread.max() - spread.min():.1f}")
    s3.metric("Standard deviation", f"{spread.std(ddof=0):.1f}")

# --- Import and export -----------------------------------------------------
with tab_data:
    st.subheader("Download results")
    st.download_button(
        "Download as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="class_results.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("Import from CSV")
    st.write("The file needs two columns: **name** and **mark**. Grades are worked out for you.")
    upload = st.file_uploader("Choose a CSV file", type="csv")
    mode = st.radio("When importing", ["Add to the current list", "Replace the current list"],
                    horizontal=True)

    if upload is not None and st.button("Import students"):
        try:
            raw = pd.read_csv(upload)
        except Exception:
            st.error("This file couldn't be read. Check that it's a valid CSV.")
            st.stop()

        raw.columns = [c.strip().lower() for c in raw.columns]
        if not {"name", "mark"}.issubset(raw.columns):
            st.error("The file needs columns named 'name' and 'mark'.")
            st.stop()

        base = [] if mode.startswith("Replace") else list(st.session_state.students)
        existing = {s["name"].lower() for s in base}
        added, skipped = 0, 0

        for _, row in raw.iterrows():
            row_name = str(row["name"]).strip() if pd.notna(row["name"]) else ""
            row_mark = pd.to_numeric(row["mark"], errors="coerce")
            if (not row_name or pd.isna(row_mark) or not 0 <= row_mark <= 100
                    or row_name.lower() in existing):
                skipped += 1
                continue
            base.append(make_student(row_name, row_mark))
            existing.add(row_name.lower())
            added += 1

        st.session_state.students = base
        note = f" Skipped {skipped} row(s) with missing, invalid or duplicate data." if skipped else ""
        flash(f"Imported {added} student(s).{note}")
        st.rerun()