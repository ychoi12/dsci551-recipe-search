"""
DSCI 551 Project — Benchmark
=============================

import argparse
import time

import mysql.connector
from tabulate import tabulate


QUERIES = {
    "Q1_ingredient_search": """
        SELECT r.recipe_id, r.title
        FROM   recipes r
        JOIN   recipe_ingredients ri ON ri.recipe_id = r.recipe_id
        JOIN   ingredients i          ON i.ingredient_id = ri.ingredient_id
        WHERE  i.ingredient_name_norm = 'garlic'
        LIMIT 20;
    """,
    "Q2_top_rated": """
        SELECT r.title, AVG(x.rating) AS avg_rating, COUNT(*) AS n_ratings
        FROM   interactions x
        JOIN   recipes r ON r.recipe_id = x.recipe_id
        GROUP BY x.recipe_id, r.title
        HAVING COUNT(*) >= 20
        ORDER BY avg_rating DESC
        LIMIT 20;
    """,
    "Q3_quick_recipes": """
        SELECT recipe_id, title, minutes
        FROM   recipes
        WHERE  minutes < 30
        ORDER BY minutes ASC
        LIMIT 20;
    """,
    "Q4_multi_ingredient": """
        SELECT r.recipe_id, r.title
        FROM   recipes r
        WHERE  r.recipe_id IN (
            SELECT ri.recipe_id FROM recipe_ingredients ri
            JOIN ingredients i ON i.ingredient_id = ri.ingredient_id
            WHERE i.ingredient_name_norm = 'garlic'
        )
        AND r.recipe_id IN (
            SELECT ri.recipe_id FROM recipe_ingredients ri
            JOIN ingredients i ON i.ingredient_id = ri.ingredient_id
            WHERE i.ingredient_name_norm = 'chicken'
        )
        LIMIT 20;
    """,
}


def time_query(cur, sql, trials=3):
    best = float("inf")
    rows = 0
    for _ in range(trials):
        t0 = time.perf_counter()
        cur.execute(sql)
        result = cur.fetchall()
        dt = time.perf_counter() - t0
        best = min(best, dt)
        rows = len(result)
    return best, rows


def explain(cur, sql):
    cur.execute("EXPLAIN " + sql.strip().rstrip(";"))
    cols = [d[0] for d in cur.description]
    return cols, cur.fetchall()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--user", default="dsci551")
    ap.add_argument("--password", default=None,
                    help="Prompt will appear if omitted.")
    ap.add_argument("--database", default="recipe_project")
    ap.add_argument("--label", required=True,
                    help="'before' or 'after' index creation.")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if args.password is None:
        import getpass
        args.password = getpass.getpass("MySQL password: ")

    conn = mysql.connector.connect(
        host=args.host, user=args.user, password=args.password,
        database=args.database, autocommit=True,
    )
    cur = conn.cursor()

    # Warm up the buffer pool once
    cur.execute("SELECT COUNT(*) FROM recipes")
    cur.fetchall()

    lines = [f"# Benchmark report — `{args.label}` indexes", ""]
    timing_rows = []

    for name, sql in QUERIES.items():
        print(f"Running {name} ...")
        sec, rows = time_query(cur, sql, trials=3)
        timing_rows.append([name, f"{sec*1000:.1f} ms", rows])

        cols, plan = explain(cur, sql)
        lines.append(f"## {name}")
        lines.append("")
        lines.append("```sql")
        lines.append(sql.strip())
        lines.append("```")
        lines.append("")
        lines.append(f"**Best of 3 runs:** {sec*1000:.1f} ms  |  rows returned: {rows}")
        lines.append("")
        lines.append("**EXPLAIN:**")
        lines.append("")
        lines.append(tabulate(plan, headers=cols, tablefmt="github"))
        lines.append("")

    summary = tabulate(
        timing_rows,
        headers=["Query", "Best time", "Rows"],
        tablefmt="github",
    )
    lines.insert(2, "## Summary")
    lines.insert(3, "")
    lines.insert(4, summary)
    lines.insert(5, "")

    with open(args.out, "w") as f:
        f.write("\n".join(lines))

    print("\nWrote", args.out)
    print(summary)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
