import sqlite3
import os
import pandas as pd
from utils import get_root
from queries import SCHEMA_STATEMENTS

######################################################
## 1. Data Management
######################################################

## 1.2. Define relational database schema
### Projects -> Subjects -> Samples -> Measurements
### from queries: SCHEMA_STATEMENTS for the schema query

## 1.3. create a SQLite database file 

def initialize_db(db_path, csv_path):

    """
    Objective: Initialize the database from a defined relational database schema

    db_path: path for the db files
    csv_path: path for the csv file
    """

    # Delete the old db file
    if os.path.exists(db_path):
        os.remove(db_path) 

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # initialize all the tables
        for statement in SCHEMA_STATEMENTS:
            cursor.execute(statement)
        
        if os.path.exists(csv_path):

            df = pd.read_csv(csv_path)
            
            # 1: Unique Projects
            df[['project']].drop_duplicates().to_sql('projects', conn, if_exists='append', index=False)

            # 2: Unique Subjects
            df[['subject', 'project', 'condition', 'age', 'sex']].drop_duplicates().to_sql('subjects', conn, if_exists='append', index=False)

            # 3: Samples
            df[['sample', 'subject', 'treatment', 'response', 'sample_type', 'time_from_treatment_start']].to_sql('samples', conn, if_exists='append', index=False)
            
            # 4: Measurements
            df[['sample', 'b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']].to_sql('measurements', conn, if_exists='append', index=False)


if __name__ == "__main__":
    
    # name the db file
    print("")
    print("------------------ 1.1 Data Management ------------------")
    print("")

    repo_root = get_root()
    db_path = os.path.join(repo_root, 'research_data.db')
    print(f"Database Path: {db_path}")

    ## 1. Data Management
    # load the csv file
    print(""); print("Load the csv file.")
    csv_path = os.path.join(repo_root, 'cell-count.csv')
    
    print(""); print("Inintialize the db file.")
    initialize_db(db_path = db_path, csv_path = csv_path)
    print("Successfully initialize the db file.")
    print("")