import sqlite3
import subprocess
import os
import pandas as pd
from scipy.stats import mannwhitneyu
from queries import query_data_overview, query_stat_analysis

######################################################
## 1. Data Management
######################################################

## 1.1. Set the csv and db path in the root

def get_root():
    
    # get the repository root 

    try: # find the repository root 
        return subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], stderr=subprocess.stderr).decode('utf-8').strip()
    
    except Exception: # if git is not available 
        return os.getcwd()
    

######################################################
## 2. Initial Analysis - Data Overview
######################################################

## "What is the frequency of each cell type in each sample?"

def cell_frequency_summary(db_path):
    
    # display a summary table of the relative frequency of each cell population from a db file
    
    query = query_data_overview

    with sqlite3.connect(db_path) as conn:
        summary_df = pd.read_sql_query(query, conn)

    return summary_df


######################################################
## 3. Statistical Analysis
######################################################

# Compare the differences in cell population relative frequencies of melanoma patients receiving miraclib 
# who respond (responders) versus those who do not (non-responders), 
# with the overarching aim of predicting response to the treatment miraclib. 
# Response information can be found in column "response", 
# with value "yes" for responding and value "no" for non-responding. 
# Please only include PBMC samples.

def get_responder_frequencies(db_path, summary):

    """
    Objective: Get the relative frequencies of selected responders / non-responders

    db_path: path for the db files
    summary: the summary table in part 2
    """

    with sqlite3.connect(db_path) as conn:

        # 1. Get metadata to link samples to subjects and conditions
        metadata_query = query_stat_analysis
        metadata = pd.read_sql_query(metadata_query, conn)
    
    # 2. Merge previous summary with this metadata
    merged_df = pd.merge(summary, metadata, on='sample')

    return merged_df


# Report which cell populations have a significant difference in relative frequencies between responders and non-responders

def report_significance(db_path, merged_df):

    """
    Objective: Get the statistics (including p values) between responders and non-responders 

    db_path: path for the db files
    merged_df: the relative frequencies of selected responders / non-responders
    """

    populations = merged_df['population'].unique()
    stats_results = []

    # Perform statistical testing for each population
    for pop in populations:

        responders = merged_df[(merged_df['population'] == pop) & (merged_df['response'] == 'yes')]['percentage']
        non_responders = merged_df[(merged_df['population'] == pop) & (merged_df['response'] == 'no')]['percentage']
        
        # Mann-Whitney U Test
        u_stat, p_value = mannwhitneyu(responders, non_responders, alternative='two-sided')
        
        stats_results.append({
            'population': pop,
            'median responder': responders.median(),
            'median non-responder': non_responders.median(),
            'p value': p_value,
            'significant': 'Yes' if p_value < 0.05 else 'No'
        })

    return pd.DataFrame(stats_results).sort_values('p value')


######################################################
## 4-5. Data Subset Analysis & Final Parts
######################################################

def get_data_subset(db_path, summary, query, merge = True):

    """

    Objective: Get the metadata from a query and a summary table (optional)

    db_path: db path for the csv file
    summary: the summary table in Part 2 
    query: the query needed for metadata
    merge: whether the metadata is merged to the summary table

    """

    with sqlite3.connect(db_path) as conn:
        
        # 1. Get metadata to link samples to subjects and conditions
        metadata = pd.read_sql_query(query, conn)
    
    # 2. Merge previous summary with this metadata if merge
    if merge:
        return pd.merge(summary, metadata, on='sample')
    else:
        return metadata