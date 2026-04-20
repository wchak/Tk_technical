# Variables
PYTHON = python3
PIP = pip

.PHONY: setup pipeline dashboard clean

# 1. make setup: Install all necessary dependencies
setup:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# 2. make pipeline: Execute data pipeline sequentially from start to finish without any manual intervention
# Part 1: initialize the database, load the data
# Part 2: generate all required output tables and plots
pipeline:
	$(PYTHON) load_data.py
	$(PYTHON) analyze_data.py

# 3. make dashboard: Start the local Streamlit server
dashboard:
	streamlit run dashboard.py