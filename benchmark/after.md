# Benchmark report — `after` indexes

## Summary

| Query                | Best time   |   Rows |
|----------------------|-------------|--------|
| Q1_ingredient_search | 0.2 ms      |     20 |
| Q2_top_rated         | 1529.5 ms   |     20 |
| Q3_quick_recipes     | 0.2 ms      |     20 |
| Q4_multi_ingredient  | 1.9 ms      |      3 |

## Q1_ingredient_search

```sql
SELECT r.recipe_id, r.title
        FROM   recipes r
        JOIN   recipe_ingredients ri ON ri.recipe_id = r.recipe_id
        JOIN   ingredients i          ON i.ingredient_id = ri.ingredient_id
        WHERE  i.ingredient_name_norm = 'garlic'
        LIMIT 20;
```

**Best of 3 runs:** 0.2 ms  |  rows returned: 20

**EXPLAIN:**

| EXPLAIN                                                                                                                                                                                                                                                                                                                    |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -> Limit: 20 row(s)  (cost=1268 rows=20)
    -> Nested loop inner join  (cost=1268 rows=2797)
        -> Covering index lookup on ri using idx_ri_ingredient_recipe (ingredient_id = '2331353')  (cost=289 rows=2797)
        -> Single-row index lookup on r using PRIMARY (recipe_id = ri.recipe_id)  (cost=0.25 rows=1) |

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

**Best of 3 runs:** 1529.5 ms  |  rows returned: 20

**EXPLAIN:**

| EXPLAIN                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -> Limit: 20 row(s)
    -> Sort: avg_rating DESC
        -> Filter: (count(0) >= 20)
            -> Table scan on <temporary>
                -> Aggregate using temporary table
                    -> Nested loop inner join  (cost=344359 rows=1.05e+6)
                        -> Table scan on r  (cost=22177 rows=215441)
                        -> Covering index lookup on x using idx_interactions_recipe_rating (recipe_id = r.recipe_id)  (cost=1.01 rows=4.87) |

## Q3_quick_recipes

```sql
SELECT recipe_id, title, minutes
        FROM   recipes
        WHERE  minutes < 30
        ORDER BY minutes ASC
        LIMIT 20;
```

**Best of 3 runs:** 0.2 ms  |  rows returned: 20

**EXPLAIN:**

| EXPLAIN                                                                                                                                                                                                   |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -> Limit: 20 row(s)  (cost=22177 rows=20)
    -> Index range scan on recipes using idx_recipes_minutes over (NULL < minutes < 30), with index condition: (recipes.minutes < 30)  (cost=22177 rows=107720) |

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

**Best of 3 runs:** 1.9 ms  |  rows returned: 3

**EXPLAIN:**

| EXPLAIN                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -> Limit: 20 row(s)  (cost=3166 rows=20)
    -> Nested loop inner join  (cost=3166 rows=2068)
        -> Nested loop inner join  (cost=2443 rows=2068)
            -> Covering index lookup on ri using idx_ri_ingredient_recipe (ingredient_id = '2693299')  (cost=214 rows=2068)
            -> Single-row covering index lookup on ri using PRIMARY (recipe_id = ri.recipe_id, ingredient_id = '2331353')  (cost=0.978 rows=1)
        -> Single-row index lookup on r using PRIMARY (recipe_id = ri.recipe_id)  (cost=0.25 rows=1) |
