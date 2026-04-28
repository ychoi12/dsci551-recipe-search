#!/bin/bash
# ============================================================
# DSCI 551 Project
#   bash 00_setup_check.sh
# ============================================================

echo "=========================================="
echo " DSCI 551 Environment Check"
echo "=========================================="
echo ""

echo "[1] MySQL"
if command -v mysql >/dev/null 2>&1; then
  mysql --version
else
  echo "  NOT INSTALLED.  Install with:  brew install mysql"
fi
echo ""

echo "[2] Python 3"
if command -v python3 >/dev/null 2>&1; then
  python3 --version
else
  echo "  NOT INSTALLED.  Install with:  brew install python"
fi
echo ""

echo "[3] Java (required for Hadoop/Spark)"
if command -v java >/dev/null 2>&1; then
  java -version 2>&1 | head -1
else
  echo "  NOT INSTALLED.  Install with:  brew install openjdk@11"
fi
echo ""

echo "[4] Hadoop / HDFS"
if command -v hdfs >/dev/null 2>&1; then
  hdfs version 2>&1 | head -1
else
  echo "  NOT INSTALLED.  Install with:  brew install hadoop"
fi
echo ""

echo "[5] Spark (pyspark)"
if command -v spark-submit >/dev/null 2>&1; then
  spark-submit --version 2>&1 | grep -i version | head -2
elif python3 -c "import pyspark" 2>/dev/null; then
  python3 -c "import pyspark; print('pyspark', pyspark.__version__, '(pip)')"
else
  echo "  NOT INSTALLED.  Install with:  pip3 install pyspark"
fi
echo ""

echo "[6] Python MySQL connector"
if python3 -c "import mysql.connector" 2>/dev/null; then
  echo "  mysql-connector-python: OK"
else
  echo "  NOT INSTALLED.  Install with:  pip3 install mysql-connector-python"
fi
echo ""

echo "=========================================="
echo " Done. Marked should be installed,
       before running the pipeline."
echo "=========================================="
