-- ============================================================
-- DSCI 551 Project — Load the Spark ETL outputs into MySQL
-- Run AFTER spark/etl_pipeline.py has produced the four CSVs.
-- ============================================================
-- Launch MySQL with LOCAL INFILE enabled:
--   mysql --local-infile=1 -u dsci551 -p recipe_project
-- 
--   mysql> SET GLOBAL local_infile = 1;
--   mysql> SOURCE /path/to/sql/01_schema.sql;
--   mysql> SOURCE /path/to/sql/05_load_data.sql;
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;
SET UNIQUE_CHECKS      = 0;
SET autocommit         = 0;

-- Note: I replace the paths below with, absolute path to ETL output
-- folder, e.g. /Users/yeoeunchoi/Downloads/DSCI 551/Project/dsci551_project/out
-- -----------------------------------------------------------

LOAD DATA LOCAL INFILE 'REPLACE_WITH_ABS_PATH/out/recipes.csv'
INTO TABLE recipes
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(recipe_id, title, @minutes, @n_steps, @n_ingredients, @submitted, source)
SET minutes       = NULLIF(@minutes,''),
    n_steps       = NULLIF(@n_steps,''),
    n_ingredients = NULLIF(@n_ingredients,''),
    submitted     = NULLIF(@submitted,'');

LOAD DATA LOCAL INFILE 'REPLACE_WITH_ABS_PATH/out/ingredients.csv'
INTO TABLE ingredients
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(ingredient_id, ingredient_name_raw, ingredient_name_norm);

LOAD DATA LOCAL INFILE 'REPLACE_WITH_ABS_PATH/out/recipe_ingredients.csv'
INTO TABLE recipe_ingredients
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(recipe_id, ingredient_id);

LOAD DATA LOCAL INFILE 'REPLACE_WITH_ABS_PATH/out/interactions.csv'
INTO TABLE interactions
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(user_id, recipe_id, @rating, @interaction_date)
SET rating           = NULLIF(@rating,''),
    interaction_date = NULLIF(@interaction_date,'');

COMMIT;
SET FOREIGN_KEY_CHECKS = 1;
SET UNIQUE_CHECKS      = 1;

-- Sanity checks
SELECT 'recipes'            AS tbl, COUNT(*) FROM recipes            UNION ALL
SELECT 'ingredients'        AS tbl, COUNT(*) FROM ingredients        UNION ALL
SELECT 'recipe_ingredients' AS tbl, COUNT(*) FROM recipe_ingredients UNION ALL
SELECT 'interactions'       AS tbl, COUNT(*) FROM interactions;
