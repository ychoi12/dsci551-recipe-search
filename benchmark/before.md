# Benchmark report — `before` indexes

## Summary

| Query                | Best time   |   Rows |
|----------------------|-------------|--------|
| Q1_ingredient_search | 11.5 ms     |     20 |
| Q2_top_rated         | 2853.7 ms   |     20 |
| Q3_quick_recipes     | 30.9 ms     |     20 |
| Q4_multi_ingredient  | 213.6 ms    |      3 |

## Q1_ingredient_search

```sql
SELECT r.recipe_id, r.title
        FROM   recipes r
        JOIN   recipe_ingredients ri ON ri.recipe_id = r.recipe_id
        JOIN   ingredients i          ON i.ingredient_id = ri.ingredient_id
        WHERE  i.ingredient_name_norm = 'garlic'
        LIMIT 20;
```

**Best of 3 runs:** 11.5 ms  |  rows returned: 20

**EXPLAIN:**

| EXPLAIN                                                                                                                                                                                                                                                                                            |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -> Limit: 20 row(s)  (cost=252526 rows=20)
    -> Nested loop inner join  (cost=252526 rows=215441)
        -> Table scan on r  (cost=22177 rows=215441)
        -> Single-row covering index lookup on ri using PRIMARY (recipe_id = r.recipe_id, ingredient_id = '2331353')  (cost=0.969 rows=1) |

## Q2_top_rated

```sql
SELECT r.title, AVG(x.rating) AS avg_rating, COUNT(*) AS n_ratings
        FROM   interactions x
        JOIN   recipes r ON r.recipe_id = x.recipe_id
        GROUP BY x.recipe_id, r.title
        HAVING COUNT(*) >= 20
        ORDER BY avg_rating DESC
        LIMIT 20;
```

**Best of 3 runs:** 2853.7 ms  |  rows returned: 20

**EXPLAIN:**

| EXPLAIN                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -> Limit: 20 row(s)
    -> Sort: avg_rating DESC
        -> Filter: (count(0) >= 20)
            -> Table scan on <temporary>
                -> Aggregate using temporary table
                    -> Nested loop inner join  (cost=509964 rows=1.13e+6)
                        -> Filter: (x.recipe_id is not null)  (cost=114289 rows=1.13e+6)
                            -> Table scan on x  (cost=114289 rows=1.13e+6)
                        -> Single-row index lookup on r using PRIMARY (recipe_id = x.recipe_id)  (cost=0.25 rows=1) |

## Q3_quick_recipes

```sql
SELECT recipe_id, title, minutes
        FROM   recipes
        WHERE  minutes < 30
        ORDER BY minutes ASC
        LIMIT 20;
```

**Best of 3 runs:** 30.9 ms  |  rows returned: 20

**EXPLAIN:**

| EXPLAIN                                                                                                                                                                                                                                                                 |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -> Limit: 20 row(s)  (cost=22177 rows=20)
    -> Sort: recipes.minutes, limit input to 20 row(s) per chunk  (cost=22177 rows=215441)
        -> Filter: (recipes.minutes < 30)  (cost=22177 rows=215441)
            -> Table scan on recipes  (cost=22177 rows=215441) |

## Q4_multi_ingredient

```sql
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
```

**Best of 3 runs:** 213.6 ms  |  rows returned: 3

**EXPLAIN:**

| EXPLAIN                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -> Limit: 20 row(s)  (cost=479518 rows=20)
    -> Nested loop inner join  (cost=479518 rows=215441)
        -> Nested loop inner join  (cost=250935 rows=215441)
            -> Table scan on r  (cost=22351 rows=215441)
            -> Single-row covering index lookup on ri using PRIMARY (recipe_id = r.recipe_id, ingredient_id = '2331353')  (cost=0.961 rows=1)
        -> Single-row covering index lookup on ri using PRIMARY (recipe_id = r.recipe_id, ingredient_id = '2693299')  (cost=0.961 rows=1) |
