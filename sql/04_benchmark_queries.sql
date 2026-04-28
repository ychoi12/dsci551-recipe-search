-- ============================================================
-- DSCI 551 Project — Benchmark Queries
-- Run each query with EXPLAIN to capture plan, then run
-- the query itself to capture wall-clock time.
-- ============================================================

-- ---- Q1: Ingredient search ("find recipes containing garlic") ----
EXPLAIN
SELECT r.recipe_id, r.title
FROM   recipes r
JOIN   recipe_ingredients ri ON ri.recipe_id = r.recipe_id
JOIN   ingredients i          ON i.ingredient_id = ri.ingredient_id
WHERE  i.ingredient_name_norm = 'garlic';

SELECT r.recipe_id, r.title
FROM   recipes r
JOIN   recipe_ingredients ri ON ri.recipe_id = r.recipe_id
JOIN   ingredients i          ON i.ingredient_id = ri.ingredient_id
WHERE  i.ingredient_name_norm = 'garlic'
LIMIT 20;


-- ---- Q2: Top-rated recipes (min 20 ratings) ----
EXPLAIN
SELECT r.title, AVG(x.rating) AS avg_rating, COUNT(*) AS n_ratings
FROM   interactions x
JOIN   recipes r ON r.recipe_id = x.recipe_id
GROUP BY x.recipe_id, r.title
HAVING COUNT(*) >= 20
ORDER BY avg_rating DESC
LIMIT 20;

SELECT r.title, AVG(x.rating) AS avg_rating, COUNT(*) AS n_ratings
FROM   interactions x
JOIN   recipes r ON r.recipe_id = x.recipe_id
GROUP BY x.recipe_id, r.title
HAVING COUNT(*) >= 20
ORDER BY avg_rating DESC
LIMIT 20;


-- ---- Q3: Quick weeknight recipes (minutes < 30) ----
EXPLAIN
SELECT recipe_id, title, minutes
FROM   recipes
WHERE  minutes < 30
ORDER BY minutes ASC
LIMIT 20;

SELECT recipe_id, title, minutes
FROM   recipes
WHERE  minutes < 30
ORDER BY minutes ASC
LIMIT 20;


-- ---- Q4: Multi-ingredient search ("garlic AND chicken") ----
EXPLAIN
SELECT r.recipe_id, r.title
FROM   recipes r
WHERE  r.recipe_id IN (
    SELECT ri.recipe_id
    FROM   recipe_ingredients ri
    JOIN   ingredients i ON i.ingredient_id = ri.ingredient_id
    WHERE  i.ingredient_name_norm = 'garlic'
)
AND r.recipe_id IN (
    SELECT ri.recipe_id
    FROM   recipe_ingredients ri
    JOIN   ingredients i ON i.ingredient_id = ri.ingredient_id
    WHERE  i.ingredient_name_norm = 'chicken'
)
LIMIT 20;
