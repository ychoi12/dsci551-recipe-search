-- ============================================================
-- DSCI 551 Project — Secondary Indexes
-- Run AFTER the benchmark "before" pass, to measure speedup.
-- ============================================================

-- Ingredient search: recipe_ingredients(ingredient_id, recipe_id)
-- B+Tree clustered on (ingredient_id) lets us seek the leaf
-- range for one ingredient and read recipe_ids sequentially.
CREATE INDEX idx_ri_ingredient_recipe
  ON recipe_ingredients (ingredient_id, recipe_id);

-- Top-rated: cover (recipe_id, rating) so GROUP BY recipe_id
-- and AVG(rating) are satisfied by the index alone ("Using index").
CREATE INDEX idx_interactions_recipe_rating
  ON interactions (recipe_id, rating);

-- Recipes under N minutes.
CREATE INDEX idx_recipes_minutes
  ON recipes (minutes);

-- Inspect
SHOW INDEX FROM recipe_ingredients;
SHOW INDEX FROM interactions;
SHOW INDEX FROM recipes;
SHOW INDEX FROM ingredients;
