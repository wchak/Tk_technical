######################################################
## 1. Data Management
######################################################

## 1.2. Define relational database schema
### Projects -> Subjects -> Samples -> Measurements

SCHEMA_STATEMENTS = [

    "PRAGMA foreign_keys = on",

    # a. Projects Table 
    # -- Handles 'prj1' to 'prj3'
    """
    CREATE TABLE IF NOT EXISTS projects (
        project TEXT PRIMARY KEY  
    )
    """,

    # b. Subjects Table (linked to Projects)
    # -- Handles 'sbj000' to 'sbj3499'
    # -- condition: 'melanoma', 'carcinoma', 'healthy'
    # -- sex: ('M': male, 'F': female)
    """
    CREATE TABLE IF NOT EXISTS subjects (
        subject TEXT PRIMARY KEY, 
        project TEXT NOT NULL,
        condition TEXT, 
        age INTEGER,
        sex TEXT CHECK (sex IN ('M', 'F')), 
        FOREIGN KEY (project) REFERENCES projects(project)
    )
    """,

    # c. Samples Table (linked to Subjects) 
    # -- Handles 'sample00001' to 'sample10499'
    # -- treatment: 'miraclib', 'phauximab', 'none'
    # -- response: 'no', 'yes', nan
    # -- sample_type: 'PBMC', 'WB'
    # -- time_from_treatment_start: 0, 7, 14
    """
    CREATE TABLE IF NOT EXISTS samples (
        sample TEXT PRIMARY KEY, 
        subject TEXT NOT NULL, 
        treatment TEXT,
        response TEXT CHECK (response in ('yes', 'no') or response is NULL), 
        sample_type TEXT,
        time_from_treatment_start INTEGER CHECK (time_from_treatment_start in (0, 7, 14)),
        FOREIGN KEY (subject) REFERENCES subjects(subject)
    )
    """,

    # d. Measurements Table (linked to Samples)
    # -- all integer measurements (known as populations)
    """
    CREATE TABLE IF NOT EXISTS measurements (
        sample TEXT PRIMARY KEY,
        b_cell INTEGER,
        cd8_t_cell INTEGER,
        cd4_t_cell INTEGER,
        nk_cell INTEGER,
        monocyte INTEGER,
        FOREIGN KEY (sample) REFERENCES samples(sample)
    )
    """
]


######################################################
## 2. Initial Analysis - Data Overview
######################################################

# for each sample, calculate the total number of cells by summing the counts across all five populations
# compute the relative frequency of each population as a percentage of the total cell count for that sample
# Each row represents one population from one sample and should have the following columns
    
query_data_overview = """

    WITH t AS (
        SELECT
            sample,
            (b_cell + cd8_t_cell + cd4_t_cell + nk_cell + monocyte) AS total_count,
            b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
        FROM measurements
    )

    SELECT 
        sample, 
        total_count, 
        'b_cell' AS population, 
        b_cell as count, 
        (ROUND( b_cell * 100.0 / total_count, 2)) AS percentage

    FROM t
    UNION ALL SELECT sample, total_count, 'cd8_t_cell', cd8_t_cell, (ROUND( cd8_t_cell * 100.0 / total_count, 2)) FROM t
    UNION ALL SELECT sample, total_count, 'cd4_t_cell', cd4_t_cell, (ROUND( cd4_t_cell * 100.0 / total_count, 2)) FROM t
    UNION ALL SELECT sample, total_count, 'nk_cell', nk_cell, (ROUND( nk_cell * 100.0 / total_count, 2)) FROM t
    UNION ALL SELECT sample, total_count, 'monocyte', monocyte, (ROUND( monocyte * 100.0 / total_count, 2)) FROM t
    ORDER BY sample

"""


######################################################
## 3. Statistical Analysis
######################################################

# Compare the differences in cell population relative frequencies of melanoma patients receiving miraclib 
# who respond (responders) versus those who do not (non-responders), 
# with the overarching aim of predicting response to the treatment miraclib. 
# Response information can be found in column "response", 
# with value "yes" for responding and value "no" for non-responding. 
# Please only include PBMC samples.

query_stat_analysis = """
    SELECT 
        samples.sample, 
        subjects.condition, 
        samples.treatment, 
        samples.sample_type, 
        samples.response
    FROM samples
    JOIN subjects on samples.subject = subjects.subject
    WHERE subjects.condition = 'melanoma' 
        AND samples.treatment = 'miraclib' 
        AND samples.sample_type = 'PBMC'
        AND samples.response in ('yes', 'no')
    """


######################################################
## 4. Data Subset Analysis
######################################################

# explore specific subsets of the data to understand early treatment effects

# Identify all melanoma PBMC samples at baseline (time_from_treatment_start is 0) 
# from patients who have been treated with miraclib

query_part4_1 = """
    SELECT 
        subjects.project,
        samples.sample, 
        subjects.condition, 
        samples.treatment, 
        samples.sample_type, 
        samples.response,
        samples.time_from_treatment_start,
        subjects.sex
    FROM samples
    JOIN subjects on samples.subject = subjects.subject
    WHERE subjects.condition = 'melanoma' 
        AND samples.treatment = 'miraclib' 
        AND samples.sample_type = 'PBMC'
        AND samples.response in ('yes', 'no')
        AND samples.time_from_treatment_start = 0
    """

# Among these samples, extend the query to determine
# How many samples from each project
# How many subjects were responders/non-responders 
# How many subjects were males/females

query_part4_2 = """
    SELECT 
        subjects.project,
        COUNT(samples.sample) AS samples_count,
        SUM(CASE WHEN samples.response = 'yes' THEN 1 ELSE 0 END) AS responders,
        SUM(CASE WHEN samples.response = 'no' THEN 1 ELSE 0 END) AS non_responders,
        SUM(CASE WHEN subjects.sex = 'M' THEN 1 ELSE 0 END) AS males,
        SUM(CASE WHEN subjects.sex = 'F' THEN 1 ELSE 0 END) AS females
    FROM samples 
    JOIN subjects on samples.subject = subjects.subject 
    WHERE subjects.condition = 'melanoma' 
    AND samples.treatment = 'miraclib' 
    AND samples.sample_type = 'PBMC' 
    AND samples.response IN ('yes', 'no') 
    AND samples.time_from_treatment_start = 0
    GROUP BY subjects.project
"""


######################################################
## 5. Final Part
######################################################

# Considering Melanoma males, what is the average number of B cells for responders at time=0? 

metadata_final = """
SELECT 
    ROUND(AVG(measurements.b_cell), 2) as avg_b_cells
FROM measurements
JOIN samples on measurements.sample = samples.sample
JOIN subjects on samples.subject = subjects.subject
WHERE subjects.condition = 'melanoma'
    AND subjects.sex = 'M'
    AND samples.response = 'yes'
    AND samples.time_from_treatment_start = 0;
"""