"""
DSCI 551 Project — Spark ETL pipeline
======================================
Reads the three raw CSVs, normalizes + explodes ingredients, and writes
four clean CSVs that are loaded into MySQL with LOAD DATA LOCAL INFILE.

Inputs (default paths — override with CLI args):
    ~/Downloads/DSCI 551/Project/RAW_recipes.csv
    ~/Downloads/DSCI 551/Project/RAW_interactions.csv
    ~/Downloads/DSCI 551/Project/RecipeNLG_dataset.csv

Outputs:
    out/recipes.csv
    out/ingredients.csv
    out/recipe_ingredients.csv
    out/interactions.csv

Run locally:
    python3 -m pip install pyspark
    python3 spark/etl_pipeline.py \
        --foodcom-recipes      "/Users/yeoeunchoi/Downloads/DSCI 551/Project/RAW_recipes.csv" \
        --foodcom-interactions "/Users/yeoeunchoi/Downloads/DSCI 551/Project/RAW_interactions.csv" \
        --recipenlg            "/Users/yeoeunchoi/Downloads/DSCI 551/Project/RecipeNLG_dataset.csv" \
        --out                  "./out"

Or via spark-submit once Spark is installed:
    spark-submit spark/etl_pipeline.py --out ./out
"""

import argparse
import os
import re

from pyspark.sql import SparkSession, functions as F, types as T


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def build_spark(app_name: str = "dsci551-etl") -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


# The ingredient column in both RAW_recipes.csv and RecipeNLG_dataset.csv
# is stored as a string like: ['winter squash', 'mexican seasoning', ...]
# We parse it with a regex instead of eval() for safety.
_ING_RE = re.compile(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"")


def _parse_ingredients(s):
    if s is None:
        return []
    return [a or b for (a, b) in _ING_RE.findall(s)]


parse_ingredients = F.udf(_parse_ingredients, T.ArrayType(T.StringType()))


def normalize_ingredient(col):
    """lower-case, collapse whitespace, strip punctuation."""
    c = F.lower(col)
    c = F.regexp_replace(c, r"[^a-z0-9\s]", " ")   # drop punctuation
    c = F.regexp_replace(c, r"\s+", " ")
    c = F.trim(c)
    return c


# ------------------------------------------------------------------
# ETL steps
# ------------------------------------------------------------------
def etl_foodcom_recipes(spark, path):
    df = (
        spark.read
        .option("header", True)
        .option("multiLine", True)
        .option("escape", '"')
        .csv(path)
    )
    recipes = (
        df.select(
            F.col("id").cast("long").alias("recipe_id"),
            F.col("name").alias("title"),
            F.col("minutes").cast("int").alias("minutes"),
            F.col("n_steps").cast("int").alias("n_steps"),
            F.col("n_ingredients").cast("int").alias("n_ingredients"),
            F.to_date("submitted").alias("submitted"),
            F.lit("foodcom").alias("source"),
        )
        .filter(F.col("recipe_id").isNotNull())
        .dropDuplicates(["recipe_id"])
    )
    ri_raw = (
        df.select(
            F.col("id").cast("long").alias("recipe_id"),
            parse_ingredients(F.col("ingredients")).alias("ing_arr"),
        )
        .filter(F.col("recipe_id").isNotNull())
        .withColumn("ingredient_name_raw", F.explode("ing_arr"))
        .drop("ing_arr")
    )
    return recipes, ri_raw


def etl_recipenlg(spark, path):
    df = (
        spark.read
        .option("header", True)
        .option("multiLine", True)
        .option("escape", '"')
        .csv(path)
    )
    # RecipeNLG uses a 0-based row index. Offset by 10,000,000 so its
    # recipe_ids cannot collide with Food.com ids (which max out ~550k).
    recipes = (
        df.select(
            (F.col("_c0").cast("long") + F.lit(10_000_000)).alias("recipe_id"),
            F.col("title").alias("title"),
            F.lit(None).cast("int").alias("minutes"),
            F.lit(None).cast("int").alias("n_steps"),
            F.lit(None).cast("int").alias("n_ingredients"),
            F.lit(None).cast("date").alias("submitted"),
            F.lit("recipenlg").alias("source"),
        )
        .filter(F.col("recipe_id").isNotNull() & F.col("title").isNotNull())
        .dropDuplicates(["recipe_id"])
    )
    ri_raw = (
        df.select(
            (F.col("_c0").cast("long") + F.lit(10_000_000)).alias("recipe_id"),
            parse_ingredients(F.col("NER")).alias("ing_arr"),
        )
        .filter(F.col("recipe_id").isNotNull())
        .withColumn("ingredient_name_raw", F.explode("ing_arr"))
        .drop("ing_arr")
    )
    return recipes, ri_raw


def etl_interactions(spark, path):
    df = (
        spark.read
        .option("header", True)
        .option("multiLine", True)
        .option("escape", '"')
        .csv(path)
    )
    return (
        df.select(
            F.col("user_id").cast("long").alias("user_id"),
            F.col("recipe_id").cast("long").alias("recipe_id"),
            F.col("rating").cast("tinyint").alias("rating"),
            F.to_date("date").alias("interaction_date"),
        )
        .filter(F.col("user_id").isNotNull() & F.col("recipe_id").isNotNull())
    )


def build_ingredients_and_junction(ri_raw_all):
    """
    From a DF of (recipe_id, ingredient_name_raw) produce:
       ingredients(ingredient_id, ingredient_name_raw, ingredient_name_norm)
       recipe_ingredients(recipe_id, ingredient_id)
    """
    ri_norm = (
        ri_raw_all
        .withColumn("ingredient_name_norm", normalize_ingredient("ingredient_name_raw"))
        .filter(F.length("ingredient_name_norm") > 0)
    )

    # Distinct normalized names -> surrogate ingredient_id
    ingredients = (
        ri_norm.select("ingredient_name_norm")
        .distinct()
        .withColumn("ingredient_id",
                    F.row_number().over(
                        __import__("pyspark.sql.window", fromlist=["Window"])
                            .Window.orderBy("ingredient_name_norm")))
        .withColumn("ingredient_name_raw", F.col("ingredient_name_norm"))
        .select("ingredient_id", "ingredient_name_raw", "ingredient_name_norm")
    )

    recipe_ingredients = (
        ri_norm.join(ingredients, "ingredient_name_norm")
        .select("recipe_id", "ingredient_id")
        .dropDuplicates(["recipe_id", "ingredient_id"])
    )
    return ingredients, recipe_ingredients


def write_single_csv(df, path):
    """Write one CSV (with header) to `path`."""
    (
        df.coalesce(1)
        .write.mode("overwrite")
        .option("header", True)
        .csv(path + "__tmp")
    )
    # move the single part file up to the target name
    import glob
    import shutil
    part = glob.glob(os.path.join(path + "__tmp", "part-*.csv"))[0]
    shutil.move(part, path)
    shutil.rmtree(path + "__tmp")


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--foodcom-recipes",
                    default="/Users/yeoeunchoi/Downloads/DSCI 551/Project/RAW_recipes.csv")
    ap.add_argument("--foodcom-interactions",
                    default="/Users/yeoeunchoi/Downloads/DSCI 551/Project/RAW_interactions.csv")
    ap.add_argument("--recipenlg",
                    default="/Users/yeoeunchoi/Downloads/DSCI 551/Project/RecipeNLG_dataset.csv")
    ap.add_argument("--out", default="./out")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    print("[1/5] Food.com recipes")
    fc_recipes, fc_ri_raw = etl_foodcom_recipes(spark, args.foodcom_recipes)

    print("[2/5] RecipeNLG")
    nlg_recipes, nlg_ri_raw = etl_recipenlg(spark, args.recipenlg)

    print("[3/5] Interactions")
    interactions = etl_interactions(spark, args.foodcom_interactions)

    print("[4/5] Union + ingredient dimension")
    recipes_all = fc_recipes.unionByName(nlg_recipes).dropDuplicates(["recipe_id"])
    ri_raw_all  = fc_ri_raw.unionByName(nlg_ri_raw)
    ingredients, recipe_ingredients = build_ingredients_and_junction(ri_raw_all)

    # Drop interactions whose recipe_id is not in our recipes table
    recipe_ids = recipes_all.select("recipe_id")
    interactions = interactions.join(recipe_ids, "recipe_id", "inner")

    print("[5/5] Writing output CSVs")
    write_single_csv(recipes_all,          os.path.join(args.out, "recipes.csv"))
    write_single_csv(ingredients,          os.path.join(args.out, "ingredients.csv"))
    write_single_csv(recipe_ingredients,   os.path.join(args.out, "recipe_ingredients.csv"))
    write_single_csv(interactions,         os.path.join(args.out, "interactions.csv"))

    print("\n=== Row counts ===")
    print(f"  recipes            : {recipes_all.count():,}")
    print(f"  ingredients        : {ingredients.count():,}")
    print(f"  recipe_ingredients : {recipe_ingredients.count():,}")
    print(f"  interactions       : {interactions.count():,}")

    spark.stop()


if __name__ == "__main__":
    main()
