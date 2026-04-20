# Clinical Data Analysis Pipeline

## Project Overview
This task generates a Python program and an interactive dashboard to understand how drug candidate affects immune cell populations.

## File Structure
- **load_data.py**: Initializes the SQLite database and loads `cell-count.csv`.
- **queries.py**: Contains all SQL query constants used across the project.
- **utils.py**: Shared logic for database connections and statistical testing.
- **analyze_data.py**: Executes the data pipeline and prints statistical results (for `make pipeline`).
- **dashboard.py**: Interactive dashboard for data visualization (for `make dashboard`).
- **requirements.txt**: List of external dependencies.
- **research_data.db**: The generated SQLite database.
- **cell-count.csv**: The raw input data.

## How to Run (Step by Step)
### 1. **Setup dependencies**: `make setup`
### 2. **Run Pipeline**: `make pipeline`
- python `load_data.py`
- python `analyze_data.py`
### 3. **Launch Dashboard**: `make dashboard` 
- streamlit run `dashboard.py`

---

## Relational Database Schema
The SQLite database (`research_data.db`) follows **3rd Normal Form (3NF)** to ensure data integrity and minimize redundancy.

### 1. **Projects** (Top Level)
- `project` (TEXT, Primary Key): UID for the research project.

### 2. **Subjects** (Patient Level)
- `subject` (TEXT, Primary Key): Patient ID (e.g., `sbj001`).
- `project` (TEXT, Foreign Key): Link to parent project.
- `condition` (TEXT): Clinical conditions (e.g., `melanoma`, `carcinoma`, `healthy`).
- `age` (INT): Patient age.
- `sex` (TEXT): Biological sex (Enforced: `M`, `F`).

### 3. **Samples** (Event Level)
- `sample` (TEXT, Primary Key): Unique ID for each event.
- `subject` (TEXT, Foreign Key): Link to subject.
- `treatment` (TEXT): Treatment administered (e.g., `miraclib`).
- `response` (TEXT): Clinical outcome (`yes`, `no`, or `NULL`).
- `time_from_treatment_start` (INT): Study day (Enforced: `0`, `7`, `14`).

### 4. **Measurements** (Data Level)
- `sample` (TEXT, Primary / Foreign Key): Link to specific sample event.
- `b_cell`, `cd8_t_cell`, `cd4_t_cell`, `nk_cell`, `monocyte` (INT): Raw immune cell counts.
