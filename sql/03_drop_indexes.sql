-- Drop the secondary indexes so, re-benchmark the "before" case.
-- The PRIMARY KEYs, UNIQUE uq_ing_norm stay.
-- Uses a stored procedure, because MySQL does not support
-- `ALTER TABLE ... DROP INDEX IF EXISTS` as a single statement.
-- Safe to re-run; tolerant of legacy index names (`ingredient_id`).

DELIMITER //

DROP PROCEDURE IF EXISTS drop_idx_if_exists //
CREATE PROCEDURE drop_idx_if_exists(IN tbl VARCHAR(64), IN idx VARCHAR(64))
BEGIN
  IF EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME   = tbl
      AND INDEX_NAME   = idx
  ) THEN
    SET @s = CONCAT('ALTER TABLE ', tbl, ' DROP INDEX ', idx);
    PREPARE stmt FROM @s;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
  END IF;
END //

DELIMITER ;

CALL drop_idx_if_exists('recipe_ingredients', 'idx_ri_ingredient_recipe');
CALL drop_idx_if_exists('recipe_ingredients', 'ingredient_id');
CALL drop_idx_if_exists('interactions',       'idx_interactions_recipe_rating');
CALL drop_idx_if_exists('recipes',            'idx_recipes_minutes');

DROP PROCEDURE drop_idx_if_exists;
