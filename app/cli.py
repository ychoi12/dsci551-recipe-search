"""
DSCI 551 Project — Demo CLI
============================
Small interactive CLI that exposes the three core features:
   1) Recipes containing one ingredient
   2) Recipes containing two ingredients (AND)
   3) Top-rated recipes

Run:
    pip3 install mysql-connector-python tabulate
    python3 app/cli.py
"""

import getpass
import sys

import mysql.connector
from tabulate import tabulate


DISPLAY_LIMIT = 20


def connect():
    host = "127.0.0.1"
    user = "dsci551"
    db = "recipe_project"
    pwd = getpass.getpass("MySQL password: ")
    print(f"Connecting to {db}@{host} as {user} ...")
    return mysql.connector.connect(
        host=host,
        user=user,
        password=pwd,
        database=db,
        autocommit=True,
    )


def run(cur, sql, params=()):
    cur.execute(sql, params)
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchall() if cur.description else []
    return cols, rows


def explain(cur, sql, params=()):
    cur.execute("EXPLAIN " + sql.rstrip(";"), params)
    cols = [d[0] for d in cur.description]
    return cols, cur.fetchall()


def show_results(cur, sql, params=(), intro=None):
    cols, rows = run(cur, sql, params)
    if intro:
        print(f"\n{intro}")
    print("\nResults:")
    print(tabulate(rows, headers=cols, tablefmt="github"))
    ec, ep = explain(cur, sql, params)
    print("\nEXPLAIN:")
    print(tabulate(ep, headers=ec, tablefmt="github"))


def feat_ingredient_search(cur):
    ing = input("Ingredient to contain (normalized, e.g. 'garlic'): ").strip().lower()
    sql = f"""
      SELECT r.recipe_id,
             r.title,
             i.ingredient_name_norm AS matched_ingredient
      FROM   recipes r
      JOIN   recipe_ingredients ri ON ri.recipe_id = r.recipe_id
      JOIN   ingredients i          ON i.ingredient_id = ri.ingredient_id
      WHERE  i.ingredient_name_norm = %s
      LIMIT  {DISPLAY_LIMIT}
    """
    show_results(
        cur,
        sql,
        (ing,),
        intro="Showing recipes whose ingredient list contains the requested ingredient.",
    )


def feat_multi_ingredient(cur):
    a = input("First ingredient to contain  : ").strip().lower()
    b = input("Second ingredient to contain : ").strip().lower()
    sql = f"""
      SELECT r.recipe_id,
             r.title,
             CONCAT(%s, ', ', %s) AS matched_ingredients
      FROM   recipes r
      WHERE  r.recipe_id IN (
          SELECT ri.recipe_id
          FROM   recipe_ingredients ri
          JOIN   ingredients i ON i.ingredient_id = ri.ingredient_id
          WHERE  i.ingredient_name_norm = %s
      )
      AND r.recipe_id IN (
          SELECT ri.recipe_id
          FROM   recipe_ingredients ri
          JOIN   ingredients i ON i.ingredient_id = ri.ingredient_id
          WHERE  i.ingredient_name_norm = %s
      )
      LIMIT  {DISPLAY_LIMIT}
    """
    show_results(
        cur,
        sql,
        (a, b, a, b),
        intro="Showing recipes whose ingredient list contains both requested ingredients.",
    )


def feat_top_rated(cur):
    raw = input("Min # of ratings a recipe must have (e.g. 20): ").strip() or "20"
    try:
        n = int(raw)
    except ValueError:
        print(f"  '{raw}' is not a whole number — using 20.")
        n = 20
    sql = f"""
      SELECT r.title,
             AVG(x.rating) AS avg_rating,
             COUNT(*) AS n_ratings
      FROM   interactions x
      JOIN   recipes r ON r.recipe_id = x.recipe_id
      GROUP BY x.recipe_id, r.title
      HAVING COUNT(*) >= %s
      ORDER BY avg_rating DESC
      LIMIT  {DISPLAY_LIMIT}
    """
    show_results(
        cur,
        sql,
        (n,),
        intro="Showing the highest-rated recipes among recipes meeting the minimum rating count.",
    )


MENU = """
================ DSCI 551 — Recipe DB demo ================
  1) Recipes containing one ingredient
  2) Recipes containing two ingredients (AND)
  3) Top-rated recipes
  q) quit
===========================================================
choice> """


def main():
    conn = connect()
    cur = conn.cursor()
    try:
        while True:
            choice = input(MENU).strip().lower()
            if choice == "1":
                feat_ingredient_search(cur)
            elif choice == "2":
                feat_multi_ingredient(cur)
            elif choice == "3":
                feat_top_rated(cur)
            elif choice == "q":
                break
            else:
                print("Unknown choice.")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
