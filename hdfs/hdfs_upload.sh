#!/bin/bash
# ============================================================
# DSCI 551 Project — HDFS upload + verification
# Uploads the three raw CSVs into an HDFS "raw zone" and prints
# evidence (listing, disk usage, replication, block count).
# ============================================================
#
# Prereqs: Hadoop installed and the local pseudo-distributed
# cluster running.
#
#   start-dfs.sh                    # (once per session)
#   jps                             # expect NameNode + DataNode
#
# Usage:
#   bash hdfs/hdfs_upload.sh
# ============================================================

set -euo pipefail

# SRC_DIR holds the three raw CSVs. Override with:
#   SRC_DIR="/path/to/csvs" bash hdfs/hdfs_upload.sh
# Common locations:
#   ~/Downloads/DSCI 551/Project
#   ~/Library/Mobile Documents/com~apple~CloudDocs/USC/DSCI 551/Project
SRC_DIR="${SRC_DIR:-$HOME/Library/Mobile Documents/com~apple~CloudDocs/USC/DSCI 551/Project}"
HDFS_ROOT="/project"

# Fail fast with a clear message if the CSVs are not where expected.
for f in RAW_recipes.csv RAW_interactions.csv RecipeNLG_dataset.csv; do
  if [ ! -f "${SRC_DIR}/${f}" ]; then
    echo "ERROR: ${SRC_DIR}/${f} not found."
    echo "       Set SRC_DIR to the folder that holds the three raw CSVs:"
    echo "         SRC_DIR=\"/path/to/csvs\" bash hdfs/hdfs_upload.sh"
    exit 1
  fi
done

echo "== [1/4] Creating HDFS directories =="
hdfs dfs -mkdir -p "${HDFS_ROOT}/raw/foodcom"
hdfs dfs -mkdir -p "${HDFS_ROOT}/raw/recipenlg"
hdfs dfs -mkdir -p "${HDFS_ROOT}/curated"

echo ""
echo "== [2/4] Uploading raw CSVs =="
hdfs dfs -put -f "${SRC_DIR}/RAW_recipes.csv"        "${HDFS_ROOT}/raw/foodcom/"
hdfs dfs -put -f "${SRC_DIR}/RAW_interactions.csv"   "${HDFS_ROOT}/raw/foodcom/"
hdfs dfs -put -f "${SRC_DIR}/RecipeNLG_dataset.csv"  "${HDFS_ROOT}/raw/recipenlg/"

echo ""
echo "== [3/4] Listing =="
hdfs dfs -ls -R "${HDFS_ROOT}/raw"

echo ""
echo "== [4/4] Sizes + replication + block count =="
hdfs dfs -du -h        "${HDFS_ROOT}/raw/foodcom"
hdfs dfs -du -h        "${HDFS_ROOT}/raw/recipenlg"
hdfs dfs -stat "%r replicas, %o block size (bytes), %b bytes total" \
  "${HDFS_ROOT}/raw/foodcom/RAW_recipes.csv"
hdfs dfs -stat "%r replicas, %o block size (bytes), %b bytes total" \
  "${HDFS_ROOT}/raw/foodcom/RAW_interactions.csv"
hdfs dfs -stat "%r replicas, %o block size (bytes), %b bytes total" \
  "${HDFS_ROOT}/raw/recipenlg/RecipeNLG_dataset.csv"

echo ""
echo "Block count per file (fsck -blocks -files):"
hdfs fsck "${HDFS_ROOT}/raw/foodcom/RAW_recipes.csv"       -files -blocks | tail -5
hdfs fsck "${HDFS_ROOT}/raw/foodcom/RAW_interactions.csv"  -files -blocks | tail -5
hdfs fsck "${HDFS_ROOT}/raw/recipenlg/RecipeNLG_dataset.csv" -files -blocks | tail -5

echo ""
echo "Done. Take a screenshot of this output for the report."
