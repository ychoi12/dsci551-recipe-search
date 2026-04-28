-- ============================================================
-- DSCI 551 Project — MySQL Schema (InnoDB)
-- Relational model for Food.com (RAW_recipes/RAW_interactions)
-- & RecipeNLG datasets.
-- ============================================================
-- Run with:
--   mysql -u dsci551 -p
--   mysql> CREATE DATABASE IF NOT EXISTS recipe_project;
--   mysql> USE recipe_project;
--   mysql> SOURCE /path/to/01_schema.sql;
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS recipe_ingredients;
DROP TABLE IF EXISTS interactions;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS recipes;

-- ---------- recipes ----------
CREATE TABLE recipes (
  recipe_id      BIGINT        NOT NULL,
  title          VARCHAR(512)  NOT NULL,
  minutes        INT           NULL,
  n_steps        INT           NULL,
  n_ingredients  INT           NULL,
  submitted      DATE          NULL,
  source         VARCHAR(32)   NOT NULL,  -- 'foodcom' or 'recipenlg'
  PRIMARY KEY (recipe_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- ingredients (dimension table) ----------
CREATE TABLE ingredients (
  ingredient_id        INT           NOT NULL AUTO_INCREMENT,
  ingredient_name_raw  VARCHAR(255)  NOT NULL,
  ingredient_name_norm VARCHAR(255)  NOT NULL,
  PRIMARY KEY (ingredient_id),
  UNIQUE KEY uq_ing_norm (ingredient_name_norm)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- recipe_ingredients (junction) ----------
CREATE TABLE recipe_ingredients (
  recipe_id      BIGINT  NOT NULL,
  ingredient_id  INT     NOT NULL,
  PRIMARY KEY (recipe_id, ingredient_id),
  CONSTRAINT fk_ri_recipe
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),
  CONSTRAINT fk_ri_ingredient
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- interactions (user ratings) ----------
CREATE TABLE interactions (
  interaction_id    BIGINT  NOT NULL AUTO_INCREMENT,
  user_id           BIGINT  NOT NULL,
  recipe_id         BIGINT  NOT NULL,
  rating            TINYINT NULL,
  interaction_date  DATE    NULL,
  PRIMARY KEY (interaction_id),
  CONSTRAINT fk_int_recipe
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;

-- Verify
SHOW TABLES;
