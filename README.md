# DSCI 551 Individual Project — Recipe Search over HDFS → Spark → MySQL

**Author:** Yeoeun Choi (ychoi12)
**Repo:** https://github.com/ychoi12/dsci551-recipe-search
**Datasets:** Food.com (`RAW_recipes.csv`, `RAW_interactions.csv`) and RecipeNLG (`RecipeNLG_dataset.csv`)
**Internal focus:** MySQL InnoDB B+Tree secondary indexes

---

## What this repo is

An end-to-end pipeline that:

1. Uploads 3 raw CSVs to **HDFS** (raw zone, distributed storage proof).
2. Runs a **PySpark** ETL that parses/explodes the messy ingredient lists, normalizes them, and writes 4 clean CSVs.
3. Loads the CSVs into a normalized **MySQL (InnoDB)** schema.
4. Adds three secondary **B+Tree indexes** and benchmarks the speedup with EXPLAIN.
5. Ships a small **Python CLI** that runs the three demo features.
6. Includes full **Word report** in `report/DSCI551_Final_Report.docx`.

---

## Folder layout

```
dsci551_finalproject/
├── 00_setup_check.sh              # check MySQL / Java / Hadoop / Spark / Python
├── sql/
│   ├── 01_schema.sql              # CREATE TABLE (4 tables, InnoDB)
│   ├── 02_indexes.sql             # 3 secondary indexes
│   ├── 03_drop_indexes.sql        # to re-run the "before" benchmark
│   ├── 04_benchmark_queries.sql   # copy/paste EXPLAIN + query set
│   └── 05_load_data.sql           # LOAD DATA LOCAL INFILE from Spark output
├── spark/
│   └── etl_pipeline.py            # PySpark — reads 3 CSVs, writes 4 clean CSVs
├── hdfs/
│   └── hdfs_upload.sh             # puts the raw CSVs into /project/raw/...
├── benchmark/
│   └── benchmark.py               # times 4 queries, captures EXPLAIN plans
├── app/
│   └── cli.py                     # interactive demo used during the Zoom call
└── report/
    └── DSCI551_Final_Report.docx  # 8-page final report
```

---

### 0) Check what is installed

```bash
bash 00_setup_check.sh
```

Install anything marked NOT INSTALLED:

```bash
brew install mysql openjdk@11 hadoop
pip3 install pyspark mysql-connector-python tabulate
```

Start the single-node HDFS cluster:

```bash
start-dfs.sh
# expect: NameNode + DataNode + SecondaryNameNode
jps                 
```

### 1) Raw zone in HDFS

```bash
# prints sizes, replication, block counts
bash hdfs/hdfs_upload.sh            
```



### 2) Spark ETL

```bash
python3 spark/etl_pipeline.py \
  --foodcom-recipes      /path/to/RAW_recipes.csv \
  --foodcom-interactions /path/to/RAW_interactions.csv \
  --recipenlg            /path/to/RecipeNLG_dataset.csv \
  --out                  ./out
```

Produces `out/recipes.csv`, `out/ingredients.csv`, `out/recipe_ingredients.csv`, `out/interactions.csv` and prints row counts.

### 3) MySQL: schema + load

```bash
mysql -u dsci551 -p -e "CREATE DATABASE IF NOT EXISTS recipe_project;"
mysql --local-infile=1 -u dsci551 -p recipe_project < sql/01_schema.sql

# edit REPLACE_WITH_ABS_PATH
# path of the ./out folder produced above, then:
mysql --local-infile=1 -u dsci551 -p recipe_project < sql/05_load_data.sql
```

### 4) Benchmark — before vs after indexes

```bash
# BEFORE (no secondary indexes)
mysql -u dsci551 -p recipe_project < sql/03_drop_indexes.sql 
python3 benchmark/benchmark.py --label before --out benchmark/before.md

# Create the 3 secondary indexes
mysql -u dsci551 -p recipe_project < sql/02_indexes.sql

# AFTER
python3 benchmark/benchmark.py --label after  --out benchmark/after.md
```

### 5) Demo

```bash
python3 app/cli.py
```

Menu lets you run: ingredient search, multi-ingredient AND, top-rated recipes.

---
